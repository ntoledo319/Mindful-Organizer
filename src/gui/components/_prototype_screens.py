"""Reimagined Hearth screen prototypes — composed from the real components.

Two standalone ``QWidget`` screens that embody ``docs/design/VISION.md`` and
``docs/design/DESIGN_SYSTEM.md``, built *only* from the signature primitives
already in this package — never raw native Qt chrome:

  * :class:`TodayScreen`   — "the doorway" (DESIGN_SYSTEM Wave 2 / audit_02).
    A warm dark room: the Hearthlight encoding energy at the top of a narrow
    reading column, one serif "true sentence" greeting that speaks like a
    companion, one primary "door", two-to-three receding ghost side-doors,
    and a quiet muted timestamp. No card stack. No upsell. A room prepared
    for someone.

  * :class:`BreatheScreen` — "the practice" (audit_04). A full-bleed dim warm
    canvas with the BreathOrb as the hero, a single serif phase line, and the
    barest "I'm done" ghost affordance. The orb is the whole focus.

These are *prototypes*: they render against a hard-coded Onyx ``ROOM`` palette
(a stand-in to be replaced by ``ResolvedTokens`` from the State Engine) and pull
the two-font voice from the same macOS faces the components use. They are
importable and self-contained::

    from gui.components._prototype_screens import TodayScreen, BreatheScreen

Run the bottom ``__main__`` block (or the sibling demo script) under the
offscreen render harness to grab the two screen PNGs.
"""

from __future__ import annotations

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import (
    QColor,
    QFont,
    QFontDatabase,
    QPainter,
    QRadialGradient,
)
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from gui.components.breath_orb import BreathOrb
from gui.components.hearth_surfaces import HearthButton
from gui.components.hearthlight import Hearthlight

# ---------------------------------------------------------------------------
# Room palette — Onyx, the warm dark default.
# TO BE REPLACED BY ResolvedTokens resolved per HearthState at render time.
# ---------------------------------------------------------------------------
ROOM: dict[str, str] = {
    "bg": "#0F0F11",  # warm near-black, never pure black
    "bg_low": "#0A0A0C",  # the dimmer edges of the room
    "surface": "#18181A",
    "raised": "#211C17",
    "text": "#F2EDE6",  # warm off-white
    "text_muted": "#A99B88",  # clears AA 4.5:1 on surface
    "text_faint": "#6F6453",  # the quietest chrome — timestamps, captions
    "accent": "#D9A05B",  # hearthlight amber
    "ember": "#C2703D",  # deeper ember
    "border": "#2E2A24",
}

# Two-font voice (DESIGN_SYSTEM §1). macOS faces for the prototype; the real
# bundled fonts arrive later. Same stacks the components use, so the screen and
# its widgets speak in one voice.
_SERIF_STACK = ["Charter", "Cochin", "Baskerville", "Georgia"]
_SANS_STACK = ["SF Pro Text", "Helvetica Neue", "Helvetica"]


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


def _sans(size: int, weight: QFont.Weight = QFont.Weight.Medium) -> QFont:
    f = QFont(_pick(_SANS_STACK), size)
    f.setWeight(weight)
    f.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    f.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 0.4)
    return f


# ===========================================================================
# A shared dark-room canvas: a warm vignette, painted, not a flat fill.
# ===========================================================================
class _Room(QWidget):
    """Base canvas that paints the warm dark room itself.

    Not a flat ``bg`` rectangle — a real room has light that falls off toward
    its edges. We lay down the near-black ground, darken the corners with a
    wide vignette, and (optionally) let a faint hearth-warmth pool high and
    centred, as if a fire we can't quite see is lighting the page. This is the
    "warm, dim, prepared" feeling the chair test asks for, done in paint.
    """

    def __init__(self, parent=None, *, warm_top: float = 0.0, warm_y: float = 0.20):
        super().__init__(parent)
        # 0..1 — how much warmth pools where the hearth sits (the doorway
        # carries a little; the breathing room stays nearly black so the orb
        # is the only light). ``warm_y`` is the fractional height the warmth
        # centres on, so it can emanate from the ember rather than the ceiling.
        self._warm_top = warm_top
        self._warm_y = warm_y

    def paintEvent(self, _event):  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        rect = QRectF(self.rect())

        # 1) Ground — warm near-black.
        p.fillRect(rect, QColor(ROOM["bg"]))

        # 2) Corner vignette — the room darkens toward its edges so the centre
        #    feels held. A wide radial from the centre out to the far corner,
        #    with extra stops so the falloff is smooth (no concentric banding).
        cx, cy = rect.center().x(), rect.center().y()
        far = (rect.width() ** 2 + rect.height() ** 2) ** 0.5 / 2.0
        vig = QRadialGradient(cx, cy, far)
        low = QColor(ROOM["bg_low"])
        for stop, frac in (
            (0.0, 0.0),
            (0.45, 0.0),
            (0.70, 0.18),
            (0.86, 0.5),
            (1.0, 1.0),
        ):
            c = QColor(low)
            c.setAlpha(int(255 * frac))
            vig.setColorAt(stop, c)
        p.fillRect(rect, vig)

        # 3) Optional hearth-warmth pooling around where the ember sits —
        #    ambient light from the hearth itself spilling into the air. Very
        #    low opacity, many stops; it reads as warmth in the room, never a
        #    swatch or a hard disc.
        if self._warm_top > 0.001:
            wx = rect.center().x()
            wy = rect.top() + rect.height() * self._warm_y
            warm = QRadialGradient(wx, wy, rect.height() * 0.92)
            peak = 30 * self._warm_top
            for stop, frac in (
                (0.0, 1.0),
                (0.22, 0.62),
                (0.45, 0.30),
                (0.70, 0.10),
                (1.0, 0.0),
            ):
                c = QColor(ROOM["accent"])
                c.setAlpha(int(peak * frac))
                warm.setColorAt(stop, c)
            p.fillRect(rect, warm)

        p.end()


