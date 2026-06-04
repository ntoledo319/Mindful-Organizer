"""
BreathOrb — Hearth's immersive breathing guide.

A custom-painted breathing companion that replaces the dead static "Ready"
circle. The orb *expands on inhale, holds, contracts on exhale, holds* —
a true box-breathing rhythm (default 4/4/4/4), driven by a single eased
``expansion`` property chained through a ``QSequentialAnimationGroup`` with
real pauses for the holds.

Two painted bodies make it feel alive instead of mechanical:
  * the **core** — a warm hearthlight orb (``QRadialGradient``) that *brightens*
    as it fills with breath and *dims* as it empties, so you can pace your
    breathing by light alone, without reading a number;
  * a **lagging halo** — a softer, larger ember bloom that trails the core a
    beat behind (its own slower-following property), so the breath looks like
    warmth spreading through air rather than a circle being scaled.

The phase word ("Breathe in", "Hold", "Breathe out", "Hold") is set in the
reading serif and **cross-fades** between phases — it never snaps.

``reduced_motion`` is honoured with a calm static fallback: a steady,
mid-filled glow and a held instruction, with no animation running.

The local ``_PALETTE`` dict is a stand-in for the Onyx tokens and is to be
replaced by ``ResolvedTokens`` from the State Engine once that lands.
"""

from __future__ import annotations

