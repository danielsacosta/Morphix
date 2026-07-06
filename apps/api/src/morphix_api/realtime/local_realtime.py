"""Local realtime bridge.

In production the realtime path is:

    API Gateway (WebSocket) -> Lambda connection_handler -> DynamoDB connections
    DynamoDB Streams         -> Lambda broadcaster       -> API Gateway Management API
                                                                       |
                                                                       v
                                                                browser WebSocket

In local we run a single uvicorn process. To stay behaviorally identical
to prod while reusing as much prod code as possible:

  - A FastAPI ``/ws`` WebSocket endpoint wires into the SAME prod Lambda
    ``connection_handler.handler`` to put/delete rows in the SAME
    DynamoDB ``connections`` table (LocalStack). The handler runs with
    synthetic API Gateway WebSocket events, so its DynamoDB writes are
    real and observable.

  - A background thread polls LocalStack's DynamoDB Streams for the jobs
    table. On INSERT/MODIFY it deserializes new images with the SAME
    prod ``_deserialize``/``_job_event`` helpers from
    ``realtime.broadcaster`` and dispatches the same ``job.updated``
    payload shape to every in-process WebSocket owned by the same
    ``user_id``.

    The only deviation is the delivery transport: instead of
    ``apigatewaymanagementapi.post_to_connection`` (which has no local
    equivalent), we send directly through the in-process WebSocket
    registry. Payload format, job field projection and connection
    table lifecycle are unmodified.
"""

from __future__ import annotations

import asyncio
import json
import os
import threading
import time
from typing import Any
from uuid import uuid4

import boto3
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from .broadcaster import _deserialize, _job_event
from .connection_handler import handler as connection_handler

_CONNECTIONS: dict[str, tuple[str, WebSocket]] = {}
_LOOP: asyncio.AbstractEventLoop | None = None
_POLLER_STOP = threading.Event()
_POLLER_THREAD: threading.Thread | None = None


def _event(route_key: str, connection_id: str, user_id: str | None = None) -> dict[str, Any]:
    event: dict[str, Any] = {
        "requestContext": {"routeKey": route_key, "connectionId": connection_id},
        "headers": {},
    }
    if user_id is not None:
        event["queryStringParameters"] = {"user_id": user_id}
    return event


async def _websocket_endpoint(ws: WebSocket) -> None:
    await ws.accept()
    user_id = (ws.query_params.get("user_id") or ws.query_params.get("userId") or "").strip()
    if not user_id:
        await ws.close(code=4401)
        return

    connection_id = uuid4().hex
    try:
        connection_handler(_event("$connect", connection_id, user_id), None)
    except Exception:
        # Keep the socket alive even if the DynamoDB put for the
        # connections table fails; the in-process registry still
        # broadcasts to this client.
        pass

    _CONNECTIONS[connection_id] = (user_id, ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        _CONNECTIONS.pop(connection_id, None)
        try:
            connection_handler(_event("$disconnect", connection_id), None)
        except Exception:
            pass


def _broadcast_local(job: dict[str, Any]) -> None:
    user_id = str(job.get("user_id") or "")
    if not user_id or _LOOP is None:
        return

    payload = json.dumps(_job_event(job), separators=(",", ":"))
    matching = [cid for cid, (uid, _ws) in _CONNECTIONS.items() if uid == user_id]
    for cid in matching:
        registered = _CONNECTIONS.get(cid)
        if not registered:
            continue
        _, ws = registered
        try:
            asyncio.run_coroutine_threadsafe(ws.send_text(payload), _LOOP)
        except Exception:
            _CONNECTIONS.pop(cid, None)


def _streams_poller() -> None:
    region = os.getenv("AWS_REGION", "us-east-1")
    endpoint_url = os.getenv("AWS_ENDPOINT_URL") or None
    jobs_table_name = os.getenv("JOBS_TABLE_NAME", "")
    if not jobs_table_name:
        return

    dynamodb = boto3.client("dynamodb", region_name=region, endpoint_url=endpoint_url)
    streams = boto3.client("dynamodbstreams", region_name=region, endpoint_url=endpoint_url)

    stream_arn: str | None = None
    while not _POLLER_STOP.is_set() and stream_arn is None:
        try:
            response = dynamodb.describe_table(TableName=jobs_table_name)
            stream_arn = (response.get("Table") or {}).get("LatestStreamArn")
        except Exception:
            time.sleep(1)
        if stream_arn is None:
            time.sleep(1)

    if stream_arn is None:
        return

    iterator_id: str | None = None
    while not _POLLER_STOP.is_set():
        try:
            if iterator_id is None:
                description = streams.describe_stream(StreamArn=stream_arn)
                shards = (description.get("StreamDescription") or {}).get("Shards") or []
                if not shards:
                    time.sleep(1)
                    continue
                shard_id = shards[0]["ShardId"]
                iterator_response = streams.get_shard_iterator(
                    StreamArn=stream_arn,
                    ShardId=shard_id,
                    ShardIteratorType="LATEST",
                )
                iterator_id = iterator_response.get("ShardIterator")

            if iterator_id is None:
                time.sleep(1)
                continue

            records_response = streams.get_records(ShardIterator=iterator_id)
            iterator_id = records_response.get("NextShardIterator") or iterator_id
            for record in records_response.get("Records") or []:
                if record.get("eventName") not in {"INSERT", "MODIFY"}:
                    continue
                image = (record.get("dynamodb") or {}).get("NewImage")
                if not image:
                    continue
                try:
                    job = _deserialize(image)
                except Exception:
                    continue
                if isinstance(job, dict):
                    _broadcast_local(job)
        except Exception:
            iterator_id = None
            time.sleep(1)
            continue
        time.sleep(1)


def register_local_realtime(app: FastAPI) -> None:
    @app.websocket("/ws")
    async def _ws_endpoint(ws: WebSocket) -> None:
        await _websocket_endpoint(ws)

    @app.on_event("startup")
    async def _start_local_realtime() -> None:
        global _LOOP, _POLLER_THREAD
        _LOOP = asyncio.get_running_loop()
        _POLLER_STOP.clear()
        if _POLLER_THREAD is None or not _POLLER_THREAD.is_alive():
            _POLLER_THREAD = threading.Thread(target=_streams_poller, name="morphix-local-streams", daemon=True)
            _POLLER_THREAD.start()

    @app.on_event("shutdown")
    async def _stop_local_realtime() -> None:
        _POLLER_STOP.set()