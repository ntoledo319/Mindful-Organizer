"""
Smoke test for Hearth — headless widget instantiation and import validation.

Runs without starting the Qt event loop.  Exits with code 0 on success,
code 1 on failure.
"""

from __future__ import annotations

import sys
import tempfile
import traceback
from pathlib import Path
from typing import Any

# Ensure src/ is on path when script is run directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))


def _section(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def _ok(msg: str) -> None:
    print(f"  ✅ {msg}")


def _fail(msg: str) -> None:
    print(f"  ❌ {msg}")


# ---------------------------------------------------------------------------
# 1. Import smoke test
# ---------------------------------------------------------------------------
def test_imports() -> bool:
    _section("1. Import Smoke Test")
    errors: list[str] = []

    try:
        __import__("main")

        _ok("main import OK")
    except Exception as exc:
        errors.append(f"main import failed: {exc}")
        _fail(f"main import failed: {exc}")
        traceback.print_exc()

    core_modules = [
        "core.database",
        "core.task_manager",
        "core.mood_manager",
        "core.system_automation",
        "core.wellness_orchestrator",
        "core.ai_optimizer",
        "core.file_organizer",
        "core.notification_manager",
        "core.subscription_manager",
        "gui.main_window",
        "gui.themes",
        "gui.state_bus",
        "profiles.mental_health_profile_builder",
        "utils.accessibility",
        "wellness.breathing",
        "wellness.meditation",
        "wellness.journaling",
    ]

    for mod in core_modules:
        try:
            __import__(mod)
            _ok(f"{mod} import OK")
        except Exception as exc:
            errors.append(f"{mod} import failed: {exc}")
            _fail(f"{mod} import failed: {exc}")

    if errors:
        print(f"\n  {len(errors)} import error(s)")
        return False
    print("\n  All imports passed.")
    return True


# ---------------------------------------------------------------------------
# 2. Dependency check
# ---------------------------------------------------------------------------
def test_dependencies() -> bool:
    _section("2. Dependency Check")
    ok = True

    core_deps = [
        "PyQt6",
        "numpy",
        "cryptography",
        "psutil",
        "keyring",
        "certifi",
    ]
    for dep in core_deps:
        try:
            __import__(dep)
            _ok(f"{dep} import OK")
        except Exception as exc:
            _fail(f"{dep} import FAILED: {exc}")
            ok = False

    optional_deps = [
        ("sklearn", "scikit-learn"),
        ("pandas", "pandas"),
        ("matplotlib", "matplotlib"),
        ("sentence_transformers", "sentence-transformers"),
        ("hdbscan", "hdbscan"),
        ("umap", "umap-learn"),
    ]
    for mod, pkg in optional_deps:
        try:
            __import__(mod)
            _ok(f"{pkg} import OK (optional)")
        except ImportError:
            _ok(f"{pkg} not installed — gracefully skipped (optional)")
        except Exception as exc:
            _fail(f"{pkg} import FAILED unexpectedly: {exc}")
            ok = False

    return ok


# ---------------------------------------------------------------------------
# 3. Resource verification
# ---------------------------------------------------------------------------
def test_resources() -> bool:
    _section("3. Resource Verification")
    ok = True

    required = [
        PROJECT_ROOT / "resources" / "guideds.json",
        PROJECT_ROOT / "resources" / "vendor" / "chart.umd.min.js",
        PROJECT_ROOT / "resources" / "meditations",
    ]
    for path in required:
        if path.exists():
            _ok(f"{path.relative_to(PROJECT_ROOT)} exists")
        else:
            _fail(f"{path.relative_to(PROJECT_ROOT)} MISSING")
            ok = False

    # Check guideds.json is valid JSON and non-empty
    guideds_path = PROJECT_ROOT / "resources" / "guideds.json"
    try:
        import json

        with open(guideds_path) as fh:
            data = json.load(fh)
        if data:
            _ok(f"guideds.json loads ({len(data)} entries)")
        else:
            _ok("guideds.json loads (empty array)")
    except Exception as exc:
        _fail(f"guideds.json parse error: {exc}")
        ok = False

    # Check meditation dirs have audio files
    for subdir in (PROJECT_ROOT / "resources" / "meditations").iterdir():
        if subdir.is_dir():
            mp3s = list(subdir.glob("*.mp3"))
            if mp3s:
                _ok(f"{subdir.name}/ has {len(mp3s)} audio file(s)")
            else:
                _ok(f"{subdir.name}/ has no audio (license-only dir is OK)")

    return ok


# ---------------------------------------------------------------------------
# 4. Accessibility audit
# ---------------------------------------------------------------------------
def test_accessibility() -> bool:
    _section("4. Accessibility Audit")
    ok = True

    from utils.accessibility import (
        AccessibilityManager,
        AccessibilitySettings,
        ColorBlindnessMode,
        ContrastLevel,
        FontScale,
        get_palette,
    )

    # Verify enums and dataclasses construct
    settings = AccessibilitySettings(
        font_scale=FontScale.LARGE,
        color_blindness_mode=ColorBlindnessMode.DEUTERANOPIA,
        contrast_level=ContrastLevel.HIGH,
    )
    _ok("AccessibilitySettings constructs")

    _ = get_palette(settings)
    _ok("get_palette() returns palette")

    # Round-trip dict serialization
    data = settings.to_dict()
    restored = AccessibilitySettings.from_dict(data)
    assert restored.font_scale == FontScale.LARGE
    assert restored.contrast_level == ContrastLevel.HIGH
    _ok("AccessibilitySettings round-trips through dict")

    # Manager constructs and auto-detects
    mgr = AccessibilityManager(settings)
    mgr.auto_detect()
    _ok("AccessibilityManager constructs + auto_detect()")

    # Check for wired settings keys in ThemeManager (from main_window load path)
    from gui.themes import ThemeManager

    tm = ThemeManager()
    tm.font_scale = 1.25
    tm.color_blind_mode = "deuteranopia"
    tm.reduced_motion = True
    tm.dyslexia_font = True
    _ok("ThemeManager accepts font_scale / color_blind_mode / reduced_motion / dyslexia_font")

    # Verify stylesheet generation doesn't explode
    ss = mgr.get_stylesheet()
    if ss and "font-family" in ss:
        _ok("AccessibilityManager.get_stylesheet() generates QSS")
    else:
        _fail("AccessibilityManager.get_stylesheet() returned empty/invalid QSS")
        ok = False

    return ok


# ---------------------------------------------------------------------------
# 5. Headless widget instantiation
# ---------------------------------------------------------------------------
def test_headless_widgets() -> bool:
    _section("5. Headless Widget Instantiation")
    ok = True

    from PyQt6.QtWidgets import QApplication

    app = QApplication.instance()
    if app is None:
        # Use a hidden dummy arg so Qt doesn't steal sys.argv
        app = QApplication(["smoke_test"])
        _ok("QApplication created")
    else:
        _ok("Reusing existing QApplication")

    from gui.themes import ThemeManager

    theme = ThemeManager().get_colors()
    _ok("ThemeManager.get_colors() returns dict")

    widgets_created: list[Any] = []

    # --- VoiceJournalWidget ---
    try:
        from gui.widgets.voice_journal_widget import VoiceJournalWidget

        w = VoiceJournalWidget()
        widgets_created.append(w)
        _ok("VoiceJournalWidget instantiated")
    except Exception as exc:
        _fail(f"VoiceJournalWidget failed: {exc}")
        traceback.print_exc()
        ok = False

    # --- FocusSessionWidget ---
    try:
        from gui.widgets.focus_session_widget import FocusSessionWidget

        w = FocusSessionWidget(theme, focus_manager=None)
        widgets_created.append(w)
        _ok("FocusSessionWidget instantiated")
    except Exception as exc:
        _fail(f"FocusSessionWidget failed: {exc}")
        traceback.print_exc()
        ok = False

    # --- TaskManagerWidget ---
    try:
        from gui.widgets.task_manager_widget import TaskManagerWidget

        w = TaskManagerWidget(theme, task_manager=None, nlp_parser=None)
        widgets_created.append(w)
        _ok("TaskManagerWidget instantiated")
    except Exception as exc:
        _fail(f"TaskManagerWidget failed: {exc}")
        traceback.print_exc()
        ok = False

    # --- DashboardWidget ---
    try:
        from gui.widgets.dashboard import DashboardWidget

        w = DashboardWidget(
            theme,
            task_manager=None,
            profile_manager=None,
            mood_manager=None,
            energy_predictor=None,
            gamification_manager=None,
            wellness_orchestrator=None,
            subscription_manager=None,
        )
        widgets_created.append(w)
        _ok("DashboardWidget instantiated")
    except Exception as exc:
        _fail(f"DashboardWidget failed: {exc}")
        traceback.print_exc()
        ok = False

    # --- AdaptiveMainWindow ---
    # This is the heaviest one: it builds the DB, loads profiles, creates tabs.
    # We monkey-patch _get_data_dir so it uses a temp directory.
    from gui.main_window import AdaptiveMainWindow

    tmp_dir = Path(tempfile.mkdtemp(prefix="hearth_smoke_"))
    original_get_data_dir = AdaptiveMainWindow._get_data_dir

    def _patched_get_data_dir(self: AdaptiveMainWindow) -> Path:
        return tmp_dir

    AdaptiveMainWindow._get_data_dir = _patched_get_data_dir  # type: ignore[method-assign]

    # Also suppress the onboarding wizard (exec() would block)
    original_show_onboarding = AdaptiveMainWindow._show_onboarding

    def _patched_show_onboarding(self: AdaptiveMainWindow) -> None:
        self._create_default_profile()
        self._initialize_ui()

    AdaptiveMainWindow._show_onboarding = _patched_show_onboarding  # type: ignore[method-assign]

    try:
        win = AdaptiveMainWindow()
        widgets_created.append(win)
        _ok("AdaptiveMainWindow instantiated")

        # Verify key child widgets were created
        if hasattr(win, "tabs") and win.tabs.count() > 0:
            _ok(f"AdaptiveMainWindow has {win.tabs.count()} tabs")
        else:
            _fail("AdaptiveMainWindow has no tabs")
            ok = False

        if hasattr(win, "_widgets") and win._widgets:
            _ok(f"AdaptiveMainWindow created {len(win._widgets)} widget(s)")
        else:
            _fail("AdaptiveMainWindow._widgets is empty")
            ok = False

    except Exception as exc:
        _fail(f"AdaptiveMainWindow failed: {exc}")
        traceback.print_exc()
        ok = False
    finally:
        # Restore patched methods
        AdaptiveMainWindow._get_data_dir = original_get_data_dir  # type: ignore[method-assign]
        AdaptiveMainWindow._show_onboarding = original_show_onboarding  # type: ignore[method-assign]

    # Cleanup: hide / deleteLater every widget so Qt doesn't complain
    for w in widgets_created:
        try:
            w.hide()
            w.deleteLater()
        except Exception:
            pass
    _ok(f"Cleaned up {len(widgets_created)} widget(s)")

    # Clean up temp data dir
    import shutil

    try:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        _ok("Temp data directory removed")
    except Exception as exc:
        _fail(f"Failed to remove temp dir: {exc}")

    return ok


# ---------------------------------------------------------------------------
# 6. Circular-import probe
# ---------------------------------------------------------------------------
def test_circular_imports() -> bool:
    _section("6. Circular-Import Probe")
    ok = True

    # Re-import the main entry point in a fresh subprocess to guarantee
    # no stale modules hide a cycle.
    import subprocess

    result = subprocess.run(
        [sys.executable, "-c", "from main import main; print('OK')"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0 and "OK" in result.stdout:
        _ok("main imports cleanly in fresh subprocess")
    else:
        _fail(f"Subprocess import failed: {result.stderr}")
        ok = False

    return ok


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------
def main() -> int:
    print("\n" + "=" * 60)
    print("  HEARTH SMOKE TEST")
    print("  " + PROJECT_ROOT.name)
    print("=" * 60)

    results = [
        test_imports(),
        test_dependencies(),
        test_resources(),
        test_accessibility(),
        test_headless_widgets(),
        test_circular_imports(),
    ]

    _section("Summary")
    passed = sum(results)
    total = len(results)
    if all(results):
        print(f"\n  🎉 ALL {total} CHECKS PASSED\n")
        return 0
    else:
        print(f"\n  ⚠️  {passed}/{total} checks passed\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
