"""Duty-of-care: a diary card whose notes signal self-harm must route to help.

The diary card invites people to log their worst urges and darkest notes. If the
free-text notes trip the same risk-language detection the journal uses, saving
must surface the crisis resources (988 + the crisis plan via ``crisis_requested``)
rather than a quiet "set down" acknowledgement. An ordinary hard day must NOT.

Per docs/design/VISION.md (principle 4: "Disclosure is met with adaptation,
never with a dialog box"), the diary no longer pops a ``QMessageBox`` after a
save. A routine save lights an ambient ember confirmation; a risky save turns the
room toward help in-surface. These tests assert which of those two paths a save
takes, and that the crisis path emits the one-tap jump signal.
"""

from __future__ import annotations

import pytest

# A QApplication must exist before any QWidget is constructed. The suite runs
# under QT_QPA_PLATFORM=offscreen, so this never opens a real window.
QtWidgets = pytest.importorskip("PyQt6.QtWidgets")

from gui.widgets.diary_card_widget import DiaryCardWidget  # noqa: E402


@pytest.fixture(scope="module")
def qapp():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    yield app


@pytest.fixture
def theme():
    # Minimal theme dict — the widget paints from the Onyx component palette and
    # only stashes this for apply_theme, but the constructor still expects it.
    return {
        "background": "#0F0F11",
        "text": "#F2EDE6",
        "accent": "#D9A05B",
        "border": "#2E2A24",
    }


@pytest.fixture
def surfaces(monkeypatch):
    """Capture which surface a save produces without driving any real dialog.

    A save either lights the ambient ember confirmation (routine "set down") or
    routes to ``_surface_crisis_resources`` (the crisis path). We record both so
    the suite stays headless and unattended.
    """
    seen: dict[str, int] = {"saved": 0, "crisis": 0}

    def fake_acknowledge(self, _text):
        seen["saved"] += 1

    def fake_crisis(self):
        seen["crisis"] += 1

    from gui.widgets import diary_card_widget as dcw

    monkeypatch.setattr(dcw._EmberConfirm, "acknowledge", fake_acknowledge)
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
    assert surfaces["saved"] == 0, "no quiet 'set down' line for a risky entry"


def test_ordinary_hard_day_gets_saved_toast_not_crisis(qapp, theme, surfaces):
    _save_with_notes(theme, "Work was exhausting and I felt overwhelmed and frustrated.")
    assert surfaces["crisis"] == 0, "an ordinary hard day must not trip the crisis surface"
    assert surfaces["saved"] == 1


def test_empty_notes_get_saved_toast_not_crisis(qapp, theme, surfaces):
    _save_with_notes(theme, "")
    assert surfaces["crisis"] == 0
    assert surfaces["saved"] == 1


def test_high_care_urge_routes_to_crisis(qapp, theme, surfaces):
    """A strong self-harm / suicide answer routes to help, even with calm notes."""
    widget = DiaryCardWidget(theme, diary_card_manager=None, profile_manager=None)
    widget._notes.setPlainText("")
    widget._care_sliders["Suicide"].setValue(1.0, animate=False)  # "Loud all day"
    widget._save_card()
    assert surfaces["crisis"] == 1, "a strong care-urge must surface crisis resources"
    assert surfaces["saved"] == 0


def test_crisis_surface_emits_one_tap_jump(qapp, theme):
    """Surfacing crisis resources emits crisis_requested for the tab jump — and
    does so in-surface, with no modal dialog."""
    widget = DiaryCardWidget(theme, diary_card_manager=None, profile_manager=None)
    fired: list[bool] = []
    widget.crisis_requested.connect(lambda: fired.append(True))
    widget._surface_crisis_resources()
    assert fired == [True]
    # The in-surface "hand on the shoulder" is lit (no modal dialog). The widget
    # is never shown in the headless suite, so check the warm door was un-hidden
    # explicitly rather than its effective on-screen visibility.
    assert not widget._care_btn.isHidden()
    assert "988" in widget._care_hand.text()
