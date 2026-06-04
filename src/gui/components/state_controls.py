"""
Hearth check-in controls — the warm, tactile inputs for the daily check-in.

DESIGN_SYSTEM §4: StateDial / StateSlider / Pill. These replace the raw native
Qt mood widgets (QSlider, QSpinBox, QCheckBox grids) that read as "a tracker with
a dark coat." Every value the user sets warms or cools the control along a single
ember ramp, and every state-word is rendered in the reading serif — the way you
read a feeling, not a number.

Two-font voice (DESIGN_SYSTEM §1):
- reading serif  -> the value WORD ("Okay", "Low", "Good"), prompts.
- control sans   -> the small caption rows, the pill labels (they are controls).

All color is local for now. ``PALETTE`` is a stand-in for the runtime
``ResolvedTokens`` the State Engine will eventually supply; nothing here should
hardcode a hex outside of it.
"""

from __future__ import annotations

import math

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
    QFontDatabase,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QRadialGradient,
)
from PyQt6.QtWidgets import (
    QAbstractButton,
    QGraphicsDropShadowEffect,
    QWidget,
)

# ---------------------------------------------------------------------------
# Palette — Onyx (the warm dark default).
# TODO: replace with ResolvedTokens resolved per HearthState at render time.
# ---------------------------------------------------------------------------
PALETTE = {
    "bg": "#0F0F11",  # warm near-black, not pure black
    "surface": "#18181A",  # quiet card surface
    "raised": "#211C17",  # warmer raised surface
    "text": "#F2EDE6",  # warm off-white
    "text_muted": "#A99B88",  # clears AA 4.5:1 on surface
    "accent": "#D9A05B",  # hearthlight — warm amber/ember
    "ember": "#C2703D",  # deeper ember
    "border": "#2E2A24",  # warm hairline
    "danger": "#C8736B",  # calm crisis outline (never filled red)
}

# The warmth ramp: cool faded slate -> dried-clay -> ember -> hearthlight.
# Walking this ramp is how every control "warms as the value rises."
_RAMP = [
    (0.00, QColor("#534A40")),  # cold ash — the lowest reading
    (0.26, QColor("#8A5E42")),  # banked coal beginning to catch
    (0.52, QColor(PALETTE["ember"])),  # ember
    (0.78, QColor(PALETTE["accent"])),  # hearthlight
    (1.00, QColor("#EEC489")),  # the brightest glow
]

# Reading serif faces, in order of preference (macOS prototype set).
_SERIF_STACK = ["Charter", "Cochin", "Baskerville", "Georgia"]
# Control sans faces.
_SANS_STACK = ["SF Pro Text", "Helvetica Neue", "Helvetica"]


def _pick(stack: list[str]) -> str:
    available = set(QFontDatabase.families())
    for fam in stack:
        if fam in available:
            return fam
    return stack[-1]


def serif_font(size: int, weight: QFont.Weight = QFont.Weight.Normal) -> QFont:
    f = QFont(_pick(_SERIF_STACK), size)
    f.setWeight(weight)
    f.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    return f


def sans_font(size: int, weight: QFont.Weight = QFont.Weight.Medium) -> QFont:
    f = QFont(_pick(_SANS_STACK), size)
    f.setWeight(weight)
    f.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    return f


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def _mix(c1: QColor, c2: QColor, t: float) -> QColor:
    t = max(0.0, min(1.0, t))
    return QColor(
        int(_lerp(c1.red(), c2.red(), t)),
        int(_lerp(c1.green(), c2.green(), t)),
        int(_lerp(c1.blue(), c2.blue(), t)),
        int(_lerp(c1.alpha(), c2.alpha(), t)),
    )


def warmth_color(t: float) -> QColor:
    """Sample the ember ramp at t in [0, 1]."""
    t = max(0.0, min(1.0, t))
    for i in range(len(_RAMP) - 1):
        t0, c0 = _RAMP[i]
        t1, c1 = _RAMP[i + 1]
        if t <= t1:
            span = (t1 - t0) or 1.0
            return _mix(c0, c1, (t - t0) / span)
    return _RAMP[-1][1]


# The state vocabulary — a feeling reads as a word, never a 0–100 number.
# Five steady-state words across the ramp; the slider/dial pick the nearest.
STATE_WORDS = ["Bad", "Low", "Okay", "Good", "Bright"]


def word_for(t: float) -> str:
    idx = int(round(max(0.0, min(1.0, t)) * (len(STATE_WORDS) - 1)))
    return STATE_WORDS[idx]


