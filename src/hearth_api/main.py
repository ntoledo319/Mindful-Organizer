"""FastAPI application entrypoint for Hearth.

Run locally:
    uvicorn hearth_api.main:app --host 127.0.0.1 --port 9173 --reload

In production, the Tauri shell spawns this as a sidecar child process and
the frontend talks to it on loopback.
"""
from __future__ import annotations

import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

# Ensure src/ is on sys.path so core/, wellness/, etc. import cleanly.
_SRC = Path(__file__).parent.parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from fastapi import FastAPI  # noqa: E402  (path setup must precede import)
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

from hearth_api.routes import journal, system, today  # noqa: E402
from hearth_api.settings import get_settings  # noqa: E402

logger = logging.getLogger("hearth_api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown hooks."""
    logger.info("Hearth API starting on %s:%d", get_settings().host, get_settings().port)
    yield
    logger.info("Hearth API shutting down")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
        description=settings.api_description,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(system.router)
    app.include_router(today.router)
    app.include_router(journal.router)

    @app.get("/")
    async def root():
        return {
            "service": settings.api_title,
            "version": settings.api_version,
            "docs": "/docs",
        }

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    s = get_settings()
    uvicorn.run("hearth_api.main:app", host=s.host, port=s.port, reload=True)
