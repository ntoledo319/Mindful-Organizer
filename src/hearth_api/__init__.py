"""Hearth — FastAPI layer.

This package wraps the existing Python managers in src/core, src/wellness,
src/profiles, src/security, and src/utils as HTTP/WebSocket endpoints, so
the Next.js frontend (via Tauri shell on desktop, PWA on web) can talk to
the same business logic the PyQt6 UI currently uses.

During the migration, the PyQt6 UI (src/gui) and the FastAPI layer
(src/hearth_api) coexist. The Python managers are the shared backend.

Phase 5 (retire PyQt6) removes src/gui entirely; this layer becomes the
sole interface to the core.
"""

__version__ = "0.1.0"
