"""FastAPI runtime configuration.

Reads from environment variables with sensible local-only defaults.
"""
from __future__ import annotations

import os
import sys
from functools import lru_cache
from pathlib import Path


class Settings:
    """Runtime config.

    Local-only by default; the Tauri sidecar process runs on localhost and
    the frontend talks to it over loopback. No cloud deploy assumptions.
    """

    # Data directory — same convention as main.py for backward compat
    @property
    def data_dir(self) -> Path:
        env = os.environ.get("HEARTH_DATA_DIR")
        if env:
            return Path(env)
        if sys.platform == "win32":
            base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        elif sys.platform == "darwin":
            base = Path.home() / "Library" / "Application Support"
        else:
            base = Path.home()
        return base / ".mindful_organizer"

    # Host / port for the local API
    host: str = os.environ.get("HEARTH_API_HOST", "127.0.0.1")
    port: int = int(os.environ.get("HEARTH_API_PORT", "9173"))

    # CORS — Tauri uses tauri://localhost in dev; Vite uses localhost:1420
    cors_origins: list[str] = [
        "http://localhost:1420",
        "http://localhost:3000",
        "tauri://localhost",
        "https://tauri.localhost",
    ]

    # Auth — only allow loopback access; the Tauri shell signs requests
    # with a per-launch token written to a file in data_dir. The PWA
    # deploy adds proper auth in Phase 5.
    require_loopback_token: bool = (
        os.environ.get("HEARTH_REQUIRE_TOKEN", "true").lower() == "true"
    )

    api_title: str = "Hearth"
    api_version: str = "0.1.0"
    api_description: str = (
        "Local-only HTTP API for the Hearth desktop application. "
        "Wraps the psychological-OS managers and exposes them to the "
        "Tauri + Next.js frontend."
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