# ---------------------------------------------------------------------------
# StateDial — a painted arc you turn to set how you are.
# ---------------------------------------------------------------------------
class StateDial(QWidget):
    """A warm arc-dial with one draggable knob.

    The arc sweeps a conical warmth gradient; the filled portion grows and
    *warms* as the value rises. The center shows the value as a reading-serif
    word, not a number. Emits ``valueChanged(float)`` in [0, 1].
    """

    valueChanged = pyqtSignal(float)  # noqa: N815

    # Arc geometry: a generous open dial, gap at the bottom.
    _START_DEG = 225.0  # bottom-left
    _SWEEP_DEG = 270.0  # clockwise (negative in Qt angles) to bottom-right

    def __init__(self, value: float = 0.5, reduced_motion: bool = False, parent=None):
        super().__init__(parent)
        self._value = max(0.0, min(1.0, value))
        self._display = self._value  # eased toward _value
        self._reduced_motion = reduced_motion
        self._dragging = False
        self.setMinimumSize(220, 200)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._anim = QPropertyAnimation(self, b"display", self)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.setDuration(0 if reduced_motion else 520)

    # -- eased display property -------------------------------------------
    def _get_display(self) -> float:
        return self._display

    def _set_display(self, v: float) -> None:
        self._display = v
        self.update()

    display = pyqtProperty(float, fget=_get_display, fset=_set_display)

    # -- public value ------------------------------------------------------
    def value(self) -> float:
        return self._value

    def setValue(self, v: float, *, animate: bool = True) -> None:  # noqa: N802
        v = max(0.0, min(1.0, v))
        if abs(v - self._value) < 1e-4:
            return
        self._value = v
        if animate and not self._reduced_motion:
            self._anim.stop()
            self._anim.setStartValue(self._display)
            self._anim.setEndValue(v)
            self._anim.start()
        else:
            self._display = v
            self.update()
        self.valueChanged.emit(v)

    # -- geometry helpers --------------------------------------------------
    def _arc_rect(self) -> QRectF:
        side = min(self.width(), self.height() - 8)
        pad = side * 0.16
        r = side - 2 * pad
        cx = self.width() / 2
        cy = (self.height() - 8) / 2 + 6
        return QRectF(cx - r / 2, cy - r / 2, r, r)

    def _angle_for(self, t: float) -> float:
        # value 0 -> start angle; value 1 -> start - sweep (clockwise)
        return self._START_DEG - self._SWEEP_DEG * t

    def _knob_center(self, t: float) -> QPointF:
        rect = self._arc_rect()
        a = math.radians(self._angle_for(t))
        rad = rect.width() / 2
        return QPointF(
            rect.center().x() + rad * math.cos(a),
            rect.center().y() - rad * math.sin(a),
        )

    def _value_from_pos(self, pos: QPointF) -> float:
        rect = self._arc_rect()
        dx = pos.x() - rect.center().x()
        dy = rect.center().y() - pos.y()
        ang = math.degrees(math.atan2(dy, dx)) % 360.0
        # Map angle back onto the start->sweep range.
        delta = (self._START_DEG - ang) % 360.0
        if delta > self._SWEEP_DEG:
            # Snap to whichever end is nearer when in the bottom gap.
            return 0.0 if delta - self._SWEEP_DEG < (360.0 - self._SWEEP_DEG) / 2 else 1.0
        return max(0.0, min(1.0, delta / self._SWEEP_DEG))

    # -- interaction -------------------------------------------------------
    def mousePressEvent(self, e):  # noqa: N802
        self._dragging = True
        self.setCursor(Qt.CursorShape.ClosedHandCursor)
        self.setValue(self._value_from_pos(e.position()), animate=False)

    def mouseMoveEvent(self, e):  # noqa: N802
        if self._dragging:
            self.setValue(self._value_from_pos(e.position()), animate=False)

    def mouseReleaseEvent(self, e):  # noqa: N802
        self._dragging = False
        self.setCursor(Qt.CursorShape.OpenHandCursor)

    def keyPressEvent(self, e):  # noqa: N802
        step = 1.0 / (len(STATE_WORDS) - 1)
        if e.key() in (Qt.Key.Key_Right, Qt.Key.Key_Up):
            self.setValue(self._value + step)
        elif e.key() in (Qt.Key.Key_Left, Qt.Key.Key_Down):
            self.setValue(self._value - step)
        else:
            super().keyPressEvent(e)

    # -- paint -------------------------------------------------------------
    def paintEvent(self, _):  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self._arc_rect()
        center = rect.center()
        thickness = rect.width() * 0.085
        glow = warmth_color(self._display)

        # Stroke arcs along the centreline of the groove.
        stroke_rect = rect.adjusted(thickness / 2, thickness / 2, -thickness / 2, -thickness / 2)

        # 1) The unlit track — a quiet warm groove across the full sweep.
        track_pen = QPen(QColor(PALETTE["border"]))
        track_pen.setWidthF(thickness)
        track_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(track_pen)
        # Qt drawArc: start at value=1 angle, sweep positive (CCW) back to start.
        p.drawArc(stroke_rect, int(self._angle_for(1.0) * 16), int(self._SWEEP_DEG * 16))

        # 2) A soft, contained ember bloom inside the ring.
        bloom = QRadialGradient(center, rect.width() * 0.46)
        b0 = QColor(glow)
        b0.setAlpha(int(64 * self._display + 12))
        bloom.setColorAt(0.0, b0)
        bloom.setColorAt(1.0, QColor(glow.red(), glow.green(), glow.blue(), 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(bloom)
        p.drawEllipse(center, rect.width() * 0.45, rect.width() * 0.45)

        # 3) The lit arc — the warmth ramp painted directly along the arc by
        #    walking short segments from the cold start to the knob. A conical
        #    gradient cannot follow an arc's angular span cleanly (it bleeds
        #    colour into the unlit region), so we stroke the ramp ourselves.
        if self._display > 0.002:
            total_deg = self._SWEEP_DEG * self._display
            n = max(2, int(total_deg / 5))  # ~5 deg per segment
            seg = total_deg / n
            for i in range(n):
                a0 = self._START_DEG - seg * i  # clockwise
                frac0 = (seg * i) / self._SWEEP_DEG  # ramp position at a0
                col = warmth_color(frac0)
                pen = QPen(col)
                pen.setWidthF(thickness)
                # Round caps only on the very ends; flat in the middle so
                # segments butt together without gaps or overlap seams.
                pen.setCapStyle(
                    Qt.PenCapStyle.RoundCap if (i == 0 or i == n - 1) else Qt.PenCapStyle.FlatCap
                )
                p.setPen(pen)
                # +1 deg overlap to hide hairline seams between segments.
                span = -(seg + (1.0 if i < n - 1 else 0.0))
                p.drawArc(stroke_rect, int(a0 * 16), int(span * 16))

        # 4) The knob — a warm coal with a soft halo.
        kc = self._knob_center(self._display)
        knob_r = thickness * 1.05
        halo = QRadialGradient(kc, knob_r * 2.6)
        hc = QColor(glow)
        hc.setAlpha(160)
        halo.setColorAt(0.0, hc)
        halo.setColorAt(1.0, QColor(glow.red(), glow.green(), glow.blue(), 0))
        p.setBrush(halo)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(kc, knob_r * 2.3, knob_r * 2.3)

        knob_grad = QRadialGradient(
            QPointF(kc.x() - knob_r * 0.35, kc.y() - knob_r * 0.35), knob_r * 1.8
        )
        knob_grad.setColorAt(0.0, _mix(glow, QColor("#FFFFFF"), 0.4))
        knob_grad.setColorAt(1.0, _mix(glow, QColor(PALETTE["bg"]), 0.28))
        p.setBrush(knob_grad)
        p.setPen(QPen(_mix(QColor(PALETTE["bg"]), glow, 0.3), 1.5))
        p.drawEllipse(kc, knob_r, knob_r)

        # 5) The interior: a small caption above, the value WORD below — both
        #    centred in the open middle of the ring, clear of the arc.
        cap_rect = QRectF(
            rect.left(), center.y() - rect.height() * 0.22, rect.width(), rect.height() * 0.16
        )
        p.setPen(QColor(PALETTE["text_muted"]))
        p.setFont(sans_font(10, QFont.Weight.DemiBold))
        p.drawText(cap_rect, Qt.AlignmentFlag.AlignCenter, "HOW YOU ARE")

        word = word_for(self._display)
        word_rect = QRectF(
            rect.left(), center.y() - rect.height() * 0.06, rect.width(), rect.height() * 0.30
        )
        p.setPen(QColor(PALETTE["text"]))
        p.setFont(serif_font(33, QFont.Weight.Medium))
        p.drawText(word_rect, Qt.AlignmentFlag.AlignCenter, word)
        p.end()


# ---------------------------------------------------------------------------
# StateSlider — a horizontal track whose fill warms as you drag.
# ---------------------------------------------------------------------------
class StateSlider(QWidget):
    """A custom horizontal control replacing raw QSlider.

    The fill shifts along the warmth ramp as dragged; the current value reads as
    a word above the knob, eased when it changes. Emits ``valueChanged(float)``.
    """

    valueChanged = pyqtSignal(float)  # noqa: N815

    def __init__(
        self, value: float = 0.5, label: str = "", reduced_motion: bool = False, parent=None
    ):
        super().__init__(parent)
        self._value = max(0.0, min(1.0, value))
        self._display = self._value
        self._label = label
        self._reduced_motion = reduced_motion
        self._dragging = False
        self.setMinimumSize(300, 96)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._anim = QPropertyAnimation(self, b"display", self)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._anim.setDuration(0 if reduced_motion else 460)

    def _get_display(self) -> float:
        return self._display

    def _set_display(self, v: float) -> None:
        self._display = v
        self.update()

    display = pyqtProperty(float, fget=_get_display, fset=_set_display)

    def value(self) -> float:
        return self._value

    def setValue(self, v: float, *, animate: bool = True) -> None:  # noqa: N802
        v = max(0.0, min(1.0, v))
        if abs(v - self._value) < 1e-4:
            return
        self._value = v
        if animate and not self._reduced_motion:
            self._anim.stop()
            self._anim.setStartValue(self._display)
            self._anim.setEndValue(v)
            self._anim.start()
        else:
            self._display = v
            self.update()
        self.valueChanged.emit(v)

    def _track_rect(self) -> QRectF:
        m = 18.0
        h = 12.0
        y = self.height() * 0.62
        return QRectF(m, y - h / 2, self.width() - 2 * m, h)

    def _value_from_x(self, x: float) -> float:
        tr = self._track_rect()
        return max(0.0, min(1.0, (x - tr.left()) / tr.width()))

    def mousePressEvent(self, e):  # noqa: N802
        self._dragging = True
        self.setValue(self._value_from_x(e.position().x()), animate=False)

    def mouseMoveEvent(self, e):  # noqa: N802
        if self._dragging:
            self.setValue(self._value_from_x(e.position().x()), animate=False)

    def mouseReleaseEvent(self, e):  # noqa: N802
        self._dragging = False

    def keyPressEvent(self, e):  # noqa: N802
        step = 1.0 / (len(STATE_WORDS) - 1)
        if e.key() in (Qt.Key.Key_Right, Qt.Key.Key_Up):
            self.setValue(self._value + step)
        elif e.key() in (Qt.Key.Key_Left, Qt.Key.Key_Down):
            self.setValue(self._value - step)
        else:
            super().keyPressEvent(e)

    def paintEvent(self, _):  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        tr = self._track_rect()
        radius = tr.height() / 2
        glow = warmth_color(self._display)

        # Optional control-sans label, top-left.
        if self._label:
            p.setPen(QColor(PALETTE["text_muted"]))
            p.setFont(sans_font(11, QFont.Weight.Medium))
            p.drawText(
                QRectF(tr.left(), 4, tr.width(), 18),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                self._label,
            )

        # Unlit groove.
        groove = QPainterPath()
        groove.addRoundedRect(tr, radius, radius)
        p.fillPath(groove, QColor(PALETTE["border"]))

        # Lit fill — gradient warming left to right along the ramp.
        knob_x = tr.left() + tr.width() * self._display
        fill_rect = QRectF(tr.left(), tr.top(), max(radius * 2, knob_x - tr.left()), tr.height())
        fill_path = QPainterPath()
        fill_path.addRoundedRect(fill_rect, radius, radius)
        grad = QLinearGradient(tr.left(), 0, tr.right(), 0)
        grad.setColorAt(0.0, warmth_color(0.08))
        grad.setColorAt(max(0.001, self._display * 0.5), warmth_color(self._display * 0.6))
        grad.setColorAt(min(0.999, self._display), glow)
        p.fillPath(fill_path, grad)

        # Soft ember bloom under the knob.
        bloom = QRadialGradient(QPointF(knob_x, tr.center().y()), 34)
        b0 = QColor(glow)
        b0.setAlpha(120)
        bloom.setColorAt(0.0, b0)
        bloom.setColorAt(1.0, QColor(glow.red(), glow.green(), glow.blue(), 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(bloom)
        p.drawEllipse(QPointF(knob_x, tr.center().y()), 28, 28)

        # Knob — warm coal.
        kr = 13.0
        kg = QRadialGradient(QPointF(knob_x - 3, tr.center().y() - 3), kr * 1.7)
        kg.setColorAt(0.0, _mix(glow, QColor("#FFFFFF"), 0.34))
        kg.setColorAt(1.0, _mix(glow, QColor(PALETTE["bg"]), 0.22))
        p.setBrush(kg)
        p.setPen(QPen(QColor(PALETTE["bg"]), 1.5))
        p.drawEllipse(QPointF(knob_x, tr.center().y()), kr, kr)

        # The word — reading serif, riding above the knob.
        word = word_for(self._display)
        p.setFont(serif_font(20, QFont.Weight.Medium))
        fm = p.fontMetrics()
        w = fm.horizontalAdvance(word)
        wx = max(tr.left(), min(tr.right() - w, knob_x - w / 2))
        p.setPen(QColor(PALETTE["text"]))
        p.drawText(
            QRectF(wx, tr.top() - 36, w + 4, 30),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            word,
        )
        p.end()


# ---------------------------------------------------------------------------
# Pill — a checkable soft token for symptoms / feelings.
# ---------------------------------------------------------------------------
class Pill(QAbstractButton):
    """A checkable soft rounded token.

    Unselected: a quiet warm outline. Selected: warm amber fill + a soft glow
    (QGraphicsDropShadowEffect). Built for a wrapping symptom/feeling picker.
    """

    def __init__(self, text: str, reduced_motion: bool = False, parent=None):
        super().__init__(parent)
        self.setText(text)
        self.setCheckable(True)
        self._reduced_motion = reduced_motion
        self._fill = 0.0  # eased 0->1 with checked state
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFont(sans_font(13, QFont.Weight.Medium))
        self._recompute_size()

        # The selection glow — soft, warm, never a hard ring.
        self._glow = QGraphicsDropShadowEffect(self)
        self._glow.setColor(QColor(217, 160, 91, 0))  # accent, alpha animated
        self._glow.setBlurRadius(26)
        self._glow.setOffset(0, 0)
        self.setGraphicsEffect(self._glow)

        self._anim = QPropertyAnimation(self, b"fill", self)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.setDuration(0 if reduced_motion else 300)
        self.toggled.connect(self._on_toggled)

    def _recompute_size(self):
        fm = self.fontMetrics()
        w = fm.horizontalAdvance(self.text()) + 40
        h = 40
        self.setMinimumSize(w, h)
        self.setMaximumHeight(h)

    def _get_fill(self) -> float:
        return self._fill

    def _set_fill(self, v: float) -> None:
        self._fill = v
        self._glow.setColor(QColor(217, 160, 91, int(150 * v)))
        self.update()

    fill = pyqtProperty(float, fget=_get_fill, fset=_set_fill)

    def _on_toggled(self, checked: bool):
        target = 1.0 if checked else 0.0
        # Settle to the final value immediately, then let the animation glide
        # over it for the visual transition. This keeps the painted state
        # correct even when no event loop is spinning the animation (e.g. an
        # offscreen grab, or checked() set before the widget is shown).
        if self._reduced_motion or not self.isVisible():
            self._set_fill(target)
            return
        self._set_fill(target)
        self._anim.stop()
        self._anim.setStartValue(0.0 if checked else 1.0)
        self._anim.setEndValue(target)
        self._anim.start()

    def sizeHint(self):  # noqa: N802
        from PyQt6.QtCore import QSize

        fm = self.fontMetrics()
        return QSize(fm.horizontalAdvance(self.text()) + 40, 40)

    def paintEvent(self, _):  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(1, 1, self.width() - 2, self.height() - 2)
        radius = rect.height() / 2
        f = self._fill

        # Base: quiet surface with a warm outline, warming toward amber fill.
        base = _mix(QColor(PALETTE["surface"]), QColor(PALETTE["accent"]), f * 0.92)
        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)
        p.fillPath(path, base)

        # The outline — quiet border when off, vanishes into the fill when on.
        border = _mix(QColor(PALETTE["border"]), QColor(PALETTE["accent"]), f)
        pen = QPen(border)
        pen.setWidthF(1.4)
        p.setPen(pen)
        p.drawPath(path)

        # Label — control sans. Reads warm-dark on amber when selected.
        on_text = _mix(QColor(PALETTE["text"]), QColor(PALETTE["bg"]), f)
        p.setPen(on_text)
        p.setFont(self.font())
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())
        p.end()
