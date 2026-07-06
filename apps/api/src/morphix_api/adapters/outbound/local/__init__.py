"""Local development outbound adapters.

These adapters implement the same ports as the production AWS-SDK
adapters but bypass Step Functions / ECS, allowing the project to run
end-to-end on `docker compose up` with only LocalStack.
"""

from __future__ import annotations