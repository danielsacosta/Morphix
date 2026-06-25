from __future__ import annotations

from fastapi.testclient import TestClient

from morphix_api.adapters.inbound.http.dependencies import (
    get_conversion_orchestrator,
    get_object_url_service,
    get_repository,
    get_settings,
)
from morphix_api.application.ports.conversion_orchestrator import FakeConversionOrchestrator
from morphix_api.application.ports.jobs_repository import InMemoryJobsRepository
from morphix_api.application.ports.object_url_service import FakeObjectUrlService
from morphix_api.core.config import Settings
from morphix_api.domain.value_objects.job_status import JobStatus
from morphix_api.main import app


def make_client() -> tuple[TestClient, InMemoryJobsRepository, FakeConversionOrchestrator]:
    repository = InMemoryJobsRepository()
    object_url_service = FakeObjectUrlService()
    orchestrator = FakeConversionOrchestrator()
    settings = Settings(
        project_name="morphix",
        environment="test",
        aws_region="us-east-1",
        jobs_table_name="jobs",
        input_bucket="input",
        output_bucket="output",
        state_machine_arn="arn:aws:states:us-east-1:000000000000:stateMachine:test",
        max_file_size_mb=100,
        allowed_origins=["http://localhost:5173"],
    )
    app.dependency_overrides[get_repository] = lambda: repository
    app.dependency_overrides[get_object_url_service] = lambda: object_url_service
    app.dependency_overrides[get_conversion_orchestrator] = lambda: orchestrator
    app.dependency_overrides[get_settings] = lambda: settings
    return TestClient(app), repository, orchestrator


def create_docx_job(client: TestClient) -> str:
    response = client.post(
        "/jobs",
        headers={"X-User-Id": "user-1"},
        json={
            "filename": "report.docx",
            "file_size": 1024,
            "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "target_format": "pdf",
        },
    )
    assert response.status_code == 201
    return response.json()["job"]["job_id"]


def test_create_upload_start_and_download_job() -> None:
    client, repository, orchestrator = make_client()
    job_id = create_docx_job(client)

    upload = client.post(
        f"/jobs/{job_id}/upload-url",
        headers={"X-User-Id": "user-1"},
        json={"content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
    )
    assert upload.status_code == 200
    assert upload.json()["method"] == "PUT"
    assert repository.get_job(job_id).status == JobStatus.upload_requested

    started = client.post(f"/jobs/{job_id}/start", headers={"X-User-Id": "user-1"})
    assert started.status_code == 200
    assert started.json()["job"]["status"] == "QUEUED"
    assert started.json()["job"]["state_machine_execution_arn"]
    assert orchestrator.started_jobs == [job_id]

    repository.update_job(job_id, status=JobStatus.completed)
    download = client.get(f"/jobs/{job_id}/download-url", headers={"X-User-Id": "user-1"})
    assert download.status_code == 200
    assert download.json()["download_url"].startswith("https://downloads.example.test/")


def test_rejects_unsupported_conversion() -> None:
    client, _, _ = make_client()
    response = client.post(
        "/jobs",
        headers={"X-User-Id": "user-1"},
        json={"filename": "archive.zip", "file_size": 100, "target_format": "pdf"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported conversion format"


def test_rejects_oversized_file() -> None:
    client, _, _ = make_client()
    response = client.post(
        "/jobs",
        headers={"X-User-Id": "user-1"},
        json={"filename": "video.mp4", "file_size": 101 * 1024 * 1024, "target_format": "mp3"},
    )
    assert response.status_code == 413


def test_prevents_cross_user_access() -> None:
    client, _, _ = make_client()
    job_id = create_docx_job(client)
    response = client.get(f"/jobs/{job_id}", headers={"X-User-Id": "user-2"})
    assert response.status_code == 404


def test_lists_only_current_user_jobs() -> None:
    client, _, _ = make_client()
    create_docx_job(client)
    client.post(
        "/jobs",
        headers={"X-User-Id": "user-2"},
        json={"filename": "image.png", "file_size": 100, "target_format": "jpg"},
    )

    response = client.get("/jobs", headers={"X-User-Id": "user-1"})
    assert response.status_code == 200
    assert len(response.json()["jobs"]) == 1
    assert response.json()["jobs"][0]["user_id"] == "user-1"


def test_deleted_job_is_removed_from_history() -> None:
    client, _, _ = make_client()
    job_id = create_docx_job(client)

    deleted = client.delete(f"/jobs/{job_id}", headers={"X-User-Id": "user-1"})
    assert deleted.status_code == 200
    assert deleted.json()["job"]["status"] == "DELETED"

    response = client.get("/jobs", headers={"X-User-Id": "user-1"})
    assert response.status_code == 200
    assert response.json()["jobs"] == []


def test_creates_batch_jobs_with_positions() -> None:
    client, _, _ = make_client()
    response = client.post(
        "/jobs/batch",
        headers={"X-User-Id": "user-1"},
        json={
            "files": [
                {"filename": "a.pdf", "file_size": 100, "target_format": "docx"},
                {"filename": "b.pdf", "file_size": 200, "target_format": "docx"},
            ]
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["batch_id"]
    assert [job["queue_position"] for job in payload["jobs"]] == [1, 2]
    assert {job["batch_id"] for job in payload["jobs"]} == {payload["batch_id"]}

    create_docx_job(client)
    filtered = client.get(f"/jobs?batch_id={payload['batch_id']}", headers={"X-User-Id": "user-1"})

    assert filtered.status_code == 200
    assert {job["job_id"] for job in filtered.json()["jobs"]} == {job["job_id"] for job in payload["jobs"]}
