from __future__ import annotations

from dataclasses import dataclass

import boto3

from ....core.config import Settings


@dataclass(frozen=True)
class QueueMessage:
    body: str
    receipt_handle: str


class SQSConversionQueue:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._sqs = boto3.client("sqs", region_name=settings.aws_region)

    def receive_one(self) -> QueueMessage | None:
        response = self._sqs.receive_message(
            QueueUrl=self.settings.conversion_queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=self.settings.queue_wait_time_seconds,
        )
        messages = response.get("Messages", [])
        if not messages:
            return None
        message = messages[0]
        return QueueMessage(body=str(message["Body"]), receipt_handle=str(message["ReceiptHandle"]))

    def delete(self, message: QueueMessage) -> None:
        self._sqs.delete_message(QueueUrl=self.settings.conversion_queue_url, ReceiptHandle=message.receipt_handle)
