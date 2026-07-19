"""Redis-backed realtime bridge for the local Docker Compose runtime."""

from __future__ import annotations

import asyncio
import json
import threading
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from ..core.config import Settings

_CONNECTIONS: dict[str, tuple[str, WebSocket]] = {}
_LOOP: asyncio.AbstractEventLoop | None = None
_SUBSCRIBER_STOP = threading.Event()
_SUBSCRIBER_THREAD: threading.Thread | None = None


def _broadcast_local(event: dict[str, Any]) -> None:
    job = event.get("job") or {}
    user_id = str(job.get("user_id") or "")
    if not user_id or _LOOP is None:
        return

    payload = json.dumps(event, separators=(",", ":"))
    matching = [cid for cid, (uid, _ws) in _CONNECTIONS.items() if uid == user_id]
    for connection_id in matching:
        registered = _CONNECTIONS.get(connection_id)
        if not registered:
            continue
        _, websocket = registered
        try:
            asyncio.run_coroutine_threadsafe(websocket.send_text(payload), _LOOP)
        except Exception:
            _CONNECTIONS.pop(connection_id, None)


def _redis_subscriber(settings: Settings) -> None:
    from redis import Redis

    while not _SUBSCRIBER_STOP.is_set():
        try:
            redis = Redis.from_url(settings.redis_url, decode_responses=True, socket_connect_timeout=1)
            pubsub = redis.pubsub(ignore_subscribe_messages=True)
            pubsub.subscribe(settings.realtime_channel)
            for message in pubsub.listen():
                if _SUBSCRIBER_STOP.is_set():
                    break
                if message.get("type") != "message":
                    continue
                try:
                    event = json.loads(str(message.get("data") or "{}"))
                except json.JSONDecodeError:
                    continue
                if isinstance(event, dict):
                    _broadcast_local(event)
            pubsub.close()
        except Exception:
            if not _SUBSCRIBER_STOP.wait(1):
                continue


async def _websocket_endpoint(ws: WebSocket) -> None:
    await ws.accept()
    user_id = (ws.query_params.get("user_id") or ws.query_params.get("userId") or "").strip()
    if not user_id:
        await ws.close(code=4401)
        return

    connection_id = uuid4().hex
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


def register_local_realtime(app: FastAPI, settings: Settings) -> None:
    @app.websocket("/ws")
    async def _ws_endpoint(ws: WebSocket) -> None:
        await _websocket_endpoint(ws)

    @app.on_event("startup")
    async def _start_local_realtime() -> None:
        global _LOOP, _SUBSCRIBER_THREAD
        _LOOP = asyncio.get_running_loop()
        _SUBSCRIBER_STOP.clear()
        if _SUBSCRIBER_THREAD is None or not _SUBSCRIBER_THREAD.is_alive():
            _SUBSCRIBER_THREAD = threading.Thread(
                target=_redis_subscriber,
                args=(settings,),
                name="morphix-local-realtime",
                daemon=True,
            )
            _SUBSCRIBER_THREAD.start()

    @app.on_event("shutdown")
    async def _stop_local_realtime() -> None:
        _SUBSCRIBER_STOP.set()
        if _SUBSCRIBER_THREAD and _SUBSCRIBER_THREAD.is_alive():
            _SUBSCRIBER_THREAD.join(timeout=2)
