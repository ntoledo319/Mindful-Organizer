"""
The daily check-in — Hearth's warmest, most-used surface.

This is not a clinical intake. It is the moment you tell the room how you are.
One serif question, one warm dial, a small handful of feelings worth naming,
an optional read on your energy — then it's saved, with a quiet ember of a
confirmation rather than a popup demanding "OK".

It replaces (docs/design/audit_03) the native ``QCalendarWidget``, the wall of
twenty-eight symptom checkboxes (with "Suicidal Ideation" buried as one of
them), and the clinical "New Mood Entry" form. The new entry experience is
built from the signature controls in ``gui.components``:

  * :class:`StateDial`   — "How are you, right now?" The value reads as a word.
  * :class:`Pill`        — "Anything sitting with you?" A short, condition-aware
                            row of feelings; the rest hide behind a quiet "more…".
  * :class:`StateSlider` — an optional, word-valued read on your energy.

Self-harm and ideation are never one undistinguished checkbox in a grid. A low
dial, or naming the feeling that needs care, routes — gently — to crisis
resources via the ``crisis_requested`` signal the main window already wires.

Persistence is unchanged: the same ``mood_manager.add_entry`` (or
``_entries`` + ``MoodEntry``) path, the same ``mood_saved`` payload. The
history list stays for now; the entry flow is the heart of the rebuild.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from PyQt6.QtCore import (
    QEasingCurve,
    QPoint,
    QPropertyAnimation,
    QRect,
    QSize,
    Qt,
    pyqtProperty,
    pyqtSignal,
)
from PyQt6.QtGui import QColor, QFont, QPainter, QRadialGradient
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLayout,
    QLayoutItem,
    QListWidget,
    QListWidgetItem,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from gui.components.hearth_surfaces import ONYX, HearthButton, HearthCard
from gui.components.state_controls import (
    Pill,
    StateDial,
    StateSlider,
    sans_font,
    serif_font,
    word_for,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# FlowLayout — a wrapping row, so the feeling pills break to a new line instead
# of forcing the card wider than its window (the classic Qt flow layout).
# ---------------------------------------------------------------------------
class FlowLayout(QLayout):
    """A left-to-right layout that wraps its items onto new rows as needed."""

    def __init__(self, parent: QWidget | None = None, spacing: int = 8) -> None:
        super().__init__(parent)
        self._items: list[QLayoutItem] = []
        self._spacing = spacing
        self.setContentsMargins(0, 0, 0, 0)

    def addItem(self, item: QLayoutItem) -> None:  # noqa: N802
        self._items.append(item)

    def count(self) -> int:
        return len(self._items)

    def itemAt(self, index: int):  # noqa: N802
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index: int):  # noqa: N802
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def expandingDirections(self):  # noqa: N802
        return Qt.Orientation(0)

    def hasHeightForWidth(self) -> bool:  # noqa: N802
        return True

    def heightForWidth(self, width: int) -> int:  # noqa: N802
        return self._do_layout(QRect(0, 0, width, 0), test_only=True)

    def setGeometry(self, rect: QRect) -> None:  # noqa: N802
        super().setGeometry(rect)
        self._do_layout(rect, test_only=False)

    def sizeHint(self) -> QSize:  # noqa: N802
        return self.minimumSize()

    def minimumSize(self) -> QSize:  # noqa: N802
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        return size

    def _do_layout(self, rect: QRect, *, test_only: bool) -> int:
        x = rect.x()
        y = rect.y()
        line_height = 0
        for item in self._items:
            if item.widget() is not None and not item.widget().isVisible():
                continue
            hint = item.sizeHint()
            next_x = x + hint.width() + self._spacing
            if next_x - self._spacing > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + self._spacing
                next_x = x + hint.width() + self._spacing
                line_height = 0
            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), hint))
            x = next_x
            line_height = max(line_height, hint.height())
        return y + line_height - rect.y()


# A feeling reads as a word, so the dial maps onto the five steady-state words
# the controls already speak (Bad / Low / Okay / Good / Bright). On save we
# carry that back to the 1–10 score the rest of the app stores.
def _dial_to_score(t: float) -> int:
    """Map the dial's [0, 1] position onto the stored 1–10 mood score."""
    return max(1, min(10, round(1 + t * 9)))


