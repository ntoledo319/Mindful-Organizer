"""
Meditate — Hearth's still room (docs/design/audit_04 §3.4, VISION.md, DESIGN_SYSTEM.md).

A person reaches this surface wanting a contained, timed pause — calmer than
Breathe or Panic, but still seeking quiet. So the screen leads with the
*practice*, not a form. The old build opened with five clipped ``QGroupBox``
cards, a 54px digital clock, a duration ``QComboBox``, and two pre/post mood
sliders before you could sit. That is all gone.

What's here instead:

  * **One line of intention** — "Sit for [10 min] · [Mindfulness]" — where the
    two blanks are low-chrome painted pickers, not labelled dropdowns.
  * **A breathing-ring timer** (:class:`MeditationRing`): a custom-painted warm
    ring whose filled arc *is* the elapsed session, with a soft ember bloom and
    numerals that exhale on a slow loop, so a still screen stays gently alive.
    It speaks the same gradient language as the Breathe orb — the two rooms feel
    like siblings.
  * **One calm affordance** to begin or let go (a ghost :class:`HearthButton`).
  * **The library**, as warm :class:`HearthCard`s in the reading serif — a shelf
    of practices, not a ``QComboBox``.
  * **Recent sittings**, as a quiet stream of warm rows, not a ``QListWidget``
    data dump.

Completion is in-surface and warm — "Ten minutes. You stayed." — with one
optional, dismissible after-check-in (lighter · same · heavier). Never a
``QMessageBox``.

Persistence is **untouched**: the local ``meditation_sessions.json``
(``_load_sessions`` / ``_save_sessions``), the optional
``meditation_manager.log_session(...)`` hand-off, the ``session_completed``
signal, the session dict shape, and ``save_state()`` all keep working exactly
as the app expects.
"""

from __future__ import annotations

import contextlib
import json
import logging
import math
from datetime import date, datetime
from pathlib import Path
from typing import Any

from PyQt6.QtCore import (
    QEasingCurve,
    QPointF,
    QPropertyAnimation,
    QRectF,
    QSequentialAnimationGroup,
    Qt,
    QTimer,
    pyqtProperty,
    pyqtSignal,
)
from PyQt6.QtGui import (
    QColor,
    QFont,
    QPainter,
    QPainterPath,
    QPen,
    QRadialGradient,
)
from PyQt6.QtWidgets import (
    QAbstractButton,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from core.paths import get_data_dir
from gui.components.hearth_surfaces import ONYX, HearthButton, HearthCard
from gui.components.state_controls import sans_font, serif_font

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Local palette — Onyx (the warm dark default), a stand-in for ResolvedTokens.
# Mirrors the component palettes so nothing here hardcodes a stray hex.
# ---------------------------------------------------------------------------
_PAL = {
    "bg": ONYX["background"],
    "surface": ONYX["surface"],
    "raised": ONYX["surface_raised"],
    "text": ONYX["text"],
    "text_muted": ONYX["text_muted"],
    "accent": ONYX["accent"],
    "ember": ONYX["ember"],
    "border": ONYX["border"],
    "core": "#FFE9C2",  # warm white-hot, never clinical
    "ember_deep": "#8C4A28",  # the cooling edge of the bloom
}


# ---------------------------------------------------------------------------
# The practices. Plain, human names with a one-line companion description —
# what the sitting *feels* like, not a clinical technique sheet.
# ---------------------------------------------------------------------------
_PRACTICES: list[tuple[str, str]] = [
    ("Mindfulness", "Rest your attention on this moment, and let it be enough."),
    ("Body Scan", "Travel slowly through your body, listening for what's there."),
    ("Loving-Kindness", "Turn a little warmth toward yourself, then outward."),
    ("Breath Awareness", "Follow your breath. When you drift, come gently back."),
    ("Visualization", "Picture somewhere safe, and let yourself arrive there."),
    ("Letting Go", "Soften, on purpose. Release each held place, one by one."),
    ("Open Awareness", "Sit in the open, and let whatever comes simply pass."),
]

_DURATIONS = [5, 10, 15, 20, 30, 45]

# A quiet recommendation, in companion voice — surfaced only if you linger
# without starting. Never "Recommended Based on Mood".
_DEFAULT_NUDGE = "However you arrived, you're allowed to just sit."


def _two(n: int) -> str:
    return f"{n:02d}"


# ===========================================================================
# A small inline picker chip — replaces the QComboBox for duration / practice.
# ===========================================================================
class _Picker(QAbstractButton):
    """A low-chrome painted chip that cycles through quiet options on click.

    Reads as part of the sentence ("Sit for [10 min]"), not a form control —
    a faint warm underline, the value in the reading serif, and a soft warm
    bloom on hover. Cycling is forward on left-click; it never opens a menu.
    """

    changed = pyqtSignal(int)  # noqa: N815 (Qt-style signal name)

    def __init__(self, options: list[str], index: int = 0, parent=None):
        super().__init__(parent)
        self._options = options
        self._index = max(0, min(len(options) - 1, index))
        self._hover = 0.0
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFont(serif_font(20, QFont.Weight.Medium))
        self.setMinimumHeight(40)
        self._recompute_width()
        self.clicked.connect(self._advance)

    def _recompute_width(self) -> None:
        fm = self.fontMetrics()
        widest = max((fm.horizontalAdvance(o) for o in self._options), default=40)
        self.setMinimumWidth(widest + 30)

    def current_index(self) -> int:
        return self._index

    def current_text(self) -> str:
        return self._options[self._index]

    def set_index(self, i: int) -> None:
        self._index = max(0, min(len(self._options) - 1, i))
        self._recompute_width()
        self.updateGeometry()
        self.update()

    def set_enabled_quiet(self, on: bool) -> None:
        """Enable/disable without a jarring grey — just dim the chip."""
        self.setEnabled(on)
        self.update()

    def _advance(self) -> None:
        self._index = (self._index + 1) % len(self._options)
        self._recompute_width()
        self.updateGeometry()
        self.update()
        self.changed.emit(self._index)

    def enterEvent(self, event):  # noqa: N802
        self._hover = 1.0 if self.isEnabled() else 0.0
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):  # noqa: N802
        self._hover = 0.0
        self.update()
        super().leaveEvent(event)

    def sizeHint(self):  # noqa: N802
        from PyQt6.QtCore import QSize

        fm = self.fontMetrics()
        widest = max((fm.horizontalAdvance(o) for o in self._options), default=40)
        return QSize(widest + 30, 44)

    def paintEvent(self, _):  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(2, 2, -2, -4)
        radius = 11.0
        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)

        on = self.isEnabled()
        # A faint warm wash, brightening on hover — it reads as a soft pocket
        # the word sits in, not a button.
        wash = QColor(_PAL["accent"])
        wash.setAlpha(int((10 + 20 * self._hover) if on else 6))
        p.fillPath(path, wash)

        # A warm baseline underline — the visual cue that the word is editable.
        ul = QColor(_PAL["accent"])
        ul.setAlpha(150 if on else 60)
        pen = QPen(ul)
        pen.setWidthF(1.6)
        p.setPen(pen)
        y = rect.bottom() - 1
        p.drawLine(QPointF(rect.left() + 8, y), QPointF(rect.right() - 8, y))

        # The value, in the reading serif.
        col = QColor(_PAL["text"]) if on else QColor(_PAL["text_muted"])
        p.setPen(col)
        p.setFont(self.font())
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.current_text())
        p.end()


