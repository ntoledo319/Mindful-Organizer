"""The evening card — Hearth's DBT diary, rewritten as a quiet end-of-day sit.

A diary card is opened at the end of the hardest days. The old screen met that
moment with a vertical wall: a mood slider, twenty-seven emotion checkboxes, ten
native urge steppers with "Suicide" filed between "Substance use" and
"Binge/purge", a skills grid, target steppers, a meds radio — then a gray
``QMessageBox`` saying "Saved." (docs/design/audit_03). That is an intake form,
not a refuge.

This rebuild keeps the clinical document a therapist actually reads — every
field of :class:`~core.diary_card_manager.DiaryCard` is still filled and saved —
but it asks for it the way a companion would: one warm card at a time, feelings
and skills as soft :class:`~gui.components.state_controls.Pill` tokens, urge
intensities as word-valued :class:`StateSlider`\\s that warm as they rise, never
a native spinbox or checkbox grid.

The two answers that can mean danger — thoughts of harming yourself, thoughts of
suicide — are **lifted out of the urge grid** entirely. They live alone, set
apart, in a card that speaks gently and, when an answer carries real weight,
turns toward the person with one warm door to help (the existing
``crisis_requested`` signal, already wired to the crisis surface in
``main_window``). Disclosure is met with a quiet ember of a confirmation, never a
popup.

Persistence is unchanged: the same ``DiaryCard`` shape, the same
``diary_card_manager.save`` / ``.get`` path, the same ``card_saved`` payload.
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
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
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from gui.components.hearth_surfaces import ONYX, HearthButton, HearthCard
from gui.components.state_controls import (
    Pill,
    StateDial,
    StateSlider,
    serif_font,
    word_for,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Mapping between Hearth's warm word-valued controls and the stored numbers.
# The data model is unchanged (mood 1–10, urges/targets/effectiveness as ints);
# only how a person *sets* them becomes warm and wordless.
# ---------------------------------------------------------------------------
def _dial_to_mood(t: float) -> int:
    """Dial position [0,1] -> stored 1–10 mood score."""
    return max(1, min(10, round(1 + t * 9)))


def _mood_to_dial(score: float) -> float:
    return max(0.0, min(1.0, (float(score) - 1.0) / 9.0))


def _slider_to_level(t: float, top: int = 5) -> int:
    """Slider position [0,1] -> a 0..top intensity (urges, effectiveness)."""
    return max(0, min(top, round(t * top)))


def _level_to_slider(level: int, top: int = 5) -> float:
    if top <= 0:
        return 0.0
    return max(0.0, min(1.0, float(level) / top))


# How strong a self-harm / suicide answer must be before the room turns toward
# help on save. One mark up from "none" already earns a gentle hand; this is the
# floor for the firmer crisis routing.
_CARE_THRESHOLD = 3

# The two answers that are never one more cell in a grid. Pulled out, asked last,
# asked gently — and routed to help, not to a JSON file.
_CARE_URGES = ("Self-harm", "Suicide")

# A short caption per urge-intensity word, so 0–5 reads as language, not a number.
_URGE_WORDS = {
    0: "Not today",
    1: "A flicker",
    2: "Now and then",
    3: "Pulling at me",
    4: "Hard to ignore",
    5: "Loud all day",
}


def _urge_word(level: int) -> str:
    return _URGE_WORDS.get(max(0, min(5, level)), "")


_EFFECTIVENESS_WORDS = {
    1: "Barely",
    2: "A little",
    3: "Some",
    4: "A good deal",
    5: "They carried me",
}


# ---------------------------------------------------------------------------
# FlowLayout — the wrapping row for pill pickers (the classic Qt flow layout,
# same one the mood check-in uses). Pills break to a new line instead of
# forcing the card wider than its window.
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
            w = item.widget()
            if w is not None and not w.isVisible():
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


# ---------------------------------------------------------------------------
# A quiet ember that fades up, holds, and recedes — the save confirmation.
# Lifted in spirit from the mood check-in: never a popup, just a warm word.
# ---------------------------------------------------------------------------
class _EmberConfirm(QLabel):
    """An inline, fading acknowledgement. Warm serif, glows up and recedes."""

    def __init__(self, reduced_motion: bool = False, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._reduced_motion = reduced_motion
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFont(serif_font(17))
        self.setWordWrap(True)
        self._opacity = 0.0
        self.setVisible(False)
        self._set_glow(0.0)

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
        self._fade.setDuration(2800)
        self._fade.setKeyValueAt(0.0, 0.0)
        self._fade.setKeyValueAt(0.14, 1.0)
        self._fade.setKeyValueAt(0.72, 1.0)
        self._fade.setKeyValueAt(1.0, 0.0)
        self._fade.start()


# ---------------------------------------------------------------------------
# A small painted day-stepper — replaces the native QDateEdit calendar popup.
# Most evenings you write tonight's card; back-dating is the rare case, so it is
# one quiet gesture (← a day, today →), not an OS month grid taking the corner.
# ---------------------------------------------------------------------------
class _DayStepper(QWidget):
    """Tonight by default; step back a day or two when you missed one."""

    dateChanged = pyqtSignal()  # noqa: N815

    def __init__(self, reduced_motion: bool = False, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._date = date.today()
        self._reduced_motion = reduced_motion

        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(10)
        row.addStretch()

        self._prev = HearthButton("← the day before", role="ghost", reduced_motion=reduced_motion)
        self._prev.clicked.connect(self._go_back)
        row.addWidget(self._prev)

        self._label = QLabel("")
        self._label.setFont(serif_font(18, QFont.Weight.Medium))
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setMinimumWidth(180)
        self._label.setStyleSheet(f"color: {ONYX['text']}; background: transparent;")
        row.addWidget(self._label)

        self._next = HearthButton("today →", role="ghost", reduced_motion=reduced_motion)
        self._next.clicked.connect(self._go_forward)
        row.addWidget(self._next)
        row.addStretch()

        self._refresh()

    def selected_date(self) -> date:
        return self._date

    def set_date(self, value: date) -> None:
        self._date = value
        self._refresh()

    def _go_back(self) -> None:
        self._date = self._date - timedelta(days=1)
        self._refresh()
        self.dateChanged.emit()

    def _go_forward(self) -> None:
        if self._date >= date.today():
            return
        self._date = min(date.today(), self._date + timedelta(days=1))
        self._refresh()
        self.dateChanged.emit()

    def _refresh(self) -> None:
        today = date.today()
        if self._date == today:
            self._label.setText("Tonight")
        elif self._date == today - timedelta(days=1):
            self._label.setText("Yesterday")
        else:
            self._label.setText(self._date.strftime("%A, %d %b"))
        self._next.setVisible(self._date < today)


# ---------------------------------------------------------------------------
# Widget
# ---------------------------------------------------------------------------
class DiaryCardWidget(QWidget):
    """The evening card: how the day sat, set down one warm section at a time."""

    card_saved = pyqtSignal(dict)
    crisis_requested = pyqtSignal()  # carries the person to 988 + their crisis plan

    def __init__(
        self,
        theme: dict[str, str],
        diary_card_manager: Any = None,
        profile_manager: Any = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._theme = theme
        self._manager = diary_card_manager
        self._profile_manager = profile_manager

        self._reduced_motion = self._detect_reduced_motion()
        self._bg = QColor(ONYX["background"])

        # Pills and sliders, kept by the label the data model stores them under,
        # so save/load round-trip without renaming anything in the DB.
        self._emotion_pills: list[Pill] = []
        self._emotion_more: list[Pill] = []
        self._emotion_more_revealed = False
        self._skill_pills: list[Pill] = []
        self._skill_more: list[Pill] = []
        self._skill_more_revealed = False
        self._urge_pills: dict[str, Pill] = {}
        self._target_pills: dict[str, Pill] = {}
        self._care_sliders: dict[str, StateSlider] = {}

        self._build_ui()
        self._load_today()

    # ------------------------------------------------------------------
    # The warm room behind the cards (matches the daily check-in)
    # ------------------------------------------------------------------
    def paintEvent(self, _event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), self._bg)
        grad = QRadialGradient(self.width() / 2, self.height() * 0.10, self.width() * 0.62)
        warm = QColor(ONYX["accent"])
        warm.setAlpha(20)
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
        root.setContentsMargins(40, 34, 40, 34)
        scroll.setWidget(container)

        # The opening — a sentence, not a form title.
        intro = QLabel("Tonight's card")
        intro.setFont(serif_font(27, QFont.Weight.Medium))
        intro.setAlignment(Qt.AlignmentFlag.AlignCenter)
        intro.setStyleSheet(f"color: {ONYX['text']}; background: transparent;")
        root.addWidget(intro)

        sub = QLabel("A quiet sit with how the day went. Take only the parts that feel true.")
        sub.setFont(serif_font(15))
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setWordWrap(True)
        sub.setStyleSheet(f"color: {ONYX['text_muted']}; background: transparent;")
        root.addWidget(sub)

        self._day = _DayStepper(reduced_motion=self._reduced_motion)
        self._day.dateChanged.connect(self._on_date_changed)
        root.addWidget(self._day)

        root.addSpacing(2)

        root.addWidget(self._build_mood_card())
        root.addWidget(self._build_emotions_card())
        root.addWidget(self._build_urges_card())
        root.addWidget(self._build_skills_card())
        root.addWidget(self._build_targets_card())
        root.addWidget(self._build_meds_card())
        root.addWidget(self._build_notes_card())

        # The one door out, with the care card woven in just above it.
        root.addWidget(self._build_care_card())

        save_row = QHBoxLayout()
        save_row.addStretch()
        self._save_btn = HearthButton(
            "Set the card down", role="primary", reduced_motion=self._reduced_motion
        )
        self._save_btn.clicked.connect(self._save_card)
        save_row.addWidget(self._save_btn)
        save_row.addStretch()
        root.addLayout(save_row)

        self._confirm = _EmberConfirm(reduced_motion=self._reduced_motion)
        root.addWidget(self._confirm)

        root.addStretch()

    # -- a section card with a serif lead --------------------------------
    def _section_card(
        self, lead: str, hint: str = "", *, elevation: int = 1
    ) -> tuple[QWidget, QVBoxLayout]:
        card = HearthCard(elevation=elevation, radius=20)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(30, 26, 30, 26)
        layout.setSpacing(14)

        title = QLabel(lead)
        title.setFont(serif_font(20, QFont.Weight.Medium))
        title.setWordWrap(True)
        title.setStyleSheet(f"color: {ONYX['text']}; background: transparent;")
        layout.addWidget(title)

        if hint:
            sub = QLabel(hint)
            sub.setFont(serif_font(14))
            sub.setWordWrap(True)
            sub.setStyleSheet(f"color: {ONYX['text_muted']}; background: transparent;")
            layout.addWidget(sub)
        return card, layout

    def _build_mood_card(self) -> QWidget:
        card, layout = self._section_card("How did the day sit with you?")
        dial_row = QHBoxLayout()
        dial_row.addStretch()
        self._mood_dial = StateDial(value=0.5, reduced_motion=self._reduced_motion)
        self._mood_dial.setFixedSize(244, 196)
        self._mood_dial.valueChanged.connect(self._on_mood_changed)
        dial_row.addWidget(self._mood_dial)
        dial_row.addStretch()
        layout.addLayout(dial_row)

        self._mood_echo = QLabel("")
        self._mood_echo.setFont(serif_font(15))
        self._mood_echo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._mood_echo.setWordWrap(True)
        self._mood_echo.setStyleSheet(f"color: {ONYX['text_muted']}; background: transparent;")
        layout.addWidget(self._mood_echo)
        self._on_mood_changed(self._mood_dial.value())
        return card

    def _build_emotions_card(self) -> QWidget:
        card, layout = self._section_card(
            "What came through?",
            "The feelings that visited today — tap the ones that ring true.",
        )
        host = QWidget()
        host.setStyleSheet("background: transparent;")
        self._emotion_flow = FlowLayout(host, spacing=8)
        self._build_emotion_pills()
        layout.addWidget(host)
        self._emotion_host = host
        return card

    def _build_emotion_pills(self) -> None:
        self._emotion_pills.clear()
        self._emotion_more.clear()
        while self._emotion_flow.count():
            item = self._emotion_flow.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        emotions = self._get_emotions()
        # A calm handful first (condition packs are appended after the defaults
        # by the manager, so the most-relevant tend to ride at the front for the
        # user's conditions); the rest tuck behind a quiet "more…".
        target = 10
        shown = emotions[:target]
        hidden = emotions[target:]

        for text in shown:
            pill = Pill(text, reduced_motion=self._reduced_motion)
            self._emotion_pills.append(pill)
            self._emotion_flow.addWidget(pill)
        for text in hidden:
            pill = Pill(text, reduced_motion=self._reduced_motion)
            pill.setVisible(self._emotion_more_revealed)
            self._emotion_pills.append(pill)
            self._emotion_more.append(pill)
            self._emotion_flow.addWidget(pill)

        if hidden:
            self._emotion_more_btn = HearthButton(
                "more…", role="ghost", reduced_motion=self._reduced_motion
            )
            self._emotion_more_btn.setVisible(not self._emotion_more_revealed)
            self._emotion_more_btn.clicked.connect(self._reveal_emotion_more)
            self._emotion_flow.addWidget(self._emotion_more_btn)

    def _reveal_emotion_more(self) -> None:
        self._emotion_more_revealed = True
        for pill in self._emotion_more:
            pill.setVisible(True)
        self._emotion_flow.invalidate()
        self._emotion_host.updateGeometry()
        if hasattr(self, "_emotion_more_btn"):
            self._emotion_more_btn.setVisible(False)

    def _build_urges_card(self) -> QWidget:
        card, layout = self._section_card(
            "Anything pulling at you?",
            "The everyday pulls — tap whichever showed up today. (The heavier"
            " ones are asked gently further down.)",
        )
        host = QWidget()
        host.setStyleSheet("background: transparent;")
        self._urge_flow = FlowLayout(host, spacing=8)
        self._urge_pills.clear()
        any_added = False
        for name in self._get_urges():
            if name in _CARE_URGES:
                continue  # these are asked alone, later, in the care card
            any_added = True
            pill = Pill(name, reduced_motion=self._reduced_motion)
            self._urge_pills[name] = pill
            self._urge_flow.addWidget(pill)
        if not any_added:
            empty = QLabel("Nothing here tonight. That's a fine thing.")
            empty.setFont(serif_font(14))
            empty.setStyleSheet(f"color: {ONYX['text_muted']}; background: transparent;")
            layout.addWidget(empty)
        layout.addWidget(host)
        return card

    def _build_care_row(self, data_name: str, prompt: str) -> QWidget:
        """One care-urge: a gentle prompt and a warm slider that reads its own
        intensity as a word. Stored under ``data_name`` (the DB key), asked under
        ``prompt`` (the kind words on screen)."""
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent;")
        col = QVBoxLayout(wrap)
        col.setContentsMargins(0, 6, 0, 6)
        col.setSpacing(2)

        lbl = QLabel(prompt)
        lbl.setFont(serif_font(16))
        lbl.setWordWrap(True)
        lbl.setStyleSheet(f"color: {ONYX['text']}; background: transparent;")
        col.addWidget(lbl)

        # The slider carries its own warm word above the knob; the gentle
        # intensity caption ("A flicker" … "Loud all day") tracks the value too.
        slider = StateSlider(value=0.0, reduced_motion=self._reduced_motion)
        slider.setMinimumHeight(72)
        col.addWidget(slider)

        self._care_sliders[data_name] = slider
        return wrap

    def _build_skills_card(self) -> QWidget:
        card, layout = self._section_card(
            "What helped you carry it?",
            "The skills you reached for today.",
        )
        host = QWidget()
        host.setStyleSheet("background: transparent;")
        self._skill_flow = FlowLayout(host, spacing=8)
        self._build_skill_pills()
        layout.addWidget(host)
        self._skill_host = host

        layout.addSpacing(6)
        eff_head = QLabel("And did they help?")
        eff_head.setFont(serif_font(16, QFont.Weight.Medium))
        eff_head.setStyleSheet(f"color: {ONYX['text']}; background: transparent;")
        layout.addWidget(eff_head)

        eff_word_row = QHBoxLayout()
        eff_word_row.addStretch()
        self._eff_word = QLabel(_EFFECTIVENESS_WORDS[3])
        self._eff_word.setFont(serif_font(15))
        self._eff_word.setStyleSheet(f"color: {ONYX['text_muted']}; background: transparent;")
        eff_word_row.addWidget(self._eff_word)
        layout.addLayout(eff_word_row)

        # Effectiveness is 1..5; seed at 3 ("Some"). Map the 0..1 slider onto 1..5.
        self._eff_slider = StateSlider(value=0.5, reduced_motion=self._reduced_motion)
        self._eff_slider.setMinimumHeight(58)
        self._eff_slider.valueChanged.connect(self._on_eff_changed)
        layout.addWidget(self._eff_slider)
        return card

    def _build_skill_pills(self) -> None:
        self._skill_pills.clear()
        self._skill_more.clear()
        while self._skill_flow.count():
            item = self._skill_flow.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        skills = self._get_skills()
        target = 9
        shown = skills[:target]
        hidden = skills[target:]
        for text in shown:
            pill = Pill(text, reduced_motion=self._reduced_motion)
            self._skill_pills.append(pill)
            self._skill_flow.addWidget(pill)
        for text in hidden:
            pill = Pill(text, reduced_motion=self._reduced_motion)
            pill.setVisible(self._skill_more_revealed)
            self._skill_pills.append(pill)
            self._skill_more.append(pill)
            self._skill_flow.addWidget(pill)
        if hidden:
            self._skill_more_btn = HearthButton(
                "more…", role="ghost", reduced_motion=self._reduced_motion
            )
            self._skill_more_btn.setVisible(not self._skill_more_revealed)
            self._skill_more_btn.clicked.connect(self._reveal_skill_more)
            self._skill_flow.addWidget(self._skill_more_btn)

    def _reveal_skill_more(self) -> None:
        self._skill_more_revealed = True
        for pill in self._skill_more:
            pill.setVisible(True)
        self._skill_flow.invalidate()
        self._skill_host.updateGeometry()
        if hasattr(self, "_skill_more_btn"):
            self._skill_more_btn.setVisible(False)

    def _build_targets_card(self) -> QWidget:
        card, layout = self._section_card(
            "Anything you'd rather not repeat?",
            "Tap whatever happened today — no tallies, no scores.",
        )
        host = QWidget()
        host.setStyleSheet("background: transparent;")
        self._target_flow = FlowLayout(host, spacing=8)
        self._target_pills.clear()
        for name in self._get_targets():
            pill = Pill(name, reduced_motion=self._reduced_motion)
            self._target_pills[name] = pill
            self._target_flow.addWidget(pill)
        layout.addWidget(host)
        return card

    def _build_meds_card(self) -> QWidget:
        card, layout = self._section_card("Medications & substances")

        med_row = QHBoxLayout()
        med_lbl = QLabel("Took your medications as planned?")
        med_lbl.setFont(serif_font(16))
        med_lbl.setWordWrap(True)
        med_lbl.setStyleSheet(f"color: {ONYX['text']}; background: transparent;")
        med_row.addWidget(med_lbl)
        med_row.addStretch()

        # Two soft pills instead of a Yes/No radio pair. They behave as a small
        # toggle group: exactly one is lit at a time.
        self._meds_yes = Pill("Yes", reduced_motion=self._reduced_motion)
        self._meds_no = Pill("Not today", reduced_motion=self._reduced_motion)
        self._meds_yes.setChecked(True)
        self._meds_yes.toggled.connect(self._on_meds_yes)
        self._meds_no.toggled.connect(self._on_meds_no)
        med_row.addWidget(self._meds_yes)
        med_row.addWidget(self._meds_no)
        layout.addLayout(med_row)

        sub_lbl = QLabel("Anything you used to cope? (only if you want to note it)")
        sub_lbl.setFont(serif_font(15))
        sub_lbl.setWordWrap(True)
        sub_lbl.setStyleSheet(f"color: {ONYX['text_muted']}; background: transparent;")
        layout.addWidget(sub_lbl)

        self._substances = QTextEdit()
        self._substances.setPlaceholderText("e.g. a glass of wine, an extra coffee…")
        self._substances.setFixedHeight(48)
        self._substances.setStyleSheet(self._field_style())
        layout.addWidget(self._substances)
        return card

    def _on_meds_yes(self, checked: bool) -> None:
        if checked and self._meds_no.isChecked():
            self._meds_no.blockSignals(True)
            self._meds_no.setChecked(False)
            self._meds_no.blockSignals(False)
        elif not checked and not self._meds_no.isChecked():
            # Keep one always lit — re-light Yes if both would be off.
            self._meds_yes.blockSignals(True)
            self._meds_yes.setChecked(True)
            self._meds_yes.blockSignals(False)

    def _on_meds_no(self, checked: bool) -> None:
        if checked and self._meds_yes.isChecked():
            self._meds_yes.blockSignals(True)
            self._meds_yes.setChecked(False)
            self._meds_yes.blockSignals(False)
        elif not checked and not self._meds_yes.isChecked():
            self._meds_no.blockSignals(True)
            self._meds_no.setChecked(True)
            self._meds_no.blockSignals(False)

    def _build_notes_card(self) -> QWidget:
        card, layout = self._section_card(
            "Anything else worth keeping?",
            "A line for tomorrow's you, if there's something to say.",
        )
        self._notes = QTextEdit()
        self._notes.setPlaceholderText("Whatever's still sitting with you…")
        self._notes.setFixedHeight(110)
        self._notes.setStyleSheet(self._field_style())
        layout.addWidget(self._notes)
        return card

    def _build_care_card(self) -> QWidget:
        """The two heavy answers, set apart and asked gently.

        Self-harm and Suicide are never one more cell in a grid. They live here,
        alone, in a card edged with the calm danger hue — and an answer that
        carries real weight turns the screen toward help on save.
        """
        card = HearthCard(elevation=2, radius=20)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(30, 26, 30, 26)
        layout.setSpacing(12)

        lead = QLabel("If something heavier was here today")
        lead.setFont(serif_font(20, QFont.Weight.Medium))
        lead.setWordWrap(True)
        lead.setStyleSheet(f"color: {ONYX['text']}; background: transparent;")
        layout.addWidget(lead)

        hint = QLabel(
            "You can name it here. Nothing about saying so makes it more real —"
            " it only means you don't have to hold it by yourself."
        )
        hint.setFont(serif_font(14))
        hint.setWordWrap(True)
        hint.setStyleSheet(f"color: {ONYX['text_muted']}; background: transparent;")
        layout.addWidget(hint)

        rule = QWidget()
        rule.setFixedHeight(1)
        rule.setStyleSheet(f"background: {ONYX['crisis']};")
        layout.addWidget(rule)

        self._care_sliders.clear()
        prompts = {
            "Self-harm": "Thoughts of hurting yourself",
            "Suicide": "Thoughts of not being here",
        }
        for name in _CARE_URGES:
            layout.addWidget(self._build_care_row(name, prompts.get(name, name)))

        # The hand on the shoulder — hidden until an answer asks for it.
        self._care_hand = QLabel("")
        self._care_hand.setFont(serif_font(16, QFont.Weight.Medium))
        self._care_hand.setWordWrap(True)
        self._care_hand.setStyleSheet(f"color: {ONYX['crisis']}; background: transparent;")
        self._care_hand.setVisible(False)
        layout.addWidget(self._care_hand)

        hand_row = QHBoxLayout()
        hand_row.addStretch()
        self._care_btn = HearthButton(
            "Open the quiet corner", role="crisis", reduced_motion=self._reduced_motion
        )
        self._care_btn.clicked.connect(self._surface_crisis_resources)
        self._care_btn.setVisible(False)
        hand_row.addWidget(self._care_btn)
        hand_row.addStretch()
        layout.addLayout(hand_row)

        for name in _CARE_URGES:
            self._care_sliders[name].valueChanged.connect(self._on_care_changed)
        return card

    # ------------------------------------------------------------------
    # Styles
    # ------------------------------------------------------------------
    def _field_style(self) -> str:
        return (
            f"QTextEdit {{ background: {ONYX['surface']}; color: {ONYX['text']}; "
            f"border: 1px solid {ONYX['border']}; border-radius: 12px; padding: 10px; "
            f"selection-background-color: {ONYX['accent']}; }}"
        )

    # ------------------------------------------------------------------
    # Data helpers (preserve the existing manager / condition path)
    # ------------------------------------------------------------------
    def _get_conditions(self) -> list[Any]:
        if self._profile_manager and hasattr(self._profile_manager, "current_profile"):
            profile = self._profile_manager.current_profile
            if profile and hasattr(profile, "conditions") and profile.conditions:
                return list(profile.conditions)
        return []

    def _get_emotions(self) -> list[str]:
        if self._manager and hasattr(self._manager, "emotions_for_conditions"):
            return self._manager.emotions_for_conditions(self._get_conditions())
        from core.diary_card_manager import DiaryCardManager

        return DiaryCardManager.emotions_for_conditions(self._get_conditions())

    def _get_urges(self) -> dict[str, int]:
        if self._manager and hasattr(self._manager, "urges_for_conditions"):
            return self._manager.urges_for_conditions(self._get_conditions())
        from core.diary_card_manager import DiaryCardManager

        return DiaryCardManager.urges_for_conditions(self._get_conditions())

    def _get_skills(self) -> list[str]:
        if self._manager and hasattr(self._manager, "skills_for_conditions"):
            return self._manager.skills_for_conditions(self._get_conditions())
        from core.diary_card_manager import DiaryCardManager

        return DiaryCardManager.skills_for_conditions(self._get_conditions())

    def _get_targets(self) -> dict[str, int]:
        if self._manager and hasattr(self._manager, "targets_for_conditions"):
            return self._manager.targets_for_conditions(self._get_conditions())
        from core.diary_card_manager import DiaryCardManager

        return DiaryCardManager.targets_for_conditions(self._get_conditions())

    def _detect_reduced_motion(self) -> bool:
        try:
            from utils.accessibility import detect_reduced_motion

            return detect_reduced_motion()
        except Exception:  # accessibility probing must never block the screen
            return False

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------
    def _on_mood_changed(self, t: float) -> None:
        word = word_for(t)
        echoes = {
            "Bright": "A lighter day. Glad it found you.",
            "Good": "Good to hear. I'll keep it.",
            "Okay": "Okay is plenty. We don't need more than that.",
            "Low": "A low day is still a logged day. That counts.",
            "Bad": "A heavy one. You got through it, and you're here.",
        }
        self._mood_echo.setText(echoes.get(word, ""))

    def _on_eff_changed(self, t: float) -> None:
        level = max(1, _slider_to_level(t))
        self._eff_word.setText(_EFFECTIVENESS_WORDS.get(level, ""))

    def _on_care_changed(self, _t: float) -> None:
        peak = max((_slider_to_level(s.value()) for s in self._care_sliders.values()), default=0)
        if peak >= 1:
            self._care_hand.setText(
                "That's a heavy thing to be carrying. I'm right here — and"
                " there's a quiet corner with people who answer, whenever you want it."
            )
            self._care_hand.setVisible(True)
            self._care_btn.setVisible(True)
        else:
            self._care_hand.setVisible(False)
            self._care_btn.setVisible(False)

    def _on_date_changed(self) -> None:
        self._load_today()

    # ------------------------------------------------------------------
    # Save / load (persistence unchanged: DiaryCard + manager.save/.get)
    # ------------------------------------------------------------------
    def _save_card(self) -> None:
        from core.diary_card_manager import DiaryCard

        selected_date = self._selected_date()

        emotions = [p.text() for p in self._emotion_pills if p.isChecked()]
        skills = [p.text() for p in self._skill_pills if p.isChecked()]

        # Everyday urges are present/absent (a lit pill -> 1); the two care
        # urges carry a graded 0..5 intensity from their sliders.
        urges: dict[str, int] = {
            name: (1 if pill.isChecked() else 0) for name, pill in self._urge_pills.items()
        }
        for name, slider in self._care_sliders.items():
            urges[name] = _slider_to_level(slider.value())

        # Targets are kept as the data model's dict[str,int]: a lit pill is a 1
        # (it happened today), unlit a 0 — forgiving, no tally.
        targets = {
            name: (1 if pill.isChecked() else 0) for name, pill in self._target_pills.items()
        }

        effectiveness = max(1, _slider_to_level(self._eff_slider.value()))

        card = DiaryCard(
            date=selected_date,
            mood_score=_dial_to_mood(self._mood_dial.value()),
            emotions=emotions,
            urges=urges,
            skills_used=skills,
            skills_effectiveness=effectiveness,
            target_behaviors=targets,
            substances_used=self._substances.toPlainText().strip(),
            medications_taken=self._meds_yes.isChecked(),
            notes=self._notes.toPlainText().strip(),
        )

        if self._manager and hasattr(self._manager, "save"):
            try:
                self._manager.save(card)
            except Exception as exc:
                logger.error(f"Diary card save error: {exc}")
                # A save failure must not pop a modal mid-disclosure; acknowledge
                # in-surface and keep the card on screen so nothing is lost.
                self._confirm.acknowledge("I couldn't tuck that away just now — try once more?")
                return

        self.card_saved.emit(card.to_db_dict())

        # The card always saves. But a self-harm / suicide answer above the
        # floor, or risk language in the notes, turns the room toward help
        # instead of a quiet checkmark — care over a tally.
        care_peak = max(
            (_slider_to_level(s.value()) for s in self._care_sliders.values()), default=0
        )
        if care_peak >= _CARE_THRESHOLD or self._check_risk(card.notes):
            self._surface_crisis_resources()
        else:
            self._confirm.acknowledge("Set down. Rest now — tomorrow's a fresh one.")

    def _check_risk(self, text: str) -> bool:
        """Return True if the notes carry explicit self-harm / ideation language."""
        if not text:
            return False
        try:
            from wellness.journal_analyzer import JournalAnalyzer

            return JournalAnalyzer().analyze(text).risk_flagged
        except Exception as exc:  # analysis must never block saving
            logger.debug("Diary card risk analysis failed: %s", exc)
            return False

    def _surface_crisis_resources(self) -> None:
        """Turn the room toward help — ambient, never a modal.

        The card has already saved. Here we light the hand-on-the-shoulder line,
        reveal the warm door, and carry the person to crisis resources via the
        ``crisis_requested`` signal the main window routes to the crisis surface
        (988 + their crisis plan). No QMessageBox interrupts a tender moment.
        """
        self._care_hand.setText(
            "You don't have to carry this alone right now — opening 988 and your"
            " crisis plan. The card is saved; this part matters more."
        )
        self._care_hand.setVisible(True)
        self._care_btn.setVisible(True)
        self.crisis_requested.emit()

    def _load_today(self) -> None:
        if not self._manager or not hasattr(self._manager, "get"):
            return
        selected_date = self._selected_date()
        try:
            card = self._manager.get(selected_date)
        except Exception as exc:
            logger.debug(f"Diary card load error: {exc}")
            return
        if not card:
            self._clear_form()
            return

        self._mood_dial.setValue(_mood_to_dial(card.mood_score))
        self._on_mood_changed(self._mood_dial.value())

        for pill in self._emotion_pills:
            self._set_pill(pill, pill.text() in card.emotions)
        # Reveal the long tail if a saved emotion lives there.
        if any(p.isChecked() for p in self._emotion_more) and not self._emotion_more_revealed:
            self._reveal_emotion_more()

        for name, pill in self._urge_pills.items():
            self._set_pill(pill, card.urges.get(name, 0) > 0)

        for name, slider in self._care_sliders.items():
            slider.setValue(_level_to_slider(card.urges.get(name, 0)), animate=False)
        self._on_care_changed(0.0)

        for pill in self._skill_pills:
            self._set_pill(pill, pill.text() in card.skills_used)
        if any(p.isChecked() for p in self._skill_more) and not self._skill_more_revealed:
            self._reveal_skill_more()

        self._eff_slider.setValue(_level_to_slider(card.skills_effectiveness), animate=False)
        self._on_eff_changed(self._eff_slider.value())

        for name, pill in self._target_pills.items():
            self._set_pill(pill, card.target_behaviors.get(name, 0) > 0)

        self._meds_yes.blockSignals(True)
        self._meds_no.blockSignals(True)
        self._meds_yes.setChecked(card.medications_taken)
        self._meds_no.setChecked(not card.medications_taken)
        self._meds_yes.blockSignals(False)
        self._meds_no.blockSignals(False)

        self._substances.setPlainText(card.substances_used)
        self._notes.setPlainText(card.notes)

    def _set_pill(self, pill: Pill, checked: bool) -> None:
        pill.blockSignals(True)
        pill.setChecked(checked)
        pill.blockSignals(False)

    def _clear_form(self) -> None:
        self._mood_dial.setValue(0.5, animate=False)
        self._on_mood_changed(self._mood_dial.value())
        for pill in self._emotion_pills:
            self._set_pill(pill, False)
        for pill in self._urge_pills.values():
            self._set_pill(pill, False)
        for slider in self._care_sliders.values():
            slider.setValue(0.0, animate=False)
        self._on_care_changed(0.0)
        for pill in self._skill_pills:
            self._set_pill(pill, False)
        self._eff_slider.setValue(0.5, animate=False)
        self._on_eff_changed(self._eff_slider.value())
        for pill in self._target_pills.values():
            self._set_pill(pill, False)
        self._meds_yes.blockSignals(True)
        self._meds_no.blockSignals(True)
        self._meds_yes.setChecked(True)
        self._meds_no.setChecked(False)
        self._meds_yes.blockSignals(False)
        self._meds_no.blockSignals(False)
        self._substances.clear()
        self._notes.clear()

    def _selected_date(self) -> date:
        return self._day.selected_date()

    # ------------------------------------------------------------------
    # Theme
    # ------------------------------------------------------------------
    def apply_theme(self, theme: dict[str, str]) -> None:
        self._theme = theme
        self.update()

    # Kept for any external callers / wiring that referenced it historically.
    def _surface_crisis(self) -> None:
        self._surface_crisis_resources()
