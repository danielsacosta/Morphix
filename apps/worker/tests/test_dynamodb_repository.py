from __future__ import annotations

from decimal import Decimal
from typing import Any

from morphix_worker.adapters.outbound.dynamodb.jobs_repository import DynamoDBJobRepository


class FakeTable:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def update_item(self, **kwargs: Any) -> None:
        self.calls.append(kwargs)


def test_dynamodb_repository_serializes_duration_as_decimal() -> None:
    table = FakeTable()
    repository = DynamoDBJobRepository.__new__(DynamoDBJobRepository)
    repository._table = table

    repository.mark_completed("job-1", "output/user-1/job-1/file.docx", 6.92)

    values = table.calls[0]["ExpressionAttributeValues"]
    assert Decimal("6.92") in values.values()
