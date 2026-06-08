"""Focus Sessions — Pomodoro-style deep-work timer.

A warm, low-energy-first space for setting a focus block. The circular
timer reads as a hearth-coal that burns down gently; the presets meet
you where you are (gentle first), and the history quietly celebrates
what you've already done.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from PyQt6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    QRectF,
    Qt,
    QTimer,
    pyqtProperty,
    pyqtSignal,
)
from PyQt6.QtGui import (
    QColor,
    QFont,
    QPainter,
    QRadialGradient,
)
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from gui.components.hearth_surfaces import ONYX, HearthButton, HearthCard
from gui.components.state_controls import sans_font, serif_font

logger = logging.getLogger(__name__)

_PRESETS = [
    (15, "Gentle"),
    (25, "Pomodoro"),
    (45, "Deep"),
    (60, "Extended"),
]


def _format_minutes(total_seconds: int) -> str:
    mins = max(0, total_seconds // 60)
    secs = max(0, total_seconds % 60)
    return f"{mins:02d}:{secs:02d}"


def _human_when(when: datetime) -> str:
    """A plain, forgiving timestamp."""
    delta = datetime.now() - when
    if delta < timedelta(minutes=1):
        return "just now"
    if delta < timedelta(hours=1):
        return f"{int(delta.seconds / 60)} min ago"
    if delta < timedelta(hours=2):
        return "an hour ago"
    if delta < timedelta(days=1):
        return f"{delta.seconds // 3600} hours ago"
    if delta < timedelta(days=2):
        return "yesterday"
    if delta < timedelta(days=7):
        return f"{delta.days} days ago"
    return when.strftime("%a %d %b")


# ---------------------------------------------------------------------------
# _TimerRing — a circular progress ring that warms as time burns down.
# ---------------------------------------------------------------------------
class _TimerRing(QWidget):
    """Circular timer with an ember arc and reading-serif numerals."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._total_seconds = 25 * 60
        self._remaining_seconds = 25 * 60
        self._breathing = 0.0
        self._is_running = False
        self.setMinimumSize(260, 260)
        self.setMaximumSize(340, 340)

        self._breath_anim = QPropertyAnimation(self, b"breathing", self)
        self._breath_anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._breath_anim.setDuration(2600)
        self._breath_anim.setStartValue(0.0)
        self._breath_anim.setEndValue(1.0)
        self._breath_anim.finished.connect(self._on_breath_finished)

    def _get_breathing(self) -> float:
        return self._breathing

    def _set_breathing(self, v: float) -> None:
        self._breathing = v
        self.update()

    breathing = pyqtProperty(float, fget=_get_breathing, fset=_set_breathing)

    def _on_breath_finished(self) -> None:
        nxt = 1.0 if self._breath_anim.endValue() == 0.0 else 0.0
        self._breath_anim.setStartValue(self._breath_anim.endValue())
        self._breath_anim.setEndValue(nxt)
        self._breath_anim.start()

    def set_time(self, total: int, remaining: int) -> None:
        self._total_seconds = max(1, total)
        self._remaining_seconds = max(0, remaining)
        self.update()

    def start_breathing(self) -> None:
        if self._breath_anim.state() != QPropertyAnimation.State.Running:
            self._breath_anim.start()

    def stop_breathing(self) -> None:
        self._breath_anim.stop()
        self._breathing = 0.0
        self.update()

    def paintEvent(self, _) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(self.rect()).adjusted(12, 12, -12, -12)
        cx = rect.center().x()
        cy = rect.center().y()
        radius = min(rect.width(), rect.height()) / 2 - 14
        ring_rect = QRectF(cx - radius, cy - radius, radius * 2, radius * 2)

        # 1) Background track — a quiet warm groove.
        track_pen = p.pen()
        track_pen.setColor(QColor(ONYX["border"]))
        track_pen.setWidthF(10)
        track_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(track_pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(ring_rect.center(), radius, radius)

        # 2) Progress arc — warmth tracks remaining time (full when fresh,
        #    dimmed when low). The arc shrinks clockwise as time burns.
        ratio = self._remaining_seconds / self._total_seconds
        glow = QColor(ONYX["accent"])
        pulse = 1.0 + 0.06 * self._breathing
        glow.setAlpha(int(200 * pulse))

        pen = p.pen()
        pen.setColor(glow)
        pen.setWidthF(10)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)

        start_angle = 90 * 16
        span_angle = -int(360 * 16 * ratio)
        p.drawArc(ring_rect, start_angle, span_angle)

        # 3) Inner warm bloom when active.
        if self._is_running:
            bloom = QRadialGradient(cx, cy, radius * 0.65)
            warm = QColor(ONYX["accent"])
            warm.setAlpha(int(14 * pulse))
            bloom.setColorAt(0.0, warm)
            bloom.setColorAt(1.0, QColor(warm.red(), warm.green(), warm.blue(), 0))
            p.setBrush(bloom)
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(ring_rect.center(), radius * 0.65, radius * 0.65)

        # 4) Time text — reading voice, centred.
        p.setPen(QColor(ONYX["text"]))
        p.setFont(serif_font(46, QFont.Weight.Medium))
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, _format_minutes(self._remaining_seconds))

        # 5) Subtitle beneath the numerals.
        p.setFont(sans_font(12))
        p.setPen(QColor(ONYX["text_muted"]))
        sub_rect = QRectF(rect.left(), cy + 30, rect.width(), 28)
        if ratio >= 0.999:
            label = "Ready"
        elif self._remaining_seconds == 0:
            label = "Finished"
        elif self._is_running:
            label = "Focusing"
        else:
            label = "Paused"
        p.drawText(sub_rect, Qt.AlignmentFlag.AlignCenter, label)

        p.end()