from PyQt6.QtCore import (
    QEasingCurve,
    QPauseAnimation,
    QPointF,
    QPropertyAnimation,
    QSequentialAnimationGroup,
    Qt,
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
from PyQt6.QtWidgets import QWidget

# --- to be replaced by ResolvedTokens (Onyx, the warm dark default) ----------
_PALETTE = {
    "bg": "#0F0F11",  # warm near-black canvas (never pure black)
    "surface": "#18181A",
    "text": "#F2EDE6",  # warm off-white
    "text_muted": "#A99B88",  # clears AA 4.5:1 on surface
    "accent": "#D9A05B",  # hearthlight — warm amber/ember
    "ember": "#C2703D",  # deeper ember (exhale / halo edge)
    "ember_deep": "#8C4A28",  # the cooling edge of the bloom
}

# Reading serif (greetings, prompts, the one-true-sentence). Bundled faces
# arrive later; these are the warm macOS faces used for the prototype.
_SERIF_STACK = ["Charter", "Cochin", "Baskerville", "Georgia", "serif"]


def _serif(size: int, *, weight: QFont.Weight = QFont.Weight.Normal) -> QFont:
    font = QFont()
    font.setFamilies(_SERIF_STACK)
    font.setPointSize(size)
    font.setWeight(weight)
    return font


def _mix(a: QColor, b: QColor, t: float) -> QColor:
    """Linear blend of two colours, t in [0, 1] (0 = a, 1 = b)."""
    t = max(0.0, min(1.0, t))
    return QColor(
        round(a.red() + (b.red() - a.red()) * t),
        round(a.green() + (b.green() - a.green()) * t),
        round(a.blue() + (b.blue() - a.blue()) * t),
        round(a.alpha() + (b.alpha() - a.alpha()) * t),
    )


def _rgba(c: QColor, alpha: int) -> QColor:
    """A copy of ``c`` with its alpha set (clamped to 0..255)."""
    return QColor(c.red(), c.green(), c.blue(), max(0, min(255, int(alpha))))


class BreathOrb(QWidget):
    """An immersive, hypnotic breathing guide.

    Parameters
    ----------
    inhale, hold_in, exhale, hold_out:
        Phase durations in milliseconds. Defaults are box-breathing (4s each).
        A hold of ``0`` collapses that pause cleanly.
    reduced_motion:
        When ``True``, no animation runs: a calm, mid-filled static orb is
        painted with a held instruction.
    """

    cycle_completed = pyqtSignal()
    phase_changed = pyqtSignal(str)

    PHASE_INHALE = "inhale"
    PHASE_HOLD_IN = "hold_in"
    PHASE_EXHALE = "exhale"
    PHASE_HOLD_OUT = "hold_out"

    _PHASE_WORDS = {
        PHASE_INHALE: "Breathe in",
        PHASE_HOLD_IN: "Hold",
        PHASE_EXHALE: "Breathe out",
        PHASE_HOLD_OUT: "Hold",
    }

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        inhale: int = 4000,
        hold_in: int = 4000,
        exhale: int = 4000,
        hold_out: int = 4000,
        reduced_motion: bool = False,
        transparent_bg: bool = False,
    ) -> None:
        super().__init__(parent)

        self._inhale = inhale
        self._hold_in = hold_in
        self._exhale = exhale
        self._hold_out = hold_out
        self._reduced_motion = reduced_motion
        # When embedded in a screen that paints its own room, composite the orb
        # over it (no opaque background rectangle, so no hard seam).
        self._transparent_bg = transparent_bg
        if transparent_bg:
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        # core fullness: 0.0 = fully exhaled (small, dim), 1.0 = full of breath.
        # The static fallback rests at a calm, warm mid-fill — present, not a
        # dying coal.
        self._expansion = 0.42 if reduced_motion else 0.0
        # the halo follows the core a beat behind; its own value lags.
        self._halo = self._expansion
        # phase-word cross-fade opacity (the *incoming* word).
        self._word_opacity = 1.0

        self._phase = self.PHASE_INHALE
        self._word_current = "Settle in" if reduced_motion else self._PHASE_WORDS[self.PHASE_INHALE]
        self._word_outgoing = ""
        self._sub = "" if not reduced_motion else "Let your breath find its own pace."

        self._group: QSequentialAnimationGroup | None = None
        self._word_anim: QPropertyAnimation | None = None
        self._halo_anim: QPropertyAnimation | None = None

        self.setMinimumSize(360, 360)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)

    # ------------------------------------------------------------------ props
    def _get_expansion(self) -> float:
        return self._expansion

    def _set_expansion(self, value: float) -> None:
        self._expansion = value
        # The halo eases toward the core but always trails it, so the bloom
        # appears to spread outward through the air a moment after the breath.
        self._halo += (value - self._halo) * 0.18
        self.update()

    expansion = pyqtProperty(float, _get_expansion, _set_expansion)

    def _get_word_opacity(self) -> float:
        return self._word_opacity

    def _set_word_opacity(self, value: float) -> None:
        self._word_opacity = value
        self.update()

    word_opacity = pyqtProperty(float, _get_word_opacity, _set_word_opacity)

    # --------------------------------------------------------------- controls
    def start(self) -> None:
        """Begin the breathing cycle (looping). No-op under reduced motion."""
        if self._reduced_motion:
            self.update()
            return
        self.stop()
        self._build_cycle()
        if self._group is not None:
            self._group.start()

    def stop(self) -> None:
        if self._group is not None:
            self._group.stop()
            self._group.deleteLater()
            self._group = None

    def set_reduced_motion(self, enabled: bool) -> None:
        self._reduced_motion = enabled
        if enabled:
            self.stop()
            self._expansion = 0.42
            self._halo = 0.42
            self._word_current = "Settle in"
            self._sub = "Let your breath find its own pace."
            self.update()
        else:
            self._sub = ""

    # ------------------------------------------------------------- animation
    def _ease_segment(
        self, start: float, end: float, duration: int, curve: QEasingCurve.Type
    ) -> QPropertyAnimation:
        anim = QPropertyAnimation(self, b"expansion")
        anim.setStartValue(start)
        anim.setEndValue(end)
        anim.setDuration(max(1, duration))
        anim.setEasingCurve(curve)
        return anim

    def _build_cycle(self) -> None:
        group = QSequentialAnimationGroup(self)

        # Inhale: rise into fullness on a slow sine (no abrupt start/stop).
        inhale = self._ease_segment(0.0, 1.0, self._inhale, QEasingCurve.Type.InOutSine)
        inhale.stateChanged.connect(lambda *_: self._enter_phase(self.PHASE_INHALE))
        group.addAnimation(inhale)

        # Hold full — a *true* pause, the lungs stay full.
        if self._hold_in > 0:
            hold_in = QPauseAnimation(self._hold_in)
            hold_in.stateChanged.connect(
                lambda state, *_: self._on_pause(state, self.PHASE_HOLD_IN)
            )
            group.addAnimation(hold_in)

        # Exhale: release back down, dimming as it empties.
        exhale = self._ease_segment(1.0, 0.0, self._exhale, QEasingCurve.Type.InOutSine)
        exhale.stateChanged.connect(lambda *_: self._enter_phase(self.PHASE_EXHALE))
        group.addAnimation(exhale)

        # Hold empty — the still point between breaths.
        if self._hold_out > 0:
            hold_out = QPauseAnimation(self._hold_out)
            hold_out.stateChanged.connect(
                lambda state, *_: self._on_pause(state, self.PHASE_HOLD_OUT)
            )
            group.addAnimation(hold_out)

        group.setLoopCount(-1)
        group.currentLoopChanged.connect(lambda *_: self.cycle_completed.emit())
        self._group = group

    def _on_pause(self, state, phase: str) -> None:
        # QPauseAnimation flips to Running at the start of the hold.
        if state == QPropertyAnimation.State.Running:
            self._enter_phase(phase)

    def _enter_phase(self, phase: str) -> None:
        if phase == self._phase:
            return
        self._phase = phase
        self.phase_changed.emit(phase)
        self._crossfade_word(self._PHASE_WORDS[phase])

    # ------------------------------------------------------------- word fade
    def _crossfade_word(self, new_word: str) -> None:
        if new_word == self._word_current:
            return
        if self._reduced_motion:
            self._word_current = new_word
            self.update()
            return
        self._word_outgoing = self._word_current
        self._word_current = new_word
        self._word_opacity = 0.0

        if self._word_anim is not None:
            self._word_anim.stop()
        anim = QPropertyAnimation(self, b"word_opacity")
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        # Cross-fade pace tracks the phase length but stays gentle.
        anim.setDuration(min(900, max(450, self._inhale // 4)))
        anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        anim.finished.connect(self._clear_outgoing_word)
        self._word_anim = anim
        anim.start()

    def _clear_outgoing_word(self) -> None:
        self._word_outgoing = ""
        self._word_opacity = 1.0
        self.update()

    # ------------------------------------------------------------- painting
    def paintEvent(self, event) -> None:  # noqa: N802 (Qt naming)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        w = self.width()
        h = self.height()
        cx = w / 2.0
        # Sit the orb a touch above centre to leave room for the word beneath.
        cy = h * 0.42

        # Warm near-black ground — fill the whole canvas so the orb has air.
        # When embedded transparently, skip it so the surrounding painted room
        # shows through and there is no rectangular seam around the orb.
        if not self._transparent_bg:
            painter.fillRect(self.rect(), QColor(_PALETTE["bg"]))
        painter.setPen(Qt.PenStyle.NoPen)

        # The orb's reach: a low coal when empty, a generous warm body when
        # full — but kept clear of the edges so the breath always has air.
        base = min(w, h)
        min_r = base * 0.135
        max_r = base * 0.275
        core_r = min_r + (max_r - min_r) * self._expansion

        accent = QColor(_PALETTE["accent"])
        ember = QColor(_PALETTE["ember"])
        ember_deep = QColor(_PALETTE["ember_deep"])
        white = QColor("#FBEAD0")  # warm white, never clinical

        # Brightness rides the breath: a banked coal when empty, luminous when
        # full. Eased so neither extreme is harsh.
        e = self._expansion
        glow = 0.30 + 0.70 * (e * e * (3 - 2 * e))  # smoothstep on fullness

        center = QPointF(cx, cy)

        # --- 1. Ambient radiance: the orb lights the room it sits in --------
        # A very wide, very soft amber wash that spills into the dark canvas,
        # so the orb reads as a *source of light*, not a pasted disc.
        amb_r = core_r * 3.4
        amb = QRadialGradient(center, amb_r)
        amb_a = int(46 * glow)
        amb.setColorAt(0.0, _rgba(_mix(accent, ember, 0.4), amb_a))
        amb.setColorAt(0.4, _rgba(ember, int(amb_a * 0.5)))
        amb.setColorAt(1.0, _rgba(ember_deep, 0))
        painter.setBrush(amb)
        painter.drawEllipse(center, amb_r, amb_r)

        # --- 2. The lagging bloom: warmth spreading through the air ----------
        # Driven by the trailing `_halo` value, so it follows the breath a beat
        # behind — expanding after the inhale, lingering after the exhale.
        halo_r = (min_r + (max_r - min_r) * self._halo) * 1.85
        halo_glow = 0.30 + 0.70 * self._halo
        halo = QRadialGradient(center, halo_r)
        halo_a = int(120 * halo_glow)
        halo.setColorAt(0.0, _rgba(_mix(accent, white, 0.25), halo_a))
        halo.setColorAt(0.45, _rgba(_mix(accent, ember, 0.35), int(halo_a * 0.55)))
        halo.setColorAt(0.8, _rgba(ember, int(halo_a * 0.18)))
        halo.setColorAt(1.0, _rgba(ember_deep, 0))
        painter.setBrush(halo)
        painter.drawEllipse(center, halo_r, halo_r)

        # --- 3. The core ember: a body of light with a dissolving edge ------
        # The gradient never hits a hard rim — it fades to zero alpha past the
        # nominal radius, so there is no billiard-ball circumference.
        soft_r = core_r * 1.32
        core_c = QPointF(cx, cy - core_r * 0.10)
        core = QRadialGradient(core_c, soft_r)
        hot = _mix(accent, white, 0.45 + 0.40 * glow)
        rim = _mix(ember, accent, 0.45 * e)
        core.setColorAt(0.0, _rgba(hot, int(210 * glow + 40)))
        core.setColorAt(0.42, _rgba(_mix(accent, white, 0.12 * glow), int(220 * glow + 30)))
        core.setColorAt(0.66, _rgba(accent, int(200 * glow + 25)))
        core.setColorAt(0.86, _rgba(rim, int(120 * glow + 20)))
        core.setColorAt(1.0, _rgba(ember_deep, 0))
        painter.setBrush(core)
        painter.drawEllipse(core_c, soft_r, soft_r)

        # --- 4. Inner pool of light: light gathers high in the body ---------
        hi_c = QPointF(cx, cy - core_r * 0.34)
        hi_r = core_r * 0.7
        hi = QRadialGradient(hi_c, hi_r)
        hi.setColorAt(0.0, _rgba(white, int(130 * glow)))
        hi.setColorAt(0.5, _rgba(white, int(40 * glow)))
        hi.setColorAt(1.0, _rgba(white, 0))
        painter.setBrush(hi)
        painter.drawEllipse(hi_c, hi_r, hi_r)

        # --- phase word, in the reading serif, cross-fading -----------------
        self._paint_word(painter, w, h, cy + max_r + base * 0.16)

        painter.end()

    def _paint_word(self, painter: QPainter, w: int, h: int, y: float) -> None:
        painter.setFont(_serif(28))
        word_color = QColor(_PALETTE["text"])

        # Outgoing word fades out as the incoming fades in.
        if self._word_outgoing:
            self._draw_centered(
                painter,
                self._word_outgoing,
                w,
                y,
                word_color,
                1.0 - self._word_opacity,
            )
        self._draw_centered(painter, self._word_current, w, y, word_color, self._word_opacity)

        if self._sub:
            painter.setFont(_serif(15))
            self._draw_centered(
                painter,
                self._sub,
                w,
                y + 42,
                QColor(_PALETTE["text_muted"]),
                1.0,
            )

    def _draw_centered(
        self,
        painter: QPainter,
        text: str,
        w: int,
        y: float,
        color: QColor,
        opacity: float,
    ) -> None:
        if opacity <= 0.01 or not text:
            return
        c = QColor(color)
        c.setAlphaF(max(0.0, min(1.0, opacity)) * (color.alphaF()))
        # A soft outline-free centred draw via QPainterPath keeps the serif
        # crisp against the dark ground.
        fm = painter.fontMetrics()
        tw = fm.horizontalAdvance(text)
        path = QPainterPath()
        path.addText(QPointF((w - tw) / 2.0, y), painter.font(), text)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(c)
        painter.drawPath(path)