# ===========================================================================
# The breathing-ring timer — the still room's quiet heart.
# ===========================================================================
class MeditationRing(QWidget):
    """A warm circular timer whose filled arc is the elapsed sitting.

    Borrows the Breath orb's gradient language — a soft ember bloom inside the
    ring, a hot core riding high — so Meditate and Breathe read as siblings.
    The numerals *exhale*: a slow 2% scale-breathe keeps the still screen
    gently alive without asking anything of the person watching it.

    The ring is purely a display; the widget drives the clock. ``progress`` in
    [0, 1] is the fraction elapsed; ``glow`` rides a slow idle breath unless
    reduced motion holds it still.
    """

    def __init__(self, reduced_motion: bool = False, parent=None):
        super().__init__(parent)
        self._reduced_motion = reduced_motion
        self._progress = 0.0  # fraction of the sitting elapsed
        self._remaining_label = "10:00"
        self._caption = ""  # a quiet word under the time ("settling", "still")
        self._breath = 0.5 if reduced_motion else 0.0  # idle exhale 0..1
        self._running = False
        self.setMinimumSize(300, 300)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        # The idle breath — a slow ~6s sine the numerals and bloom ride, so the
        # ring is never a frozen disc. Honors reduced motion (held still).
        self._breath_group = QSequentialAnimationGroup(self)
        inh = QPropertyAnimation(self, b"breath")
        inh.setStartValue(0.0)
        inh.setEndValue(1.0)
        inh.setDuration(3000)
        inh.setEasingCurve(QEasingCurve.Type.InOutSine)
        exh = QPropertyAnimation(self, b"breath")
        exh.setStartValue(1.0)
        exh.setEndValue(0.0)
        exh.setDuration(3000)
        exh.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._breath_group.addAnimation(inh)
        self._breath_group.addAnimation(exh)
        self._breath_group.setLoopCount(-1)
        if not reduced_motion:
            self._breath_group.start()

    # -- idle breath property ---------------------------------------------
    def _get_breath(self) -> float:
        return self._breath

    def _set_breath(self, v: float) -> None:
        self._breath = v
        self.update()

    breath = pyqtProperty(float, fget=_get_breath, fset=_set_breath)

    # -- state setters -----------------------------------------------------
    def set_progress(self, value: float) -> None:
        self._progress = max(0.0, min(1.0, value))
        self.update()

    def set_time_text(self, text: str) -> None:
        self._remaining_label = text
        self.update()

    def set_caption(self, text: str) -> None:
        self._caption = text
        self.update()

    def set_running(self, running: bool) -> None:
        self._running = running
        self.update()

    def set_reduced_motion(self, on: bool) -> None:
        self._reduced_motion = on
        if on:
            self._breath_group.stop()
            self._breath = 0.5
            self.update()
        elif self._breath_group.state() != QSequentialAnimationGroup.State.Running:
            self._breath_group.start()

    # -- paint -------------------------------------------------------------
    def paintEvent(self, _):  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        side = min(w, h)
        cx, cy = w / 2.0, h / 2.0
        center = QPointF(cx, cy)
        ring_r = side * 0.40
        thickness = side * 0.022

        breath = self._breath
        # When running, the bloom answers progress; idle, it rides the breath so
        # a waiting ring still feels lit — a banked coal that breathes, never a
        # faint ghost ring.
        warmth = 0.40 + 0.5 * self._progress if self._running else 0.46 + 0.20 * breath

        accent = QColor(_PAL["accent"])
        ember = QColor(_PAL["ember"])
        deep = QColor(_PAL["ember_deep"])
        core = QColor(_PAL["core"])

        # 1) The cast bloom — a wide, soft amber wash inside the ring, so the
        #    timer reads as a source of warmth, not a drawn outline.
        bloom_r = ring_r * 1.5
        bloom = QRadialGradient(center, bloom_r)
        a = int(96 * warmth)
        bloom.setColorAt(0.0, QColor(accent.red(), accent.green(), accent.blue(), a))
        bloom.setColorAt(0.45, QColor(ember.red(), ember.green(), ember.blue(), int(a * 0.5)))
        bloom.setColorAt(1.0, QColor(deep.red(), deep.green(), deep.blue(), 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(bloom)
        p.drawEllipse(center, bloom_r, bloom_r)

        # 1b) A small warm heart gathered behind the numerals — the banked coal
        #     at the centre of the still room, so the resting ring is alive.
        heart_r = ring_r * 0.62
        heart = QRadialGradient(center, heart_r)
        hb = int(40 * warmth)
        heart.setColorAt(0.0, QColor(core.red(), core.green(), core.blue(), hb))
        heart.setColorAt(0.5, QColor(accent.red(), accent.green(), accent.blue(), int(hb * 0.55)))
        heart.setColorAt(1.0, QColor(accent.red(), accent.green(), accent.blue(), 0))
        p.setBrush(heart)
        p.drawEllipse(center, heart_r, heart_r)

        # 2) The unlit track — a quiet warm groove the whole way round.
        track = QPen(QColor(_PAL["border"]))
        track.setWidthF(thickness)
        track.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(track)
        ring_rect = QRectF(cx - ring_r, cy - ring_r, ring_r * 2, ring_r * 2)
        p.drawArc(ring_rect, 0, 360 * 16)

        # 3) The lit arc — the elapsed sitting, sweeping clockwise from the top,
        #    warming from ember toward hearthlight as it fills.
        if self._progress > 0.001:
            span = -int(360 * 16 * self._progress)  # clockwise (negative)
            lit = QPen(QColor(_PAL["accent"]))
            lit.setWidthF(thickness)
            lit.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(lit)
            p.drawArc(ring_rect, 90 * 16, span)
            # The leading coal — a soft knob of light at the sweep's head.
            ang = math.radians(90 - 360 * self._progress)
            kx = cx + ring_r * math.cos(ang)
            ky = cy - ring_r * math.sin(ang)
            knob = QRadialGradient(QPointF(kx, ky), thickness * 2.4)
            hot = QColor(_PAL["core"])
            knob.setColorAt(0.0, QColor(hot.red(), hot.green(), hot.blue(), 220))
            knob.setColorAt(1.0, QColor(accent.red(), accent.green(), accent.blue(), 0))
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(knob)
            p.drawEllipse(QPointF(kx, ky), thickness * 2.0, thickness * 2.0)

        # 4) The time, in the control sans (numbers are a control, never the
        #    reading voice). The numerals exhale — a slow 2% scale-breathe.
        scale = 1.0 + (0.0 if self._reduced_motion else 0.02 * breath)
        p.save()
        p.translate(cx, cy)
        p.scale(scale, scale)
        p.translate(-cx, -cy)
        p.setPen(QColor(_PAL["text"]))
        p.setFont(sans_font(int(side * 0.16), QFont.Weight.Light))
        time_rect = QRectF(cx - ring_r, cy - ring_r * 0.55, ring_r * 2, ring_r * 1.1)
        p.drawText(time_rect, Qt.AlignmentFlag.AlignCenter, self._remaining_label)
        p.restore()

        # 5) A quiet caption beneath the numerals — the state in a single word.
        if self._caption:
            p.setPen(QColor(_PAL["text_muted"]))
            p.setFont(sans_font(11, QFont.Weight.DemiBold))
            cap_rect = QRectF(cx - ring_r, cy + ring_r * 0.34, ring_r * 2, ring_r * 0.28)
            # spaced caps read as a quiet label, not a word shouted
            spaced = " ".join(self._caption.upper())
            p.drawText(cap_rect, Qt.AlignmentFlag.AlignCenter, spaced)
        p.end()


# ===========================================================================
# A one-tap, dismissible after-check-in — lighter / same / heavier.
# ===========================================================================
class _AfterTap(QAbstractButton):
    """A soft pill for the optional post-sitting check-in. One tap, never gated."""

    def __init__(self, text: str, reduced_motion: bool = False, parent=None):
        super().__init__(parent)
        self.setText(text)
        self.setCheckable(True)
        self._reduced_motion = reduced_motion
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFont(sans_font(13, QFont.Weight.Medium))
        fm = self.fontMetrics()
        self.setMinimumSize(fm.horizontalAdvance(text) + 40, 40)
        self.setMaximumHeight(40)

    def sizeHint(self):  # noqa: N802
        from PyQt6.QtCore import QSize

        fm = self.fontMetrics()
        return QSize(fm.horizontalAdvance(self.text()) + 40, 40)

    def paintEvent(self, _):  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(1, 1, self.width() - 2, self.height() - 2)
        radius = rect.height() / 2
        f = 1.0 if self.isChecked() else 0.0

        base = QColor(_PAL["surface"])
        if f:
            warm = QColor(_PAL["accent"])
            base = QColor(
                int(base.red() + (warm.red() - base.red()) * 0.9),
                int(base.green() + (warm.green() - base.green()) * 0.9),
                int(base.blue() + (warm.blue() - base.blue()) * 0.9),
            )
        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)
        p.fillPath(path, base)

        border = QColor(_PAL["accent"]) if f else QColor(_PAL["border"])
        pen = QPen(border)
        pen.setWidthF(1.3)
        p.setPen(pen)
        p.drawPath(path)

        txt = QColor(_PAL["bg"]) if f else QColor(_PAL["text_muted"])
        p.setPen(txt)
        p.setFont(self.font())
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())
        p.end()


