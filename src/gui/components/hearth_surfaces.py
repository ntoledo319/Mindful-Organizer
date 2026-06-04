"""Hearth surface language — HearthCard + HearthButton.

The two primitives every Hearth screen is built from. They are not flat
`QFrame`s with a 1px border (the "stack of bordered cards" the audits
condemned); they are custom-painted surfaces that read as *warm paper or
river stone seen in firelight*. Elevation encodes importance: the one true
action sits on the warmest, most-lifted card.

Design references: docs/design/DESIGN_SYSTEM.md §4 (HearthCard / HearthButton),
docs/design/VISION.md (principles 3 & 5 — warmth is the work; weight tracks
human stakes).

Self-contained and importable:
    from gui.components.hearth_surfaces import HearthCard, HearthButton

Colors live in the local ``ONYX`` palette dict below. This dict is a
stand-in **to be replaced by ``ResolvedTokens``** from the State Engine
(see DESIGN_SYSTEM.md §0) once that lands — every value here maps to a
token name so the swap is mechanical.
"""

from __future__ import annotations

from PyQt6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    QRectF,
    Qt,
    pyqtProperty,
)
from PyQt6.QtGui import (
    QColor,
    QFont,
    QPainter,
    QPainterPath,
    QRadialGradient,
)
from PyQt6.QtWidgets import (
    QAbstractButton,
    QFrame,
    QGraphicsDropShadowEffect,
)

# --- Palette (Onyx, the warm dark default) ---------------------------------
# TO BE REPLACED BY ResolvedTokens. Each key is the token it stands in for.
ONYX: dict[str, str] = {
    "background": "#0F0F11",  # warm near-black (never pure black)
    "surface": "#18181A",  # default card
    "surface_raised": "#211C17",  # elevated, warmer card (leans to ember)
    "text": "#F2EDE6",  # warm off-white
    "text_muted": "#A99B88",  # clears AA 4.5:1 on surface
    "accent": "#D9A05B",  # hearthlight — warm amber/ember
    "ember": "#C2703D",  # deeper ember (hover / pressed warmth)
    "border": "#2E2A24",  # warm low-contrast hairline
    "crisis": "#C8736B",  # calm danger outline (never filled delete-red)
}

# --- Fonts ------------------------------------------------------------------
# Two-font voice (DESIGN_SYSTEM §1). macOS faces for the prototype; the real
# bundled fonts (Source Serif 4 / IBM Plex) arrive in Wave 1.
_SERIF = "Charter"  # reading voice — what you read as language
_SANS = "SF Pro Text"  # control voice — buttons, labels, numbers
_SANS_FALLBACK = "Helvetica Neue"


def _serif(size: int, weight: int = QFont.Weight.Normal) -> QFont:
    f = QFont(_SERIF, size, weight)
    f.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    return f


def _sans(size: int, weight: int = QFont.Weight.Medium) -> QFont:
    f = QFont(_SANS, size, weight)
    f.insertSubstitution(_SANS, _SANS_FALLBACK)
    f.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    return f


def _c(hex_or_token: str) -> QColor:
    """Resolve a palette token name or hex string to a QColor."""
    return QColor(ONYX.get(hex_or_token, hex_or_token))


