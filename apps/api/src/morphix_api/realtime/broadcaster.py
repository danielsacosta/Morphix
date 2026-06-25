from __future__ import annotations

import json
import os
from decimal import Decimal
from typing import Any

import boto3
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.types import TypeDeserializer
from botocore.exceptions import ClientError

_DESERIALIZER = TypeDeserializer()

JOB_FIELDS = {
    "job_id",
    "user_id",
    "input_key",
    "output_key",
    "source_format",
    "target_format",
    "status",
    "error_message",
    "created_at",
    "updated_at",
    "expires_at",
    "file_size",
    "duration_seconds",
    "state_machine_execution_arn",
    "batch_id",
    "queue_position",
    "queued_at",
    "queue_message_id",
    "progress_percent",
    "progress_stage",
}


def _json_safe(value: Any) -> Any:
    if isinstance(value, Decimal):
        return int(value) if value % 1 == 0 else float(value)
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


def _deserialize(image: dict[str, Any]) -> dict[str, Any]:
    return {key: _json_safe(_DESERIALIZER.deserialize(value)) for key, value in image.items()}


def _connections_table():
    table_name = os.getenv("CONNECTIONS_TABLE_NAME", "")
    region = os.getenv("AWS_REGION", "us-east-1")
    return boto3.resource("dynamodb", region_name=region).Table(table_name)


def _management_client():
    endpoint = os.getenv("WEBSOCKET_API_ENDPOINT", "")
    region = os.getenv("AWS_REGION", "us-east-1")
    return boto3.client("apigatewaymanagementapi", region_name=region, endpoint_url=endpoint)


def _job_event(job: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "job.updated",
        "job": {key: job.get(key) for key in JOB_FIELDS if key in job},
    }


def _delete_connection(connection_id: str) -> None:
    _connections_table().delete_item(Key={"connection_id": connection_id})


def _post_to_connection(connection_id: str, payload: bytes) -> None:
    try:
        _management_client().post_to_connection(ConnectionId=connection_id, Data=payload)
    except ClientError as error:
        code = error.response.get("Error", {}).get("Code")
        if code in {"GoneException", "410"}:
            _delete_connection(connection_id)
            return
        raise


def _broadcast(job: dict[str, Any]) -> None:
    user_id = str(job.get("user_id") or "")
    job_id = str(job.get("job_id") or "")
    if not user_id or not job_id:
        return

    payload = json.dumps(_job_event(job), separators=(",", ":")).encode("utf-8")
    response = _connections_table().query(IndexName="user_id-index", KeyConditionExpression=Key("user_id").eq(user_id))
    for connection in response.get("Items", []):
        connection_id = str(connection.get("connection_id") or "")
        if connection_id:
            _post_to_connection(connection_id, payload)


def handler(event: dict[str, Any], _context: object) -> dict[str, int]:
    for record in event.get("Records", []):
        if record.get("eventName") not in {"INSERT", "MODIFY"}:
            continue

        new_image = (record.get("dynamodb") or {}).get("NewImage")
        if new_image:
            _broadcast(_deserialize(new_image))

    return {"statusCode": 200}