def _score_to_dial(score: float) -> float:
    """Inverse of :func:`_dial_to_score`, for seeding the dial from a score."""
    return max(0.0, min(1.0, (float(score) - 1.0) / 9.0))


# The feelings worth naming, grouped so we can show a short, relevant handful
# first and tuck the rest behind a quiet "more…". These are *feelings* a person
# might want to set down, not a symptom checklist — warm, plain, human.
_EVERYDAY_FEELINGS = [
    "Tired",
    "Anxious",
    "Low",
    "Restless",
    "Foggy",
    "Tender",
    "Wired",
    "Numb",
]

_FEELINGS_BY_CONDITION: dict[str, list[str]] = {
    "ADHD": ["Scattered", "Can't start", "Hyperfocused", "Time slipped away"],
    "Anxiety": ["On edge", "Dread", "Heart racing", "Bracing for something"],
    "Depression": ["Heavy", "Hopeless", "Can't feel much", "Worthless"],
    "OCD": ["Stuck in a loop", "Checking", "Need it just-so", "Can't let it go"],
    "PTSD": ["On guard", "Far away", "Easily startled", "Haunted"],
    "Bipolar Disorder": ["Too fast", "Crashing", "Can't sleep", "Untouchable"],
    "Panic Disorder": ["Bracing for something", "Heart racing", "Can't breathe"],
    "BPD": ["Empty", "Abandoned", "Everything at once", "Raw"],
    "Dissociation": ["Far away", "Unreal", "Watching myself"],
}

# The feeling that needs care, not a checkbox. Naming this one — or a "Bad"
# dial — routes to crisis resources rather than quietly logging a symptom.
_CARE_FEELING = "Thoughts of harming myself"


