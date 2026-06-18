from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from .adapters.inbound.http.error_handlers import domain_error_handler
from .adapters.inbound.http.routes.health import router as health_router
from .adapters.inbound.http.routes.jobs import router as jobs_router
from .core.config import Settings
from .domain.errors import DomainError


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or Settings.from_env()
    api = FastAPI(title="Morphix API", version="0.1.0")
    api.add_middleware(
        CORSMiddleware,
        allow_origins=resolved_settings.allowed_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "X-User-Id"],
    )
    api.add_exception_handler(DomainError, domain_error_handler)
    api.include_router(health_router)
    api.include_router(jobs_router)
    return api


app = create_app()
handler = Mangum(app)

