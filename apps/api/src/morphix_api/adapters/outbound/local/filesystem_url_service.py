from __future__ import annotations

import base64
import hashlib
import hmac
import time

from ....application.ports.object_url_service import ObjectUrlService
from ....core.config import Settings
from ....domain.entities.job import Job


class LocalFilesystemUrlService(ObjectUrlService):
    def __init__(self, settings: Settings) -> None:
        self._base_url = settings.local_public_url.rstrip("/")
        self._secret = settings.local_url_secret.encode("utf-8")
        self._upload_ttl = settings.upload_url_ttl_seconds
        self._download_ttl = settings.download_url_ttl_seconds

    def _token(self, action: str, job_id: str, ttl: int) -> str:
        expires_at = int(time.time()) + ttl
        payload = f"{action}.{job_id}.{expires_at}".encode("utf-8")
        signature = hmac.new(self._secret, payload, hashlib.sha256).hexdigest()
        raw = f"{action}.{job_id}.{expires_at}.{signature}".encode("utf-8")
        return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")

    def create_upload_url(self, job: Job, content_type: str) -> tuple[str, dict[str, str]]:
        token = self._token("upload", job.job_id, self._upload_ttl)
        return f"{self._base_url}/local-files/{token}", {"Content-Type": content_type}

    def create_download_url(self, job: Job) -> str:
        token = self._token("download", job.job_id, self._download_ttl)
        return f"{self._base_url}/local-files/{token}"

    def verify(self, token: str, expected_action: str) -> str | None:
        try:
            padded = token + "=" * (-len(token) % 4)
            decoded = base64.urlsafe_b64decode(padded).decode("utf-8")
            action, job_id, expires_raw, signature = decoded.split(".", 3)
            expires_at = int(expires_raw)
        except (ValueError, UnicodeDecodeError, base64.binascii.Error):
            return None

        if action != expected_action or expires_at < int(time.time()):
            return None
        payload = f"{action}.{job_id}.{expires_at}".encode("utf-8")
        expected_signature = hmac.new(self._secret, payload, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected_signature):
            return None
        return job_id
