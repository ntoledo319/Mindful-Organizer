#!/usr/bin/env python3
"""Capture Microsoft Store screenshots from the live Qt application.

Run this on a machine with a display (Windows preferred for Store
submission, but macOS/Linux work for review). It launches the main window
at 1920×1080, seeds non-PII sample data, navigates each of the six
documented store-listing views, and saves PNGs into
``windows_store/assets/``.

Usage:
    source venv312/bin/activate
    python scripts/capture_screenshots.py

Tabs captured (matches windows_store/store_listing.md):
    1. Dashboard
    2. Diary Card
    3. Mood
    4. Files (condition-aware file organizer)
    5. Automation (focus / system rules)
    6. Settings (data management)
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from PyQt6.QtCore import QTimer  # noqa: E402  (path setup must precede import)
from PyQt6.QtWidgets import QApplication  # noqa: E402

OUT_DIR = PROJECT_ROOT / "windows_store" / "assets"
TARGETS = [
    ("dashboard", "screenshot_01_dashboard.png"),
    ("diary_card", "screenshot_02_diary_card.png"),
    ("mood_tracker", "screenshot_03_mood.png"),
    ("file_organizer", "screenshot_04_files.png"),
    ("automation", "screenshot_05_automation.png"),
    ("settings", "screenshot_06_settings.png"),
]


def seed_sample_data() -> None:
    """Insert realistic non-PII sample data so screenshots aren't empty."""
    # Lazy import to ensure sys.path is set
    from core.database import DatabaseManager
    from core.task_manager import TaskManager, TaskPriority

    db = DatabaseManager()
    db.initialize()

    tm = TaskManager()
    if len(tm.get_all_tasks()) < 3:
        tm.add_task("Morning meditation", priority=TaskPriority.HIGH)
        tm.add_task("Reply to therapist", priority=TaskPriority.MEDIUM)
        tm.add_task("Refill prescription", priority=TaskPriority.HIGH)
        tm.add_task("Walk for 20 minutes", priority=TaskPriority.LOW)
        tm.add_task("Journal — gratitude entry", priority=TaskPriority.MEDIUM)


def capture_one(window, widget_name: str, filename: str) -> None:
    if widget_name not in window._widgets:
        print(f"  skipped {widget_name}: not present in this profile")
        return
    idx = window.tabs.indexOf(window._widgets[widget_name])
    if idx < 0:
        print(f"  skipped {widget_name}: not in tabs")
        return
    window.tabs.setCurrentIndex(idx)
    QApplication.processEvents()
    time.sleep(0.4)  # let theme/widget settle
    QApplication.processEvents()
    pixmap = window.grab()
    out = OUT_DIR / filename
    pixmap.save(str(out), "PNG", 95)
    print(f"  wrote {out.name} ({pixmap.width()}×{pixmap.height()})")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    app = QApplication(sys.argv)

    try:
        seed_sample_data()
    except Exception as exc:
        print(f"warning: sample data seeding failed: {exc}")

    from gui.main_window import AdaptiveMainWindow

    window = AdaptiveMainWindow()
    window.resize(1920, 1080)
    window.show()

    # Defer capture until the event loop is running and widgets are laid out.
    captured = {"count": 0}

    def run_captures():
        for widget_name, filename in TARGETS:
            capture_one(window, widget_name, filename)
            captured["count"] += 1
        app.quit()

    QTimer.singleShot(1200, run_captures)
    app.exec()
    print(f"\nCaptured {captured['count']} screenshots in {OUT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
