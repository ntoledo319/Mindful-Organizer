"""
Breathe — Hearth's signature slow-down room.

A person reaches this surface in acute dysregulation: a panic spike, a racing
chest, the moment before a meltdown. The screen must *become* the pacer. So
there is almost nothing here to read or operate — a dim warm room, the
:class:`BreathOrb` as its only light, one quiet serif line, and a single calm
affordance to begin or stop. The breath is the screen; setup is a whisper
(docs/design/audit_04, the BreatheScreen prototype).

The orb owns the rhythm. Its phase durations come from the chosen pattern
(box breathing by default); the widget only starts it, stops it, counts the
cycles it completes, and records the session the same way it always has —
``create_session(..., mood_before=...)`` on begin, ``complete_session(...,
mood_after=...)`` on stop. Reduced motion is honoured by the orb itself.
"""

from __future__ import annotations

import logging
from typing import Any

from PyQt6.QtCore import QRectF, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QFontDatabase, QPainter, QRadialGradient
from PyQt6.QtWidgets import QWidget

from gui.components.breath_orb import BreathOrb
from gui.components.hearth_surfaces import HearthButton

logger = logging.getLogger(__name__)


# The reading serif — the opening line is language, not a control. Same stack
# the orb and surfaces speak in, so the room has one voice.
_SERIF_STACK = ["Charter", "Cochin", "Baskerville", "Georgia"]


def _pick(stack: list[str]) -> str:
    available = set(QFontDatabase.families())
    for fam in stack:
        if fam in available:
            return fam
    return stack[-1]


def _serif(size: int, weight: QFont.Weight = QFont.Weight.Normal) -> QFont:
    f = QFont(_pick(_SERIF_STACK), size)
    f.setWeight(weight)
    f.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    return f


def _ms(seconds: float) -> int:
    return max(0, int(round(seconds * 1000)))


