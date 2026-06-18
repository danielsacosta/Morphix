from __future__ import annotations

from ..entities.job import Job
from ..errors import JobOwnershipError


class OwnershipPolicy:
    def assert_owner(self, job: Job, user_id: str) -> None:
        if job.user_id != user_id:
            raise JobOwnershipError("Job not found")

