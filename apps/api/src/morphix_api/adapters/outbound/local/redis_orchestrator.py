from __future__ import annotations

import json
from uuid import uuid4

from ....application.ports.conversion_orchestrator import ConversionOrchestrator
from ....core.config import Settings
from ....domain.entities.job import Job


class RedisConversionOrchestrator(ConversionOrchestrator):
    def __init__(self, settings: Settings) -> None:
        from redis import Redis

        self._redis = Redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=3,
            socket_timeout=5,
        )
        self._stream = settings.conversion_stream

    def start_conversion(self, job: Job) -> str:
        payload = {"task_token": None, "payload": job.to_item()}
        message_id = self._redis.xadd(self._stream, {"body": json.dumps(payload, separators=(",", ":"))})
        return f"arn:redis:local:execution:morphix:{message_id or uuid4().hex}"