# ===========================================================================
# HearthCard
# ===========================================================================
class HearthCard(QFrame):
    """A soft rounded surface with a faint inner warmth and real elevation.

    Not a bordered box. The paintEvent lays down a rounded fill, then washes
    a very-low-opacity radial of hearthlight across the top-left — as if a
    fire off-screen is warming one corner of the stone. A real
    ``QGraphicsDropShadowEffect`` lifts it off the background; ``elevation``
    is importance, so the one true action's card sits highest and warmest.

    Args:
        elevation: 0 = resting (flush, faint shadow), 1 = standing,
            2 = the focal card (warmest fill, deepest soft shadow).
        radius: corner radius in px.
    """

    def __init__(self, parent=None, *, elevation: int = 1, radius: int = 18):
        super().__init__(parent)
        self._elevation = max(0, min(2, elevation))
        self._radius = radius
        # Focal cards use the warmer "surface_raised"; resting cards the
        # neutral surface. The warmth difference is felt, not announced.
        self._fill = _c("surface_raised") if self._elevation >= 2 else _c("surface")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)
        self.setAutoFillBackground(False)

        shadow = QGraphicsDropShadowEffect(self)
        # Soft, large-radius, slightly warm-black shadow — light from above,
        # so the card casts down. Deeper for higher elevation.
        blur = {0: 18, 1: 34, 2: 52}[self._elevation]
        offset = {0: 4, 1: 9, 2: 16}[self._elevation]
        alpha = {0: 90, 1: 130, 2: 165}[self._elevation]
        shadow.setBlurRadius(blur)
        shadow.setOffset(0, offset)
        shadow.setColor(QColor(0, 0, 0, alpha))
        self.setGraphicsEffect(shadow)

    def paintEvent(self, event):  # noqa: N802 (Qt naming)
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # Inset so the soft shadow has room to bleed and edges stay crisp.
        m = 2.0
        rect = QRectF(self.rect()).adjusted(m, m, -m, -m)
        path = QPainterPath()
        path.addRoundedRect(rect, self._radius, self._radius)
        p.setClipPath(path)

        # 1) Base fill — warm stone.
        p.fillPath(path, self._fill)

        # 2) Inner warmth — firelight POOLING in the upper third, not a
        #    diagonal gradient streak. The source sits high and centered so
        #    the glow pools symmetrically and fades to nothing well before
        #    the lower edge — like a hearth glowing somewhere above the page.
        #    Kept very low opacity so it reads as ambient light, never a swatch.
        cx = rect.left() + rect.width() * 0.5
        cy = rect.top() + rect.height() * 0.02
        glow = QRadialGradient(cx, cy, rect.width() * 1.05)
        warm = _c("accent")
        # Strength scales with elevation — the focal card glows a touch more.
        peak = {0: 11, 1: 16, 2: 24}[self._elevation]
        warm.setAlpha(peak)
        mid = QColor(warm)
        mid.setAlpha(int(peak * 0.4))
        glow.setColorAt(0.0, warm)
        glow.setColorAt(0.5, mid)
        glow.setColorAt(1.0, QColor(warm.red(), warm.green(), warm.blue(), 0))
        p.fillPath(path, glow)

        # 3) Hairline — a single soft warm edge. Not a bright box: the rim is
        #    only a shade above the fill so it holds the shape without
        #    announcing itself. Focal cards carry the faintest amber warmth.
        edge = _c("border")
        if self._elevation >= 2:
            edge = QColor(
                int(edge.red() * 0.62 + warm.red() * 0.38),
                int(edge.green() * 0.62 + warm.green() * 0.38),
                int(edge.blue() * 0.62 + warm.blue() * 0.38),
            )
        pen = p.pen()
        pen.setColor(edge)
        pen.setWidthF(1.0)
        p.setPen(pen)
        p.setClipping(False)
        p.drawPath(path)
        p.end()


