"""
Automation -> "The Hearthroom" — the core promise made visible.

This is the one screen where Hearth stops *tracking* and starts *acting*: the
cockpit of the protective companion. It must answer one question the moment you
walk in — "what is my computer doing to protect me right now, and can I trust
it?" — before you finish reading (docs/design/audit_07).

So it is not a four-tab settings panel with a pipe-delimited engine-status string
and a Bootstrap traffic-light button row. It is a single warm room with a living
Hearthstone at its center whose glow *is* the engine state (awake and watching
when guarding, banked to a coal when paused), one honest serif sentence about what
Hearth is doing, one state-aware action to start or pause protection, a segmented
trust dial ("Just tell me -> Ask me first -> Go ahead, I trust you"), and a
human-voiced ledger of the care Hearth has actually taken.

Preserved verbatim:
  * the constructor signature (theme, automation_engine, subscription_manager);
  * every engine call (enable/disable/is_enabled, manual_focus/grounding/crisis,
    config.set_execution_mode on the active profile, list_rules);
  * honest tier gating — free tier suggests, it does not act, and the room says so
    plainly without ever selling an upgrade.

Feedback is always in-surface and ambient (a slow fade), never a QMessageBox —
this is a tender room, and a blocking OS modal is the most hostile possible reply
to someone who just reached for help.
"""

from __future__ import annotations

import contextlib
import logging
from collections import deque
from datetime import datetime

