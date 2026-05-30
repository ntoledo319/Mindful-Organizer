"""Canonical filesystem locations for Hearth.

Single source of truth for where the app stores its data. Historically three
different conventions coexisted (``~/.mindful_organizer``, a platform-specific
``Library/Application Support/MindfulOrganizer``, and a dotted variant), which
silently split a user's tasks, moods, and medication logs across separate
SQLite files. Everything now routes through here so there is exactly one
database and one state directory per platform.

This module deliberately has no project-internal imports so it can be used by
``database.py``, ``main.py``, and the platform helpers without import cycles.
"""

from __future__ import annotations

import contextlib
import os
import sys
from pathlib import Path

_DIR_NAME = ".mindful_organizer"
_LEGACY_DIR_NAME = ".mindful_optimizer"
_DB_FILENAME = "mindful_organizer.db"


def _base_dir() -> Path:
    """Platform-appropriate parent directory for app data."""
    if sys.platform == "win32":
        return Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support"
    return Path.home()


def get_data_dir(create: bool = True) -> Path:
    """Return the canonical data directory, migrating the legacy name if needed.

    If a legacy ``.mindful_optimizer`` directory exists and the canonical one
    does not, it is renamed in place so no user data is lost on upgrade.
    """
    base = _base_dir()
    data_dir = base / _DIR_NAME
    legacy = base / _LEGACY_DIR_NAME

    if legacy.exists() and not data_dir.exists():
        with contextlib.suppress(OSError):
            legacy.rename(data_dir)

    if create:
        data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_db_path() -> Path:
    """Return the canonical SQLite database path."""
    return get_data_dir() / _DB_FILENAME
