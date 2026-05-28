"""System / health endpoints — used by the Tauri shell to confirm the
sidecar Python process is alive before showing the UI.
"""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel

from hearth_api import __version__

router = APIRouter(prefix="/system", tags=["system"])


class HealthResponse(BaseModel):
    status: str
    version: str
    server_time: datetime


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        version=__version__,
        server_time=datetime.now(),
    )
