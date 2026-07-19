from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from ....core.config import Settings


@dataclass(frozen=True)
class QueueMessage:
    body: str
    receipt_handle: str


class RedisConversionQueue:
    def __init__(self, settings: Settings) -> None:
        from redis import Redis

        self._redis = Redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=3,
            socket_timeout=max(5, settings.queue_wait_time_seconds + 5),
        )
        self._stream = settings.conversion_stream
        self._group = f"{settings.project_name}:workers"
        self._consumer = f"{settings.project_name}:{uuid4().hex}"
        self._block_ms = max(1, settings.queue_wait_time_seconds) * 1000
        try:
            self._redis.xgroup_create(self._stream, self._group, id="0", mkstream=True)
        except Exception as error:
            if "BUSYGROUP" not in str(error):
                raise

    def receive_one(self) -> QueueMessage | None:
        try:
            claimed = self._redis.xautoclaim(
                self._stream,
                self._group,
                self._consumer,
                min_idle_time=180_000,
                start_id="0-0",
                count=1,
            )
            if len(claimed) > 1 and claimed[1]:
                message_id, fields = claimed[1][0]
                return QueueMessage(body=str(fields["body"]), receipt_handle=str(message_id))
        except Exception:
            # Redis versions without XAUTOCLAIM still support normal reads.
            pass

        response = self._redis.xreadgroup(
            self._group,
            self._consumer,
            {self._stream: ">"},
            count=1,
            block=self._block_ms,
        )
        if not response:
            return None
        _stream_name, messages = response[0]
        if not messages:
            return None
        message_id, fields = messages[0]
        return QueueMessage(body=str(fields["body"]), receipt_handle=str(message_id))

    def delete(self, message: QueueMessage) -> None:
        self._redis.xack(self._stream, self._group, message.receipt_handle)