class BreathingWidget(QWidget):
    """The breathing room. One orb of light, one line, one calm affordance."""

    session_completed = pyqtSignal(dict)

    def __init__(
        self,
        theme: dict[str, str],
        breathing_manager: Any = None,
        profile_manager: Any = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._theme = theme or {}
        self._breathing_manager = breathing_manager
        self._profile_manager = profile_manager

        # Room colours, read from the theme (never hardcoded).
        self._bg = QColor(self._theme.get("background", "#0F0F11"))
        self._bg_low = self._dim(self._bg, 0.82)
        self._accent = QColor(self._theme.get("accent", "#D9A05B"))
        self._text = QColor(self._theme.get("text", "#F2EDE6"))
        self._text_muted = QColor(self._theme.get("text_muted", "#A99B88"))
        self._reduced_motion = bool(self._theme.get("reduced_motion", False))

        # Session bookkeeping — preserved persistence, kept invisible.
        self._running: bool = False
        self._session: Any = None
        self._cycles_completed: int = 0
        self._etype: Any = None
        # Mood capture is kept (the manager still records it) but never gates
        # the breath: it rests at a neutral middle and the user is never asked
        # to quantify themselves before being helped (audit_04 §3.1).
        self._mood_before: int = 5
        self._mood_after: int = 5

        # The chosen pattern decides the orb's rhythm. Default: box breathing.
        self._phases = self._resolve_phases()

        self._build_ui()

    # ------------------------------------------------------------------ colour
    @staticmethod
    def _dim(c: QColor, factor: float) -> QColor:
        """A darker shade of ``c`` for the room's receding edges."""
        return QColor(
            int(c.red() * factor),
            int(c.green() * factor),
            int(c.blue() * factor),
        )

    # ------------------------------------------------------------------ rhythm
    def _resolve_phases(self) -> dict[str, int]:
        """Phase durations (ms) for the orb, drawn from the chosen pattern.

        Falls back to box breathing (4/4/4/4) when no manager is present, so the
        room always breathes even with nothing wired behind it.
        """
        durations = {"inhale": 4.0, "hold_in": 4.0, "exhale": 4.0, "hold_out": 4.0}
        bm = self._breathing_manager
        if bm is not None and hasattr(bm, "list_exercises"):
            try:
                exercises = bm.list_exercises()
                if exercises:
                    ex = exercises[0]
                    self._etype = ex.exercise_type
                    found = {"inhale": 0.0, "hold_in": 0.0, "exhale": 0.0, "hold_out": 0.0}
                    for phase in ex.phases:
                        key = (
                            phase.phase.value if hasattr(phase.phase, "value") else str(phase.phase)
                        )
                        if key in found:
                            found[key] = float(phase.duration_seconds)
                    # A pattern must at least breathe in and out.
                    if found["inhale"] > 0 and found["exhale"] > 0:
                        durations = found
            except (AttributeError, TypeError, IndexError) as exc:
                logger.debug("Falling back to box breathing: %s", exc)
        return {k: _ms(v) for k, v in durations.items()}

    # ---------------------------------------------------------------------- UI
    def _build_ui(self) -> None:
        # A quiet opening line, set high and small in the serif. It is part of
        # the room (a held instruction), not a control, so it is painted —
        # see paintEvent — rather than laid out.
        self._opening = "Let's slow this down together."

        # The orb — the hero. Composited over the painted room (no opaque
        # rectangle, so no seam). It owns the breath and the phase word.
        self._orb = BreathOrb(
            self,
            inhale=self._phases["inhale"],
            hold_in=self._phases["hold_in"],
            exhale=self._phases["exhale"],
            hold_out=self._phases["hold_out"],
            reduced_motion=self._reduced_motion,
            transparent_bg=True,
        )
        self._orb.cycle_completed.connect(self._on_cycle)

        # The single calm affordance — a ghost side-door, low and centred. It
        # subordinates to the orb; it never shouts. Reads "Begin" at rest,
        # "I'm steadier now" while breathing.
        self._toggle = HearthButton("Begin", role="ghost", reduced_motion=self._reduced_motion)
        self._toggle.setMinimumHeight(40)
        self._toggle.setMinimumWidth(220)
        self._toggle.clicked.connect(self._on_toggle)

    # ------------------------------------------------------------------- paint
    def paintEvent(self, _event: Any) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        rect = QRectF(self.rect())

        # 1) Ground — warm near-black from the theme.
        p.fillRect(rect, self._bg)

        # 2) Corner vignette — the room darkens toward its edges so the breath
        #    at the centre feels held. Wide radial, extra stops for a smooth
        #    falloff with no concentric banding.
        cx, cy = rect.center().x(), rect.center().y()
        far = (rect.width() ** 2 + rect.height() ** 2) ** 0.5 / 2.0 or 1.0
        vig = QRadialGradient(cx, cy, far)
        for stop, frac in ((0.0, 0.0), (0.45, 0.0), (0.70, 0.18), (0.86, 0.5), (1.0, 1.0)):
            c = QColor(self._bg_low)
            c.setAlpha(int(255 * frac))
            vig.setColorAt(stop, c)
        p.fillRect(rect, vig)

        # 3) The opening line — serif, faint, riding high above the orb. The
        #    quietest readable tone, so the breath (not the words) is the focus.
        p.setFont(_serif(20, QFont.Weight.Normal))
        col = QColor(self._text_muted)
        col.setAlpha(190)
        p.setPen(col)
        top_rect = QRectF(0, self.height() * 0.12, self.width(), self.height() * 0.08)
        p.drawText(
            top_rect,
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
            self._opening,
        )
        p.end()

    def resizeEvent(self, event: Any) -> None:  # noqa: N802
        super().resizeEvent(event)
        w, h = self.width(), self.height()

        # The orb fills the central heart of the room — large, generous, with
        # air on every side for its radiance and lagging bloom to dissolve into
        # the dark instead of clipping. Its own geometry keeps the core clear of
        # the box, so a wide box just means more room for the light to spread.
        ow = int(min(w * 0.94, h * 1.55))
        oh = int(h * 0.82)
        ox = (w - ow) // 2
        oy = int(h * 0.10)
        self._orb.setGeometry(ox, oy, ow, oh)

        # The affordance — low, centred, barely there.
        dw, dh = 240, 40
        self._toggle.setGeometry((w - dw) // 2, int(h * 0.90), dw, dh)

    # ---------------------------------------------------------------- controls
    def _on_toggle(self) -> None:
        if self._running:
            self._stop_session()
        else:
            self._start_session()

    # -- idle: the room is alive before anyone presses anything ------------
    def showEvent(self, event: Any) -> None:  # noqa: N802
        super().showEvent(event)
        # The resting state is not a dead coal labelled "Ready" — the orb
        # breathes slowly on its own the moment you enter the room, so a person
        # in panic can simply fall into the rhythm without operating anything
        # (audit_04 §3.2). Pressing "Begin" only starts *recording* a session.
        self._orb.start()

    def hideEvent(self, event: Any) -> None:  # noqa: N802
        super().hideEvent(event)
        # Leaving the room: close out any recorded session and let the orb rest.
        if self._running:
            self._stop_session()
        self._orb.stop()

    def _start_session(self) -> None:
        if self._running:
            return
        self._running = True
        self._cycles_completed = 0

        # Record the session the same way the widget always has. Mood-before is
        # the neutral default — we never interrogate someone before helping them.
        self._session = None
        bm = self._breathing_manager
        if bm is not None and self._etype is not None and hasattr(bm, "create_session"):
            try:
                self._session = bm.create_session(self._etype, mood_before=self._mood_before)
            except (AttributeError, TypeError, ValueError) as exc:
                logger.debug("Could not create breathing session: %s", exc)
                self._session = None

        self._toggle.setText("I'm steadier now")
        # The orb is already breathing (idle since the room opened); restart it
        # so the recorded session's cycle count begins from a clean inhale.
        self._orb.start()

    def _stop_session(self) -> None:
        if not self._running:
            return
        self._running = False
        # The orb keeps breathing — leaving a session does not snuff the light;
        # the room simply returns to its calm idle rhythm.
        self._orb.start()
        self._toggle.setText("Begin")

        # Record the session — same persistence path as before.
        if self._session is not None and self._breathing_manager is not None:
            try:
                self._breathing_manager.complete_session(
                    self._session,
                    self._cycles_completed,
                    mood_after=self._mood_after,
                )
                self.session_completed.emit(
                    {
                        "exercise": getattr(self._etype, "value", str(self._etype)),
                        "cycles": self._cycles_completed,
                        "mood_before": self._mood_before,
                        "mood_after": self._mood_after,
                    }
                )
            except (AttributeError, TypeError) as exc:
                logger.debug("Breathing manager session error: %s", exc)
        self._session = None

    def _on_cycle(self) -> None:
        # Only breaths taken inside a recorded session count; the idle rhythm
        # that keeps the room alive does not inflate anyone's history.
        if self._running:
            self._cycles_completed += 1

    # ------------------------------------------------------------------- theme
    def apply_theme(self, theme: dict[str, str]) -> None:
        self._theme = theme or {}
        self._bg = QColor(self._theme.get("background", "#0F0F11"))
        self._bg_low = self._dim(self._bg, 0.82)
        self._accent = QColor(self._theme.get("accent", "#D9A05B"))
        self._text = QColor(self._theme.get("text", "#F2EDE6"))
        self._text_muted = QColor(self._theme.get("text_muted", "#A99B88"))
        self.update()
