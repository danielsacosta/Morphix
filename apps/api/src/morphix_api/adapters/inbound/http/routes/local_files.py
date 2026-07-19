from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import FileResponse

from .....adapters.outbound.local.filesystem import LocalFilesystemStorage
from .....adapters.outbound.local.filesystem_url_service import LocalFilesystemUrlService
from .....application.ports.jobs_repository import JobsRepository
from .....core.config import Settings
from .....domain.value_objects.job_status import JobStatus
from ..dependencies import get_repository, get_settings

router = APIRouter(prefix="/local-files", tags=["local-files"])


def _url_service(settings: Settings) -> LocalFilesystemUrlService:
    return LocalFilesystemUrlService(settings)


def _storage(settings: Settings) -> LocalFilesystemStorage:
    return LocalFilesystemStorage(settings.local_data_dir)


@router.put("/{token}", status_code=status.HTTP_200_OK)
async def upload_local_file(
    token: str,
    request: Request,
    repository: Annotated[JobsRepository, Depends(get_repository)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> Response:
    job_id = _url_service(settings).verify(token, "upload")
    if not job_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Upload URL is invalid or expired")
    job = repository.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    path = _storage(settings).path_for(job.input_bucket, job.input_key)
    path.parent.mkdir(parents=True, exist_ok=True)
    received = 0
    try:
        with path.open("wb") as output:
            async for chunk in request.stream():
                received += len(chunk)
                if received > settings.max_file_size_bytes:
                    raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File is too large")
                output.write(chunk)
    except HTTPException:
        path.unlink(missing_ok=True)
        raise
    except Exception:
        path.unlink(missing_ok=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not store file")

    if received != job.file_size:
        path.unlink(missing_ok=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file size does not match job metadata")
    return Response(status_code=status.HTTP_200_OK)


@router.get("/{token}")
def download_local_file(
    token: str,
    repository: Annotated[JobsRepository, Depends(get_repository)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> FileResponse:
    job_id = _url_service(settings).verify(token, "download")
    if not job_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Download URL is invalid or expired")
    job = repository.get_job(job_id)
    if job is None or job.status != JobStatus.completed or not job.output_key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Result not found")

    path = _storage(settings).path_for(job.output_bucket, job.output_key)
    if not path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Result file is not available")
    return FileResponse(path, filename=Path(job.output_key).name, media_type="application/octet-stream")