# ===========================================================================
# A warm fading acknowledgement — never a QMessageBox.
# ===========================================================================
class _EmberLine(QLabel):
    """An inline, fading line in the reading serif. Glows up, holds, recedes."""

    def __init__(self, reduced_motion: bool = False, parent=None):
        super().__init__(parent)
        self._reduced_motion = reduced_motion
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setWordWrap(True)
        self.setFont(serif_font(18))
        self._opacity = 0.0
        self.setVisible(False)
        self._fade = QPropertyAnimation(self, b"glow", self)
        self._fade.setEasingCurve(QEasingCurve.Type.InOutSine)

    def _get_glow(self) -> float:
        return self._opacity

    def _set_glow(self, v: float) -> None:
        self._opacity = v
        c = QColor(_PAL["accent"])
        self.setStyleSheet(
            f"color: rgba({c.red()}, {c.green()}, {c.blue()}, {max(0.0, min(1.0, v)):.3f}); "
            f"background: transparent;"
        )
        if v <= 0.01:
            self.setVisible(False)

    glow = pyqtProperty(float, fget=_get_glow, fset=_set_glow)

    def say(self, text: str, *, linger: bool = False) -> None:
        self.setText(text)
        self.setVisible(True)
        if self._reduced_motion or linger:
            self._set_glow(1.0)
            return
        self._fade.stop()
        self._fade.setDuration(3200)
        self._fade.setKeyValueAt(0.0, 0.0)
        self._fade.setKeyValueAt(0.12, 1.0)
        self._fade.setKeyValueAt(0.72, 1.0)
        self._fade.setKeyValueAt(1.0, 0.0)
        self._fade.start()

    def hold(self, text: str) -> None:
        """Show and keep showing (for the completion line)."""
        self.setText(text)
        self.setVisible(True)
        self._set_glow(1.0)

    def clear_line(self) -> None:
        self._set_glow(0.0)