# ===========================================================================
# HearthButton
# ===========================================================================
class HearthButton(QAbstractButton):
    """One painted button, three roles. Never Bootstrap.

    Roles (DESIGN_SYSTEM §4):
      - ``primary``  the ONE action. Warm amber fill, dark warm label.
      - ``ghost``    the recessive side-door. Text only, muted, no box;
                     warms on hover. It subordinates; it never vanishes.
      - ``crisis``   the lifeline. Calm danger **outline**, never filled red.
                     Warms toward danger on hover — care, not alarm.

    Hover is a slow warm *bloom* (a soft radial brightening) rather than a
    flat color swap. Motion eases on ``InOutSine``; ``reduced_motion`` swaps
    it for a calm static brighten.
    """

    _ROLES = ("primary", "ghost", "crisis")

    def __init__(
        self,
        text: str = "",
        role: str = "primary",
        parent=None,
        *,
        reduced_motion: bool = False,
    ):
        super().__init__(parent)
        self.setText(text)
        self._role = role if role in self._ROLES else "primary"
        self._reduced_motion = reduced_motion
        self._hover = 0.0  # 0..1 bloom amount
        self._press = 0.0
        self._radius = 14

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(46)
        self._apply_metrics()

        # Slow eased hover bloom. Honors reduced motion with a calm fallback.
        self._bloom = QPropertyAnimation(self, b"hover", self)
        self._bloom.setDuration(0 if reduced_motion else 320)
        self._bloom.setEasingCurve(QEasingCurve.Type.InOutSine)

    def _apply_metrics(self) -> None:
        self.setFont(_sans(14, QFont.Weight.DemiBold))
        # Ghost buttons sit lighter and tighter — they are side-doors.
        if self._role == "ghost":
            self.setMinimumHeight(40)

    # --- animated property ---------------------------------------------
    def _get_hover(self) -> float:
        return self._hover

    def _set_hover(self, v: float) -> None:
        self._hover = v
        self.update()

    hover = pyqtProperty(float, fget=_get_hover, fset=_set_hover)

    # --- sizing ---------------------------------------------------------
    def sizeHint(self):  # noqa: N802
        fm = self.fontMetrics()
        w = fm.horizontalAdvance(self.text())
        pad_x = 22 if self._role != "ghost" else 14
        from PyQt6.QtCore import QSize

        return QSize(w + pad_x * 2, self.minimumHeight())

    # --- interaction ----------------------------------------------------
    def enterEvent(self, event):  # noqa: N802
        if self._reduced_motion:
            self._set_hover(1.0)
        else:
            self._bloom.stop()
            self._bloom.setStartValue(self._hover)
            self._bloom.setEndValue(1.0)
            self._bloom.start()
        super().enterEvent(event)

    def leaveEvent(self, event):  # noqa: N802
        if self._reduced_motion:
            self._set_hover(0.0)
        else:
            self._bloom.stop()
            self._bloom.setStartValue(self._hover)
            self._bloom.setEndValue(0.0)
            self._bloom.start()
        super().leaveEvent(event)

    def mousePressEvent(self, event):  # noqa: N802
        self._press = 1.0
        self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):  # noqa: N802
        self._press = 0.0
        self.update()
        super().mouseReleaseEvent(event)

    # --- painting -------------------------------------------------------
    def paintEvent(self, event):  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        rect = QRectF(self.rect()).adjusted(1.5, 1.5, -1.5, -1.5)
        # A barely-perceptible press recess.
        if self._press:
            rect = rect.adjusted(0, 0.5, 0, 0.5)
        path = QPainterPath()
        path.addRoundedRect(rect, self._radius, self._radius)

        if self._role == "primary":
            self._paint_primary(p, rect, path)
        elif self._role == "crisis":
            self._paint_crisis(p, rect, path)
        else:
            self._paint_ghost(p, rect, path)
        p.end()

    def _bloom_overlay(
        self, p: QPainter, rect: QRectF, path: QPainterPath, color: QColor, peak_alpha: int
    ) -> None:
        """A soft radial warm bloom rising from the button's lower edge."""
        if self._hover <= 0.001:
            return
        g = QRadialGradient(
            rect.center().x(),
            rect.bottom(),
            rect.width() * 0.85,
        )
        a = int(peak_alpha * self._hover)
        c0 = QColor(color)
        c0.setAlpha(a)
        c1 = QColor(color)
        c1.setAlpha(0)
        g.setColorAt(0.0, c0)
        g.setColorAt(1.0, c1)
        p.save()
        p.setClipPath(path)
        p.fillPath(path, g)
        p.restore()

    def _paint_primary(self, p, rect, path):
        accent = _c("accent")
        ember = _c("ember")
        # Fill warms slightly toward ember as it blooms on hover.
        base = QColor(
            int(accent.red() + (ember.red() - accent.red()) * 0.0),
            int(accent.green() + (ember.green() - accent.green()) * 0.0),
            int(accent.blue() + (ember.blue() - accent.blue()) * 0.0),
        )
        p.fillPath(path, base)
        # Top-down sheen: a touch brighter at the top edge, like light on stone.
        sheen = QRadialGradient(rect.center().x(), rect.top(), rect.width())
        hl = QColor(255, 240, 220, 40)
        sheen.setColorAt(0.0, hl)
        sheen.setColorAt(1.0, QColor(255, 240, 220, 0))
        p.save()
        p.setClipPath(path)
        p.fillPath(path, sheen)
        p.restore()
        # Hover bloom — warm amber rising.
        self._bloom_overlay(p, rect, path, QColor(255, 214, 160), 90)
        # Label — warm near-black on amber for a soft, legible contrast.
        p.setFont(_sans(14, QFont.Weight.Bold))
        p.setPen(QColor("#2A1B0E"))
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())

    def _paint_ghost(self, p, rect, path):
        # No fill, no border at rest — a side-door. On hover, a faint warm
        # wash and the label lifts from muted toward full warm text.
        if self._hover > 0.001:
            wash = QColor(_c("accent"))
            wash.setAlpha(int(20 * self._hover))
            p.fillPath(path, wash)
        muted = _c("text_muted")
        warm = _c("text")
        t = self._hover
        col = QColor(
            int(muted.red() + (warm.red() - muted.red()) * t),
            int(muted.green() + (warm.green() - muted.green()) * t),
            int(muted.blue() + (warm.blue() - muted.blue()) * t),
        )
        p.setFont(_sans(14, QFont.Weight.Medium))
        p.setPen(col)
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())

    def _paint_crisis(self, p, rect, path):
        # Calm OUTLINED danger. Never a filled delete-red. On hover the
        # outline warms and a soft danger bloom rises — a hand reaching back,
        # care rather than alarm.
        crisis = _c("crisis")
        self._bloom_overlay(p, rect, path, crisis, 55)
        pen = p.pen()
        # Outline thickens and warms a touch on hover.
        pen.setColor(crisis)
        pen.setWidthF(1.6 + 0.6 * self._hover)
        p.setPen(pen)
        p.drawPath(path)
        # Label in the same calm danger hue, brightening slightly on hover.
        label = QColor(crisis)
        label = label.lighter(100 + int(14 * self._hover))
        p.setFont(_sans(14, QFont.Weight.DemiBold))
        p.setPen(label)
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())


__all__ = ["HearthCard", "HearthButton", "ONYX"]
