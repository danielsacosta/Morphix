from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse

from ....domain.errors import DomainError


async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": str(exc)})

