"""
Panic — the now/later split (docs/design/audit_05, VISION.md, DESIGN_SYSTEM.md).

A panicking person is not handed a form. The surface opens in **now** mode: a
warm full-bleed room with the breathing pacer (BreathOrb) set slow — its long
exhale paces the breath *down* — one grounding serif line, and a single
barely-there ghost door to move on. No logging UI is visible while the storm is
loud; breathing with the light *is* the help.

When it eases, **later** mode is a soft, one-question-at-a-time reflection
(what happened · how strong · what helped) built from the warm controls
(an intensity slider that reads in waves, Pills for triggers and what-helped) —
forgiving, never a clinical grid. It persists through the *same* panic-log
JSON the widget has always used: ``_entries`` / ``_load_entries`` /
``_save_entries`` are untouched, so history and the ``panic_logged`` signal
keep their existing data shape.

The empty state gives instead of accusing. And if the free text names
self-harm, the surface routes to help through ``crisis_requested`` — the same
signal the main window already connects for mood / diary / journal.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from PyQt6.QtCore import (
    QEasingCurve,
    QPointF,
    QPropertyAnimation,
    QRectF,
    Qt,
    pyqtSignal,
)
from PyQt6.QtGui import (
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QRadialGradient,
)
from PyQt6.QtWidgets import (
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.paths import get_data_dir
from gui.components.breath_orb import BreathOrb
from gui.components.hearth_surfaces import ONYX, HearthButton
from gui.components.state_controls import (
    PALETTE,
    Pill,
    StateSlider,
    _mix,
    sans_font,
    serif_font,
    warmth_color,
)
from gui.widgets.mood_tracker import FlowLayout

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Local palette — Onyx (the warm dark default). A stand-in for ResolvedTokens,
# mirroring the component palettes so nothing hardcodes a stray hex.
# ---------------------------------------------------------------------------
_PAL = {
    "bg": ONYX["background"],  # warm near-black room
    "surface": ONYX["surface"],
    "text": ONYX["text"],  # warm off-white
    "text_muted": ONYX["text_muted"],  # clears AA on surface
    "accent": ONYX["accent"],  # hearthlight amber
    "ember": ONYX["ember"],  # deeper ember
    "border": ONYX["border"],
}


# The triggers worth naming after the wave — plain, human, not a symptom grid.
_TRIGGER_OPTIONS = [
    "Something I read or saw",
    "A conversation",
    "Running late",
    "A crowd",
    "Out of nowhere",
    "Too much caffeine",
    "Not enough sleep",
    "A memory",
    "Money",
    "Health worry",
]

# What helped — phrased as things you *did*, not techniques to grade.
_HELPED_OPTIONS = [
    "Breathing slow",
    "Cold water",
    "Stepped outside",
    "Texted someone",
    "Called someone",
    "Took my meds",
    "Just waited",
    "Moved my body",
    "Named what's real",
]

# The intensity words the slider speaks at the panic surface — these read as how
# a wave *felt*, not a 0–10 number. Mapped back to a 1–10 score on save so the
# existing history/stats keep their data shape.
_INTENSITY_WORDS = ["A ripple", "A swell", "A strong wave", "It took over", "The worst kind"]


def _intensity_to_score(t: float) -> int:
    """Map the slider's [0, 1] position onto the stored 1–10 peak distress."""
    return max(1, min(10, round(1 + t * 9)))


def _intensity_word(t: float) -> str:
    idx = int(round(max(0.0, min(1.0, t)) * (len(_INTENSITY_WORDS) - 1)))
    return _INTENSITY_WORDS[idx]


# Conservative, multi-word self-harm phrases — a supportive nudge toward real
# help, never a diagnosis. Kept local so the panic surface has no hard dependency
# on the journal analyzer, but shares its spirit (and several of its phrases).
_RISK_PHRASES = (
    "kill myself",
    "killing myself",
    "end my life",
    "ending my life",
    "want to die",
    "wanna die",
    "wish i was dead",
    "wish i were dead",
    "better off dead",
    "no reason to live",
    "nothing to live for",
    "can't go on",
    "cannot go on",
    "hurt myself",
    "harming myself",
    "harm myself",
    "self harm",
    "self-harm",
    "cut myself",
    "suicidal",
    "suicide",
    "take my own life",
    "end it all",
)


