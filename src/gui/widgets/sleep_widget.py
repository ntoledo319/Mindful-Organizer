"""
Rest — Hearth's gentle read on how the night went.

A person opens this in the morning, often after a rough night: flat, foggy,
maybe ashamed of how little they slept. The old screen met them with clipped
``QGroupBox`` headers, hardcoded Windows fonts, native ``QTimeEdit`` steppers,
and a "Statistics" wall of em-dashes (docs/design/audit_03 §2.6, §2.9). This is
the rebuild: warm HearthCards, one serif question — "How did you sleep?" — a
calm pair of painted hour-dials for bedtime and wake, a word-valued quality
slider, and a forgiving summary that never scolds a short night.

Persistence is unchanged. The same ``sleep_entries.json`` shape is written
(``_load_entries`` / ``_save_entries``), the same ``sleep_tracker.log_sleep(...)``
backend call fires, and the same ``entry_saved`` signal carries the same payload.
Quality is now a richer 1–10 score (the backend always stored 1–10) instead of
the lossy 1/2/3, but the stored keys are identical.

Built from the signature controls in ``gui.components``:
  * :class:`StateSlider` — "How did it feel?" The value reads as a word.
  * a small painted :class:`_TimeDial` — bedtime / wake, dragged, not stepped.
  * :class:`HearthCard` / :class:`HearthButton` — the warm surface language.
"""

from __future__ import annotations

