#!/usr/bin/env python3
"""
Cleanup script for Mindful Organizer development.

Removes temporary build artifacts and cache files from the project directory.
Operates only within the repository root (detected from the script location).
"""

import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)

TEMP_PATTERNS = [
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "*.so",
    ".coverage",
    ".DS_Store",
]

TEMP_DIRS = [
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "build",
    "*.egg-info",
]


def get_project_dir() -> Path:
    """Return the repository root based on this script's location."""
    return Path(__file__).resolve().parent.parent


def remove_temp_files(project_dir: Path) -> list[Path]:
    """Remove temporary files matching known patterns."""
    removed: list[Path] = []
    for pattern in TEMP_PATTERNS:
        for item in project_dir.rglob(pattern):
            try:
                item.unlink()
                removed.append(item)
                logger.info("Removed file: %s", item.relative_to(project_dir))
            except OSError as exc:
                logger.warning("Failed to remove %s: %s", item, exc)
    return removed


def remove_temp_dirs(project_dir: Path) -> list[Path]:
    """Remove temporary directories matching known names."""
    removed: list[Path] = []
    for dir_name in TEMP_DIRS:
        for item in project_dir.rglob(dir_name):
            # Only remove if the name matches exactly (not partial)
            if item.name == dir_name or item.match(dir_name):
                try:
                    shutil.rmtree(item)
                    removed.append(item)
                    logger.info("Removed directory: %s", item.relative_to(project_dir))
                except OSError as exc:
                    logger.warning("Failed to remove %s: %s", item, exc)
    return removed


def main() -> int:
    """Run cleanup and report results."""
    project_dir = get_project_dir()
    logger.info("Cleaning project directory: %s", project_dir)

    removed_files = remove_temp_files(project_dir)
    removed_dirs = remove_temp_dirs(project_dir)

    total = len(removed_files) + len(removed_dirs)
    if total == 0:
        logger.info("No temporary files found. Project is clean.")
    else:
        logger.info("Cleanup complete. Removed %d file(s) and %d directory(s).", len(removed_files), len(removed_dirs))

    return 0


if __name__ == "__main__":
    sys.exit(main())