def _names_self_harm(text: str) -> bool:
    low = (text or "").lower()
    return any(phrase in low for phrase in _RISK_PHRASES)


# ---------------------------------------------------------------------------
# WaveSlider — a StateSlider that speaks in waves, not "Okay / Good".
# ---------------------------------------------------------------------------
class WaveSlider(StateSlider):
    """The intensity control for the panic log.

    Identical to :class:`StateSlider` in every behaviour (drag, ease, warmth
    ramp, ``valueChanged``) but it paints the value as a *wave* word
    (:data:`_INTENSITY_WORDS`) instead of the steady-state mood vocabulary, so
    a person reads "A strong wave", never a number.
    """

    def paintEvent(self, _):  # noqa: N802 — mirrors StateSlider, swaps the word
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        tr = self._track_rect()
        radius = tr.height() / 2
        glow = warmth_color(self._display)

        groove = QPainterPath()
        groove.addRoundedRect(tr, radius, radius)
        p.fillPath(groove, QColor(PALETTE["border"]))

        knob_x = tr.left() + tr.width() * self._display
        fill_rect = QRectF(tr.left(), tr.top(), max(radius * 2, knob_x - tr.left()), tr.height())
        fill_path = QPainterPath()
        fill_path.addRoundedRect(fill_rect, radius, radius)
        grad = QLinearGradient(tr.left(), 0, tr.right(), 0)
        grad.setColorAt(0.0, warmth_color(0.08))
        grad.setColorAt(max(0.001, self._display * 0.5), warmth_color(self._display * 0.6))
        grad.setColorAt(min(0.999, self._display), glow)
        p.fillPath(fill_path, grad)

        bloom = QRadialGradient(QPointF(knob_x, tr.center().y()), 34)
        b0 = QColor(glow)
        b0.setAlpha(120)
        bloom.setColorAt(0.0, b0)
        bloom.setColorAt(1.0, QColor(glow.red(), glow.green(), glow.blue(), 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(bloom)
        p.drawEllipse(QPointF(knob_x, tr.center().y()), 28, 28)

        kr = 13.0
        kg = QRadialGradient(QPointF(knob_x - 3, tr.center().y() - 3), kr * 1.7)
        kg.setColorAt(0.0, _mix(glow, QColor("#FFFFFF"), 0.34))
        kg.setColorAt(1.0, _mix(glow, QColor(PALETTE["bg"]), 0.22))
        p.setBrush(kg)
        p.setPen(QPen(QColor(PALETTE["bg"]), 1.5))
        p.drawEllipse(QPointF(knob_x, tr.center().y()), kr, kr)

        word = _intensity_word(self._display)
        p.setFont(serif_font(20, QFont.Weight.Medium))
        fm = p.fontMetrics()
        wd = fm.horizontalAdvance(word)
        wx = max(tr.left(), min(tr.right() - wd, knob_x - wd / 2))
        p.setPen(QColor(PALETTE["text"]))
        p.drawText(
            QRectF(wx, tr.top() - 36, wd + 4, 30),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            word,
        )
        p.end()


# ---------------------------------------------------------------------------
# _FlowHost — a wrapping pill container that actually reserves its height.
# ---------------------------------------------------------------------------
class _FlowHost(QWidget):
    """A host for a :class:`FlowLayout` that reports the height its rows need.

    In a centred, stretch-padded page (not a scroll area), a bare ``QWidget``
    gets squeezed to a single row and the pills overlap. Reporting
    ``heightForWidth`` and a height-for-width size policy keeps every row
    visible.
    """

    def __init__(self, parent: QWidget | None = None, spacing: int = 10) -> None:
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        self.flow = FlowLayout(self, spacing=spacing)
        from PyQt6.QtWidgets import QSizePolicy

        pol = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        pol.setHeightForWidth(True)
        self.setSizePolicy(pol)

    def add_pill(self, pill: Pill) -> None:
        self.flow.addWidget(pill)
        # Reserve enough height for the rows up front (estimated at a typical
        # page width) so pills never stack before the first real resize.
        self.setMinimumHeight(self.flow.heightForWidth(self._est_width()))

    def _est_width(self) -> int:
        return self.width() if self.width() > 80 else 760

    def hasHeightForWidth(self) -> bool:  # noqa: N802
        return True

    def heightForWidth(self, width: int) -> int:  # noqa: N802
        return self.flow.heightForWidth(width)

    def resizeEvent(self, event):  # noqa: N802
        # When the page lays us out we finally know our width — reserve exactly
        # the height the wrapped rows need so no pill stacks on top of another.
        super().resizeEvent(event)
        self.relayout()

    def relayout(self) -> None:
        """Re-wrap the pills at the current width.

        FlowLayout skips hidden widgets, so when a step page is hidden and
        re-shown its pills can collapse onto one row. Calling this when the
        step becomes visible re-lays them out and restores the reserved height.
        """
        w = self._est_width()
        h = self.flow.heightForWidth(w)
        if h > 0:
            self.setMinimumHeight(h)
            self.flow.setGeometry(self.rect())

    def minimumSizeHint(self):  # noqa: N802
        from PyQt6.QtCore import QSize

        return QSize(0, self.flow.heightForWidth(self._est_width()))

    def sizeHint(self):  # noqa: N802
        from PyQt6.QtCore import QSize

        return QSize(self._est_width(), self.flow.heightForWidth(self._est_width()))


# ---------------------------------------------------------------------------
# Widget
# ---------------------------------------------------------------------------


class PanicTrackerWidget(QWidget):
    """The panic surface, split by *state*: a "now" room, then a gentle "later".

    Opens in **now** mode — the breathing pacer and one grounding line, nothing
    to fill in. The single ghost door ("When it eases, set down what happened")
    *transitions* (it does not navigate away) into **later** mode: a one-question
    reflection that persists through the existing panic-log JSON.
    """

    panic_logged = pyqtSignal(dict)
    crisis_requested = pyqtSignal()

    def __init__(self, main_window: Any, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.main_window = main_window
        self._entries: list[dict[str, Any]] = []
        self._data_dir = self._resolve_data_dir()
        self._load_entries()
        self._reduced_motion = self._detect_reduced_motion()

        # "later" mode draft state, assembled across the one-question steps.
        self._intensity_t = 0.5
        self._trigger_pills: list[Pill] = []
        self._helped_pills: list[Pill] = []
        self._step = 0
        self._page_anim: QPropertyAnimation | None = None

        self._build_ui()

    # -- persistence (unchanged data contract) ----------------------------
    def _resolve_data_dir(self) -> Path:
        try:
            return Path(self.main_window.data_dir) / "panic_logs"
        except (AttributeError, TypeError):
            return get_data_dir() / "panic_logs"

    def _load_entries(self) -> None:
        file_path = self._data_dir / "panic_logs.json"
        if file_path.exists():
            try:
                with open(file_path) as f:
                    self._entries = json.load(f)
            except (json.JSONDecodeError, OSError) as exc:
                logger.debug(f"Panic logs load error: {exc}")

    def _save_entries(self) -> None:
        self._data_dir.mkdir(parents=True, exist_ok=True)
        try:
            with open(self._data_dir / "panic_logs.json", "w") as f:
                json.dump(self._entries, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save panic logs: {e}")

    # -- accessibility ----------------------------------------------------
    def _detect_reduced_motion(self) -> bool:
        try:
            from utils.accessibility import detect_reduced_motion

            return detect_reduced_motion()
        except Exception:  # probing must never block a distress surface
            return False

    # -- the warm room background -----------------------------------------
    def paintEvent(self, _event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), QColor(_PAL["bg"]))
        # A low warmth pooled behind the centre, where the pacer breathes — the
        # room lit from within, never a flat charcoal panel.
        cx = self.width() / 2
        cy = self.height() * 0.44
        grad = QRadialGradient(cx, cy, self.width() * 0.62)
        warm = QColor(_PAL["accent"])
        warm.setAlpha(30)
        grad.setColorAt(0.0, warm)
        edge = QColor(warm)
        edge.setAlpha(0)
        grad.setColorAt(1.0, edge)
        p.fillRect(self.rect(), grad)
        p.end()

    # -- structure --------------------------------------------------------
    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        self._stack = QStackedWidget()
        # The stack must not paint an opaque panel over our warm room.
        self._stack.setStyleSheet("background: transparent;")
        outer.addWidget(self._stack)

        self._now_page = self._build_now_page()
        self._later_page = self._build_later_page()
        self._stack.addWidget(self._now_page)  # index 0 — the default landing
        self._stack.addWidget(self._later_page)  # index 1
        self._stack.setCurrentIndex(0)

    # -- NOW: immediate, wordless help ------------------------------------
    def _build_now_page(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(page)
        lay.setContentsMargins(40, 24, 40, 28)
        lay.setSpacing(0)
        lay.addStretch(2)

        # The pacer. A long, slow exhale (paced below a panic rate) draws the
        # breath down — not box-breathing's even square. Transparent so it
        # composites over our warm room with no seam.
        self._pacer = BreathOrb(
            inhale=4000,
            hold_in=1500,
            exhale=7000,
            hold_out=1500,
            reduced_motion=self._reduced_motion,
            transparent_bg=True,
        )
        self._pacer.setMinimumHeight(380)
        lay.addWidget(self._pacer)

        # One grounding line, in the reading serif. Not instructions — a hand.
        ground = QLabel("This wave will crest and fall. It always has. Breathe with the light.")
        ground.setFont(serif_font(20))
        ground.setWordWrap(True)
        ground.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ground.setStyleSheet(f"color: {_PAL['text']}; background: transparent;")
        lay.addWidget(ground)

        lay.addSpacing(22)

        # The single, barely-there door onward. A ghost — it never competes with
        # the breath, and it never demands. It *transitions*; it does not leave.
        door_row = QHBoxLayout()
        door_row.addStretch()
        self._to_later = HearthButton(
            "When it eases, set down what happened",
            role="ghost",
            reduced_motion=self._reduced_motion,
        )
        self._to_later.clicked.connect(self._enter_later)
        door_row.addWidget(self._to_later)
        door_row.addStretch()
        lay.addLayout(door_row)

        lay.addStretch(1)
        return page

    # -- LATER: one question at a time ------------------------------------
    def _build_later_page(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(page)
        lay.setContentsMargins(48, 36, 48, 32)
        lay.setSpacing(0)
        lay.addStretch(1)

        # The quiet step kicker — small, sans, never loud.
        self._kicker = QLabel("")
        self._kicker.setFont(sans_font(11))
        self._kicker.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._kicker.setStyleSheet(
            f"color: {_PAL['text_muted']}; background: transparent; letter-spacing: 1px;"
        )
        lay.addWidget(self._kicker)
        lay.addSpacing(10)

        # The question, in the reading serif — the thing you actually read.
        self._question = QLabel("")
        self._question.setFont(serif_font(27))
        self._question.setWordWrap(True)
        self._question.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._question.setStyleSheet(f"color: {_PAL['text']}; background: transparent;")
        lay.addWidget(self._question)
        lay.addSpacing(26)

        # The body of each step swaps in here — one decision at a time.
        self._step_body = QStackedWidget()
        self._step_body.setStyleSheet("background: transparent;")
        self._step_body.addWidget(self._build_step_what())  # 0
        self._step_body.addWidget(self._build_step_strong())  # 1
        self._step_body.addWidget(self._build_step_helped())  # 2
        self._step_body.addWidget(self._build_step_done())  # 3 — the warm close
        lay.addWidget(self._step_body)

        lay.addSpacing(30)

        # The footer: a recessive "back", and the one warm action forward.
        foot = QHBoxLayout()
        self._back_btn = HearthButton("Not now", role="ghost", reduced_motion=self._reduced_motion)
        self._back_btn.clicked.connect(self._step_back)
        foot.addWidget(self._back_btn)
        foot.addStretch()
        self._next_btn = HearthButton("Next", role="primary", reduced_motion=self._reduced_motion)
        self._next_btn.clicked.connect(self._step_next)
        foot.addWidget(self._next_btn)
        lay.addLayout(foot)

        lay.addStretch(1)
        return page

    def _build_step_what(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        col = QVBoxLayout(w)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(16)

        # Triggers as soft Pills (wrapping), never a checkbox column.
        host = _FlowHost(spacing=10)
        self._trigger_host = host
        for label in _TRIGGER_OPTIONS:
            pill = Pill(label, reduced_motion=self._reduced_motion)
            host.add_pill(pill)
            self._trigger_pills.append(pill)
        col.addWidget(host)

        # One calm, optional free-text field — for the words a pill can't hold.
        self._note_edit = QTextEdit()
        self._note_edit.setPlaceholderText("Anything you want to put into words… (optional)")
        self._note_edit.setMaximumHeight(88)
        self._note_edit.setStyleSheet(
            f"""
            QTextEdit {{
                background: {_PAL["surface"]};
                color: {_PAL["text"]};
                border: 1px solid {_PAL["border"]};
                border-radius: 14px;
                padding: 12px 14px;
                selection-background-color: {_PAL["accent"]};
            }}
            """
        )
        self._note_edit.setFont(serif_font(15))
        col.addWidget(self._note_edit)
        return w

    def _build_step_strong(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        col = QVBoxLayout(w)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(8)
        col.addStretch()

        # Intensity as a word-valued slider, not a 0–10 spinbox.
        self._intensity = WaveSlider(value=0.5, reduced_motion=self._reduced_motion)
        self._intensity.valueChanged.connect(self._on_intensity)
        col.addWidget(self._intensity)

        self._intensity_echo = QLabel("")
        self._intensity_echo.setFont(serif_font(16))
        self._intensity_echo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._intensity_echo.setStyleSheet(f"color: {_PAL['text_muted']}; background: transparent;")
        col.addWidget(self._intensity_echo)
        col.addStretch()
        return w

    def _build_step_helped(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        col = QVBoxLayout(w)
        col.setContentsMargins(0, 0, 0, 0)
        host = _FlowHost(spacing=10)
        self._helped_host = host
        for label in _HELPED_OPTIONS:
            pill = Pill(label, reduced_motion=self._reduced_motion)
            host.add_pill(pill)
            self._helped_pills.append(pill)
        col.addWidget(host)
        return w

    def _build_step_done(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        col = QVBoxLayout(w)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(18)
        col.addStretch()
        self._done_line = QLabel("")
        self._done_line.setFont(serif_font(19))
        self._done_line.setWordWrap(True)
        self._done_line.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._done_line.setStyleSheet(f"color: {_PAL['text']}; background: transparent;")
        col.addWidget(self._done_line)
        col.addStretch()
        return w

    # -- mode transitions -------------------------------------------------
    def _enter_later(self) -> None:
        """Move from the breathing room into the gentle reflection."""
        self._pacer.stop()
        self._step = 0
        self._intensity_t = 0.5
        self._show_step()
        self._fade_to(1)

    def _return_to_now(self) -> None:
        if not self._reduced_motion:
            self._pacer.start()
        self._fade_to(0)

    def _fade_to(self, index: int) -> None:
        """A slow cross-dissolve between pages — never a hard cut."""
        if self._reduced_motion:
            self._stack.setCurrentIndex(index)
            return
        target = self._stack.widget(index)
        eff = QGraphicsOpacityEffect(target)
        target.setGraphicsEffect(eff)
        eff.setOpacity(0.0)
        self._stack.setCurrentIndex(index)
        anim = QPropertyAnimation(eff, b"opacity", self)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setDuration(480)
        anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        anim.finished.connect(lambda: target.setGraphicsEffect(None))
        anim.start()
        self._page_anim = anim  # keep a ref alive

    # -- the one-question flow --------------------------------------------
    _STEPS = [
        ("WHEN IT EASES", "What was happening, if anything?"),
        ("HOW IT FELT", "How big was the wave?"),
        ("WHAT HELPED", "Did anything help, even a little?"),
        ("", ""),  # the close has its own copy
    ]

    def _show_step(self) -> None:
        kicker, question = self._STEPS[self._step]
        self._kicker.setText(kicker)
        self._question.setText(question)
        self._step_body.setCurrentIndex(self._step)
        # Re-wrap the now-visible pill rows (FlowLayout collapses hidden pages).
        if self._step == 0:
            self._trigger_host.relayout()
        elif self._step == 2:
            self._helped_host.relayout()
        if self._step == 1:
            self._on_intensity(self._intensity.value())
        if self._step == 3:
            self._next_btn.setText("Done")
            self._back_btn.setText("Back")
        else:
            self._next_btn.setText("Set it down" if self._step == 2 else "Next")
            self._back_btn.setText("Back" if self._step > 0 else "Not now")

    def _step_back(self) -> None:
        if self._step == 0:
            # "Not now" — slip back to the breathing room without logging.
            self._return_to_now()
            return
        if self._step == 3:
            # From the close, "Back" just returns to a fresh room (already saved).
            self._reset_draft()
            self._return_to_now()
            return
        self._step -= 1
        self._show_step()

    def _step_next(self) -> None:
        if self._step < 2:
            self._step += 1
            self._show_step()
            return
        if self._step == 2:
            # Persist, then show the warm close.
            self._commit()
            self._step = 3
            self._show_step()
            return
        # step == 3 → done; return to a fresh breathing room.
        self._reset_draft()
        self._return_to_now()

    def _on_intensity(self, t: float) -> None:
        self._intensity_t = t
        word = _intensity_word(t)
        echoes = {
            "A ripple": "A ripple. You rode it.",
            "A swell": "A swell. You stayed with it.",
            "A strong wave": "A strong wave — and it passed.",
            "It took over": "It took over for a while. You're still here.",
            "The worst kind": "The worst kind. And you made it through.",
        }
        self._intensity_echo.setText(echoes.get(word, ""))

    # -- persistence of a "later" entry -----------------------------------
    def _commit(self) -> None:
        triggers = [p.text() for p in self._trigger_pills if p.isChecked()]
        helped = [p.text() for p in self._helped_pills if p.isChecked()]
        note = self._note_edit.toPlainText().strip()

        entry = {
            "timestamp": datetime.now().isoformat(),
            "peak_distress": _intensity_to_score(self._intensity_t),
            "symptoms": [],
            "trigger": ", ".join(triggers),
            "techniques": helped,
            "duration_minutes": 0,
            "notes": note,
        }
        self._entries.insert(0, entry)
        self._save_entries()
        self.panic_logged.emit(entry)

        # If the words name self-harm, the surface reaches back toward help —
        # the same route mood / diary / journal already use.
        if _names_self_harm(note):
            self.crisis_requested.emit()
            self._done_line.setText(
                "You named something heavy. You don't have to carry it alone — "
                "opening 988 and your crisis plan."
            )
        else:
            self._done_line.setText(self._close_line())

    def _close_line(self) -> str:
        """A warm, forgiving close — gives, never grades."""
        n = len(self._entries)
        if n <= 1:
            return "Set down. The first one's the hardest to name — thank you for it."
        return f"Set down. That's {n} you've come through now. The corner stays lit."

    def _reset_draft(self) -> None:
        for pill in self._trigger_pills + self._helped_pills:
            if pill.isChecked():
                pill.setChecked(False)
        self._note_edit.clear()
        self._intensity.setValue(0.5, animate=False)
        self._step = 0