import contextlib
import json
import logging
import math
import statistics as stats_mod
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from PyQt6.QtCore import (
    QEasingCurve,
    QPointF,
    QPropertyAnimation,
    QRectF,
    Qt,
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
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from core.paths import get_data_dir
from gui.components.hearth_surfaces import ONYX, HearthButton, HearthCard
from gui.components.state_controls import (
    StateSlider,
    sans_font,
    serif_font,
    warmth_color,
    word_for,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Condition-aware notes for rough nights — "For the kind of nights you have"
# (audit_03 §3.5). Plainspoken, second person, never a clinical checklist.
# ---------------------------------------------------------------------------

_NIGHT_NOTES: dict[str, list[str]] = {
    "General": [
        "A dark, cool room helps the body believe it's night.",
        "Screens off a little before bed makes the morning kinder.",
    ],
    "ADHD": [
        "A busy mind quiets faster with a sound to lean on — rain, a fan, low static.",
        "Keep a notepad by the bed, so a racing thought has somewhere to land.",
    ],
    "Anxiety": [
        "A long, slow exhale tells the body it's safe to let go.",
        "If worries crowd in, set them on paper — they'll keep till morning.",
    ],
    "Depression": [
        "A little daylight soon after waking helps steady the days.",
        "Oversleeping can press the mood lower — be gentle, not strict, about it.",
    ],
    "OCD": [
        "One small, same-every-night ritual can close the day softly.",
        "If checking pulls at you, let the thought pass without answering it.",
    ],
    "PTSD": [
        "Make the room feel safe — a low light is allowed if the dark is hard.",
        "If you wake from a nightmare, name five things you can see to come back.",
    ],
    "Bipolar Disorder": [
        "A steady sleep window is one of the kindest things for an even keel.",
        "Nights that shrink fast can be an early signal — worth noticing, not fearing.",
    ],
}


# ---------------------------------------------------------------------------
# _TimeDial — a small painted clock you drag to set an hour.
# Replaces the native QTimeEdit steppers (audit_03 §2.6): a warm ring with one
# coal of a hand, the time read in the reading serif. Snaps to 5-minute marks.
# ---------------------------------------------------------------------------
class _TimeDial(QWidget):
    """A draggable 12-hour face. Emits ``timeChanged(hour, minute)`` (24h)."""

    timeChanged = pyqtSignal(int, int)  # noqa: N815

    def __init__(
        self,
        hour: int = 22,
        minute: int = 30,
        caption: str = "",
        reduced_motion: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._caption = caption
        self._reduced_motion = reduced_motion
        self._dragging = False
        # Fraction of the full day [0, 1) → drives the hand angle & warmth.
        self._frac = (hour % 24 + minute / 60.0) / 24.0
        self._display = self._frac  # eased toward _frac
        self.setMinimumSize(168, 196)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._anim = QPropertyAnimation(self, b"display", self)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.setDuration(0 if reduced_motion else 420)

    # -- eased display ----------------------------------------------------
    def _get_display(self) -> float:
        return self._display

    def _set_display(self, v: float) -> None:
        self._display = v
        self.update()

    display = pyqtProperty(float, fget=_get_display, fset=_set_display)

    # -- value ------------------------------------------------------------
    def hour(self) -> int:
        return int(self._frac * 24.0) % 24

    def minute(self) -> int:
        total = self._frac * 24.0 * 60.0
        return int(round(total)) % 60

    def time_string(self) -> str:
        return f"{self.hour():02d}:{self.minute():02d}"

    def set_time(self, hour: int, minute: int, *, animate: bool = True) -> None:
        frac = ((hour % 24) + (minute % 60) / 60.0) / 24.0
        self._frac = frac % 1.0
        if animate and not self._reduced_motion and self.isVisible():
            self._anim.stop()
            self._anim.setStartValue(self._display)
            self._anim.setEndValue(self._frac)
            self._anim.start()
        else:
            self._display = self._frac
            self.update()
        self.timeChanged.emit(self.hour(), self.minute())

    # -- geometry ---------------------------------------------------------
    # A caption band rides above the face, the time band below it.
    _CAP_BAND = 24.0
    _TIME_BAND = 30.0

    def _face_rect(self) -> QRectF:
        avail_h = self.height() - self._CAP_BAND - self._TIME_BAND
        side = min(self.width(), avail_h)
        cx = self.width() / 2
        cy = self._CAP_BAND + avail_h / 2
        r = side * 0.46
        return QRectF(cx - r, cy - r, 2 * r, 2 * r)

    def _frac_from_pos(self, pos: QPointF) -> float:
        rect = self._face_rect()
        dx = pos.x() - rect.center().x()
        dy = pos.y() - rect.center().y()
        # 12 o'clock is up; clockwise. Convert to a clock fraction [0, 1).
        ang = math.degrees(math.atan2(dx, -dy)) % 360.0
        clock_frac = ang / 360.0
        # Keep the same half-day (AM/PM) the hand is currently in, so a small
        # drag near midnight doesn't jump twelve hours.
        half = 0 if (self._frac % 1.0) < 0.5 else 1
        frac = (clock_frac + half) / 2.0
        # Snap to 5-minute resolution.
        steps = round(frac * 288.0)
        return (steps / 288.0) % 1.0

    # -- interaction ------------------------------------------------------
    def mousePressEvent(self, e):  # noqa: N802
        self._dragging = True
        self.setCursor(Qt.CursorShape.ClosedHandCursor)
        self._apply_frac(self._frac_from_pos(e.position()), animate=False)

    def mouseMoveEvent(self, e):  # noqa: N802
        if self._dragging:
            self._apply_frac(self._frac_from_pos(e.position()), animate=False)

    def mouseReleaseEvent(self, e):  # noqa: N802
        self._dragging = False
        self.setCursor(Qt.CursorShape.OpenHandCursor)

    def keyPressEvent(self, e):  # noqa: N802
        step = 5.0 / (24.0 * 60.0)  # five minutes
        if e.key() in (Qt.Key.Key_Right, Qt.Key.Key_Up):
            self._apply_frac((self._frac + step) % 1.0)
        elif e.key() in (Qt.Key.Key_Left, Qt.Key.Key_Down):
            self._apply_frac((self._frac - step) % 1.0)
        else:
            super().keyPressEvent(e)

    def _apply_frac(self, frac: float, *, animate: bool = True) -> None:
        if abs(frac - self._frac) < 1e-5:
            return
        self._frac = frac % 1.0
        if animate and not self._reduced_motion and self.isVisible():
            self._anim.stop()
            self._anim.setStartValue(self._display)
            self._anim.setEndValue(self._frac)
            self._anim.start()
        else:
            self._display = self._frac
            self.update()
        self.timeChanged.emit(self.hour(), self.minute())

    # -- night/day warmth: deepest at ~3am, brightest at midday ----------
    @staticmethod
    def _daylight(frac: float) -> float:
        """0 at deep night (~3am), 1 at midday — a soft cosine of the clock."""
        # frac=0 → midnight. Shift so the trough sits near 3am.
        return 0.5 - 0.5 * math.cos((frac - 0.125) * 2.0 * math.pi)

    # -- paint ------------------------------------------------------------
    def paintEvent(self, _):  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self._face_rect()
        center = rect.center()
        # Warmth: a deep night is cool/banked; toward day it warms.
        day = self._daylight(self._display)
        glow = warmth_color(0.18 + 0.62 * day)

        # 1) The face — a quiet warm well, deeper at night.
        well = QRadialGradient(center, rect.width() * 0.62)
        floor = QColor(ONYX["surface"])
        warm = QColor(glow)
        warm.setAlpha(int(30 + 46 * day))
        well.setColorAt(0.0, warm)
        well.setColorAt(1.0, floor)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(well)
        p.drawEllipse(center, rect.width() / 2, rect.width() / 2)

        # 2) The rim — a soft warm hairline.
        rim = QPen(QColor(ONYX["border"]))
        rim.setWidthF(1.4)
        p.setPen(rim)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(center, rect.width() / 2, rect.width() / 2)

        # 3) Twelve faint tick marks — the hours, barely there.
        p.save()
        p.translate(center)
        tick = QColor(ONYX["text_muted"])
        tick.setAlpha(70)
        for i in range(12):
            a = math.radians(i * 30.0)
            outer = rect.width() / 2 - 4
            inner = outer - (8 if i % 3 == 0 else 5)
            x0, y0 = inner * math.sin(a), -inner * math.cos(a)
            x1, y1 = outer * math.sin(a), -outer * math.cos(a)
            pen = QPen(tick)
            pen.setWidthF(2.0 if i % 3 == 0 else 1.0)
            p.setPen(pen)
            p.drawLine(QPointF(x0, y0), QPointF(x1, y1))
        p.restore()

        # 4) The hand — a warm coal swinging from the centre, with a soft halo.
        ang = math.radians(self._display * 360.0)
        hand_len = rect.width() / 2 - 16
        tip = QPointF(
            center.x() + hand_len * math.sin(ang),
            center.y() - hand_len * math.cos(ang),
        )
        halo = QRadialGradient(tip, 22)
        hc = QColor(glow)
        hc.setAlpha(150)
        halo.setColorAt(0.0, hc)
        halo.setColorAt(1.0, QColor(glow.red(), glow.green(), glow.blue(), 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(halo)
        p.drawEllipse(tip, 18, 18)

        hand = QPen(glow)
        hand.setWidthF(3.2)
        hand.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(hand)
        p.drawLine(center, tip)

        # The coal at the tip and a small centre hub.
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(glow)
        p.drawEllipse(tip, 6.5, 6.5)
        hub = QColor(glow)
        p.setBrush(hub.darker(130))
        p.drawEllipse(center, 4.0, 4.0)

        # 5) The time, read as language in the band beneath the face, with its
        #    caption in the band above. Both bands are reserved by _face_rect, so
        #    nothing clips at the widget's edges.
        time_rect = QRectF(0, self.height() - self._TIME_BAND, self.width(), self._TIME_BAND)
        p.setPen(QColor(ONYX["text"]))
        p.setFont(serif_font(20, QFont.Weight.Medium))
        p.drawText(
            time_rect,
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
            self._friendly_time(),
        )
        if self._caption:
            cap_rect = QRectF(0, 0, self.width(), self._CAP_BAND)
            p.setPen(QColor(ONYX["text_muted"]))
            p.setFont(sans_font(10, QFont.Weight.DemiBold))
            p.drawText(
                cap_rect,
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                self._caption.upper(),
            )
        p.end()

    def _friendly_time(self) -> str:
        h, m = self.hour(), self.minute()
        suffix = "am" if h < 12 else "pm"
        h12 = h % 12 or 12
        return f"{h12}:{m:02d} {suffix}"


# ---------------------------------------------------------------------------
# A quiet ember confirmation — never a popup, just a warm word that fades.
# (mirrors the daily check-in's acknowledgement; audit_03 §3.3)
# ---------------------------------------------------------------------------
class _EmberConfirm(QLabel):
    """An inline, fading acknowledgement in the reading serif."""

    def __init__(self, reduced_motion: bool = False, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._reduced_motion = reduced_motion
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFont(serif_font(16))
        self.setWordWrap(True)
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
        self._fade.setDuration(3000)
        self._fade.setKeyValueAt(0.0, 0.0)
        self._fade.setKeyValueAt(0.12, 1.0)
        self._fade.setKeyValueAt(0.72, 1.0)
        self._fade.setKeyValueAt(1.0, 0.0)
        self._fade.start()


# ---------------------------------------------------------------------------
# Widget
# ---------------------------------------------------------------------------


class SleepWidget(QWidget):
    """The morning rest check-in: one question, two dials, how it felt."""

    entry_saved = pyqtSignal(dict)

    def __init__(self, main_window: Any, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.main_window = main_window

        self._sleep_tracker = None
        with contextlib.suppress(Exception):
            self._sleep_tracker = main_window.sleep_tracker

        self._reduced_motion = self._detect_reduced_motion()
        self._bg = QColor(ONYX["background"])

        self._entries: list[dict[str, Any]] = []
        self._load_entries()
        self._build_ui()
        self._refresh_summary()
        self._refresh_notes()

    # ------------------------------------------------------------------
    # Persistence  (unchanged shape — same file, same keys, same backend)
    # ------------------------------------------------------------------

    def _data_dir(self) -> Path:
        try:
            return Path(self.main_window.data_dir)
        except (AttributeError, TypeError):
            p = get_data_dir()
            p.mkdir(parents=True, exist_ok=True)
            return p

    def _data_file(self) -> Path:
        d = self._data_dir()
        d.mkdir(parents=True, exist_ok=True)
        return d / "sleep_entries.json"

    def _load_entries(self) -> None:
        path = self._data_file()
        if path.exists():
            try:
                with open(path) as fh:
                    self._entries = json.load(fh)
            except (json.JSONDecodeError, OSError) as exc:
                logger.debug(f"Sleep entries load error: {exc}")

    def _save_entries(self) -> None:
        try:
            with open(self._data_file(), "w") as fh:
                json.dump(self._entries, fh, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save sleep entries: {e}")

    # ------------------------------------------------------------------
    # The warm room behind the cards
    # ------------------------------------------------------------------
    def paintEvent(self, _event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), self._bg)
        # A low, late-night warmth pooled near the top, where the question sits.
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
        root.setContentsMargins(40, 36, 40, 36)
        scroll.setWidget(container)

        root.addWidget(self._build_entry_card())
        root.addWidget(self._build_summary_card())
        root.addWidget(self._build_notes_card())
        root.addStretch()

    # -- the morning check-in -------------------------------------------
    def _build_entry_card(self) -> QWidget:
        card = HearthCard(elevation=2, radius=24)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(34, 30, 34, 30)
        layout.setSpacing(18)

        question = QLabel("How did you sleep?")
        question.setFont(serif_font(27, QFont.Weight.Medium))
        question.setAlignment(Qt.AlignmentFlag.AlignCenter)
        question.setStyleSheet(f"color: {ONYX['text']}; background: transparent;")
        layout.addWidget(question)

        sub = QLabel("No need to be precise — close enough is plenty.")
        sub.setFont(serif_font(15))
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(f"color: {ONYX['text_muted']}; background: transparent;")
        layout.addWidget(sub)

        layout.addSpacing(6)

        # The two dials — when you settled, when you woke. Dragged, not stepped.
        dials = QHBoxLayout()
        dials.setSpacing(14)
        dials.addStretch()

        self._bed_dial = _TimeDial(
            22, 30, caption="settled in", reduced_motion=self._reduced_motion
        )
        self._bed_dial.timeChanged.connect(lambda *_: self._on_times_changed())
        dials.addWidget(self._bed_dial)

        # A soft tilde between the two, so they read as a span of night.
        tilde = QLabel("through")
        tilde.setFont(serif_font(15))
        tilde.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tilde.setStyleSheet(f"color: {ONYX['text_muted']}; background: transparent;")
        dials.addWidget(tilde)

        self._wake_dial = _TimeDial(7, 0, caption="woke", reduced_motion=self._reduced_motion)
        self._wake_dial.timeChanged.connect(lambda *_: self._on_times_changed())
        dials.addWidget(self._wake_dial)

        dials.addStretch()
        layout.addLayout(dials)

        # The span, read in plain words ("about seven and a half hours").
        self._span_label = QLabel("")
        self._span_label.setFont(serif_font(17))
        self._span_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._span_label.setStyleSheet(f"color: {ONYX['text']}; background: transparent;")
        layout.addWidget(self._span_label)

        layout.addSpacing(10)

        # How it felt — the quality slider, word-valued, forgiving.
        feel_prompt = QLabel("And how did it feel?")
        feel_prompt.setFont(serif_font(19, QFont.Weight.Medium))
        feel_prompt.setStyleSheet(f"color: {ONYX['text']}; background: transparent;")
        layout.addWidget(feel_prompt)

        self._quality = StateSlider(value=0.5, reduced_motion=self._reduced_motion)
        self._quality.setMinimumHeight(86)
        self._quality.valueChanged.connect(self._on_quality_changed)
        layout.addWidget(self._quality)

        self._feel_echo = QLabel("")
        self._feel_echo.setFont(serif_font(15))
        self._feel_echo.setWordWrap(True)
        self._feel_echo.setStyleSheet(f"color: {ONYX['text_muted']}; background: transparent;")
        layout.addWidget(self._feel_echo)

        layout.addSpacing(8)

        save_row = QHBoxLayout()
        save_row.addStretch()
        self._save_btn = HearthButton(
            "Set down the night", role="primary", reduced_motion=self._reduced_motion
        )
        self._save_btn.clicked.connect(self._save_entry)
        save_row.addWidget(self._save_btn)
        save_row.addStretch()
        layout.addLayout(save_row)

        self._confirm = _EmberConfirm(reduced_motion=self._reduced_motion)
        layout.addWidget(self._confirm)

        # Seed the live readouts.
        self._on_times_changed()
        self._on_quality_changed(self._quality.value())
        return card

    # -- the gentle summary ---------------------------------------------
    def _build_summary_card(self) -> QWidget:
        card = HearthCard(elevation=0, radius=20)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(28, 24, 28, 26)
        layout.setSpacing(10)

        title = QLabel("Lately")
        title.setFont(serif_font(18, QFont.Weight.Medium))
        title.setStyleSheet(f"color: {ONYX['text']}; background: transparent;")
        layout.addWidget(title)

        self._summary_line = QLabel("")
        self._summary_line.setFont(serif_font(17))
        self._summary_line.setWordWrap(True)
        self._summary_line.setStyleSheet(f"color: {ONYX['text']}; background: transparent;")
        layout.addWidget(self._summary_line)

        self._summary_sub = QLabel("")
        self._summary_sub.setFont(sans_font(12))
        self._summary_sub.setWordWrap(True)
        self._summary_sub.setStyleSheet(f"color: {ONYX['text_muted']}; background: transparent;")
        layout.addWidget(self._summary_sub)
        return card

    # -- notes for the kind of nights you have --------------------------
    def _build_notes_card(self) -> QWidget:
        card = HearthCard(elevation=0, radius=20)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(28, 24, 28, 26)
        layout.setSpacing(12)

        title = QLabel("For the kind of nights you have")
        title.setFont(serif_font(18, QFont.Weight.Medium))
        title.setStyleSheet(f"color: {ONYX['text']}; background: transparent;")
        layout.addWidget(title)

        self._notes_host = QVBoxLayout()
        self._notes_host.setSpacing(12)
        layout.addLayout(self._notes_host)
        return card

    # ------------------------------------------------------------------
    # Live readouts
    # ------------------------------------------------------------------

    def _calc_duration(self, bedtime_str: str, waketime_str: str) -> float:
        try:
            bed = datetime.strptime(bedtime_str, "%H:%M")
            wake = datetime.strptime(waketime_str, "%H:%M")
            if wake <= bed:
                wake += timedelta(days=1)
            return round((wake - bed).total_seconds() / 3600, 2)
        except (ValueError, TypeError):
            return 0.0

    def _on_times_changed(self) -> None:
        hours = self._calc_duration(self._bed_dial.time_string(), self._wake_dial.time_string())
        self._span_label.setText(self._span_phrase(hours))

    @staticmethod
    def _span_phrase(hours: float) -> str:
        if hours <= 0:
            return "a night that wrapped around itself"
        whole = int(hours)
        frac = hours - whole

        def part() -> str:
            if frac < 0.2:
                return ""
            if frac < 0.45:
                return " and a bit"
            if frac < 0.7:
                return " and a half"
            return "ish, nearly " + str(whole + 1)

        return f"That's about {whole}{part()} hours of rest."

    def _on_quality_changed(self, t: float) -> None:
        word = word_for(t)
        echoes = {
            "Bright": "A good one. Glad your body got what it needed.",
            "Good": "Restful enough. That's worth something.",
            "Okay": "Okay is a fine night. You showed up to the morning.",
            "Low": "A thin night. Be gentle with yourself today.",
            "Bad": "A rough one. It happens — today doesn't have to be perfect.",
        }
        self._feel_echo.setText(echoes.get(word, ""))

    # ------------------------------------------------------------------
    # Save  (same backend call, same JSON keys, same signal payload)
    # ------------------------------------------------------------------

    def _quality_score(self) -> int:
        """Map the slider's [0, 1] feel onto the stored 1–10 quality score."""
        return max(1, min(10, round(1 + self._quality.value() * 9)))

    def _save_entry(self) -> None:
        bed_str = self._bed_dial.time_string()
        wake_str = self._wake_dial.time_string()
        duration = self._calc_duration(bed_str, wake_str)
        quality = self._quality_score()

        entry: dict[str, Any] = {
            "date": date.today().isoformat(),
            "bedtime": bed_str,
            "wake_time": wake_str,
            "duration_hours": duration,
            "quality": quality,
            "interruptions": 0,
            "notes": "",
            "created_at": datetime.now().isoformat(),
        }

        # SAME backend call the widget has always made.
        try:
            if self._sleep_tracker and hasattr(self._sleep_tracker, "log_sleep"):
                self._sleep_tracker.log_sleep(
                    date=entry["date"],
                    bedtime=bed_str,
                    wake_time=wake_str,
                    quality=quality,
                    interruptions=0,
                    notes="",
                )
        except (AttributeError, TypeError) as exc:
            logger.debug(f"Sleep tracker log error: {exc}")

        self._entries.append(entry)
        self._save_entries()
        self.entry_saved.emit(entry)

        # A warm, forgiving acknowledgement — never a popup, never a scolding
        # of a short night.
        self._confirm.acknowledge(self._farewell(quality, duration))

        self._reset_form()
        self._refresh_summary()

    @staticmethod
    def _farewell(quality: int, hours: float) -> str:
        if quality <= 3 or (0 < hours < 5):
            return "Set down. A hard night is still behind you now."
        if quality >= 8:
            return "Set down. Carry the good rest into the day."
        return "Set down. Thanks for telling me how the night went."

    def _reset_form(self) -> None:
        self._bed_dial.set_time(22, 30)
        self._wake_dial.set_time(7, 0)
        self._quality.setValue(0.5)
        self._on_times_changed()
        self._on_quality_changed(self._quality.value())

    # ------------------------------------------------------------------
    # Summary + notes
    # ------------------------------------------------------------------

    def _refresh_summary(self) -> None:
        if not self._entries:
            self._summary_line.setText(
                "A couple of mornings here and I'll start noticing how your nights run."
            )
            self._summary_sub.setText("")
            return

        durations = [e.get("duration_hours", 0) for e in self._entries if e.get("duration_hours")]
        qualities = [e.get("quality", 0) for e in self._entries if e.get("quality")]

        if not durations:
            self._summary_line.setText(
                "A couple of mornings here and I'll start noticing how your nights run."
            )
            self._summary_sub.setText("")
            return

        avg_dur = stats_mod.mean(durations)
        recent = durations[-7:]
        debt = sum(max(0, 8.0 - d) for d in recent)
        nights = len(durations)

        line = (
            f"Across {nights} {'night' if nights == 1 else 'nights'}, "
            f"you've rested about {avg_dur:.1f} hours."
        )
        self._summary_line.setText(line)

        sub_bits: list[str] = []
        if qualities:
            avg_q = stats_mod.mean(qualities)
            sub_bits.append(f"and most felt {word_for((avg_q - 1) / 9.0).lower()}")
        if debt >= 5:
            sub_bits.append("the last week has run a little short — easy does it")
        elif debt >= 2:
            sub_bits.append("the last week's been mostly steady")
        else:
            sub_bits.append("the last week's been kind to you")
        self._summary_sub.setText("  ·  ".join(sub_bits).capitalize())

    def _refresh_notes(self) -> None:
        conditions: list[str] = ["General"]
        try:
            profile = self.main_window.profile_manager.current_profile
            if profile and hasattr(profile, "conditions") and profile.conditions:
                for c in profile.conditions:
                    name = c.value if hasattr(c, "value") else str(c)
                    if name in _NIGHT_NOTES:
                        conditions.append(name)
        except (AttributeError, TypeError) as exc:
            logger.debug(f"Sleep notes refresh error: {exc}")

        # Clear any previous rows.
        while self._notes_host.count():
            item = self._notes_host.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        seen: set[str] = set()
        notes: list[str] = []
        for cond in conditions:
            for note in _NIGHT_NOTES.get(cond, []):
                if note not in seen:
                    seen.add(note)
                    notes.append(note)

        for note in notes[:4]:
            self._notes_host.addWidget(self._note_row(note))

    def _note_row(self, text: str) -> QWidget:
        row = QWidget()
        row.setStyleSheet("background: transparent;")
        h = QHBoxLayout(row)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(12)

        # A small warm ember dot, so each note reads as a kept coal, not a bullet.
        dot = _NoteDot()
        h.addWidget(dot, alignment=Qt.AlignmentFlag.AlignTop)

        label = QLabel(text)
        label.setFont(serif_font(15))
        label.setWordWrap(True)
        label.setStyleSheet(f"color: {ONYX['text']}; background: transparent;")
        h.addWidget(label, stretch=1)
        return row

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _detect_reduced_motion(self) -> bool:
        try:
            from utils.accessibility import detect_reduced_motion

            return detect_reduced_motion()
        except Exception:  # accessibility probing must never block the screen
            return False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def save_state(self) -> None:
        """Called by main window on close."""
        self._save_entries()


# ---------------------------------------------------------------------------
# A tiny warm coal used as a note marker.
# ---------------------------------------------------------------------------
class _NoteDot(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(14, 24)

    def paintEvent(self, _):  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        c = QPointF(self.width() / 2, 9)
        glow = QColor(ONYX["accent"])
        halo = QRadialGradient(c, 9)
        h0 = QColor(glow)
        h0.setAlpha(120)
        halo.setColorAt(0.0, h0)
        halo.setColorAt(1.0, QColor(glow.red(), glow.green(), glow.blue(), 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(halo)
        p.drawEllipse(c, 8, 8)
        path = QPainterPath()
        path.addEllipse(c, 3.2, 3.2)
        p.fillPath(path, glow)
        p.end()