# ===========================================================================
# Widget
# ===========================================================================
class MeditationWidget(QWidget):
    """The still room: an intention, a breathing-ring, a shelf of practices."""

    session_completed = pyqtSignal(dict)

    def __init__(self, main_window: Any, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.main_window = main_window

        self._meditation_manager = None
        with contextlib.suppress(Exception):
            self._meditation_manager = main_window.meditation_manager

        self._reduced_motion = self._detect_reduced_motion()

        # Session state (preserved semantics from the original widget).
        self._running = False
        self._remaining_sec = 0
        self._total_sec = 0
        self._after_choice: str | None = None

        # The chosen practice index (drives both the picker and the library).
        self._practice_index = 0

        # Tick timer.
        self._tick_timer = QTimer(self)
        self._tick_timer.setInterval(1000)
        self._tick_timer.timeout.connect(self._tick)

        # A gentle nudge that surfaces only if the person lingers without
        # starting — companion voice, never a recommendation engine.
        self._nudge_timer = QTimer(self)
        self._nudge_timer.setSingleShot(True)
        self._nudge_timer.setInterval(9000)
        self._nudge_timer.timeout.connect(self._offer_nudge)

        # Session history (local JSON — unchanged persistence).
        self._sessions: list[dict[str, Any]] = []
        self._load_sessions()

        self._bg = QColor(_PAL["bg"])
        self._build_ui()
        self._refresh_history()
        self._reset_clock_display()

    # ------------------------------------------------------------------
    # Persistence (UNCHANGED — same files, same shape, same hand-off)
    # ------------------------------------------------------------------
    def _data_dir(self) -> Path:
        try:
            return Path(self.main_window.data_dir)
        except (AttributeError, TypeError):
            p = get_data_dir()
            p.mkdir(parents=True, exist_ok=True)
            return p

    def _sessions_file(self) -> Path:
        d = self._data_dir()
        d.mkdir(parents=True, exist_ok=True)
        return d / "meditation_sessions.json"

    def _load_sessions(self) -> None:
        path = self._sessions_file()
        if path.exists():
            try:
                with open(path) as fh:
                    self._sessions = json.load(fh)
            except (json.JSONDecodeError, OSError) as exc:
                logger.debug(f"Meditation sessions load error: {exc}")

    def _save_sessions(self) -> None:
        try:
            with open(self._sessions_file(), "w") as fh:
                json.dump(self._sessions, fh, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save meditation sessions: {e}")

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------
    def _detect_reduced_motion(self) -> bool:
        try:
            from utils.accessibility import detect_reduced_motion

            return detect_reduced_motion()
        except Exception:  # accessibility probing must never block the room
            return False

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
        root.setSpacing(22)
        root.setContentsMargins(40, 34, 40, 36)
        scroll.setWidget(container)

        root.addWidget(self._build_practice_card())
        root.addWidget(self._build_library_card())
        root.addWidget(self._build_history_card())
        root.addStretch()

    # -- the practice (the heart of the room) ---------------------------
    def _build_practice_card(self) -> QWidget:
        card = HearthCard(elevation=2, radius=26)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(36, 32, 36, 32)
        layout.setSpacing(18)

        # The intention line — "Sit for [10 min] · [Mindfulness]" — built from
        # plain serif words with two inline pickers. No labels above combos.
        intent = QHBoxLayout()
        intent.setSpacing(8)
        intent.addStretch()

        lead = QLabel("Sit for")
        lead.setFont(serif_font(20))
        lead.setStyleSheet(f"color: {_PAL['text']}; background: transparent;")
        intent.addWidget(lead, 0, Qt.AlignmentFlag.AlignVCenter)

        self._dur_picker = _Picker([f"{m} min" for m in _DURATIONS], index=1)
        self._dur_picker.changed.connect(self._on_duration_changed)
        intent.addWidget(self._dur_picker, 0, Qt.AlignmentFlag.AlignVCenter)

        dot = QLabel("·")
        dot.setFont(serif_font(20))
        dot.setStyleSheet(f"color: {_PAL['text_muted']}; background: transparent;")
        intent.addWidget(dot, 0, Qt.AlignmentFlag.AlignVCenter)

        self._practice_picker = _Picker([name for name, _ in _PRACTICES], index=0)
        self._practice_picker.changed.connect(self._on_practice_changed)
        intent.addWidget(self._practice_picker, 0, Qt.AlignmentFlag.AlignVCenter)

        intent.addStretch()
        layout.addLayout(intent)

        # The breathing-ring timer — large, generous, the focus.
        ring_row = QHBoxLayout()
        ring_row.addStretch()
        self._ring = MeditationRing(reduced_motion=self._reduced_motion)
        self._ring.setFixedSize(320, 320)
        ring_row.addWidget(self._ring)
        ring_row.addStretch()
        layout.addLayout(ring_row)

        # A quiet nudge / description line beneath the ring — the practice's
        # own words at rest; a gentle companion line if you linger.
        self._nudge = QLabel(_PRACTICES[0][1])
        self._nudge.setFont(serif_font(16))
        self._nudge.setWordWrap(True)
        self._nudge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._nudge.setStyleSheet(f"color: {_PAL['text_muted']}; background: transparent;")
        layout.addWidget(self._nudge)

        # The one calm affordance — begin, or let go. A ghost side-door.
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self._toggle = HearthButton("Begin", role="ghost", reduced_motion=self._reduced_motion)
        self._toggle.setMinimumWidth(220)
        self._toggle.clicked.connect(self._on_toggle)
        btn_row.addWidget(self._toggle)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        # The completion line + the optional after-check-in (hidden until a
        # sitting ends). Warm, in-surface, never a popup.
        self._ember = _EmberLine(reduced_motion=self._reduced_motion)
        layout.addWidget(self._ember)

        self._after_row = self._build_after_row()
        self._after_row.setVisible(False)
        layout.addWidget(self._after_row)

        return card

    def _build_after_row(self) -> QWidget:
        host = QWidget()
        host.setStyleSheet("background: transparent;")
        row = QVBoxLayout(host)
        row.setContentsMargins(0, 4, 0, 0)
        row.setSpacing(10)

        prompt = QLabel("How do you feel, leaving it?")
        prompt.setFont(serif_font(15))
        prompt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        prompt.setStyleSheet(f"color: {_PAL['text_muted']}; background: transparent;")
        row.addWidget(prompt)

        taps = QHBoxLayout()
        taps.setSpacing(10)
        taps.addStretch()
        self._after_taps: list[_AfterTap] = []
        for label in ("Lighter", "About the same", "Heavier"):
            tap = _AfterTap(label, reduced_motion=self._reduced_motion)
            tap.clicked.connect(lambda _=False, t=tap: self._on_after_tap(t))
            self._after_taps.append(tap)
            taps.addWidget(tap)
        taps.addStretch()
        row.addLayout(taps)
        return host

    # -- the library (a warm shelf of practices) ------------------------
    def _build_library_card(self) -> QWidget:
        card = HearthCard(elevation=0, radius=22)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(30, 26, 30, 26)
        layout.setSpacing(14)

        title = QLabel("Ways to sit")
        title.setFont(serif_font(19, QFont.Weight.Medium))
        title.setStyleSheet(f"color: {_PAL['text']}; background: transparent;")
        layout.addWidget(title)

        self._practice_rows: list[_PracticeRow] = []
        for i, (name, desc) in enumerate(_PRACTICES):
            row = _PracticeRow(name, desc, selected=(i == 0))
            row.chosen.connect(lambda _=False, idx=i: self._choose_practice(idx))
            self._practice_rows.append(row)
            layout.addWidget(row)
        return card

    # -- recent sittings (a quiet stream, not a QListWidget) ------------
    def _build_history_card(self) -> QWidget:
        card = HearthCard(elevation=0, radius=20)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(30, 24, 30, 26)
        layout.setSpacing(10)

        title = QLabel("Lately")
        title.setFont(serif_font(18, QFont.Weight.Medium))
        title.setStyleSheet(f"color: {_PAL['text']}; background: transparent;")
        layout.addWidget(title)

        self._history_empty = QLabel("No sittings yet. When you stay with one, it'll rest here.")
        self._history_empty.setFont(serif_font(15))
        self._history_empty.setWordWrap(True)
        self._history_empty.setStyleSheet(f"color: {_PAL['text_muted']}; background: transparent;")
        layout.addWidget(self._history_empty)

        self._history_host = QWidget()
        self._history_host.setStyleSheet("background: transparent;")
        self._history_layout = QVBoxLayout(self._history_host)
        self._history_layout.setContentsMargins(0, 0, 0, 0)
        self._history_layout.setSpacing(8)
        layout.addWidget(self._history_host)
        return card

    # ------------------------------------------------------------------
    # Painting — the warm room behind the cards
    # ------------------------------------------------------------------
    def paintEvent(self, _event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        rect = QRectF(self.rect())
        p.fillRect(rect, self._bg)
        # A faint warmth gathering from the top — a hearth glowing somewhere
        # above the room, so the dark never reads as flat black.
        glow = QRadialGradient(rect.center().x(), rect.top(), rect.width() * 0.9)
        warm = QColor(_PAL["accent"])
        warm.setAlpha(20)
        glow.setColorAt(0.0, warm)
        warm2 = QColor(warm)
        warm2.setAlpha(0)
        glow.setColorAt(1.0, warm2)
        p.fillRect(rect, glow)
        p.end()

    # ------------------------------------------------------------------
    # Practice / duration selection
    # ------------------------------------------------------------------
    def _on_duration_changed(self, _index: int) -> None:
        if not self._running:
            self._reset_clock_display()

    def _on_practice_changed(self, index: int) -> None:
        self._set_practice(index, from_picker=True)

    def _choose_practice(self, index: int) -> None:
        self._set_practice(index, from_picker=False)

    def _set_practice(self, index: int, *, from_picker: bool) -> None:
        self._practice_index = max(0, min(len(_PRACTICES) - 1, index))
        # Keep the inline picker and the library shelf in agreement.
        if not from_picker:
            self._practice_picker.set_index(self._practice_index)
        for i, row in enumerate(self._practice_rows):
            row.set_selected(i == self._practice_index)
        # The description line under the ring follows the chosen practice,
        # unless a sitting is running (then the ring's caption is the focus).
        if not self._running:
            self._nudge.setText(_PRACTICES[self._practice_index][1])

    def _current_duration_min(self) -> int:
        return _DURATIONS[self._dur_picker.current_index()]

    def _current_practice_name(self) -> str:
        return _PRACTICES[self._practice_index][0]

    # ------------------------------------------------------------------
    # The lingering nudge
    # ------------------------------------------------------------------
    def _offer_nudge(self) -> None:
        if self._running:
            return
        self._nudge.setText(_DEFAULT_NUDGE)

    # ------------------------------------------------------------------
    # Session control (preserved semantics + persistence)
    # ------------------------------------------------------------------
    def _on_toggle(self) -> None:
        if self._running:
            self._stop_session(completed=False)
        else:
            self._start_session()

    def _start_session(self) -> None:
        if self._running:
            return
        self._nudge_timer.stop()
        self._after_row.setVisible(False)
        self._ember.clear_line()
        for tap in getattr(self, "_after_taps", []):
            tap.setChecked(False)
        self._after_choice = None

        self._total_sec = self._current_duration_min() * 60
        self._remaining_sec = self._total_sec
        self._running = True

        self._dur_picker.set_enabled_quiet(False)
        self._practice_picker.set_enabled_quiet(False)
        for row in self._practice_rows:
            row.set_locked(True)

        self._toggle.setText("Let it go")
        self._ring.set_running(True)
        self._ring.set_caption("settling")
        self._update_clock()
        self._tick_timer.start()

    def _stop_session(self, *, completed: bool) -> None:
        was_running = self._running
        self._tick_timer.stop()
        elapsed_sec = self._total_sec - self._remaining_sec

        self._running = False
        self._dur_picker.set_enabled_quiet(True)
        self._practice_picker.set_enabled_quiet(True)
        for row in self._practice_rows:
            row.set_locked(False)
        self._toggle.setText("Begin")
        self._ring.set_running(False)
        self._ring.set_caption("")

        if not was_running:
            self._reset_clock_display()
            return

        # Record the session — same dict shape, same files, same hand-off.
        session = {
            "type": self._current_practice_name(),
            "duration_sec": elapsed_sec,
            "planned_duration_sec": self._total_sec,
            "mood_before": None,
            "mood_after": None,
            "completed": completed or self._remaining_sec <= 0,
            "timestamp": datetime.now().isoformat(),
            "date": date.today().isoformat(),
        }
        self._sessions.append(session)
        self._save_sessions()
        self.session_completed.emit(session)

        try:
            if self._meditation_manager and hasattr(self._meditation_manager, "log_session"):
                self._meditation_manager.log_session(session)
        except (AttributeError, TypeError) as exc:
            logger.debug(f"Meditation manager log error: {exc}")

        self._last_session = session
        self._refresh_history()
        self._reset_clock_display()

        # Warm, in-surface completion — never a QMessageBox.
        minutes = max(1, round(elapsed_sec / 60))
        if session["completed"]:
            word = "minute" if minutes == 1 else "minutes"
            self._ember.hold(f"{minutes} {word}. You stayed.")
        else:
            self._ember.hold("You sat for a while. That counts.")
        self._after_row.setVisible(True)

    def _tick(self) -> None:
        if not self._running:
            return
        self._remaining_sec -= 1
        # A soft caption arc: settling at the start, still in the middle.
        if self._total_sec:
            frac = 1.0 - (self._remaining_sec / self._total_sec)
            self._ring.set_caption("settling" if frac < 0.18 else "still")
        self._update_clock()
        if self._remaining_sec <= 0:
            self._stop_session(completed=True)

    def _update_clock(self) -> None:
        mins = max(0, self._remaining_sec) // 60
        secs = max(0, self._remaining_sec) % 60
        self._ring.set_time_text(f"{_two(mins)}:{_two(secs)}")
        if self._total_sec:
            self._ring.set_progress(1.0 - (self._remaining_sec / self._total_sec))

    def _reset_clock_display(self) -> None:
        mins = self._current_duration_min()
        self._remaining_sec = mins * 60
        self._ring.set_progress(0.0)
        self._ring.set_time_text(f"{_two(mins)}:00")

    # ------------------------------------------------------------------
    # The optional after-check-in
    # ------------------------------------------------------------------
    def _on_after_tap(self, tapped: _AfterTap) -> None:
        for tap in self._after_taps:
            tap.setChecked(tap is tapped)
        self._after_choice = tapped.text()
        # Record it onto the just-finished session, without a second dialog.
        last = getattr(self, "_last_session", None)
        if last is not None:
            last["after_feeling"] = self._after_choice
            self._save_sessions()
        replies = {
            "Lighter": "Glad it eased something. Come back when you need to.",
            "About the same": "Even so, you gave yourself the time. That's enough.",
            "Heavier": "Some sittings stir things up. I'm here, however it landed.",
        }
        self._ember.say(replies.get(self._after_choice, ""), linger=False)

    # ------------------------------------------------------------------
    # History (a warm stream of rows, not a QListWidget dump)
    # ------------------------------------------------------------------
    def _refresh_history(self) -> None:
        # Clear existing rows.
        while self._history_layout.count():
            item = self._history_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        recent = list(reversed(self._sessions[-8:]))
        self._history_empty.setVisible(not recent)
        self._history_host.setVisible(bool(recent))
        for s in recent:
            self._history_layout.addWidget(_SittingRow(s))

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        # Offer the lingering nudge only if nothing is running.
        if not self._running:
            self._nudge_timer.start()

    def hideEvent(self, event) -> None:  # noqa: N802
        super().hideEvent(event)
        self._nudge_timer.stop()
        if self._running:
            self._stop_session(completed=False)

    # ------------------------------------------------------------------
    # Public API (UNCHANGED contract)
    # ------------------------------------------------------------------
    def save_state(self) -> None:
        """Called by main window on close."""
        if self._running:
            self._stop_session(completed=False)
        self._save_sessions()


# ===========================================================================
# A library row — a warm, selectable practice on the shelf.
# ===========================================================================
class _PracticeRow(QAbstractButton):
    """One practice on the shelf: its name in serif, a line of what it feels like.

    Selected: a warm left-edge ember bar and a faint warm fill. Unselected: a
    quiet row. Locked (a sitting is running): dimmed, not clickable.
    """

    chosen = pyqtSignal()

    def __init__(self, name: str, desc: str, selected: bool = False, parent=None):
        super().__init__(parent)
        self._name = name
        self._desc = desc
        self._selected = selected
        self._locked = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(64)
        self.clicked.connect(self._on_click)

    def _on_click(self) -> None:
        if not self._locked:
            self.chosen.emit()

    def set_selected(self, on: bool) -> None:
        self._selected = on
        self.update()

    def set_locked(self, on: bool) -> None:
        self._locked = on
        self.setCursor(Qt.CursorShape.ArrowCursor if on else Qt.CursorShape.PointingHandCursor)
        self.update()

    def sizeHint(self):  # noqa: N802
        from PyQt6.QtCore import QSize

        return QSize(360, 66)

    def paintEvent(self, _):  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(0, 3, 0, -3)
        radius = 14.0
        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)

        dim = 0.5 if self._locked else 1.0

        if self._selected:
            fill = QColor(_PAL["raised"])
            p.fillPath(path, fill)
            # The warm left-edge ember bar — this row is the chosen one.
            bar = QColor(_PAL["accent"])
            bar.setAlphaF(0.92 * dim)
            bar_rect = QRectF(rect.left() + 4, rect.top() + 12, 3.5, rect.height() - 24)
            bp = QPainterPath()
            bp.addRoundedRect(bar_rect, 1.75, 1.75)
            p.fillPath(bp, bar)

        # Name — reading serif.
        name_col = QColor(_PAL["text"])
        name_col.setAlphaF(dim)
        p.setPen(name_col)
        p.setFont(serif_font(18, QFont.Weight.Medium))
        name_rect = QRectF(rect.left() + 22, rect.top() + 9, rect.width() - 40, 26)
        p.drawText(
            name_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self._name
        )

        # Description — a quiet line of what it feels like.
        desc_col = QColor(_PAL["text_muted"])
        desc_col.setAlphaF(dim)
        p.setPen(desc_col)
        p.setFont(serif_font(13))
        desc_rect = QRectF(rect.left() + 22, rect.top() + 33, rect.width() - 40, 22)
        p.drawText(
            desc_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self._desc
        )
        p.end()


# ===========================================================================
# A recent-sitting row — one warm line in the "Lately" stream.
# ===========================================================================
class _SittingRow(QWidget):
    """A single recent sitting: a warm dot, the practice, the time, how long."""

    def __init__(self, session: dict[str, Any], parent=None):
        super().__init__(parent)
        self._session = session
        self.setMinimumHeight(44)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

    def _when(self) -> str:
        ts = self._session.get("timestamp") or self._session.get("date") or ""
        try:
            dt = datetime.fromisoformat(str(ts))
            today = date.today()
            if dt.date() == today:
                return dt.strftime("Today, %-I:%M %p").lower().replace("today,", "Today,")
            return dt.strftime("%b %-d")
        except (ValueError, TypeError):
            return str(ts)[:10]

    def paintEvent(self, _):  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect())

        completed = bool(self._session.get("completed"))
        dur_min = max(0, int(self._session.get("duration_sec", 0)) // 60)
        practice = str(self._session.get("type", "Sitting"))

        # A warm dot — filled when the sitting was seen through, a soft hollow
        # ring when it was let go early. A skip is never a red mark.
        cy = rect.center().y()
        dot_c = QPointF(rect.left() + 8, cy)
        accent = QColor(_PAL["accent"])
        if completed:
            bloom = QRadialGradient(dot_c, 9)
            b0 = QColor(accent)
            b0.setAlpha(110)
            bloom.setColorAt(0.0, b0)
            bloom.setColorAt(1.0, QColor(accent.red(), accent.green(), accent.blue(), 0))
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(bloom)
            p.drawEllipse(dot_c, 8, 8)
            p.setBrush(accent)
            p.drawEllipse(dot_c, 4, 4)
        else:
            ring = QColor(_PAL["ember"])
            pen = QPen(ring)
            pen.setWidthF(1.5)
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(dot_c, 4, 4)

        # The line: practice (serif) · how long & when (sans, muted).
        p.setPen(QColor(_PAL["text"]))
        p.setFont(serif_font(15))
        name_rect = QRectF(rect.left() + 24, rect.top(), rect.width() * 0.5, rect.height())
        p.drawText(name_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, practice)

        p.setPen(QColor(_PAL["text_muted"]))
        p.setFont(sans_font(12))
        meta = f"{dur_min} min · {self._when()}"
        meta_rect = QRectF(
            rect.left() + rect.width() * 0.5, rect.top(), rect.width() * 0.5 - 6, rect.height()
        )
        p.drawText(meta_rect, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, meta)
        p.end()
