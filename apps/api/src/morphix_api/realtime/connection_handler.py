from __future__ import annotations

import os
import time
from typing import Any

import boto3


def _table():
    table_name = os.getenv("CONNECTIONS_TABLE_NAME", "")
    region = os.getenv("AWS_REGION", "us-east-1")
    return boto3.resource("dynamodb", region_name=region).Table(table_name)


def _response(status_code: int) -> dict[str, int]:
    return {"statusCode": status_code}


def _extract_user_id(event: dict[str, Any]) -> str:
    query = event.get("queryStringParameters") or {}
    headers = event.get("headers") or {}
    return str(query.get("user_id") or query.get("userId") or headers.get("x-user-id") or headers.get("X-User-Id") or "").strip()


def handler(event: dict[str, Any], _context: object) -> dict[str, int]:
    request_context = event.get("requestContext") or {}
    route_key = request_context.get("routeKey")
    connection_id = request_context.get("connectionId")

    if not connection_id:
        return _response(400)

    if route_key == "$connect":
        user_id = _extract_user_id(event)
        if not user_id:
            return _response(401)

        now = int(time.time())
        ttl_seconds = int(os.getenv("CONNECTION_TTL_SECONDS", "86400"))
        _table().put_item(
            Item={
                "connection_id": connection_id,
                "user_id": user_id,
                "connected_at": now,
                "expires_at": now + ttl_seconds,
            }
        )
        return _response(200)

    if route_key == "$disconnect":
        _table().delete_item(Key={"connection_id": connection_id})
        return _response(200)

    return _response(200)
