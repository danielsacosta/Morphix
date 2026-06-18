from __future__ import annotations

from fastapi.testclient import TestClient

from morphix_api.aws_clients import FakeConversionGateway
from morphix_api.config import Settings
from morphix_api.main import app, get_gateway, get_repository, get_settings
from morphix_api.models import JobStatus
from morphix_api.repository import InMemoryJobsRepository


def make_client() -> tuple[TestClient, InMemoryJobsRepository, FakeConversionGateway]:
    repository = InMemoryJobsRepository()
    gateway = FakeConversionGateway()
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
    app.dependency_overrides[get_gateway] = lambda: gateway
    app.dependency_overrides[get_settings] = lambda: settings
    return TestClient(app), repository, gateway


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
    client, repository, gateway = make_client()
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
    assert started.json()["job"]["status"] == "PROCESSING"
    assert gateway.started_jobs == [job_id]

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