# ===========================================================================
# 1. Today — the doorway.
# ===========================================================================
class TodayScreen(_Room):
    """The doorway: a warm room prepared for one person.

    Layout is a single centred reading column (~600px). Top to bottom:
      * the Hearthlight, encoding today's energy as warmth;
      * one warm-serif "true sentence" that speaks like a companion;
      * one primary "door" (the single obvious next thing);
      * two receding ghost side-doors, smaller and muted;
      * a quiet muted timestamp/caption.

    There is no card, no grid, no upsell. The greeting is set as language in
    the reading serif; the doors are controls. Stakes-led whitespace does the
    framing work that a card stack would otherwise do badly (audit_02).
    """

    def __init__(
        self,
        parent=None,
        *,
        name: str = "Alex",
        energy: float = 0.34,
        reduced_motion: bool = False,
    ):
        # The room's warmth pools around where the ember sits (~22% down),
        # so the doorway's light feels like it comes from the hearth itself.
        super().__init__(parent, warm_top=0.75, warm_y=0.22)
        self.setMinimumSize(1440, 900)

        # The true sentence: a companion's voice, present-tense, plainspoken.
        # Two lines so the second can land softer than the first.
        self._line_a = f"It's a heavy morning, {name}."
        self._line_b = "Let's keep today small."
        # The quiet caption — muted chrome, the only place a timestamp lives.
        self._caption = "Tuesday, a little after nine. Nothing is due."

        col = QWidget(self)
        col.setObjectName("readingColumn")
        col.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)

        lay = QVBoxLayout(col)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # --- The Hearthlight, encoding energy. -----------------------------
        # Low-ish energy reads as a banked, smaller-feeling coal. It breathes
        # unless reduced motion is asked for.
        ember = Hearthlight(glow=energy, reduced_motion=reduced_motion, transparent_bg=True)
        ember.setFixedSize(200, 200)
        ember_row = QHBoxLayout()
        ember_row.addStretch(1)
        ember_row.addWidget(ember)
        ember_row.addStretch(1)
        lay.addLayout(ember_row)
        self._ember = ember

        lay.addSpacing(34)

        # --- The true sentence — two serif lines. --------------------------
        line_a = QLabel(self._line_a)
        line_a.setFont(_serif(34, QFont.Weight.Medium))
        line_a.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        line_a.setStyleSheet(f"color: {ROOM['text']}; background: transparent;")
        lay.addWidget(line_a)

        lay.addSpacing(8)

        line_b = QLabel(self._line_b)
        line_b.setFont(_serif(34, QFont.Weight.Normal))
        line_b.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        # The second line eases back toward muted — a softer, lower register,
        # like a voice trailing off into something gentle.
        line_b.setStyleSheet(f"color: {ROOM['accent']}; background: transparent;")
        lay.addWidget(line_b)

        lay.addSpacing(48)

        # --- The one door. -------------------------------------------------
        primary = HearthButton(
            "Sit with me for a minute",
            role="primary",
            reduced_motion=reduced_motion,
        )
        primary.setMinimumHeight(58)
        primary.setMinimumWidth(360)
        door_row = QHBoxLayout()
        door_row.addStretch(1)
        door_row.addWidget(primary)
        door_row.addStretch(1)
        lay.addLayout(door_row)
        self._primary = primary

        lay.addSpacing(26)

        # --- The receding side-doors. --------------------------------------
        # Smaller, muted, no box — they subordinate, they do not vanish.
        side = QVBoxLayout()
        side.setSpacing(4)
        for text in (
            "A few words about today",
            "Tend the medication shelf",
            "Quiet everything for a while",
        ):
            g = HearthButton(text, role="ghost", reduced_motion=reduced_motion)
            g.setMinimumHeight(38)
            r = QHBoxLayout()
            r.addStretch(1)
            r.addWidget(g)
            r.addStretch(1)
            side.addLayout(r)
        lay.addLayout(side)

        lay.addSpacing(40)

        # --- The quiet caption — the only muted-chrome line on the screen. -
        cap = QLabel(self._caption)
        cap.setFont(_sans(12, QFont.Weight.Normal))
        cap.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        cap.setStyleSheet(f"color: {ROOM['text_faint']}; background: transparent;")
        lay.addWidget(cap)

        self._column = col
        self._col_width = 600

    def resizeEvent(self, event):  # noqa: N802
        # Centre the reading column in the room, sized to a page not a
        # dashboard. Sit it a touch above true centre so the room breathes
        # below it (a doorway has floor in front of it).
        super().resizeEvent(event)
        w = self._col_width
        self._column.adjustSize()
        h = self._column.sizeHint().height()
        x = (self.width() - w) // 2
        y = int((self.height() - h) * 0.42)
        self._column.setGeometry(x, y, w, h)


