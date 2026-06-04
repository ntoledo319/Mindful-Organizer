"""Duty-of-care: a diary card whose notes signal self-harm must route to help.

The diary card invites people to log their worst urges and darkest notes. If the
free-text notes trip the same risk-language detection the journal uses, saving
must surface 988 + "Open crisis plan" and offer a one-tap jump to crisis
resources — never a bare "Saved" checkmark. An ordinary hard day must NOT.
"""

from __future__ import annotations

import pytest

# A QApplication must exist before any QWidget is constructed. The suite runs
# under QT_QPA_PLATFORM=offscreen, so this never opens a real window.
QtWidgets = pytest.importorskip("PyQt6.QtWidgets")

from gui.widgets import diary_card_widget as dcw  # noqa: E402
from gui.widgets.diary_card_widget import DiaryCardWidget  # noqa: E402


@pytest.fixture(scope="module")
def qapp():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    yield app


@pytest.fixture
def theme():
    # Minimal theme dict — the widget reads colors via .get() with fallbacks.
    return {
        "background": "#ffffff",
        "text": "#222222",
        "accent": "#c4622d",
        "secondary": "#cccccc",
        "card_bg": "#ffffff",
        "border": "#dddddd",
    }


@pytest.fixture
def surfaces(monkeypatch):
    """Capture which surface a save produces without blocking on a dialog.

    The widget either calls QMessageBox.information(...) (routine 'Saved' toast)
    or its own _surface_crisis_resources() (the crisis path). We record both and
    short-circuit the real dialogs so the suite stays headless and unattended.
    """
    seen: dict[str, int] = {"saved": 0, "crisis": 0}

    def fake_information(*_a, **_k):
        seen["saved"] += 1

    def fake_crisis(self):
        seen["crisis"] += 1

    monkeypatch.setattr(dcw.QMessageBox, "information", staticmethod(fake_information))
    monkeypatch.setattr(DiaryCardWidget, "_surface_crisis_resources", fake_crisis)
    return seen


def _save_with_notes(theme, notes: str) -> DiaryCardWidget:
    widget = DiaryCardWidget(theme, diary_card_manager=None, profile_manager=None)
    widget._notes.setPlainText(notes)
    widget._save_card()
    return widget


def test_risky_notes_route_to_crisis_not_saved_toast(qapp, theme, surfaces):
    _save_with_notes(theme, "Logged my urges. Honestly I just want to die today.")
    assert surfaces["crisis"] == 1, "risky notes must surface the crisis resources"
    assert surfaces["saved"] == 0, "no bare 'Saved' toast for a risky entry"


def test_ordinary_hard_day_gets_saved_toast_not_crisis(qapp, theme, surfaces):
    _save_with_notes(theme, "Work was exhausting and I felt overwhelmed and frustrated.")
    assert surfaces["crisis"] == 0, "an ordinary hard day must not trip the crisis surface"
    assert surfaces["saved"] == 1


def test_empty_notes_get_saved_toast_not_crisis(qapp, theme, surfaces):
    _save_with_notes(theme, "")
    assert surfaces["crisis"] == 0
    assert surfaces["saved"] == 1


def test_crisis_surface_emits_one_tap_jump_when_plan_chosen(qapp, theme, monkeypatch):
    """Tapping 'Open crisis plan' must emit crisis_requested for the tab jump."""
    widget = DiaryCardWidget(theme, diary_card_manager=None, profile_manager=None)
    fired: list[bool] = []
    widget.crisis_requested.connect(lambda: fired.append(True))

    # Drive the real _surface_crisis_resources, but make the dialog auto-accept
    # the first button (AcceptRole 'Open crisis plan') without blocking.
    class _AutoAcceptBox:
        Icon = QtWidgets.QMessageBox.Icon
        ButtonRole = QtWidgets.QMessageBox.ButtonRole

        def __init__(self, *_a, **_k):
            self._first = None
            self._clicked = None

        def setIcon(self, *_a):  # noqa: N802 — mirrors the QMessageBox API
            pass

        def setWindowTitle(self, *_a):  # noqa: N802 — mirrors the QMessageBox API
            pass

        def setText(self, *_a):  # noqa: N802 — mirrors the QMessageBox API
            pass

        def addButton(self, *_a):  # noqa: N802 — mirrors the QMessageBox API
            btn = object()
            if self._first is None:
                self._first = btn
            return btn

        def exec(self):
            self._clicked = self._first  # tap 'Open crisis plan'
            return 0

        def clickedButton(self):  # noqa: N802 — mirrors the QMessageBox API
            return self._clicked

    monkeypatch.setattr(dcw, "QMessageBox", _AutoAcceptBox)
    widget._surface_crisis_resources()
    assert fired == [True]