# ---------------------------------------------------------------------------
# A quiet ember that fades up, holds, and fades away — the confirmation.
# ---------------------------------------------------------------------------
class _EmberConfirm(QLabel):
    """An inline, fading acknowledgement. Never a popup; just a warm word.

    It says one plain thing ("Saved. Thank you for telling me.") in the reading
    serif, glows up, holds a moment, and recedes. Under reduced motion it simply
    appears and lingers without the fade.
    """

    def __init__(self, reduced_motion: bool = False, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._reduced_motion = reduced_motion
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFont(serif_font(17))
        self.setStyleSheet(f"color: {ONYX['accent']}; background: transparent;")
        self._opacity = 0.0
        self.setVisible(False)

        self._fade = QPropertyAnimation(self, b"glow", self)
        self._fade.setEasingCurve(QEasingCurve.Type.InOutSine)

    def _get_glow(self) -> float:
        return self._opacity

    def _set_glow(self, v: float) -> None:
        self._opacity = v
        c = QColor(ONYX["accent"])
        c.setAlphaF(max(0.0, min(1.0, v)))
        self.setStyleSheet(
            f"color: rgba({c.red()}, {c.green()}, {c.blue()}, {c.alphaF():.3f}); "
            f"background: transparent;"
        )
        if v <= 0.01:
            self.setVisible(False)

    glow = pyqtProperty(float, fget=_get_glow, fset=_set_glow)

    def acknowledge(self, text: str) -> None:
        self.setText(text)
        self.setVisible(True)
        if self._reduced_motion:
            self._set_glow(1.0)
            return
        self._fade.stop()
        self._fade.setDuration(2600)
        self._fade.setKeyValueAt(0.0, 0.0)
        self._fade.setKeyValueAt(0.14, 1.0)
        self._fade.setKeyValueAt(0.7, 1.0)
        self._fade.setKeyValueAt(1.0, 0.0)
        self._fade.start()


# ---------------------------------------------------------------------------
# Widget
# ---------------------------------------------------------------------------
class MoodTrackerWidget(QWidget):
    """The daily check-in: one warm question, a few feelings, your energy."""

    mood_saved = pyqtSignal(dict)
    # Emitted when the dial bottoms out or a care-feeling is named, so the main
    # window can carry the person straight to 988 + their crisis plan. The main
    # window already connects this to the crisis tab.
    crisis_requested = pyqtSignal()

    def __init__(
        self,
        theme: dict[str, str],
        mood_manager: Any = None,
        profile_manager: Any = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._theme = theme
        self._mood_manager = mood_manager
        self._profile_manager = profile_manager

        self._reduced_motion = self._detect_reduced_motion()
        self._bg = QColor(ONYX["background"])

        self._feeling_pills: list[Pill] = []
        self._care_pill: Pill | None = None
        self._more_pills: list[Pill] = []
        self._more_revealed = False

        self._build_ui()
        self._refresh_history()

    # ------------------------------------------------------------------
    # The warm room behind the cards
    # ------------------------------------------------------------------
    def paintEvent(self, _event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), self._bg)
        # A faint warmth pooled near the top, where the question sits — the same
        # off-screen hearth that warms HearthToday.
        grad = QRadialGradient(self.width() / 2, self.height() * 0.12, self.width() * 0.6)
        warm = QColor(ONYX["accent"])
        warm.setAlpha(22)
        grad.setColorAt(0.0, warm)
        warm2 = QColor(warm)
        warm2.setAlpha(0)
        grad.setColorAt(1.0, warm2)
        p.fillRect(self.rect(), grad)
        p.end()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        scroll.viewport().setStyleSheet("background: transparent;")
        outer.addWidget(scroll)

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        root = QVBoxLayout(container)
        root.setSpacing(20)
        root.setContentsMargins(40, 36, 40, 36)
        scroll.setWidget(container)

        # The entry is the heart of the screen; it gets the room. The history is
        # a quiet drawer beneath it, narrower and dimmer.
        root.addWidget(self._build_checkin_card())
        root.addWidget(self._build_history_card())
        root.addStretch()

    # -- the check-in ---------------------------------------------------
    def _build_checkin_card(self) -> QWidget:
        card = HearthCard(elevation=2, radius=24)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(34, 30, 34, 30)
        layout.setSpacing(18)

        # The one question, in the reading voice.
        question = QLabel("How are you, right now?")
        question.setFont(serif_font(27, QFont.Weight.Medium))
        question.setAlignment(Qt.AlignmentFlag.AlignCenter)
        question.setStyleSheet(f"color: {ONYX['text']}; background: transparent;")
        layout.addWidget(question)

        # The dial — turned, not typed. Its centre already reads as a word.
        # The arc sits in the dial's upper two-thirds, so a slim fixed height
        # keeps the reassurance line riding just beneath the word, not adrift.
        dial_row = QHBoxLayout()
        dial_row.setContentsMargins(0, 0, 0, 0)
        dial_row.addStretch()
        self._dial = StateDial(value=0.5, reduced_motion=self._reduced_motion)
        self._dial.setFixedSize(244, 196)
        self._dial.valueChanged.connect(self._on_dial_changed)
        dial_row.addWidget(self._dial)
        dial_row.addStretch()
        layout.addLayout(dial_row)

        # A soft line of reassurance under the dial — the room is listening.
        self._dial_echo = QLabel("")
        self._dial_echo.setFont(serif_font(15))
        self._dial_echo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._dial_echo.setWordWrap(True)
        self._dial_echo.setStyleSheet(f"color: {ONYX['text_muted']}; background: transparent;")
        layout.addWidget(self._dial_echo)
        self._on_dial_changed(self._dial.value())

        layout.addSpacing(8)

        # The feelings — a short, relevant handful, with the rest tucked away.
        feelings_prompt = QLabel("Anything sitting with you?")
        feelings_prompt.setFont(serif_font(19, QFont.Weight.Medium))
        feelings_prompt.setStyleSheet(f"color: {ONYX['text']}; background: transparent;")
        layout.addWidget(feelings_prompt)

        self._feelings_host = QWidget()
        self._feelings_host.setStyleSheet("background: transparent;")
        self._feelings_flow = FlowLayout(self._feelings_host, spacing=8)
        self._build_feeling_pills()
        layout.addWidget(self._feelings_host)

        # The care line — set apart, never crowded among the everyday feelings.
        self._build_care_row(layout)

        layout.addSpacing(8)

        # Energy — optional, word-valued, quietly offered.
        energy_prompt = QLabel("And your energy?  (only if you want to)")
        energy_prompt.setFont(serif_font(17))
        energy_prompt.setStyleSheet(f"color: {ONYX['text_muted']}; background: transparent;")
        layout.addWidget(energy_prompt)

        self._energy = StateSlider(value=0.5, reduced_motion=self._reduced_motion)
        self._energy.setMinimumHeight(86)
        layout.addWidget(self._energy)

        layout.addSpacing(6)

        # The one door out of the check-in, plus the quiet ember of a thank-you.
        save_row = QHBoxLayout()
        save_row.addStretch()
        self._save_btn = HearthButton(
            "Set it down", role="primary", reduced_motion=self._reduced_motion
        )
        self._save_btn.clicked.connect(self._save_entry)
        save_row.addWidget(self._save_btn)
        save_row.addStretch()
        layout.addLayout(save_row)

        self._confirm = _EmberConfirm(reduced_motion=self._reduced_motion)
        layout.addWidget(self._confirm)

        return card

    def _build_feeling_pills(self) -> None:
        """Fill the wrapping flow with the relevant feelings first, then the
        rest behind a quiet 'more…'. One flow row, wrapping as the card narrows."""
        # Clear any previous pills (apply_theme can rebuild).
        self._feeling_pills.clear()
        self._more_pills.clear()
        while self._feelings_flow.count():
            item = self._feelings_flow.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        shown, hidden = self._partition_feelings()

        for text in shown:
            pill = self._make_pill(text)
            self._feeling_pills.append(pill)
            self._feelings_flow.addWidget(pill)

        # The hidden feelings sit in the same flow, simply not shown until asked.
        for text in hidden:
            pill = self._make_pill(text)
            pill.setVisible(self._more_revealed)
            self._feeling_pills.append(pill)
            self._more_pills.append(pill)
            self._feelings_flow.addWidget(pill)

        # The "more…" toggle — a recessive ghost that flows in line with the
        # pills, present but never loud. It removes itself once everything shows.
        if hidden:
            self._more_btn = HearthButton(
                "more…", role="ghost", reduced_motion=self._reduced_motion
            )
            self._more_btn.setVisible(not self._more_revealed)
            self._more_btn.clicked.connect(self._reveal_more)
            self._feelings_flow.addWidget(self._more_btn)

    def _build_care_row(self, layout: QVBoxLayout) -> None:
        # The care-feeling sits on its own, set apart by a thin warm rule and a
        # quiet caption — never one more pill in the grid. It is a door to help,
        # not a symptom to tally; tapping it (or a "Bad" dial) opens crisis
        # resources at once.
        layout.addSpacing(4)
        rule = QWidget()
        rule.setFixedHeight(1)
        rule.setStyleSheet(f"background: {ONYX['border']};")
        layout.addWidget(rule)

        care_caption = QLabel("If something heavier is here, you can say it:")
        care_caption.setFont(serif_font(14))
        care_caption.setStyleSheet(f"color: {ONYX['text_muted']}; background: transparent;")
        layout.addWidget(care_caption)

        care_wrap = QHBoxLayout()
        self._care_pill = Pill(_CARE_FEELING, reduced_motion=self._reduced_motion)
        self._care_pill.toggled.connect(self._on_care_toggled)
        care_wrap.addWidget(self._care_pill)
        care_wrap.addStretch()
        layout.addLayout(care_wrap)

    def _make_pill(self, text: str) -> Pill:
        return Pill(text, reduced_motion=self._reduced_motion)

    def _reveal_more(self) -> None:
        self._more_revealed = True
        for pill in self._more_pills:
            pill.setVisible(True)
        self._feelings_flow.invalidate()
        self._feelings_host.updateGeometry()
        if hasattr(self, "_more_btn"):
            self._more_btn.setVisible(False)

    def _partition_feelings(self) -> tuple[list[str], list[str]]:
        """Return (shown, hidden) feeling labels for the current profile.

        Shown: condition-specific feelings first (they're why this person is
        here), then enough everyday feelings to reach a calm handful (~7).
        Hidden: the remaining everyday feelings, behind 'more…'.
        """
        conditions = self._conditions()
        specific: list[str] = []
        for cond in conditions:
            for feeling in _FEELINGS_BY_CONDITION.get(cond, []):
                if feeling not in specific:
                    specific.append(feeling)

        ordered: list[str] = []
        for feeling in specific + _EVERYDAY_FEELINGS:
            if feeling not in ordered:
                ordered.append(feeling)

        target = 8 if specific else 6
        shown = ordered[:target]
        hidden = ordered[target:]
        return shown, hidden

    def _conditions(self) -> list[str]:
        conditions: list[str] = []
        pm = self._profile_manager
        if pm and hasattr(pm, "current_profile"):
            profile = pm.current_profile
            if profile and getattr(profile, "conditions", None):
                for cond in profile.conditions:
                    conditions.append(cond.value if hasattr(cond, "value") else str(cond))
        return conditions

    # -- history (kept, but quieted) ------------------------------------
    def _build_history_card(self) -> QWidget:
        card = HearthCard(elevation=0, radius=20)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(28, 22, 28, 24)
        layout.setSpacing(12)

        title = QLabel("Lately")
        title.setFont(serif_font(18, QFont.Weight.Medium))
        title.setStyleSheet(f"color: {ONYX['text']}; background: transparent;")
        layout.addWidget(title)

        self._history_empty = QLabel("Nothing set down yet. When you do, it'll rest here.")
        self._history_empty.setFont(sans_font(12))
        self._history_empty.setWordWrap(True)
        self._history_empty.setStyleSheet(f"color: {ONYX['text_muted']}; background: transparent;")
        layout.addWidget(self._history_empty)

        self._history_list = QListWidget()
        self._history_list.setMinimumHeight(150)
        self._history_list.setFrameShape(QListWidget.Shape.NoFrame)
        self._history_list.setStyleSheet(
            f"QListWidget {{ background: transparent; border: none; "
            f"color: {ONYX['text']}; }}"
            f"QListWidget::item {{ padding: 9px 4px; "
            f"border-bottom: 1px solid {ONYX['border']}; }}"
            f"QListWidget::item:selected {{ background: {ONYX['surface_raised']}; "
            f"color: {ONYX['text']}; }}"
        )
        layout.addWidget(self._history_list)
        return card

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------
    def _detect_reduced_motion(self) -> bool:
        try:
            from utils.accessibility import detect_reduced_motion

            return detect_reduced_motion()
        except Exception:  # accessibility probing must never block the screen
            return False

    def _on_dial_changed(self, t: float) -> None:
        # Mirror the dial's word in a gentle, plain echo — and, at the very
        # bottom, soften toward an offer of help rather than a logged "Bad".
        word = word_for(t)
        echoes = {
            "Bright": "Glad it's a brighter one. I'll remember.",
            "Good": "Good to hear. Thanks for telling me.",
            "Okay": "Okay is allowed. I'm here either way.",
            "Low": "Low is worth naming. We can go slow.",
            "Bad": "That sounds heavy. You don't have to hold it alone.",
        }
        self._dial_echo.setText(echoes.get(word, ""))

    def _on_care_toggled(self, checked: bool) -> None:
        if checked:
            # Don't wait for "save" — naming this opens the door to help now.
            self._surface_crisis()

    def _surface_crisis(self) -> None:
        """Carry the person to crisis resources via the wired signal.

        No QMessageBox: the main window already routes ``crisis_requested`` to
        the crisis tab (988 + the crisis plan). We add a warm inline line so the
        screen itself acknowledges the moment.
        """
        self._dial_echo.setText(
            "You don't have to carry this alone — opening 988 and your crisis plan."
        )
        self.crisis_requested.emit()

    def _save_entry(self) -> None:
        dial_t = self._dial.value()
        score = _dial_to_score(dial_t)

        feelings = [p.text() for p in self._feeling_pills if p.isChecked()]
        care_named = bool(self._care_pill and self._care_pill.isChecked())
        if care_named:
            feelings.append(_CARE_FEELING)

        energy_word = word_for(self._energy.value())
        energy_score = round(self._energy.value() * 100)

        timestamp = datetime.now()
        notes = f"Energy: {energy_word}" if energy_word else ""

        entry: dict[str, Any] = {
            "timestamp": timestamp.isoformat(),
            "mood_score": score,
            "symptoms": feelings,
            "therapy_skills": [],
            "energy_score": energy_score,
            "notes": notes,
        }

        # SAME persistence the widget has always used.
        if self._mood_manager:
            try:
                if hasattr(self._mood_manager, "add_entry"):
                    self._mood_manager.add_entry(entry)
                elif hasattr(self._mood_manager, "_entries"):
                    from core.mood_analytics import MoodEntry

                    me = MoodEntry(
                        timestamp=timestamp,
                        mood_score=float(score),
                        energy_score=float(energy_score),
                        symptoms=feelings,
                        notes=notes,
                        activities=[],
                    )
                    self._mood_manager._entries.append(me)
            except (AttributeError, TypeError) as exc:
                logger.debug(f"Mood save error: {exc}")

        self.mood_saved.emit(entry)

        # A low dial or a named care-feeling routes to help — care over a
        # checkmark. (If the care pill was tapped, the door already opened.)
        risk = score <= 2 or word_for(dial_t) == "Bad"
        if risk and not care_named:
            self._surface_crisis()
        else:
            self._confirm.acknowledge("Set down. Thank you for telling me.")

        self._reset_form()
        self._refresh_history()

    def _reset_form(self) -> None:
        self._dial.setValue(0.5)
        self._energy.setValue(0.5)
        for pill in self._feeling_pills:
            if pill.isChecked():
                pill.setChecked(False)
        if self._care_pill and self._care_pill.isChecked():
            # Avoid re-triggering the crisis route while clearing.
            self._care_pill.blockSignals(True)
            self._care_pill.setChecked(False)
            self._care_pill.blockSignals(False)

    def _refresh_history(self) -> None:
        self._history_list.clear()
        entries: list = []
        if self._mood_manager and hasattr(self._mood_manager, "_entries"):
            try:
                entries = list(self._mood_manager._entries)
                entries.sort(key=lambda e: e.timestamp, reverse=True)
            except (AttributeError, TypeError) as exc:
                logger.debug(f"History refresh error: {exc}")
                entries = []

        has_any = bool(entries)
        self._history_empty.setVisible(not has_any)
        self._history_list.setVisible(has_any)

        for entry in entries[:50]:
            try:
                ts = entry.timestamp.strftime("%a %d %b · %H:%M")
                word = word_for(_score_to_dial(entry.mood_score))
                feelings = list(getattr(entry, "symptoms", []) or [])
                tail = f"  —  {', '.join(feelings[:3])}" if feelings else ""
                item = QListWidgetItem(f"{ts}     {word}{tail}")
                item.setFont(sans_font(12))
                self._history_list.addItem(item)
            except (AttributeError, TypeError) as exc:
                logger.debug(f"History row error: {exc}")

    # ------------------------------------------------------------------
    # Theme
    # ------------------------------------------------------------------
    def apply_theme(self, theme: dict[str, str]) -> None:
        self._theme = theme
        self.update()
