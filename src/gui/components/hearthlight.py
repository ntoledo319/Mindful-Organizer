"""
Hearthlight — Hearth's signature living ember.

The one warm focal element, reused across the whole product (onboarding progress,
the dashboard header, the breath pacer, the automation "Hearthstone", the tray).
It is never decoration: its brightness *is* a live readout of state. Brighter glow
reads as more energy / warmth; the slow idle "breath" is the room being alive in the
background.

This widget custom-paints a coal in a dark room with layered QRadialGradients
(hot near-white core -> amber body -> deep-ember rim -> dark char falloff) plus a
wide, soft halo for the light it casts. A slow ~6s InOutSine breath drives the
``pulse`` property; the steady ``glow`` property sets the baseline brightness.

Exposed Qt properties (animatable):
    glow  (float 0..1) — baseline brightness / energy. Set this to reflect state.
    pulse (float 0..1) — the idle breath, driven internally by an animation group.

Public API:
    Hearthlight(parent=None, glow=0.6, reduced_motion=False)
    .set_glow(value, animate=True)      # ease to a new baseline brightness
    .set_reduced_motion(flag)           # calm static fallback (no breath)
    .start_breathing() / .stop_breathing()

Colors are pulled from a small local palette dict below. This is a deliberate
stand-in: when the token system lands, replace ``_ONYX`` with the resolved tokens
from ThemeManager (``accent`` -> ember mid, ``background`` -> the dark room, etc.).
"""

from __future__ import annotations

from PyQt6.QtCore import (
    QEasingCurve,
    QPointF,
    QPropertyAnimation,
    QSequentialAnimationGroup,
    Qt,
    pyqtProperty,
)
from PyQt6.QtGui import QColor, QPainter, QRadialGradient
from PyQt6.QtWidgets import QWidget

# --- Local palette (to be replaced by ResolvedTokens from ThemeManager) -------
# Targets from the Onyx (warm dark) palette. These are colors, not hex strings,
# so the paint code can interpolate brightness without re-parsing.
_ONYX = {
    "room": QColor("#0F0F11"),  # warm near-black the ember sits in
    "char": QColor("#140C07"),  # near-black charred crust at the ember's edge
    "ember_cool": QColor("#7A3A1E"),  # cooled outer coal — dark burnt sienna
    "ember_deep": QColor("#C2703D"),  # deeper ember — the rim where heat fades
    "ember": QColor("#D9A05B"),  # hearthlight amber — the glowing body
    "ember_hot": QColor("#F3B765"),  # hotter amber just inside the body
    "core": QColor("#FFE9C2"),  # white-hot heart (warm, never pure white)
}


def _mix(a: QColor, b: QColor, t: float) -> QColor:
    """Linear blend a->b in RGB; t in 0..1. Keeps things warm, no HSV surprises."""
    t = 0.0 if t < 0.0 else 1.0 if t > 1.0 else t
    return QColor(
        round(a.red() + (b.red() - a.red()) * t),
        round(a.green() + (b.green() - a.green()) * t),
        round(a.blue() + (b.blue() - a.blue()) * t),
    )


def _alpha(c: QColor, a: float) -> QColor:
    """Return a copy of c with alpha set from a 0..1 float."""
    out = QColor(c)
    out.setAlpha(max(0, min(255, round(a * 255))))
    return out


