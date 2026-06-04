"""HearthToday — the reimagined "Today" doorway.

Replaces the eight-gray-card status board (see docs/design/audit_02) with a warm,
near-empty room: the Hearthlight encoding your energy, one serif sentence Hearth says
to you, one primary door, and a few receding side-doors. It re-composes itself to your
state via gui.state_engine — the moment the thesis becomes felt (docs/design/VISION.md).

Drop-in for DashboardWidget: same constructor kwargs and the same quick-action signals,
plus navigate_requested(str) for arbitrary rooms.
"""

from __future__ import annotations

import logging
from typing import Any

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QRadialGradient
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from gui import state_engine
from gui.components.hearth_surfaces import HearthButton
from gui.components.hearthlight import Hearthlight
from gui.components.state_controls import sans_font, serif_font

logger = logging.getLogger(__name__)


class HearthToday(QWidget):
    """The warm doorway. One ember, one sentence, one door."""

    # Legacy quick-action signals (kept for compatibility with existing wiring)
    mood_track_requested = pyqtSignal()
    task_add_requested = pyqtSignal()
    breathing_requested = pyqtSignal()
    journal_requested = pyqtSignal()
    stats_requested = pyqtSignal()
    # The general one: navigate to any room by name.
    navigate_requested = pyqtSignal(str)

    def __init__(
        self,
        theme: dict[str, str] | None = None,
        task_manager: Any = None,
        profile_manager: Any = None,
        mood_manager: Any = None,
        energy_predictor: Any = None,
        gamification_manager: Any = None,
        wellness_orchestrator: Any = None,
        subscription_manager: Any = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._theme = theme or {}
        self._task_manager = task_manager
        self._profile_manager = profile_manager
        self._mood_manager = mood_manager
        self._wellness_orchestrator = wellness_orchestrator
        self._bg = QColor(self._theme.get("background", "#0F0F11"))
        self._door_buttons: list[HearthButton] = []

        self._build_ui()
        self.refresh()

        # A gentle idle re-read so the room can warm/cool as the day moves.
        self._timer = QTimer(self)
        self._timer.setInterval(60_000)
        self._timer.timeout.connect(self.refresh)
        self._timer.start()

    # -- painting: the warm room ------------------------------------------
    def paintEvent(self, _event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), self._bg)
        # A faint warmth pooled at the top, where the ember sits.
        cx = self.width() / 2
        grad = QRadialGradient(cx, self.height() * 0.16, self.width() * 0.55)
        warm = QColor(self._theme.get("accent", "#D9A05B"))
        warm.setAlpha(26)
        grad.setColorAt(0.0, warm)
        warm2 = QColor(warm)
        warm2.setAlpha(0)
        grad.setColorAt(1.0, warm2)
        p.fillRect(self.rect(), grad)
        p.end()

    # -- structure --------------------------------------------------------
    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addStretch(3)

        # The ember
        ember_row = QHBoxLayout()
        ember_row.addStretch()
        # transparent_bg so the ember composites over our warm room with no seam.
        self._ember = Hearthlight(transparent_bg=True)
        self._ember.setFixedSize(150, 150)
        ember_row.addWidget(self._ember)
        ember_row.addStretch()
        root.addLayout(ember_row)
        root.addSpacing(28)

        # The one true sentence (two serif lines)
        self._line1 = QLabel("")
        self._line1.setFont(serif_font(30))
        self._line1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._line1.setStyleSheet(
            f"color: {self._theme.get('text', '#F2EDE6')}; background: transparent;"
        )
        root.addWidget(self._line1)

        self._line2 = QLabel("")
        self._line2.setFont(serif_font(26))
        self._line2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._line2.setWordWrap(True)
        self._line2.setStyleSheet(
            f"color: {self._theme.get('accent', '#D9A05B')}; background: transparent;"
        )
        root.addWidget(self._line2)
        root.addSpacing(30)

        # The one door
        door_row = QHBoxLayout()
        door_row.addStretch()
        self._primary = HearthButton("", role="primary")
        self._primary.clicked.connect(self._on_primary)
        door_row.addWidget(self._primary)
        door_row.addStretch()
        root.addLayout(door_row)
        root.addSpacing(8)

        # The receding side-doors
        self._doors_box = QVBoxLayout()
        self._doors_box.setSpacing(2)
        doors_wrap = QHBoxLayout()
        doors_wrap.addStretch()
        doors_inner = QWidget()
        doors_inner.setLayout(self._doors_box)
        doors_wrap.addWidget(doors_inner)
        doors_wrap.addStretch()
        root.addLayout(doors_wrap)

        root.addSpacing(26)

        # The quiet caption
        self._caption = QLabel("")
        self._caption.setFont(sans_font(12))
        self._caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._caption.setStyleSheet(
            f"color: {self._theme.get('text_muted', '#8E8E93')}; background: transparent;"
        )
        root.addWidget(self._caption)

        root.addStretch(4)

    # -- state → room -----------------------------------------------------
    def refresh(self) -> None:
        snapshot = None
        if self._wellness_orchestrator is not None:
            try:
                snapshot = self._wellness_orchestrator.snapshot()
            except Exception as exc:  # noqa: BLE001
                logger.debug("Today snapshot unavailable: %s", exc)

        pending = self._pending_task_count()
        name = self._user_name()
        state = state_engine.compute_state(snapshot, self._profile_manager, pending)
        comp = state_engine.compose(state, name, pending)

        self._ember.set_glow(comp.glow)
        self._line1.setText(comp.line1)
        self._line2.setText(comp.line2)
        self._caption.setText(comp.caption)
        self._primary.setText(comp.primary_label)
        self._primary_tab = comp.primary_tab
        self._render_doors(comp.doors)

    def _render_doors(self, doors: list[tuple[str, str]]) -> None:
        while self._door_buttons:
            btn = self._door_buttons.pop()
            self._doors_box.removeWidget(btn)
            btn.deleteLater()
        for label, tab in doors:
            btn = HearthButton(label, role="ghost")
            btn.clicked.connect(lambda _checked=False, t=tab: self._go(t))
            self._doors_box.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
            self._door_buttons.append(btn)

    # -- helpers ----------------------------------------------------------
    def _pending_task_count(self) -> int:
        tm = self._task_manager
        if tm is None:
            return 0
        try:
            tasks = getattr(tm, "tasks", None)
            if tasks is not None:
                return sum(1 for t in tasks if not getattr(t, "completed", False))
        except Exception:  # noqa: BLE001
            pass
        return 0

    def _user_name(self) -> str:
        pm = self._profile_manager
        try:
            prof = getattr(pm, "current_profile", None)
            if prof is not None:
                return getattr(prof, "name", "") or ""
        except Exception:  # noqa: BLE001
            pass
        return ""

    def _on_primary(self) -> None:
        self._go(getattr(self, "_primary_tab", "task_manager"))

    def _go(self, tab: str) -> None:
        self.navigate_requested.emit(tab)
        # Mirror to the legacy signals so older wiring keeps working.
        legacy = {
            "mood_tracker": self.mood_track_requested,
            "task_manager": self.task_add_requested,
            "breathing": self.breathing_requested,
            "journaling": self.journal_requested,
        }.get(tab)
        if legacy is not None:
            legacy.emit()
