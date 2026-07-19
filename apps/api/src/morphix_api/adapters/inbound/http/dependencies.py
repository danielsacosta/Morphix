from __future__ import annotations

from typing import Annotated

from fastapi import Header

from ....adapters.outbound.dynamodb.jobs_repository import DynamoDBJobsRepository
from ....adapters.outbound.local.sqlite_jobs_repository import SQLiteJobsRepository
from ....adapters.outbound.local.filesystem_url_service import LocalFilesystemUrlService
from ....adapters.outbound.s3.presigned_url_service import S3PresignedUrlService
from ....adapters.outbound.stepfunctions.conversion_orchestrator import StepFunctionsConversionOrchestrator
from ....application.ports.conversion_orchestrator import ConversionOrchestrator
from ....application.ports.jobs_repository import JobsRepository
from ....application.ports.object_url_service import ObjectUrlService
from ....core.config import Settings
from ....domain.errors import AuthenticationRequiredError


def _build_conversion_orchestrator(settings: Settings) -> ConversionOrchestrator:
    if settings.runtime_backend == "local":
        from ....adapters.outbound.local.redis_orchestrator import RedisConversionOrchestrator

        return RedisConversionOrchestrator(settings)

    return StepFunctionsConversionOrchestrator(settings)


_settings = Settings.from_env()
if _settings.runtime_backend == "local":
    _repository = SQLiteJobsRepository(_settings)
    _object_url_service = LocalFilesystemUrlService(_settings)
else:
    _repository = DynamoDBJobsRepository(_settings)
    _object_url_service = S3PresignedUrlService(_settings)
_conversion_orchestrator = _build_conversion_orchestrator(_settings)


def get_settings() -> Settings:
    return _settings


def get_repository() -> JobsRepository:
    return _repository


def get_object_url_service() -> ObjectUrlService:
    return _object_url_service


def get_conversion_orchestrator() -> ConversionOrchestrator:
    return _conversion_orchestrator


def require_user_id(x_user_id: Annotated[str | None, Header(alias="X-User-Id")] = None) -> str:
    user_id = (x_user_id or "").strip()
    if not user_id:
        raise AuthenticationRequiredError("X-User-Id header is required")
    if len(user_id) > 128:
        raise AuthenticationRequiredError("X-User-Id is too long")
    return user_id