class Hearthlight(QWidget):
    """A soft, breathing ember. The warm corner of the computer, made visible."""

    BREATH_MS = 6000  # full inhale+exhale cycle; slow, ~10 breaths/min

    def __init__(
        self,
        parent=None,
        glow: float = 0.6,
        reduced_motion: bool = False,
        transparent_bg: bool = False,
    ):
        super().__init__(parent)
        self._glow = max(0.0, min(1.0, glow))
        self._pulse = 0.0
        self._reduced_motion = reduced_motion
        self._palette = _ONYX
        # When True, the ember does not paint its own dark room — it composites
        # its glow over whatever is behind it (e.g. a painted room canvas), so
        # there is no hard rectangular seam. Used when embedded in a screen.
        self._transparent_bg = transparent_bg
        if transparent_bg:
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        # Idle breath: pulse eases 0 -> 1 (inhale) then 1 -> 0 (exhale), looping.
        self._breath = QSequentialAnimationGroup(self)
        inhale = QPropertyAnimation(self, b"pulse")
        inhale.setStartValue(0.0)
        inhale.setEndValue(1.0)
        inhale.setDuration(self.BREATH_MS // 2)
        inhale.setEasingCurve(QEasingCurve.Type.InOutSine)
        exhale = QPropertyAnimation(self, b"pulse")
        exhale.setStartValue(1.0)
        exhale.setEndValue(0.0)
        exhale.setDuration(self.BREATH_MS // 2)
        exhale.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._breath.addAnimation(inhale)
        self._breath.addAnimation(exhale)
        self._breath.setLoopCount(-1)

        # Eased glow transitions when state changes the baseline brightness.
        self._glow_anim = QPropertyAnimation(self, b"glow")
        self._glow_anim.setDuration(1200)
        self._glow_anim.setEasingCurve(QEasingCurve.Type.InOutSine)

        self.setMinimumSize(140, 140)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)

        if not self._reduced_motion:
            self.start_breathing()

    # --- animatable properties ------------------------------------------------
    def _get_glow(self) -> float:
        return self._glow

    def _set_glow(self, value: float) -> None:
        self._glow = max(0.0, min(1.0, value))
        self.update()

    glow = pyqtProperty(float, _get_glow, _set_glow)

    def _get_pulse(self) -> float:
        return self._pulse

    def _set_pulse(self, value: float) -> None:
        self._pulse = max(0.0, min(1.0, value))
        self.update()

    pulse = pyqtProperty(float, _get_pulse, _set_pulse)

    # --- public API -----------------------------------------------------------
    def set_glow(self, value: float, animate: bool = True) -> None:
        """Ease the baseline brightness toward ``value`` (0..1)."""
        value = max(0.0, min(1.0, value))
        if animate and not self._reduced_motion:
            self._glow_anim.stop()
            self._glow_anim.setStartValue(self._glow)
            self._glow_anim.setEndValue(value)
            self._glow_anim.start()
        else:
            self._set_glow(value)

    def set_reduced_motion(self, flag: bool) -> None:
        """Honor a reduced-motion preference with a calm static ember."""
        self._reduced_motion = flag
        if flag:
            self.stop_breathing()
            self._set_pulse(0.5)  # a held, steady mid-breath — never dark, never frantic
        else:
            self.start_breathing()

    def start_breathing(self) -> None:
        if self._breath.state() != QSequentialAnimationGroup.State.Running:
            self._breath.start()

    def stop_breathing(self) -> None:
        self._breath.stop()

    # --- painting -------------------------------------------------------------
    def paintEvent(self, _event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        rect = self.rect()
        # Fill the dark room first so the halo has something warm to bleed into.
        # When embedded transparently, skip this so the ember composites over the
        # surrounding painted room (no hard square seam).
        if not self._transparent_bg:
            p.fillRect(rect, self._palette["room"])

        cx, cy = rect.center().x() + 0.5, rect.center().y() + 0.5
        center = QPointF(cx, cy)
        # The ember's drawn radius leaves headroom for the halo to spill outward.
        unit = min(rect.width(), rect.height()) / 2.0
        ember_r = unit * 0.44
        halo_r = unit * 0.99

        # Breath modulates brightness and, very subtly, the body radius — a real
        # coal pulses *light* far more than it pulses size.
        breath = self._pulse
        # Effective brightness: baseline glow lifted by the inhale.
        b = self._glow * (0.80 + 0.20 * breath)
        b = max(0.0, min(1.0, b))
        # "heat" is a nonlinear curve so a low glow reads as a genuinely banked
        # coal (mostly char, smoldering heart) rather than a slightly-dimmer disk.
        heat = b * b * (3.0 - 2.0 * b)  # smoothstep — eases the low end down hard
        ember_r *= 1.0 + 0.03 * breath

        pal = self._palette

        # --- 1. The cast halo: wide, very soft light spilling into the room. ---
        # Two stacked halos (a broad outer wash + a tighter warm bloom) read as
        # firelight in a dark room rather than a hard-edged disk. The light a coal
        # throws is dominated by heat, so it nearly vanishes when banked low.
        outer = QRadialGradient(center, halo_r)
        glow_tint = _mix(pal["ember"], pal["ember_hot"], heat)
        outer.setColorAt(0.0, _alpha(glow_tint, 0.26 * heat))
        outer.setColorAt(0.40, _alpha(pal["ember"], 0.12 * heat))
        outer.setColorAt(0.70, _alpha(pal["ember_deep"], 0.05 * heat))
        outer.setColorAt(1.0, _alpha(pal["ember_deep"], 0.0))
        p.setBrush(outer)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(center, halo_r, halo_r)

        bloom_r = ember_r * 2.3
        bloom = QRadialGradient(center, bloom_r)
        bloom.setColorAt(0.0, _alpha(pal["ember_hot"], 0.42 * heat))
        bloom.setColorAt(0.35, _alpha(pal["ember"], 0.22 * heat))
        bloom.setColorAt(1.0, _alpha(pal["ember"], 0.0))
        p.setBrush(bloom)
        p.drawEllipse(center, bloom_r, bloom_r)

        # --- 2. The coal body: a dark burnt crust lit from within. -------------
        # The light comes from the heart and dies into a charred rim. Even at full
        # heat the very edge stays a cooled, burnt sienna so it never flattens into
        # a uniform disk and melts into the halo instead of ending in a hard sphere.
        body = QRadialGradient(center, ember_r * 1.04)
        # Crust colors interpolate from "cold dark coal" toward "lit ember" by heat.
        heart = _mix(pal["ember_hot"], pal["core"], 0.25 + 0.55 * heat)
        inner = _mix(pal["ember"], pal["ember_hot"], 0.35 + 0.55 * heat)
        rim = _mix(pal["ember_cool"], pal["ember_deep"], 0.15 + 0.70 * heat)
        crust = _mix(pal["char"], pal["ember_cool"], 0.22 + 0.55 * heat)
        edge = _mix(pal["char"], pal["room"], 0.4)  # melts into the dark room
        body.setColorAt(0.0, heart)
        body.setColorAt(0.38, inner)
        body.setColorAt(0.70, rim)
        body.setColorAt(0.92, crust)
        body.setColorAt(1.0, _alpha(edge, 0.0))  # soft edge, no hard sphere line
        p.setBrush(body)
        p.drawEllipse(center, ember_r * 1.04, ember_r * 1.04)

        # --- 3. The hot core: small, intense, white-hot, riding slightly high. -
        # This is the molten heart glowing through the crust. Its sharp contrast
        # against the cooler body is what reads as *fire* rather than a tan ball.
        core_center = QPointF(cx, cy - ember_r * 0.14)
        core_r = ember_r * (0.40 + 0.12 * heat)
        core = QRadialGradient(core_center, core_r)
        # Warm white-hot heart: blend toward core but keep an amber floor so it
        # never goes ashen/gray where it meets the body.
        core_hot = _mix(pal["ember_hot"], pal["core"], 0.45 + 0.45 * heat)
        core.setColorAt(0.0, _alpha(core_hot, 0.34 + 0.62 * heat))
        core.setColorAt(0.40, _alpha(pal["ember_hot"], 0.40 * heat))
        core.setColorAt(1.0, _alpha(pal["ember_hot"], 0.0))
        p.setBrush(core)
        p.drawEllipse(core_center, core_r, core_r)

        # --- 4. A faint cooler patch low on the coal: warm-color variation. ----
        # Keeps the ember from being radially perfect — coals are never uniform.
        crest_center = QPointF(cx + ember_r * 0.16, cy + ember_r * 0.34)
        crest_r = ember_r * 0.62
        crest = QRadialGradient(crest_center, crest_r)
        crest.setColorAt(0.0, _alpha(pal["ember_cool"], 0.22 * (1.0 - 0.5 * heat)))
        crest.setColorAt(1.0, _alpha(pal["ember_cool"], 0.0))
        p.setBrush(crest)
        p.drawEllipse(crest_center, crest_r, crest_r)

        p.end()


if __name__ == "__main__":  # pragma: no cover - manual visual check
    import sys

    from PyQt6.QtWidgets import QApplication, QHBoxLayout
    from PyQt6.QtWidgets import QWidget as _W  # noqa: N814

    app = QApplication(sys.argv)
    root = _W()
    root.setStyleSheet("background-color: #0F0F11;")
    lay = QHBoxLayout(root)
    for g in (0.25, 0.6, 0.95):
        e = Hearthlight(glow=g)
        e.setFixedSize(240, 240)
        lay.addWidget(e)
    root.resize(760, 280)
    root.show()
    sys.exit(app.exec())