# ===========================================================================
# 2. Breathe — the practice.
# ===========================================================================
class BreatheScreen(_Room):
    """The practice: a dim warm room with the breath as its only light.

    Full-bleed near-black canvas. The :class:`BreathOrb` is centred and large
    — the entire focus, and the only real light in the room. A single serif
    phase line lives inside the orb component itself. The only chrome is a
    barely-there "I'm done" ghost affordance low on the screen, and a quiet
    opening line up top that recedes once breathing begins.
    """

    def __init__(
        self,
        parent=None,
        *,
        reduced_motion: bool = False,
    ):
        # The breathing room stays nearly black — the orb is the only light,
        # so no warm-top pooling competes with it.
        super().__init__(parent, warm_top=0.0)
        self.setMinimumSize(1440, 900)

        # A quiet opening line, set high and small in the serif. It is part of
        # the page (a held instruction), not a control.
        self._opening = "Let's slow this down together."

        # The orb — the hero. Box breathing, generous size.
        self._orb = BreathOrb(self, reduced_motion=reduced_motion, transparent_bg=True)

        # The barest "done" affordance — a ghost side-door, low and muted.
        self._done = HearthButton("I'm steadier now", role="ghost", reduced_motion=reduced_motion)
        self._done.setMinimumHeight(40)
        self._done.setMinimumWidth(200)

    def start(self) -> None:
        self._orb.start()

    def stop(self) -> None:
        self._orb.stop()

    def paintEvent(self, event):  # noqa: N802
        # Paint the room first (warm vignette), then the opening line above
        # where the orb will sit, so the line reads as part of the room.
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # Opening line — serif, faint, riding high above the orb. It uses the
        # quietest readable tone so the breath, not the words, is the focus.
        p.setFont(_serif(20, QFont.Weight.Normal))
        col = QColor(ROOM["text_muted"])
        col.setAlpha(190)
        p.setPen(col)
        top_rect = QRectF(0, self.height() * 0.12, self.width(), self.height() * 0.08)
        p.drawText(
            top_rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, self._opening
        )
        p.end()

    def resizeEvent(self, event):  # noqa: N802
        super().resizeEvent(event)
        # The orb fills the central heart of the room — large, generous, with
        # air on every side. It paints its own phase word beneath its centre.
        # Give the orb a wide box so its ambient radiance and lagging bloom
        # dissolve fully into the room instead of clipping at the widget edge.
        # The orb's own geometry keeps the core well clear of the box, so a
        # large box just means more air for the light to spread through. Height
        # is tuned so the orb sits a touch above true centre and its phase word
        # (painted beneath the core inside the component) lands just below the
        # orb, near it rather than stranded at the floor.
        ow = int(min(self.width() * 0.94, self.height() * 1.55))
        oh = int(self.height() * 0.82)
        ox = (self.width() - ow) // 2
        oy = int(self.height() * 0.10)
        self._orb.setGeometry(ox, oy, ow, oh)

        # The done affordance — low, centred, barely there.
        dw, dh = 220, 40
        self._done.setGeometry(
            (self.width() - dw) // 2,
            int(self.height() * 0.90),
            dw,
            dh,
        )


__all__ = ["TodayScreen", "BreatheScreen", "ROOM"]
