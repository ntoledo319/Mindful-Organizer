"""Render every Hearth UI surface to PNGs for design review (offscreen)."""

import json
import os
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, "src")

OUT = Path("/tmp/hearth_ui")
OUT.mkdir(parents=True, exist_ok=True)

from PyQt6.QtWidgets import QApplication  # noqa: E402

app = QApplication([])


def _seed(home: Path):
    os.environ["HOME"] = str(home)
    from core.paths import get_data_dir

    dd = get_data_dir()
    (dd / "current_profile.json").write_text(
        json.dumps(
            {
                "name": "Alex",
                "conditions": ["ADHD", "Anxiety", "Depression"],
                "therapy_types": ["CBT", "DBT"],
                "energy_pattern": "morning",
            }
        )
    )
    from core.database import DatabaseManager, TableName

    db = DatabaseManager(dd / "mindful_organizer.db")
    db.initialize()
    now = datetime.now()
    for i, m in enumerate([7, 6, 4, 5, 3, 6, 7]):
        db.insert(
            TableName.MOOD_ENTRIES,
            mood_score=m,
            energy_level=m,
            timestamp=(now - timedelta(days=i)).isoformat(),
            notes="felt a bit scattered today, hard to start",
            emotions="anxious,restless",
            context="work",
        )
    for i, h in enumerate([6.5, 5.0, 7.0, 4.5, 6.0]):
        db.insert(
            TableName.SLEEP_LOGS,
            date=(now - timedelta(days=i)).date().isoformat(),
            duration_hours=h,
            quality=3,
            bedtime="23:30",
            wake_time="06:30",
            interruptions=1,
            notes="",
        )
    db.insert(TableName.TASKS, guid="t1", title="Reply to landlord email",
              priority="high", energy_required=3, completed=0, created_at=now.isoformat())
    db.insert(TableName.TASKS, guid="t2", title="15-minute walk",
              priority="medium", energy_required=2, completed=0, created_at=now.isoformat())
    db.insert(TableName.TASKS, guid="t3", title="Pay electricity bill",
              priority="high", energy_required=4, completed=1, completed_at=now.isoformat(),
              created_at=now.isoformat())
    return db


def grab(win, name):
    app.processEvents()
    app.processEvents()
    pix = win.grab()
    path = OUT / f"{name}.png"
    pix.save(str(path))
    print(f"  rendered {name}: {path.stat().st_size} bytes")


def render_main_tabs():
    home = Path(tempfile.mkdtemp())
    _seed(home)
    from gui.main_window import AdaptiveMainWindow

    win = AdaptiveMainWindow()
    win.resize(1440, 920)
    win.show()
    app.processEvents()
    tabs = [
        "dashboard", "task_manager", "journaling", "mood_tracker", "diary_card",
        "breathing", "meditation", "erp", "panic_tracker", "sleep", "medication",
        "automation", "file_organizer", "crisis", "settings",
    ]
    for t in tabs:
        try:
            win._switch_to_tab(t)
            grab(win, f"{t}")
        except Exception as e:
            print(f"  !! {t}: {e}")
    win.close()


def render_onboarding():
    home = Path(tempfile.mkdtemp())
    os.environ["HOME"] = str(home)  # no profile -> onboarding
    try:
        from core.paths import get_data_dir
        from profiles.mental_health_profile_builder import ProfileManager
        from gui.widgets.onboarding import OnboardingWizard
        pm = ProfileManager(get_data_dir())
        try:
            wiz = OnboardingWizard(pm)
        except TypeError:
            wiz = OnboardingWizard(profile_manager=pm)
        wiz.resize(900, 700)
        wiz.show()
        app.processEvents()
        grab(wiz, "onboarding_00_start")
        # step through pages if the wizard exposes navigation
        for i in range(1, 7):
            try:
                if hasattr(wiz, "_next_page"):
                    wiz._next_page()
                elif hasattr(wiz, "next"):
                    wiz.next()
                elif hasattr(wiz, "_stack"):
                    s = wiz._stack
                    s.setCurrentIndex(min(i, s.count() - 1))
                grab(wiz, f"onboarding_{i:02d}")
            except Exception as e:
                print(f"  onboarding page {i}: {e}")
                break
    except Exception as e:
        print(f"  !! onboarding: {e}")


if __name__ == "__main__":
    print("Rendering main tabs...")
    render_main_tabs()
    print("Rendering onboarding...")
    render_onboarding()
    print(f"\nDone. Screens in {OUT}")