# ---------------------------------------------------------------------------
# _SessionRow — one past session, warm and quiet.
# ---------------------------------------------------------------------------
class _SessionRow(QWidget):
    """A single line of session history."""

    def __init__(self, session: Any, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        row = QHBoxLayout(self)
        row.setContentsMargins(2, 6, 2, 6)
        row.setSpacing(12)

        when = getattr(session, "started_at", None) or getattr(session, "started", None)
        duration = getattr(session, "duration_minutes", 0) or 0
        interrupted = getattr(session, "interrupted", False)
        reason = getattr(session, "reason", "") or ""

        when_text = _human_when(when) if isinstance(when, datetime) else "—"
        dur_text = f"{duration} min" if duration else "—"

        left = QVBoxLayout()
        left.setSpacing(0)
        line = QLabel(f"{dur_text}  ·  {when_text}")
        line.setFont(serif_font(15))
        line.setStyleSheet(f"color: {ONYX['text']}; background: transparent;")
        left.addWidget(line)

        if reason and reason != "manual":
            sub = QLabel(reason.replace("_", " "))
            sub.setFont(sans_font(11))
            sub.setStyleSheet(f"color: {ONYX['text_muted']}; background: transparent;")
            left.addWidget(sub)

        row.addLayout(left, stretch=1)

        if interrupted:
            mark = QLabel("interrupted")
            mark.setFont(sans_font(11, QFont.Weight.DemiBold))
            mark.setStyleSheet(f"color: {ONYX['crisis']}; background: transparent;")
            row.addWidget(mark, alignment=Qt.AlignmentFlag.AlignVCenter)
        else:
            mark = QLabel("done")
            mark.setFont(sans_font(11, QFont.Weight.DemiBold))
            mark.setStyleSheet(f"color: {ONYX['accent']}; background: transparent;")
            row.addWidget(mark, alignment=Qt.AlignmentFlag.AlignVCenter)


# ---------------------------------------------------------------------------
# FocusSessionWidget
# ---------------------------------------------------------------------------
class FocusSessionWidget(QWidget):
    """The warm focus room: set an intention, choose a duration, breathe,
    and let the session hold the noise at bay.
    """

    session_started = pyqtSignal()
    session_ended = pyqtSignal()
    session_paused = pyqtSignal()
    session_resumed = pyqtSignal()

    def __init__(
        self,
        theme: dict[str, str],
        focus_manager: Any | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._theme = theme
        self._focus_manager = focus_manager
        self._reduced_motion = self._detect_reduced_motion()
        self._bg = QColor(ONYX["background"])

        # Local timer state
        self._selected_preset = 1  # Pomodoro default
        self._total_seconds = _PRESETS[self._selected_preset][0] * 60
        self._remaining_seconds = self._total_seconds
        self._is_running = False
        self._is_paused = False

        self._tick_timer = QTimer(self)
        self._tick_timer.setInterval(1000)
        self._tick_timer.timeout.connect(self._on_tick)

        self._build_ui()
        self._sync_from_manager()

    # ------------------------------------------------------------------
    # Warm room background
    # ------------------------------------------------------------------
    def paintEvent(self, _) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), self._bg)

        # A soft warmth pool behind the timer.
        accent = QColor(ONYX["accent"])
        cx = self.width() / 2
        grad = QRadialGradient(cx, self.height() * 0.22, self.width() * 0.55)
        warm = QColor(accent)
        warm.setAlpha(18 if not self._is_running else 28)
        grad.setColorAt(0.0, warm)
        grad.setColorAt(1.0, QColor(accent.red(), accent.green(), accent.blue(), 0))
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
        container.setFixedWidth(640)
        self._root = QVBoxLayout(container)
        self._root.setSpacing(14)
        self._root.setContentsMargins(40, 34, 40, 40)

        hold = QWidget()
        hold.setStyleSheet("background: transparent;")
        hold_row = QHBoxLayout(hold)
        hold_row.setContentsMargins(0, 0, 0, 0)
        hold_row.addStretch()
        hold_row.addWidget(container)
        hold_row.addStretch()
        scroll.setWidget(hold)

        self._build_header()
        self._build_timer()
        self._build_presets()
        self._build_controls()
        self._build_intention()
        self._build_distracting_apps()
        self._build_history()
        self._root.addStretch()

    def _build_header(self) -> None:
        title = QLabel("Focus")
        title.setFont(serif_font(28, QFont.Weight.Medium))
        title.setStyleSheet(f"color: {ONYX['text']}; background: transparent;")
        self._root.addWidget(title)

        self._lede = QLabel("One block at a time. Choose what feels possible.")
        self._lede.setFont(serif_font(16))
        self._lede.setWordWrap(True)
        self._lede.setStyleSheet(f"color: {ONYX['text_muted']}; background: transparent;")
        self._root.addWidget(self._lede)
        self._root.addSpacing(8)

    def _build_timer(self) -> None:
        row = QHBoxLayout()
        row.addStretch()
        self._ring = _TimerRing()
        self._ring.set_time(self._total_seconds, self._remaining_seconds)
        row.addWidget(self._ring)
        row.addStretch()
        self._root.addLayout(row)
        self._root.addSpacing(4)

    def _build_presets(self) -> None:
        row = QHBoxLayout()
        row.setSpacing(8)
        row.addStretch()
        self._preset_buttons: list[HearthButton] = []
        for idx, (_minutes, label) in enumerate(_PRESETS):
            btn = HearthButton(label, role="ghost", reduced_motion=self._reduced_motion)
            btn.setMinimumHeight(40)
            btn.clicked.connect(lambda _checked=False, i=idx: self._select_preset(i))
            self._preset_buttons.append(btn)
            row.addWidget(btn)
        row.addStretch()
        self._root.addLayout(row)
        self._root.addSpacing(4)
        self._update_preset_styles()

    def _build_controls(self) -> None:
        row = QHBoxLayout()
        row.setSpacing(10)
        row.addStretch()

        self._start_btn = HearthButton("Start", role="primary", reduced_motion=self._reduced_motion)
        self._start_btn.clicked.connect(self._on_start)
        row.addWidget(self._start_btn)

        self._pause_btn = HearthButton("Pause", role="ghost", reduced_motion=self._reduced_motion)
        self._pause_btn.clicked.connect(self._on_pause)
        self._pause_btn.setVisible(False)
        row.addWidget(self._pause_btn)

        self._resume_btn = HearthButton(
            "Resume", role="primary", reduced_motion=self._reduced_motion
        )
        self._resume_btn.clicked.connect(self._on_resume)
        self._resume_btn.setVisible(False)
        row.addWidget(self._resume_btn)

        self._stop_btn = HearthButton("Stop", role="crisis", reduced_motion=self._reduced_motion)
        self._stop_btn.clicked.connect(self._on_stop)
        self._stop_btn.setVisible(False)
        row.addWidget(self._stop_btn)

        row.addStretch()
        self._root.addLayout(row)
        self._root.addSpacing(12)

    def _build_intention(self) -> None:
        card = HearthCard(elevation=1, radius=18)
        col = QVBoxLayout(card)
        col.setContentsMargins(20, 16, 20, 16)
        col.setSpacing(8)

        prompt = QLabel("What are you focusing on?")
        prompt.setFont(sans_font(12, QFont.Weight.DemiBold))
        prompt.setStyleSheet(f"color: {ONYX['text_muted']}; background: transparent;")
        col.addWidget(prompt)

        self._intention_input = QLineEdit()
        self._intention_input.setPlaceholderText("Name it, gently…")
        self._intention_input.setFont(serif_font(16))
        self._intention_input.setStyleSheet(
            "QLineEdit { background: transparent; border: none; "
            f"color: {ONYX['text']}; padding: 4px 2px; }}"
            f"QLineEdit::placeholder {{ color: {ONYX['text_muted']}; }}"
        )
        col.addWidget(self._intention_input)

        self._root.addWidget(card)
        self._root.addSpacing(10)

    def _build_distracting_apps(self) -> None:
        card = HearthCard(elevation=0, radius=18)
        col = QVBoxLayout(card)
        col.setContentsMargins(20, 16, 20, 16)
        col.setSpacing(10)

        header = QLabel("Quieted while you work")
        header.setFont(sans_font(12, QFont.Weight.DemiBold))
        header.setStyleSheet(f"color: {ONYX['text_muted']}; background: transparent;")
        col.addWidget(header)

        apps = self._distracting_apps()
        if apps:
            wrap = QWidget()
            wrap.setStyleSheet("background: transparent;")
            flow = QHBoxLayout(wrap)
            flow.setContentsMargins(0, 0, 0, 0)
            flow.setSpacing(6)
            for app in sorted(apps):
                pill = QLabel(app)
                pill.setFont(sans_font(11))
                pill.setStyleSheet(
                    f"color: {ONYX['text']}; background: {ONYX['surface']}; "
                    f"border: 1px solid {ONYX['border']}; border-radius: 10px; "
                    "padding: 4px 10px;"
                )
                flow.addWidget(pill)
            flow.addStretch()
            col.addWidget(wrap)
        else:
            none = QLabel("No apps configured yet.")
            none.setFont(serif_font(14))
            none.setStyleSheet(f"color: {ONYX['text_muted']}; background: transparent;")
            col.addWidget(none)

        self._root.addWidget(card)
        self._root.addSpacing(10)

    def _build_history(self) -> None:
        cap = QLabel("Recent sessions")
        cap.setFont(sans_font(11, QFont.Weight.DemiBold))
        cap.setStyleSheet(
            f"color: {ONYX['text_muted']}; background: transparent; letter-spacing: 1px;"
        )
        self._root.addWidget(cap)

        self._history_card = HearthCard(elevation=0, radius=18)
        self._history_box = QVBoxLayout(self._history_card)
        self._history_box.setContentsMargins(18, 12, 18, 12)
        self._history_box.setSpacing(0)
        self._root.addWidget(self._history_card)

        self._refresh_history()

    # ------------------------------------------------------------------
    # Data & state
    # ------------------------------------------------------------------
    def _distracting_apps(self) -> set[str]:
        if self._focus_manager is None:
            return set()
        try:
            return set(self._focus_manager.get_distracting_apps())
        except Exception:
            return set()

    def _history(self) -> list[Any]:
        if self._focus_manager is None:
            return []
        try:
            return list(self._focus_manager.get_sessions(days=30))
        except Exception:
            return []

    def _sync_from_manager(self) -> None:
        """If focus mode is already active elsewhere, mirror its state."""
        if self._focus_manager is None:
            return
        try:
            state = self._focus_manager.state
        except Exception:
            return

        if state.name == "ACTIVE" and self._focus_manager.current_session:
            sess = self._focus_manager.current_session
            dur = getattr(sess, "duration_minutes", 0) or 0
            started = getattr(sess, "started_at", None)
            if dur > 0 and isinstance(started, datetime):
                elapsed = int((datetime.now() - started).total_seconds())
                self._total_seconds = dur * 60
                self._remaining_seconds = max(0, self._total_seconds - elapsed)
                self._is_running = True
                self._is_paused = False
                self._ring._is_running = True
                self._ring.start_breathing()
                self._tick_timer.start()
                self._update_controls()
                self._update_preset_styles()
        elif state.name == "PAUSED" and self._focus_manager.current_session:
            sess = self._focus_manager.current_session
            dur = getattr(sess, "duration_minutes", 0) or 0
            self._total_seconds = dur * 60
            self._is_running = False
            self._is_paused = True
            self._ring._is_running = False
            self._ring.stop_breathing()
            self._tick_timer.stop()
            self._update_controls()
            self._update_preset_styles()

    def _select_preset(self, idx: int) -> None:
        if self._is_running or self._is_paused:
            return
        self._selected_preset = idx
        minutes = _PRESETS[idx][0]
        self._total_seconds = minutes * 60
        self._remaining_seconds = self._total_seconds
        self._ring.set_time(self._total_seconds, self._remaining_seconds)
        self._update_preset_styles()

    def _update_preset_styles(self) -> None:
        for i, btn in enumerate(self._preset_buttons):
            if self._is_running or self._is_paused:
                btn.setEnabled(False)
                continue
            btn.setEnabled(True)
            if i == self._selected_preset:
                btn.setProperty("role", "primary")
                # Rebuild the button style to reflect role change.
                btn._role = "primary"
            else:
                btn.setProperty("role", "ghost")
                btn._role = "ghost"
            btn.update()

    def _update_controls(self) -> None:
        if self._is_running:
            self._start_btn.setVisible(False)
            self._pause_btn.setVisible(True)
            self._resume_btn.setVisible(False)
            self._stop_btn.setVisible(True)
            self._lede.setText("The room is holding the noise back. One breath at a time.")
        elif self._is_paused:
            self._start_btn.setVisible(False)
            self._pause_btn.setVisible(False)
            self._resume_btn.setVisible(True)
            self._stop_btn.setVisible(True)
            self._lede.setText("Paused. The coals are banked — ready when you are.")
        else:
            self._start_btn.setVisible(True)
            self._pause_btn.setVisible(False)
            self._resume_btn.setVisible(False)
            self._stop_btn.setVisible(False)
            self._lede.setText("One block at a time. Choose what feels possible.")

    def _refresh_history(self) -> None:
        while self._history_box.count():
            item = self._history_box.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()

        sessions = self._history()
        if not sessions:
            empty = QLabel("No sessions yet. The first one is always the hardest.")
            empty.setFont(serif_font(15))
            empty.setWordWrap(True)
            empty.setStyleSheet(f"color: {ONYX['text_muted']}; background: transparent;")
            self._history_box.addWidget(empty)
            return

        # Show most recent first
        for sess in reversed(sessions):
            self._history_box.addWidget(_SessionRow(sess))

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def _on_start(self) -> None:
        minutes = _PRESETS[self._selected_preset][0]
        self._total_seconds = minutes * 60
        self._remaining_seconds = self._total_seconds
        self._is_running = True
        self._is_paused = False

        if self._focus_manager is not None:
            try:
                self._focus_manager.activate(
                    reason="focus_session",
                    trigger="user",
                    duration_minutes=minutes,
                )
            except Exception as exc:
                logger.warning("Focus activation failed: %s", exc)

        self._ring.set_time(self._total_seconds, self._remaining_seconds)
        self._ring._is_running = True
        self._ring.start_breathing()
        self._tick_timer.start()
        self._update_controls()
        self._update_preset_styles()
        self.session_started.emit()

    def _on_pause(self) -> None:
        if not self._is_running:
            return
        self._is_running = False
        self._is_paused = True
        self._tick_timer.stop()
        self._ring._is_running = False
        self._ring.stop_breathing()

        if self._focus_manager is not None:
            try:
                self._focus_manager.pause()
            except Exception as exc:
                logger.warning("Focus pause failed: %s", exc)

        self._update_controls()
        self.session_paused.emit()

    def _on_resume(self) -> None:
        if not self._is_paused:
            return
        self._is_running = True
        self._is_paused = False
        self._tick_timer.start()
        self._ring._is_running = True
        self._ring.start_breathing()

        if self._focus_manager is not None:
            try:
                self._focus_manager.resume()
            except Exception as exc:
                logger.warning("Focus resume failed: %s", exc)

        self._update_controls()
        self.session_resumed.emit()

    def _on_stop(self) -> None:
        was_running = self._is_running or self._is_paused
        self._is_running = False
        self._is_paused = False
        self._tick_timer.stop()
        self._ring._is_running = False
        self._ring.stop_breathing()

        if self._focus_manager is not None:
            try:
                self._focus_manager.deactivate(interrupted=True)
            except Exception as exc:
                logger.warning("Focus deactivate failed: %s", exc)

        self._remaining_seconds = self._total_seconds
        self._ring.set_time(self._total_seconds, self._remaining_seconds)
        self._update_controls()
        self._update_preset_styles()
        self._refresh_history()
        if was_running:
            self.session_ended.emit()

    def _on_tick(self) -> None:
        if not self._is_running:
            return
        self._remaining_seconds -= 1
        self._ring.set_time(self._total_seconds, self._remaining_seconds)

        if self._remaining_seconds <= 0:
            self._remaining_seconds = 0
            self._is_running = False
            self._tick_timer.stop()
            self._ring._is_running = False
            self._ring.stop_breathing()

            if self._focus_manager is not None:
                try:
                    self._focus_manager.deactivate(interrupted=False)
                except Exception as exc:
                    logger.warning("Focus auto-deactivate failed: %s", exc)

            self._update_controls()
            self._update_preset_styles()
            self._refresh_history()
            self.session_ended.emit()

    # ------------------------------------------------------------------
    # Misc
    # ------------------------------------------------------------------
    def _detect_reduced_motion(self) -> bool:
        try:
            from utils.accessibility import detect_reduced_motion

            return detect_reduced_motion()
        except Exception:
            return False

    def apply_theme(self, theme: dict[str, str]) -> None:
        self._theme = theme
        self.update()

    def save_state(self) -> None:
        """Called on app close for parity with other widgets."""
        pass