from PyQt6.QtCore import (
    QEasingCurve,
    QPointF,
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
    QPainterPath,
    QRadialGradient,
)
from PyQt6.QtWidgets import (
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from core.automation_config import ExecutionMode
from core.subscription_manager import SubscriptionManager
from core.system_automation import SystemAutomationEngine
from gui.components.hearth_surfaces import HearthButton, HearthCard
from gui.components.hearthlight import Hearthlight
from gui.components.state_controls import sans_font, serif_font

logger = logging.getLogger(__name__)


# The trust steps, in the warm order the audit asks for. Index lines up with the
# three ExecutionMode values so the dial maps cleanly onto the engine.
_TRUST_STEPS = [
    ("Just tell me", ExecutionMode.SUGGESTIONS_ONLY),
    ("Ask me first", ExecutionMode.ASK_FIRST),
    ("Go ahead, I trust you", ExecutionMode.AUTONOMOUS),
]

# How an ember should sit for each engine state. Awake and watching is a warm,
# breathing coal; paused is a banked, dim coal you can read as "off" at a glance.
_GLOW_WATCHING = 0.74
_GLOW_PAUSED = 0.16


# ===========================================================================
# TrustDial — a segmented control for the "how much should I help?" decision.
# Replaces the execution-mode QComboBox. Three painted segments; the warm
# selection slides; the active step reads in the reading serif. Gated honestly:
# on the free tier the higher steps are present but quietly out of reach, with
# the truth stated, never an upsell.
# ===========================================================================
class TrustDial(QWidget):
    """A warm three-step segmented control for the trust decision."""

    selectionChanged = pyqtSignal(int)  # noqa: N815

    def __init__(
        self,
        theme: dict[str, str],
        selected: int = 0,
        max_reachable: int = 2,
        reduced_motion: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._theme = theme
        self._selected = max(0, min(len(_TRUST_STEPS) - 1, selected))
        self._max_reachable = max(0, min(len(_TRUST_STEPS) - 1, max_reachable))
        self._reduced_motion = reduced_motion
        self._pos = float(self._selected)  # eased index for the sliding pill
        self.setMinimumHeight(58)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._slide = QPropertyAnimation(self, b"pos", self)
        self._slide.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._slide.setDuration(0 if reduced_motion else 360)

    # -- eased slide position --------------------------------------------
    def _get_pos(self) -> float:
        return self._pos

    def _set_pos(self, v: float) -> None:
        self._pos = v
        self.update()

    pos = pyqtProperty(float, fget=_get_pos, fset=_set_pos)

    # -- public ----------------------------------------------------------
    def selected(self) -> int:
        return self._selected

    def set_selected(self, idx: int, *, animate: bool = True, emit: bool = True) -> None:
        idx = max(0, min(len(_TRUST_STEPS) - 1, idx))
        changed = idx != self._selected
        self._selected = idx
        if animate and not self._reduced_motion:
            self._slide.stop()
            self._slide.setStartValue(self._pos)
            self._slide.setEndValue(float(idx))
            self._slide.start()
        else:
            self._set_pos(float(idx))
        if changed and emit:
            self.selectionChanged.emit(idx)

    def set_max_reachable(self, idx: int) -> None:
        self._max_reachable = max(0, min(len(_TRUST_STEPS) - 1, idx))
        self.update()

    # -- geometry --------------------------------------------------------
    def _seg_rect(self, i: int) -> QRectF:
        n = len(_TRUST_STEPS)
        m = 4.0
        inner = QRectF(self.rect()).adjusted(m, m, -m, -m)
        w = inner.width() / n
        return QRectF(inner.left() + w * i, inner.top(), w, inner.height())

    def mousePressEvent(self, e):  # noqa: N802
        for i in range(len(_TRUST_STEPS)):
            if self._seg_rect(i).contains(e.position()):
                if i <= self._max_reachable:
                    self.set_selected(i)
                return

    # -- paint -----------------------------------------------------------
    def paintEvent(self, _):  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        border = QColor(self._theme.get("border", "#2E2A24"))
        accent = QColor(self._theme.get("accent", "#D9A05B"))
        text = QColor(self._theme.get("text", "#F2EDE6"))
        muted = QColor(self._theme.get("text_muted", "#A99B88"))
        bg = QColor(self._theme.get("background", "#0F0F11"))

        m = 4.0
        track = QRectF(self.rect()).adjusted(m, m, -m, -m)
        radius = track.height() / 2
        track_path = QPainterPath()
        track_path.addRoundedRect(track, radius, radius)
        # The unlit groove — a quiet warm hollow the selection slides along.
        p.fillPath(track_path, QColor(self._theme.get("surface", "#18181A")))
        pen = p.pen()
        pen.setColor(border)
        pen.setWidthF(1.0)
        p.setPen(pen)
        p.drawPath(track_path)

        # The warm selection pill, eased to the current position.
        sel = self._seg_rect(int(round(self._pos)))
        pill = self._seg_rect(0)
        pill_w = pill.width()
        pill_x = track.left() + (track.width() / len(_TRUST_STEPS)) * self._pos
        pill_rect = QRectF(pill_x, track.top(), pill_w, track.height()).adjusted(2, 2, -2, -2)
        pill_path = QPainterPath()
        pr = pill_rect.height() / 2
        pill_path.addRoundedRect(pill_rect, pr, pr)
        p.fillPath(pill_path, accent)
        # A soft top sheen so the pill reads as lit stone, not a flat chip.
        sheen = QRadialGradient(pill_rect.center().x(), pill_rect.top(), pill_rect.width())
        sheen.setColorAt(0.0, QColor(255, 240, 220, 46))
        sheen.setColorAt(1.0, QColor(255, 240, 220, 0))
        p.save()
        p.setClipPath(pill_path)
        p.fillPath(pill_path, sheen)
        p.restore()
        _ = sel  # selection geometry retained for clarity

        # The three labels. The selected one rides dark-on-amber in the serif;
        # reachable steps are warm; the out-of-reach step is quietly dimmed.
        for i, (label, _mode) in enumerate(_TRUST_STEPS):
            seg = self._seg_rect(i)
            near = abs(self._pos - i) < 0.5
            if near:
                col = QColor("#2A1B0E")
                p.setFont(serif_font(15, QFont.Weight.Medium))
            elif i <= self._max_reachable:
                col = text
                p.setFont(sans_font(12, QFont.Weight.DemiBold))
            else:
                col = QColor(
                    int(muted.red() * 0.7 + bg.red() * 0.3),
                    int(muted.green() * 0.7 + bg.green() * 0.3),
                    int(muted.blue() * 0.7 + bg.blue() * 0.3),
                )
                p.setFont(sans_font(12, QFont.Weight.Medium))
            p.setPen(col)
            p.drawText(seg, Qt.AlignmentFlag.AlignCenter, label)
        p.end()


# ===========================================================================
# CareRow — one human-voiced line in the recent-care ledger. A warm dot, a
# sentence, a quiet timestamp. No grid, no columns, no "Cooldown: 15 min".
# ===========================================================================
class CareRow(QWidget):
    """A single warm row of care Hearth took (or chose not to take)."""

    def __init__(
        self,
        theme: dict[str, str],
        sentence: str,
        when: str,
        magnitude: float = 0.6,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._theme = theme
        self._magnitude = max(0.15, min(1.0, magnitude))
        row = QHBoxLayout(self)
        row.setContentsMargins(2, 8, 2, 8)
        row.setSpacing(14)
        row.addSpacing(16)  # leaves room for the painted warmth dot

        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(2)
        line = QLabel(sentence)
        line.setFont(serif_font(15))
        line.setWordWrap(True)
        line.setStyleSheet(f"color: {theme.get('text', '#F2EDE6')}; background: transparent;")
        stamp = QLabel(when)
        stamp.setFont(sans_font(11))
        stamp.setStyleSheet(
            f"color: {theme.get('text_muted', '#A99B88')}; background: transparent;"
        )
        text_col.addWidget(line)
        text_col.addWidget(stamp)
        row.addLayout(text_col, 1)

    def paintEvent(self, _):  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        accent = QColor(self._theme.get("accent", "#D9A05B"))
        # A warm coal-dot at the left, its size and warmth tracking magnitude.
        cy = 18.0
        r = 3.0 + 3.0 * self._magnitude
        center = QPointF(7.0, cy)
        halo = QRadialGradient(center, r * 3.0)
        h = QColor(accent)
        h.setAlpha(int(80 * self._magnitude))
        halo.setColorAt(0.0, h)
        halo.setColorAt(1.0, QColor(accent.red(), accent.green(), accent.blue(), 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(halo)
        p.drawEllipse(center, r * 2.6, r * 2.6)
        p.setBrush(accent)
        p.drawEllipse(center, r, r)
        p.end()


# ===========================================================================
# AutomationWidget — "The Hearthroom"
# ===========================================================================
class AutomationWidget(QWidget):
    """The protective companion's room: presence first, configuration last."""

    # The integrator wires this; the widget emits whenever protection turns on
    # or off so the rest of the app (tray, shell warmth) can respond. Not wired
    # in main_window by this widget — see the build summary.
    protection_changed = pyqtSignal(bool)

    def __init__(
        self,
        theme: dict,
        automation_engine: SystemAutomationEngine,
        subscription_manager: SubscriptionManager,
    ) -> None:
        super().__init__()
        self.theme = theme
        self.engine = automation_engine
        self.subscription = subscription_manager
        self.config = automation_engine.config

        self._reduced_motion = self._resolve_reduced_motion()
        # The session's care ledger — what Hearth actually did while you were
        # here. The engine keeps no durable history, so we honestly record real
        # actions as they happen rather than inventing a fake feed.
        self._care: deque[tuple[str, str, float]] = deque(maxlen=8)

        self._build_ui()
        self._refresh()

    # -- tier helpers (preserved) --------------------------------------------

    @property
    def _is_pro(self) -> bool:
        from core.subscription_manager import SubscriptionTier

        return self.subscription.current_tier in (SubscriptionTier.PRO, SubscriptionTier.PREMIUM)

    @property
    def _is_premium(self) -> bool:
        from core.subscription_manager import SubscriptionTier

        return self.subscription.current_tier == SubscriptionTier.PREMIUM

    @property
    def _can_change_execution_mode(self) -> bool:
        return self.subscription.has_feature("autonomous_mode")

    @property
    def _can_act(self) -> bool:
        """Whether Hearth may actually touch the system, or only suggest."""
        try:
            return bool(self.engine._can_execute_system_actions)
        except Exception:  # noqa: BLE001
            return False

    def _resolve_reduced_motion(self) -> bool:
        # Honor a reduced-motion preference if the theme dict carries one.
        val = self.theme.get("reduced_motion") if isinstance(self.theme, dict) else None
        return bool(val)

    def _c(self, key: str, fallback: str) -> str:
        return self.theme.get(key, fallback) if isinstance(self.theme, dict) else fallback

    # -- the warm room (painted, not a card stack) ---------------------------

    def paintEvent(self, _event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        bg = QColor(self._c("background", "#0F0F11"))
        p.fillRect(self.rect(), bg)

        # Warmth pools behind the Hearthstone at the top, where the engine's
        # presence sits — the room lit from its own hearth. When protection is
        # paused the pool dims with the coal (set in _apply_state).
        accent = QColor(self._c("accent", "#D9A05B"))
        cx = self.width() / 2
        top = QRadialGradient(cx, self.height() * 0.17, self.width() * 0.6)
        warm = QColor(accent)
        warm.setAlpha(self._room_alpha)
        top.setColorAt(0.0, warm)
        top.setColorAt(1.0, QColor(accent.red(), accent.green(), accent.blue(), 0))
        p.fillRect(self.rect(), top)
        p.end()

    # -- structure -----------------------------------------------------------

    def _build_ui(self) -> None:
        text = self._c("text", "#F2EDE6")
        muted = self._c("text_muted", "#A99B88")
        self._room_alpha = 30  # eased by _apply_state with the coal

        root = QVBoxLayout(self)
        root.setContentsMargins(40, 26, 40, 26)
        root.setSpacing(0)
        root.addStretch(1)

        column = QWidget()
        column.setMaximumWidth(640)
        col = QVBoxLayout(column)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(0)
        col.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # The Hearthstone — the engine's living presence.
        stone_row = QHBoxLayout()
        stone_row.addStretch()
        self._stone = Hearthlight(
            glow=_GLOW_WATCHING,
            reduced_motion=self._reduced_motion,
            transparent_bg=True,
        )
        self._stone.setFixedSize(150, 150)
        stone_row.addWidget(self._stone)
        stone_row.addStretch()
        col.addLayout(stone_row)
        col.addSpacing(18)

        # The one honest sentence — what Hearth is doing, in its own voice.
        self._sentence = QLabel("")
        self._sentence.setFont(serif_font(25))
        self._sentence.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._sentence.setWordWrap(True)
        self._sentence.setStyleSheet(f"color: {text}; background: transparent;")
        col.addWidget(self._sentence)
        col.addSpacing(24)

        # The one state-aware action — start or pause protection.
        action_row = QHBoxLayout()
        action_row.addStretch()
        self._primary = HearthButton("", role="primary", reduced_motion=self._reduced_motion)
        self._primary.setMinimumHeight(54)
        self._primary.clicked.connect(self._on_toggle_protection)
        action_row.addWidget(self._primary)
        action_row.addStretch()
        col.addLayout(action_row)
        col.addSpacing(8)

        # The quieter ways to help — recede as ghost side-doors, never a triad
        # of equal Bootstrap buttons. A user is in one state; these wait.
        doors_row = QHBoxLayout()
        doors_row.setSpacing(8)
        doors_row.addStretch()
        self._focus_door = HearthButton(
            "Guard a focus block", role="ghost", reduced_motion=self._reduced_motion
        )
        self._focus_door.clicked.connect(self._on_focus)
        self._ground_door = HearthButton(
            "Help me settle", role="ghost", reduced_motion=self._reduced_motion
        )
        self._ground_door.clicked.connect(self._on_ground)
        self._crisis_door = HearthButton(
            "When it's bad", role="crisis", reduced_motion=self._reduced_motion
        )
        self._crisis_door.clicked.connect(self._on_crisis)
        doors_row.addWidget(self._focus_door)
        doors_row.addWidget(self._ground_door)
        doors_row.addWidget(self._crisis_door)
        doors_row.addStretch()
        col.addLayout(doors_row)
        col.addSpacing(10)

        # When protection is banked, the contextual side-doors recede (Hearth
        # can't guard or settle while it isn't watching). Crisis is never gated.
        self._focus_fx = QGraphicsOpacityEffect(self._focus_door)
        self._focus_door.setGraphicsEffect(self._focus_fx)
        self._ground_fx = QGraphicsOpacityEffect(self._ground_door)
        self._ground_door.setGraphicsEffect(self._ground_fx)

        # The ambient, in-surface confirmation — a slow fade, never a modal.
        self._toast = QLabel("")
        self._toast.setFont(sans_font(13))
        self._toast.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._toast.setWordWrap(True)
        self._toast.setStyleSheet(
            f"color: {self._c('accent', '#D9A05B')}; background: transparent;"
        )
        self._toast_fx = QGraphicsOpacityEffect(self._toast)
        self._toast_fx.setOpacity(0.0)
        self._toast.setGraphicsEffect(self._toast_fx)
        self._toast_fade = QPropertyAnimation(self._toast_fx, b"opacity", self)
        self._toast_fade.setDuration(0 if self._reduced_motion else 600)
        self._toast_fade.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._toast_timer = QTimer(self)
        self._toast_timer.setSingleShot(True)
        self._toast_timer.timeout.connect(self._fade_toast_out)
        col.addWidget(self._toast)
        col.addSpacing(26)

        # The trust dial — "how much should I help?" — momentous, not a combo.
        trust_intro = QLabel("How much should I help?")
        trust_intro.setFont(sans_font(11, QFont.Weight.DemiBold))
        trust_intro.setAlignment(Qt.AlignmentFlag.AlignCenter)
        trust_intro.setStyleSheet(f"color: {muted}; background: transparent;")
        col.addWidget(trust_intro)
        col.addSpacing(8)

        cur_idx = self._current_mode_index()
        max_reach = 2 if self._can_change_execution_mode else 0
        self._trust = TrustDial(
            self.theme if isinstance(self.theme, dict) else {},
            selected=cur_idx,
            max_reachable=max_reach,
            reduced_motion=self._reduced_motion,
        )
        self._trust.selectionChanged.connect(self._on_trust_changed)
        col.addWidget(self._trust)
        col.addSpacing(6)

        # An honest one-liner under the dial — what the chosen step means, and
        # (free tier) the plain truth that acting on its own comes with Pro.
        self._trust_note = QLabel("")
        self._trust_note.setFont(sans_font(12))
        self._trust_note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._trust_note.setWordWrap(True)
        self._trust_note.setStyleSheet(f"color: {muted}; background: transparent;")
        col.addWidget(self._trust_note)
        col.addSpacing(30)

        # The recent-care ledger — the human-voiced record of what Hearth did,
        # replacing the rules table and the analytics logfile entirely.
        feed_intro = QLabel("Lately, in this room")
        feed_intro.setFont(sans_font(11, QFont.Weight.DemiBold))
        feed_intro.setAlignment(Qt.AlignmentFlag.AlignLeft)
        feed_intro.setStyleSheet(f"color: {muted}; background: transparent;")
        col.addWidget(feed_intro)
        col.addSpacing(8)

        self._feed_card = HearthCard(elevation=1, radius=18)
        self._feed_box = QVBoxLayout(self._feed_card)
        self._feed_box.setContentsMargins(22, 14, 22, 14)
        self._feed_box.setSpacing(0)
        col.addWidget(self._feed_card)

        column_row = QHBoxLayout()
        column_row.addStretch()
        column_row.addWidget(column)
        column_row.addStretch()
        root.addLayout(column_row)
        root.addStretch(2)

    # -- state -> room -------------------------------------------------------

    def _refresh(self) -> None:
        self._apply_state()
        self._refresh_trust_note()
        self._render_feed()

    def _current_mode_index(self) -> int:
        try:
            mode = self.config.active_profile.execution_mode
        except Exception:  # noqa: BLE001
            mode = ExecutionMode.SUGGESTIONS_ONLY
        for i, (_label, m) in enumerate(_TRUST_STEPS):
            if m == mode:
                return i
        return 0

    def _apply_state(self) -> None:
        """Drive the Hearthstone, the sentence, and the primary action from the
        engine's real state — the glow IS the engine state."""
        try:
            enabled = bool(self.engine.is_enabled)
        except Exception:  # noqa: BLE001
            enabled = False

        if enabled:
            self._stone.set_glow(_GLOW_WATCHING, animate=True)
            if not self._reduced_motion:
                self._stone.start_breathing()
            self._sentence.setText(self._watching_sentence())
            self._primary.setText("Step back for now")
            self._room_alpha = 32
            self._focus_door.setEnabled(True)
            self._ground_door.setEnabled(True)
            self._focus_fx.setOpacity(1.0)
            self._ground_fx.setOpacity(1.0)
        else:
            # Banked to a coal — you can see at a glance that protection is off.
            self._stone.stop_breathing()
            self._stone.set_glow(_GLOW_PAUSED, animate=True)
            self._sentence.setText(
                "I've stepped back. You're on your own for now —\n"
                "press when you want me watching again."
            )
            self._primary.setText("Start watching over me")
            self._room_alpha = 12
            self._focus_door.setEnabled(False)
            self._ground_door.setEnabled(False)
            self._focus_fx.setOpacity(0.4)
            self._ground_fx.setOpacity(0.4)
        self.update()

    def _watching_sentence(self) -> str:
        """The honest hero line — promoted from the old hidden _summarize()."""
        if not self._can_act:
            return (
                "I'm keeping an eye on things. Nothing's changed your setup —\n"
                "I'll suggest, not act, until you say so."
            )
        mode = self.config.active_profile.execution_mode
        if mode == ExecutionMode.SUGGESTIONS_ONLY:
            return (
                "I'm watching, quietly. I'll point things out when they'd help,\n"
                "and leave the deciding to you."
            )
        if mode == ExecutionMode.ASK_FIRST:
            return "I'm watching. I'll check with you before I change anything."
        return "I'm watching, and I'll handle the small things so you don't have to."

    def _refresh_trust_note(self) -> None:
        idx = self._trust.selected()
        if not self._can_change_execution_mode:
            self._trust_note.setText(
                "Right now I only suggest — letting me act on my own is part of Pro."
            )
            return
        note = {
            0: "I'll notice things and tell you. You make every call.",
            1: "I'll ask before I touch anything — a quiet nudge, then your yes.",
            2: "I'll quietly handle the small protective things myself.",
        }.get(idx, "")
        self._trust_note.setText(note)

    # -- the care ledger -----------------------------------------------------

    def _clear_feed(self) -> None:
        while self._feed_box.count():
            item = self._feed_box.takeAt(0)
            if item is None:
                continue
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()

    def _render_feed(self) -> None:
        self._clear_feed()
        theme = self.theme if isinstance(self.theme, dict) else {}

        if self._care:
            for sentence, when, mag in reversed(self._care):
                self._feed_box.addWidget(CareRow(theme, sentence, when, mag))
            return

        # Empty: a calm invitation, plus an honest note of what Hearth watches
        # for — drawn from the real rule set, in plain language, not a table.
        invite = QLabel(self._empty_invitation())
        invite.setFont(serif_font(15))
        invite.setWordWrap(True)
        invite.setStyleSheet(f"color: {self._c('text', '#F2EDE6')}; background: transparent;")
        self._feed_box.addWidget(invite)

        watching = self._watch_summary()
        if watching:
            sub = QLabel(watching)
            sub.setFont(sans_font(12))
            sub.setWordWrap(True)
            sub.setStyleSheet(
                f"color: {self._c('text_muted', '#A99B88')}; background: transparent;"
            )
            self._feed_box.addSpacing(8)
            self._feed_box.addWidget(sub)

    def _empty_invitation(self) -> str:
        try:
            enabled = bool(self.engine.is_enabled)
        except Exception:  # noqa: BLE001
            enabled = False
        if enabled:
            return (
                "Nothing yet today. When I help, you'll see it here — and you can undo any of it."
            )
        return "We haven't started yet. When you're ready, I'll begin keeping watch."

    def _watch_summary(self) -> str:
        try:
            rules = self.engine.list_rules()
        except Exception:  # noqa: BLE001
            rules = []
        active = [r for r in rules if r.get("enabled") and r.get("in_profile", True)]
        n = len(active)
        if n == 0:
            return ""
        verb = "suggest a hand with" if not self._can_act else "step in for"
        return f"I'm set up to {verb} {n} kind{'s' if n != 1 else ''} of moment when they come up."

    def _note_care(self, sentence: str, magnitude: float = 0.6) -> None:
        """Record a real act of care and re-render the ledger."""
        when = datetime.now().strftime("%I:%M%p").lstrip("0").lower()
        self._care.append((sentence, when, magnitude))
        self._render_feed()

    # -- ambient feedback ----------------------------------------------------

    def _show_toast(self, text: str) -> None:
        """A calm in-surface fade — never a QMessageBox in a tender room."""
        self._toast.setText(text)
        self._toast_timer.stop()
        if self._reduced_motion:
            self._toast_fx.setOpacity(1.0)
        else:
            self._toast_fade.stop()
            self._toast_fade.setStartValue(self._toast_fx.opacity())
            self._toast_fade.setEndValue(1.0)
            self._toast_fade.start()
        self._toast_timer.start(6000)

    def _fade_toast_out(self) -> None:
        if self._reduced_motion:
            self._toast_fx.setOpacity(0.0)
            return
        self._toast_fade.stop()
        self._toast_fade.setStartValue(self._toast_fx.opacity())
        self._toast_fade.setEndValue(0.0)
        self._toast_fade.start()

    # -- event handlers (engine wiring preserved) ----------------------------

    def _on_toggle_protection(self) -> None:
        if self.engine.is_enabled:
            self.engine.disable()
            self._show_toast("I've banked the coals. Tap when you want me back.")
            self._note_care("Stepped back when you asked. I'll wait.", magnitude=0.4)
            self.protection_changed.emit(False)
        else:
            self.engine.enable()
            self._show_toast("I'm back, and watching over things.")
            self._note_care("Started keeping watch.", magnitude=0.7)
            self.protection_changed.emit(True)
        self._apply_state()

    def _on_focus(self) -> None:
        focus = self.engine.focus
        if focus.state.name == "ACTIVE":
            focus.deactivate()
            self._show_toast("Focus is off. The room opens back up.")
            self._note_care("Let the focus block go when you were done.", magnitude=0.5)
        else:
            self.engine.manual_focus()
            if self._can_act:
                self._show_toast("Focus is on. I've quieted the noise and I'm guarding this block.")
                self._note_care("Quieted the noise and guarded a focus block.", magnitude=0.8)
            else:
                self._show_toast(
                    "Focus is set. On this plan I'll nudge rather than close things for you."
                )
                self._note_care("Suggested a focus block — yours to act on.", magnitude=0.5)

    def _on_ground(self) -> None:
        self.engine.manual_grounding()
        if self._can_act:
            self._show_toast("Slowing things down. I've eased the screen and hushed the apps.")
            self._note_care("Eased the screen and hushed things to help you settle.", magnitude=0.7)
        else:
            self._show_toast(
                "I'm here. On this plan I'll suggest ways to settle rather than change your setup."
            )
            self._note_care("Suggested some ways to settle.", magnitude=0.5)

    def _on_crisis(self) -> None:
        self.engine.manual_crisis()
        if self._can_act:
            self._show_toast(
                "I've narrowed everything down to you — dimmed the rest, cleared the clamor."
            )
            self._note_care("Drew the room in close around you.", magnitude=1.0)
        else:
            self._show_toast(
                "I'm right here with you. On this plan I'll point you toward help, gently."
            )
            self._note_care("Stayed close and pointed toward help.", magnitude=0.9)

    def _on_trust_changed(self, idx: int) -> None:
        if not self._can_change_execution_mode:
            # Snap back honestly — the higher steps aren't reachable on this plan.
            self._trust.set_selected(self._current_mode_index(), emit=False)
            self._refresh_trust_note()
            return
        mode = _TRUST_STEPS[idx][1]
        try:
            self.config.set_execution_mode(self.config.active_profile_id, mode)
        except Exception as exc:  # noqa: BLE001
            logger.debug("set_execution_mode failed: %s", exc)
        self._refresh_trust_note()
        # The hero sentence reflects the new trust level if we're watching.
        if self.engine.is_enabled:
            self._sentence.setText(self._watching_sentence())

    # -- public API ----------------------------------------------------------

    def save_state(self) -> None:
        """Persist on close — the config owns its own save; called for parity."""
        with contextlib.suppress(Exception):
            self.config.save()
