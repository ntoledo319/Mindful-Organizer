"""
ERP — the planning / in-session split (docs/design/audit_05, VISION.md, DESIGN_SYSTEM.md).

ERP is voluntary, supervised distress: someone with OCD deliberately walking into
their worst fear while holding a compulsion they're trying not to perform. The job
is not to log a specimen — it is to be a steady hand on the shoulder and a witness
while they white-knuckle through habituation.

So the surface is two rooms, not one instrument panel.

**Planning** (calm): a painted exposure *ladder* — rungs sorted by predicted SUDS,
each a warm HearthCard with a fill bar showing how high it sits and how many times
it's been faced. Climbing from the bottom is the whole metaphor. Adding a rung is a
quiet inline flow (a word-valued StateSlider + one line), never a native dialog.

**In-session** (radical subtraction): the instrument panel collapses. One exposure
name, a slow breathing timer arc (time as a tide going *out*, not a stopwatch
counting *up*), a live *falling* habituation curve as the emotional payoff, and the
gentlest prompts. The SUDS check is never a QMessageBox — it fades in at the edge as
a non-modal in-canvas prompt with one word-valued slider, so logging never yanks the
person out of the exposure. "I felt an urge" is a single affordance with a quiet
confirming glow.

PRESERVES the data contract: ``_hierarchy`` / ``_sessions`` and the
``hierarchy.json`` + ``erp_sessions.json`` files, ``_load_data`` / ``_save_data`` /
``save_state``, and the ``session_completed`` signal all keep their exact shapes, so
history and the app's wiring are untouched. Adds ``crisis_requested`` (the same
signal mood / diary / journal / panic already use) for when response-prevention
notes name self-harm — note for the integrator: main_window does not yet connect
this for ERP.
"""

from __future__ import annotations

import contextlib
import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

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
    QFontMetrics,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QRadialGradient,
)
from PyQt6.QtWidgets import (
    QFileDialog,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from core.paths import get_data_dir
from gui.components.hearth_surfaces import ONYX, HearthButton, HearthCard
from gui.components.state_controls import (
    PALETTE,
    StateSlider,
    _mix,
    sans_font,
    serif_font,
    warmth_color,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Local palette — Onyx (the warm dark default). A stand-in for ResolvedTokens,
# mirroring the component palettes so nothing hardcodes a stray hex.
# ---------------------------------------------------------------------------
_PAL = {
    "bg": ONYX["background"],
    "surface": ONYX["surface"],
    "raised": ONYX["surface_raised"],
    "text": ONYX["text"],
    "text_muted": ONYX["text_muted"],
    "accent": ONYX["accent"],
    "ember": ONYX["ember"],
    "border": ONYX["border"],
}


# The same conservative self-harm phrasing the other distress surfaces share —
# a supportive nudge toward real help, never a diagnosis.
_RISK_PHRASES = (
    "kill myself",
    "killing myself",
    "end my life",
    "ending my life",
    "want to die",
    "wanna die",
    "wish i was dead",
    "wish i were dead",
    "better off dead",
    "no reason to live",
    "nothing to live for",
    "can't go on",
    "cannot go on",
    "hurt myself",
    "harming myself",
    "harm myself",
    "self harm",
    "self-harm",
    "cut myself",
    "suicidal",
    "suicide",
    "take my own life",
    "end it all",
)


def _names_self_harm(text: str) -> bool:
    low = (text or "").lower()
    return any(phrase in low for phrase in _RISK_PHRASES)


# SUDS reads as a *height* you're facing, not a clinical 0–100. The slider speaks
# these words; they map back onto 0–100 on save so history keeps its data shape.
_HEIGHT_WORDS = [
    "Barely there",
    "A low rung",
    "Halfway up",
    "High and loud",
    "The top of the ladder",
]


def _suds_to_score(t: float) -> int:
    return max(0, min(100, round(t * 100)))


def _score_to_t(score: int) -> float:
    return max(0.0, min(1.0, score / 100.0))


def _height_word(t: float) -> str:
    idx = int(round(max(0.0, min(1.0, t)) * (len(_HEIGHT_WORDS) - 1)))
    return _HEIGHT_WORDS[idx]


# ---------------------------------------------------------------------------
# HeightSlider — a StateSlider that speaks in rungs, not "Okay / Good".
# ---------------------------------------------------------------------------
class HeightSlider(StateSlider):
    """The SUDS control for ERP: the value reads as how high the fear sits."""

    def paintEvent(self, _):  # noqa: N802 — mirrors StateSlider, swaps the word
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        tr = self._track_rect()
        radius = tr.height() / 2
        glow = warmth_color(self._display)

        groove = QPainterPath()
        groove.addRoundedRect(tr, radius, radius)
        p.fillPath(groove, QColor(PALETTE["border"]))

        knob_x = tr.left() + tr.width() * self._display
        fill_rect = QRectF(tr.left(), tr.top(), max(radius * 2, knob_x - tr.left()), tr.height())
        fill_path = QPainterPath()
        fill_path.addRoundedRect(fill_rect, radius, radius)
        grad = QLinearGradient(tr.left(), 0, tr.right(), 0)
        grad.setColorAt(0.0, warmth_color(0.08))
        grad.setColorAt(max(0.001, self._display * 0.5), warmth_color(self._display * 0.6))
        grad.setColorAt(min(0.999, self._display), glow)
        p.fillPath(fill_path, grad)

        bloom = QRadialGradient(QPointF(knob_x, tr.center().y()), 34)
        b0 = QColor(glow)
        b0.setAlpha(120)
        bloom.setColorAt(0.0, b0)
        bloom.setColorAt(1.0, QColor(glow.red(), glow.green(), glow.blue(), 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(bloom)
        p.drawEllipse(QPointF(knob_x, tr.center().y()), 28, 28)

        kr = 13.0
        kg = QRadialGradient(QPointF(knob_x - 3, tr.center().y() - 3), kr * 1.7)
        kg.setColorAt(0.0, _mix(glow, QColor("#FFFFFF"), 0.34))
        kg.setColorAt(1.0, _mix(glow, QColor(PALETTE["bg"]), 0.22))
        p.setBrush(kg)
        p.setPen(QPen(QColor(PALETTE["bg"]), 1.5))
        p.drawEllipse(QPointF(knob_x, tr.center().y()), kr, kr)

        word = _height_word(self._display)
        p.setFont(serif_font(18, QFont.Weight.Medium))
        fm = p.fontMetrics()
        wd = fm.horizontalAdvance(word)
        wx = max(tr.left(), min(tr.right() - wd, knob_x - wd / 2))
        p.setPen(QColor(PALETTE["text"]))
        p.drawText(
            QRectF(wx, tr.top() - 36, wd + 4, 30),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            word,
        )
        p.end()


# ---------------------------------------------------------------------------
# LadderRung — one painted rung in the exposure hierarchy.
# ---------------------------------------------------------------------------
class LadderRung(HearthCard):
    """A rung you can step onto: title, a warm fill bar of its height, times faced.

    A HearthCard (warm stone, soft shadow), painted *over* with a fill bar that
    fills from the left in proportion to the rung's predicted SUDS and warms along
    the ember ramp — so a glance reads "how high is this one" without a number. The
    card lifts a touch on hover; clicking it begins the exposure.
    """

    clicked = pyqtSignal(str)  # emits the rung's id
    remove_requested = pyqtSignal(str)

    def __init__(self, item: dict[str, Any], faced: int, reduced_motion: bool = False, parent=None):
        super().__init__(parent, elevation=1, radius=16)
        self._item = item
        self._faced = faced
        self._reduced_motion = reduced_motion
        self._t = _score_to_t(int(item.get("predicted_suds", 0)))
        self._hover = 0.0
        self.setMinimumHeight(84)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMouseTracking(True)

        # A small recessive "let it go" door, only visible on hover.
        self._remove = HearthButton("Let it go", role="ghost", reduced_motion=reduced_motion)
        self._remove.setParent(self)
        self._remove.setFixedHeight(30)
        self._remove.clicked.connect(lambda: self.remove_requested.emit(self._item.get("id", "")))
        self._remove.hide()

        self._lift = QPropertyAnimation(self, b"hoverAmt", self)
        self._lift.setDuration(0 if reduced_motion else 240)
        self._lift.setEasingCurve(QEasingCurve.Type.OutCubic)

    def _get_hover(self) -> float:
        return self._hover

    def _set_hover(self, v: float) -> None:
        self._hover = v
        self.update()

    hoverAmt = pyqtProperty(float, fget=_get_hover, fset=_set_hover)  # noqa: N815

    def enterEvent(self, e):  # noqa: N802
        self._remove.show()
        if self._reduced_motion:
            self._set_hover(1.0)
        else:
            self._lift.stop()
            self._lift.setStartValue(self._hover)
            self._lift.setEndValue(1.0)
            self._lift.start()
        super().enterEvent(e)

    def leaveEvent(self, e):  # noqa: N802
        self._remove.hide()
        if self._reduced_motion:
            self._set_hover(0.0)
        else:
            self._lift.stop()
            self._lift.setStartValue(self._hover)
            self._lift.setEndValue(0.0)
            self._lift.start()
        super().leaveEvent(e)

    def mouseReleaseEvent(self, e):  # noqa: N802
        if self.rect().contains(e.pos()) and not self._remove.geometry().contains(e.pos()):
            self.clicked.emit(self._item.get("id", ""))
        super().mouseReleaseEvent(e)

    def resizeEvent(self, e):  # noqa: N802
        super().resizeEvent(e)
        bw = self._remove.sizeHint().width()
        self._remove.setGeometry(self.width() - bw - 18, 14, bw, 30)

    def paintEvent(self, event):  # noqa: N802
        super().paintEvent(event)  # the warm card stone + shadow
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        m = 20.0
        glow = warmth_color(self._t)

        # How many times it's been faced — quiet, human, never "(3 sessions)". It
        # rides the right of the title row, ceding the corner to "Let it go" on hover.
        faced = (
            "Not faced yet"
            if self._faced == 0
            else ("Faced once" if self._faced == 1 else f"Faced {self._faced} times")
        )
        faced_w = 0.0
        if not (self._hover > 0.4):
            p.setFont(sans_font(11, QFont.Weight.Medium))
            fmf = p.fontMetrics()
            faced_w = fmf.horizontalAdvance(faced) + 14
            p.setPen(QColor(_PAL["text_muted"]))
            p.drawText(
                QRectF(self.width() - m - faced_w, 16, faced_w, 22),
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                faced,
            )

        # The title, in the reading serif — the rung is a thing you read, not a row.
        title = str(self._item.get("title", "Untitled"))
        p.setFont(serif_font(18, QFont.Weight.Medium))
        p.setPen(QColor(_PAL["text"]))
        reserve = max(96.0, faced_w) if (faced_w or self._hover > 0.4) else 0.0
        tw = self.width() - m * 2 - reserve
        fm = p.fontMetrics()
        title = fm.elidedText(title, Qt.TextElideMode.ElideRight, int(tw))
        p.drawText(
            QRectF(m, 16, tw, 24),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            title,
        )

        # The fill bar — how high this rung sits, warming along the ember ramp.
        bar = QRectF(m, self.height() - 22, self.width() - m * 2, 7)
        br = bar.height() / 2
        groove = QPainterPath()
        groove.addRoundedRect(bar, br, br)
        p.fillPath(groove, QColor(_PAL["border"]))
        fw = max(bar.height(), bar.width() * self._t)
        fill = QRectF(bar.left(), bar.top(), fw, bar.height())
        fpath = QPainterPath()
        fpath.addRoundedRect(fill, br, br)
        fg = QLinearGradient(bar.left(), 0, bar.right(), 0)
        fg.setColorAt(0.0, warmth_color(0.1))
        fg.setColorAt(1.0, glow)
        p.fillPath(fpath, fg)
        p.end()


# ---------------------------------------------------------------------------
# HabituationCurve — the live, falling line. The emotional payoff of ERP.
# ---------------------------------------------------------------------------
class HabituationCurve(QWidget):
    """A small painted line chart that draws SUDS points as a *descending* warm line.

    The user watches their own anxiety fall during the session. Empty, it gives a
    gentle invitation rather than an axis grid; with one point it shows a warm dot;
    with more, it connects them with a smooth, eased path. No matplotlib, no list.
    """

    def __init__(self, reduced_motion: bool = False, parent=None):
        super().__init__(parent)
        self._points: list[tuple[int, int]] = []  # (elapsed_sec, suds 0-100)
        self._reduced_motion = reduced_motion
        self.setMinimumHeight(150)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

    def set_points(self, points: list[tuple[int, int]]) -> None:
        self._points = list(points)
        self.update()

    def clear(self) -> None:
        self._points = []
        self.update()

    def paintEvent(self, _):  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        m = 22.0
        plot = QRectF(m, m + 6, self.width() - 2 * m, self.height() - 2 * m - 22)

        # A single faint baseline — the floor the fear settles toward. Not a grid.
        p.setPen(QPen(QColor(_PAL["border"]), 1.0))
        p.drawLine(
            QPointF(plot.left(), plot.bottom()),
            QPointF(plot.right(), plot.bottom()),
        )

        if not self._points:
            p.setFont(serif_font(15))
            p.setPen(QColor(_PAL["text_muted"]))
            p.drawText(
                plot,
                Qt.AlignmentFlag.AlignCenter,
                "Watch it come down.\nEach check-in lands here.",
            )
            p.end()
            return

        # Map points. X by elapsed time; Y auto-scaled to the data's own range so a
        # 78→42 fall reads as a real descent, not a near-flat line lost in a 0–100
        # window. A little headroom above the peak and below the floor frames it.
        max_t = max(1, max(t for t, _ in self._points))
        n = len(self._points)
        sud_vals = [s for _, s in self._points]
        hi = max(sud_vals)
        lo = min(sud_vals)
        span = max(12, hi - lo)  # never collapse to a flat line on tiny moves
        top_v = hi + span * 0.28
        bot_v = max(0, lo - span * 0.45)
        rng = max(1.0, top_v - bot_v)

        def to_xy(i: int, t: int, suds: int) -> QPointF:
            x = plot.left() + (plot.width() * (t / max_t) if n > 1 else plot.width() * 0.5)
            y = plot.bottom() - plot.height() * ((suds - bot_v) / rng)
            return QPointF(x, y)

        pts = [to_xy(i, t, s) for i, (t, s) in enumerate(self._points)]

        # A soft warm wash under the line, so the falling shape reads as relief.
        if len(pts) >= 2:
            area = QPainterPath()
            area.moveTo(pts[0].x(), plot.bottom())
            for q in pts:
                area.lineTo(q)
            area.lineTo(pts[-1].x(), plot.bottom())
            area.closeSubpath()
            wash = QLinearGradient(0, plot.top(), 0, plot.bottom())
            top = QColor(_PAL["accent"])
            top.setAlpha(60)
            bot = QColor(_PAL["accent"])
            bot.setAlpha(0)
            wash.setColorAt(0.0, top)
            wash.setColorAt(1.0, bot)
            p.fillPath(area, wash)

            line = QPainterPath()
            line.moveTo(pts[0])
            for j in range(1, len(pts)):
                a, b = pts[j - 1], pts[j]
                cx = (a.x() + b.x()) / 2
                line.cubicTo(cx, a.y(), cx, b.y(), b.x(), b.y())
            pen = QPen(QColor(_PAL["accent"]))
            pen.setWidthF(2.6)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            p.setPen(pen)
            p.drawPath(line)

        # The points themselves — warm coals, the latest one brightest.
        for i, (q, (_, suds)) in enumerate(zip(pts, self._points, strict=True)):
            r = 4.5 if i < len(pts) - 1 else 6.5
            col = warmth_color(_score_to_t(suds))
            if i == len(pts) - 1:
                halo = QRadialGradient(q, r * 2.6)
                hc = QColor(col)
                hc.setAlpha(150)
                halo.setColorAt(0.0, hc)
                halo.setColorAt(1.0, QColor(col.red(), col.green(), col.blue(), 0))
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(halo)
                p.drawEllipse(q, r * 2.4, r * 2.4)
            p.setBrush(_mix(col, QColor("#FFFFFF"), 0.25))
            p.setPen(QPen(QColor(_PAL["bg"]), 1.4))
            p.drawEllipse(q, r, r)

        # Two quiet word markers tell the story of the fall: where it started, and
        # where it sits now — the descent as language, never a numeric axis.
        if len(pts) >= 2:
            p.setFont(sans_font(11, QFont.Weight.Medium))
            first_w = _height_word(_score_to_t(self._points[0][1]))
            p.setPen(QColor(_PAL["text_muted"]))
            p.drawText(
                QRectF(pts[0].x() - 4, pts[0].y() - 26, 200, 18),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                first_w,
            )
            now_w = _height_word(_score_to_t(self._points[-1][1]))
            p.setPen(QColor(_PAL["accent"]))
            fm = p.fontMetrics()
            tw = fm.horizontalAdvance(now_w)
            p.drawText(
                QRectF(pts[-1].x() - tw - 2, pts[-1].y() + 12, tw + 4, 18),
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                now_w,
            )
        p.end()


# ---------------------------------------------------------------------------
# SessionTimerArc — time as a tide going OUT, not a stopwatch counting up.
# ---------------------------------------------------------------------------
class SessionTimerArc(QWidget):
    """A slowly filling warm arc + a quiet elapsed read.

    Rather than a hard ``00:00:00`` counting *up* (a countup of suffering), the arc
    fills slowly toward a soft target and *breathes* — the room staying with you
    while time passes. The minutes are shown small and calm beneath, in control sans.
    """

    def __init__(self, reduced_motion: bool = False, parent=None):
        super().__init__(parent)
        self._reduced_motion = reduced_motion
        self._elapsed = 0  # seconds
        self._target = 20 * 60  # a gentle 20-minute horizon; the arc never demands
        self._breath = 0.0
        self.setMinimumSize(220, 220)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self._breathe = QPropertyAnimation(self, b"breath", self)
        self._breathe.setStartValue(0.0)
        self._breathe.setEndValue(1.0)
        self._breathe.setDuration(5000)
        self._breathe.setEasingCurve(QEasingCurve.Type.InOutSine)
        if not reduced_motion:
            self._breathe.setLoopCount(-1)
            self._breathe.start()
        else:
            self._breath = 0.5

    def _get_breath(self) -> float:
        return self._breath

    def _set_breath(self, v: float) -> None:
        # Ping-pong via a triangle so it eases up then down without a snap.
        self._breath = v
        self.update()

    breath = pyqtProperty(float, fget=_get_breath, fset=_set_breath)  # noqa: N815

    def set_elapsed(self, seconds: int) -> None:
        self._elapsed = max(0, seconds)
        self.update()

    def paintEvent(self, _):  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        side = min(self.width(), self.height())
        pad = side * 0.16
        rect = QRectF(
            (self.width() - side) / 2 + pad,
            (self.height() - side) / 2 + pad,
            side - 2 * pad,
            side - 2 * pad,
        )
        center = rect.center()
        thickness = rect.width() * 0.07

        breath_tri = 1.0 - abs(self._breath * 2.0 - 1.0)  # 0->1->0
        frac = min(1.0, self._elapsed / self._target)

        # A wide, soft pooled glow behind the arc — the room lit from within.
        bloom = QRadialGradient(center, rect.width() * 0.62)
        warm = QColor(_PAL["accent"])
        warm.setAlpha(int(26 + 18 * breath_tri))
        bloom.setColorAt(0.0, warm)
        bloom.setColorAt(1.0, QColor(warm.red(), warm.green(), warm.blue(), 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(bloom)
        p.drawEllipse(center, rect.width() * 0.6, rect.width() * 0.6)

        stroke = rect.adjusted(thickness / 2, thickness / 2, -thickness / 2, -thickness / 2)

        # The unlit groove — a full quiet ring.
        gpen = QPen(QColor(_PAL["border"]))
        gpen.setWidthF(thickness)
        gpen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(gpen)
        p.drawArc(stroke, 0, 360 * 16)

        # The filled arc — starts at top, sweeps clockwise as time goes out.
        if frac > 0.001:
            apen = QPen(_mix(QColor(_PAL["accent"]), QColor("#EEC489"), 0.3 + 0.4 * breath_tri))
            apen.setWidthF(thickness)
            apen.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(apen)
            p.drawArc(stroke, 90 * 16, -int(360 * frac * 16))

        # The elapsed minutes — small, calm, control sans. Not a loud clock.
        mins = self._elapsed // 60
        secs = self._elapsed % 60
        if mins >= 1:
            big = f"{mins}"
            unit = "minute in" if mins == 1 else "minutes in"
        else:
            big = f"{secs}"
            unit = "seconds in"
        p.setFont(serif_font(40, QFont.Weight.Medium))
        p.setPen(QColor(_PAL["text"]))
        p.drawText(
            QRectF(
                rect.left(), center.y() - rect.height() * 0.20, rect.width(), rect.height() * 0.3
            ),
            Qt.AlignmentFlag.AlignCenter,
            big,
        )
        p.setFont(sans_font(11, QFont.Weight.DemiBold))
        p.setPen(QColor(_PAL["text_muted"]))
        p.drawText(
            QRectF(
                rect.left(), center.y() + rect.height() * 0.10, rect.width(), rect.height() * 0.16
            ),
            Qt.AlignmentFlag.AlignCenter,
            unit.upper(),
        )
        p.end()


# ---------------------------------------------------------------------------
# InCanvasPrompt — the non-modal SUDS check that fades in at the edge.
# ---------------------------------------------------------------------------
class InCanvasPrompt(QWidget):
    """A translucent in-canvas card that fades in (never a QMessageBox).

    Holds one serif question, one word-valued HeightSlider, and a single warm
    "set it" action. It slides over the session canvas without stealing focus from
    the exposure — answering it is a gentle aside, not an interruption.
    """

    submitted = pyqtSignal(int)  # the SUDS score 0-100
    dismissed = pyqtSignal()

    def __init__(self, reduced_motion: bool = False, parent=None):
        super().__init__(parent)
        self._reduced_motion = reduced_motion
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)

        self._card = HearthCard(self, elevation=2, radius=18)
        lay = QVBoxLayout(self._card)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(14)

        q = QLabel("When you're ready — how high is it right now?")
        q.setFont(serif_font(18))
        q.setWordWrap(True)
        q.setStyleSheet(f"color: {_PAL['text']}; background: transparent;")
        lay.addWidget(q)

        self._slider = HeightSlider(value=0.6, reduced_motion=reduced_motion)
        lay.addWidget(self._slider)

        row = QHBoxLayout()
        not_now = HearthButton("Not yet", role="ghost", reduced_motion=reduced_motion)
        not_now.clicked.connect(self._dismiss)
        row.addWidget(not_now)
        row.addStretch()
        setit = HearthButton("Set it down", role="primary", reduced_motion=reduced_motion)
        setit.clicked.connect(self._submit)
        row.addWidget(setit)
        lay.addLayout(row)

        self._eff = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._eff)
        self._eff.setOpacity(0.0)
        self._anim = QPropertyAnimation(self._eff, b"opacity", self)
        self._anim.setDuration(0 if reduced_motion else 520)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.hide()

    def _layout_card(self) -> None:
        margin = 28
        cw = min(440, self.width() - margin * 2)
        ch = self._card.sizeHint().height()
        if ch < 200:
            ch = 230
        # Sit it low, toward the bottom edge — an aside, never centered/blocking.
        x = (self.width() - cw) // 2
        y = self.height() - ch - margin
        self._card.setGeometry(x, max(margin, y), cw, ch)

    def resizeEvent(self, e):  # noqa: N802
        super().resizeEvent(e)
        self._layout_card()

    def reveal(self, suds_t: float = 0.6) -> None:
        self._slider.setValue(suds_t, animate=False)
        # Always fill the parent page before laying the card out, so the prompt
        # never reveals at a stale (or zero) size.
        par = self.parentWidget()
        if par is not None:
            self.setGeometry(par.rect())
        self._layout_card()
        self.show()
        self.raise_()
        if self._reduced_motion:
            self._eff.setOpacity(1.0)
            return
        self._anim.stop()
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.start()

    def _fade_out(self, then) -> None:
        if self._reduced_motion:
            self.hide()
            then()
            return
        self._anim.stop()
        self._anim.setStartValue(self._eff.opacity())
        self._anim.setEndValue(0.0)

        def done():
            self.hide()
            then()

        with contextlib.suppress(TypeError):
            self._anim.finished.disconnect()
        self._anim.finished.connect(done)
        self._anim.start()

    def _submit(self) -> None:
        score = _suds_to_score(self._slider.value())
        self._fade_out(lambda: self.submitted.emit(score))

    def _dismiss(self) -> None:
        self._fade_out(self.dismissed.emit)


# ---------------------------------------------------------------------------
# _OverlayPage — a page that keeps a single child overlay sized to itself.
# ---------------------------------------------------------------------------
class _OverlayPage(QWidget):
    """A plain page whose ``overlay`` child always fills it (for the SUDS fade)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.overlay: QWidget | None = None

    def resizeEvent(self, e):  # noqa: N802
        super().resizeEvent(e)
        if self.overlay is not None:
            self.overlay.setGeometry(self.rect())


# ---------------------------------------------------------------------------
# Widget
# ---------------------------------------------------------------------------


class ERPWidget(QWidget):
    """ERP, re-architected as planning (calm) and in-session (minimal) rooms.

    Planning is a painted ladder of rungs; in-session is radical subtraction with a
    breathing timer, a falling habituation curve, and a non-modal SUDS prompt. The
    data contract (``_hierarchy`` / ``_sessions``, the JSON files, ``save_state``,
    and the ``session_completed`` signal) is preserved exactly.
    """

    session_completed = pyqtSignal(dict)
    crisis_requested = pyqtSignal()

    # The session offers a gentle SUDS check on this cadence — a quiet fade, never
    # a modal. Honors the original 5-minute rhythm.
    _SUDS_CHECK_INTERVAL_MS = 5 * 60 * 1000

    def __init__(self, main_window: Any, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.main_window = main_window

        # Preserve the original (best-effort) manager handle.
        self._erp_manager = None
        with contextlib.suppress(Exception):
            self._erp_manager = main_window.erp_tracker

        # Data (unchanged shapes).
        self._hierarchy: list[dict[str, Any]] = []
        self._sessions: list[dict[str, Any]] = []
        self._active_session: dict[str, Any] | None = None
        self._session_suds: list[dict[str, Any]] = []
        self._session_urges: list[dict[str, Any]] = []

        self._reduced_motion = self._detect_reduced_motion()
        self._adding = False  # inline add-a-rung flow open?

        # Timers (preserve cadence + signature behavior).
        self._exposure_timer = QTimer(self)
        self._exposure_timer.setInterval(1000)
        self._exposure_timer.timeout.connect(self._tick_exposure)
        self._exposure_elapsed_sec: int = 0

        self._suds_prompt_timer = QTimer(self)
        self._suds_prompt_timer.setInterval(self._SUDS_CHECK_INTERVAL_MS)
        self._suds_prompt_timer.timeout.connect(self._prompt_suds)

        self._urge_glow_timer = QTimer(self)
        self._urge_glow_timer.setSingleShot(True)
        self._urge_glow_timer.timeout.connect(self._clear_urge_echo)

        self._page_anim: QPropertyAnimation | None = None

        self._load_data()
        self._build_ui()
        self._refresh_ladder()

    # ------------------------------------------------------------------
    # Persistence (unchanged data contract)
    # ------------------------------------------------------------------

    def _data_dir(self) -> Path:
        try:
            base = Path(self.main_window.data_dir)
        except (AttributeError, TypeError):
            base = get_data_dir()
        p = base / "erp"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def _load_data(self) -> None:
        hfile = self._data_dir() / "hierarchy.json"
        sfile = self._data_dir() / "erp_sessions.json"
        if hfile.exists():
            try:
                with open(hfile) as fh:
                    self._hierarchy = json.load(fh)
            except (json.JSONDecodeError, OSError) as exc:
                logger.debug(f"ERP hierarchy load error: {exc}")
        if sfile.exists():
            try:
                with open(sfile) as fh:
                    self._sessions = json.load(fh)
            except (json.JSONDecodeError, OSError) as exc:
                logger.debug(f"ERP sessions load error: {exc}")

    def _save_data(self) -> None:
        dd = self._data_dir()
        dd.mkdir(parents=True, exist_ok=True)
        try:
            with open(dd / "hierarchy.json", "w") as fh:
                json.dump(self._hierarchy, fh, indent=2, default=str)
            with open(dd / "erp_sessions.json", "w") as fh:
                json.dump(self._sessions, fh, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save ERP data: {e}")

    # ------------------------------------------------------------------
    # Accessibility
    # ------------------------------------------------------------------

    def _detect_reduced_motion(self) -> bool:
        try:
            from utils.accessibility import detect_reduced_motion

            return detect_reduced_motion()
        except Exception:
            return False

    # ------------------------------------------------------------------
    # The warm room background
    # ------------------------------------------------------------------

    def paintEvent(self, _event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), QColor(_PAL["bg"]))
        cx = self.width() / 2
        cy = self.height() * 0.30
        grad = QRadialGradient(cx, cy, self.width() * 0.7)
        warm = QColor(_PAL["accent"])
        warm.setAlpha(24)
        grad.setColorAt(0.0, warm)
        edge = QColor(warm)
        edge.setAlpha(0)
        grad.setColorAt(1.0, edge)
        p.fillRect(self.rect(), grad)
        p.end()

    # ------------------------------------------------------------------
    # Structure
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        self._stack = QStackedWidget()
        self._stack.setStyleSheet("background: transparent;")
        outer.addWidget(self._stack)

        self._plan_page = self._build_plan_page()
        self._session_page = self._build_session_page()
        self._stack.addWidget(self._plan_page)  # index 0 — planning, the default
        self._stack.addWidget(self._session_page)  # index 1 — in-session
        self._stack.setCurrentIndex(0)

    # -- PLANNING: the ladder ---------------------------------------------

    def _build_plan_page(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        pcol = QVBoxLayout(page)
        pcol.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setStyleSheet(
            "QScrollArea { background: transparent; } QScrollArea > QWidget { background: transparent; }"
        )
        scroll.viewport().setStyleSheet("background: transparent;")
        pcol.addWidget(scroll)

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        self._plan_col = QVBoxLayout(container)
        self._plan_col.setContentsMargins(56, 40, 56, 40)
        self._plan_col.setSpacing(0)
        scroll.setWidget(container)

        # The header — a witness, not a category label.
        head = QLabel("Your ladder")
        head.setFont(serif_font(28, QFont.Weight.Medium))
        head.setStyleSheet(f"color: {_PAL['text']}; background: transparent;")
        self._plan_col.addWidget(head)
        self._plan_col.addSpacing(6)

        lede = QLabel(
            "The fears you're working through, lowest rung first. Step onto one "
            "when you're ready — you'll stay with it, and watch it come down."
        )
        lede.setFont(serif_font(16))
        lede.setWordWrap(True)
        lede.setStyleSheet(f"color: {_PAL['text_muted']}; background: transparent;")
        self._plan_col.addWidget(lede)
        self._plan_col.addSpacing(24)

        # The rungs land here, between the lede and the add flow.
        self._rungs_box = QVBoxLayout()
        self._rungs_box.setSpacing(12)
        self._plan_col.addLayout(self._rungs_box)

        # The empty-state line (shown only when there are no rungs).
        self._empty_line = QLabel(
            "No rungs yet. When you and your therapist are ready, name one fear to "
            "start with — something that scares you a little, not a lot."
        )
        self._empty_line.setFont(serif_font(16))
        self._empty_line.setWordWrap(True)
        self._empty_line.setStyleSheet(f"color: {_PAL['text_muted']}; background: transparent;")
        self._plan_col.addWidget(self._empty_line)

        self._plan_col.addSpacing(20)

        # The inline "add a rung" flow — a quiet card, not a native dialog.
        self._add_card = self._build_add_card()
        self._plan_col.addWidget(self._add_card)
        self._add_card.hide()

        # The single soft door to open the add flow.
        add_row = QHBoxLayout()
        self._add_btn = HearthButton(
            "Name a new fear to face", role="ghost", reduced_motion=self._reduced_motion
        )
        self._add_btn.clicked.connect(self._open_add)
        add_row.addWidget(self._add_btn)
        add_row.addStretch()
        self._plan_col.addLayout(add_row)

        self._plan_col.addStretch(1)

        # A de-lawyered hand on the shoulder, then the therapist export — recessive.
        self._plan_col.addSpacing(28)
        note = QLabel(
            "Do this alongside your therapist — they're the map, Hearth is the metronome."
        )
        note.setFont(serif_font(13))
        note.setWordWrap(True)
        note.setStyleSheet(f"color: {_PAL['text_muted']}; background: transparent;")
        self._plan_col.addWidget(note)
        self._plan_col.addSpacing(12)

        export_row = QHBoxLayout()
        export_row.addStretch()
        self._export_btn = HearthButton(
            "Share these notes with your therapist",
            role="ghost",
            reduced_motion=self._reduced_motion,
        )
        self._export_btn.clicked.connect(self._export_report)
        export_row.addWidget(self._export_btn)
        self._plan_col.addLayout(export_row)

        # An ambient confirmation toast, pinned by the page.
        self._toast = _Toast(page, reduced_motion=self._reduced_motion)

        return page

    def _build_add_card(self) -> HearthCard:
        card = HearthCard(elevation=2, radius=18)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(24, 22, 24, 22)
        lay.setSpacing(14)

        q = QLabel("What's the fear?")
        q.setFont(serif_font(18, QFont.Weight.Medium))
        q.setStyleSheet(f"color: {_PAL['text']}; background: transparent;")
        lay.addWidget(q)

        self._add_edit = QLineEdit()
        self._add_edit.setPlaceholderText("Touching the door handle without washing after…")
        self._add_edit.setFont(serif_font(15))
        self._add_edit.setStyleSheet(
            f"""
            QLineEdit {{
                background: {_PAL["surface"]};
                color: {_PAL["text"]};
                border: 1px solid {_PAL["border"]};
                border-radius: 12px;
                padding: 11px 14px;
                selection-background-color: {_PAL["accent"]};
            }}
            QLineEdit:focus {{ border: 1px solid {_PAL["accent"]}; }}
            """
        )
        lay.addWidget(self._add_edit)

        prompt = QLabel("How high does just thinking about it feel?")
        prompt.setFont(serif_font(15))
        prompt.setStyleSheet(f"color: {_PAL['text_muted']}; background: transparent;")
        lay.addWidget(prompt)
        lay.addSpacing(2)

        self._add_slider = HeightSlider(value=0.4, reduced_motion=self._reduced_motion)
        lay.addWidget(self._add_slider)

        row = QHBoxLayout()
        cancel = HearthButton("Never mind", role="ghost", reduced_motion=self._reduced_motion)
        cancel.clicked.connect(self._close_add)
        row.addWidget(cancel)
        row.addStretch()
        save = HearthButton(
            "Add it to the ladder", role="primary", reduced_motion=self._reduced_motion
        )
        save.clicked.connect(self._commit_add)
        row.addWidget(save)
        lay.addLayout(row)
        return card

    # -- IN-SESSION: radical subtraction ----------------------------------

    def _build_session_page(self) -> QWidget:
        page = _OverlayPage()
        page.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(page)
        lay.setContentsMargins(48, 30, 48, 28)
        lay.setSpacing(0)
        lay.addStretch(1)

        # The exposure name, in the reading serif — the one thing in focus.
        self._session_title = QLabel("")
        self._session_title.setFont(serif_font(26, QFont.Weight.Medium))
        self._session_title.setWordWrap(True)
        self._session_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._session_title.setStyleSheet(f"color: {_PAL['text']}; background: transparent;")
        lay.addWidget(self._session_title)
        lay.addSpacing(4)

        steady = QLabel("Stay with it. The fear always comes down — watch.")
        steady.setFont(serif_font(16))
        steady.setAlignment(Qt.AlignmentFlag.AlignCenter)
        steady.setStyleSheet(f"color: {_PAL['text_muted']}; background: transparent;")
        lay.addWidget(steady)
        lay.addSpacing(18)

        # The timer arc — time as a tide going out, centered.
        arc_row = QHBoxLayout()
        arc_row.addStretch()
        self._timer_arc = SessionTimerArc(reduced_motion=self._reduced_motion)
        self._timer_arc.setFixedSize(230, 230)
        arc_row.addWidget(self._timer_arc)
        arc_row.addStretch()
        lay.addLayout(arc_row)
        lay.addSpacing(14)

        # The live, falling habituation curve — the emotional payoff.
        self._curve = HabituationCurve(reduced_motion=self._reduced_motion)
        lay.addWidget(self._curve)
        lay.addSpacing(16)

        # The two gentle affordances, side by side. "I felt an urge" leaves a quiet
        # confirming glow; "How high is it?" reveals the in-canvas prompt.
        self._urge_echo = QLabel("")
        self._urge_echo.setFont(serif_font(15))
        self._urge_echo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._urge_echo.setStyleSheet(f"color: {_PAL['accent']}; background: transparent;")
        self._urge_echo.setMinimumHeight(22)
        lay.addWidget(self._urge_echo)
        lay.addSpacing(4)

        affords = QHBoxLayout()
        affords.addStretch()
        self._urge_btn = HearthButton(
            "I felt an urge", role="ghost", reduced_motion=self._reduced_motion
        )
        self._urge_btn.clicked.connect(self._record_urge)
        affords.addWidget(self._urge_btn)
        affords.addSpacing(8)
        self._check_btn = HearthButton(
            "How high is it now?", role="primary", reduced_motion=self._reduced_motion
        )
        self._check_btn.clicked.connect(self._prompt_suds)
        affords.addWidget(self._check_btn)
        affords.addStretch()
        lay.addLayout(affords)

        lay.addSpacing(20)

        # The way out — recessive. Ending is the user's call, never urged.
        end_row = QHBoxLayout()
        end_row.addStretch()
        self._end_btn = HearthButton(
            "I'm done for now", role="ghost", reduced_motion=self._reduced_motion
        )
        self._end_btn.clicked.connect(self._end_exposure)
        end_row.addWidget(self._end_btn)
        end_row.addStretch()
        lay.addLayout(end_row)

        lay.addStretch(1)

        # The non-modal SUDS prompt overlays the whole session page.
        self._suds_prompt = InCanvasPrompt(reduced_motion=self._reduced_motion, parent=page)
        self._suds_prompt.submitted.connect(self._record_suds)
        self._suds_prompt.dismissed.connect(lambda: None)
        page.overlay = self._suds_prompt

        return page

    # ------------------------------------------------------------------
    # Ladder rendering
    # ------------------------------------------------------------------

    def _clear_layout(self, layout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

    def _refresh_ladder(self) -> None:
        self._clear_layout(self._rungs_box)
        # Highest rungs at the top, lowest at the bottom — you climb upward.
        sorted_h = sorted(self._hierarchy, key=lambda h: h.get("predicted_suds", 0), reverse=True)
        for item in sorted_h:
            faced = len([s for s in self._sessions if s.get("hierarchy_id") == item.get("id")])
            rung = LadderRung(item, faced, reduced_motion=self._reduced_motion)
            rung.clicked.connect(self._start_exposure)
            rung.remove_requested.connect(self._remove_rung)
            self._rungs_box.addWidget(rung)
        self._empty_line.setVisible(not sorted_h)

    # ------------------------------------------------------------------
    # Add-a-rung inline flow
    # ------------------------------------------------------------------

    def _open_add(self) -> None:
        self._adding = True
        self._add_edit.clear()
        self._add_slider.setValue(0.4, animate=False)
        self._add_card.show()
        self._add_btn.hide()
        self._add_edit.setFocus()

    def _close_add(self) -> None:
        self._adding = False
        self._add_card.hide()
        self._add_btn.show()

    def _commit_add(self) -> None:
        title = self._add_edit.text().strip()
        if not title:
            self._add_edit.setFocus()
            return
        # ERP works with intrusive thoughts, so a named fear can carry real risk
        # language. If the words name self-harm, reach back toward help — the same
        # route mood / diary / journal / panic use — before anything else.
        if _names_self_harm(title):
            self.crisis_requested.emit()
            self._toast.show_message(
                "That sounds heavy to carry. Let's get you somewhere safer first."
            )
            return
        item = {
            "id": uuid.uuid4().hex[:12],
            "title": title,
            "predicted_suds": _suds_to_score(self._add_slider.value()),
            "created_at": datetime.now().isoformat(),
        }
        self._hierarchy.append(item)
        self._save_data()
        self._close_add()
        self._refresh_ladder()
        self._toast.show_message("Added. One rung at a time — that's the way up.")

    def _remove_rung(self, rung_id: str) -> None:
        self._hierarchy = [h for h in self._hierarchy if h.get("id") != rung_id]
        self._save_data()
        self._refresh_ladder()
        self._toast.show_message("Let go. You can always name it again.")

    # ------------------------------------------------------------------
    # Exposure session
    # ------------------------------------------------------------------

    def _start_exposure(self, rung_id: str) -> None:
        if self._active_session:
            return
        item = next((h for h in self._hierarchy if h.get("id") == rung_id), None)
        if item is None:
            return

        self._active_session = {
            "id": uuid.uuid4().hex[:12],
            "hierarchy_id": item.get("id"),
            "hierarchy_title": item.get("title"),
            "predicted_suds": item.get("predicted_suds", 0),
            "started_at": datetime.now().isoformat(),
            "suds_log": [],
            "urge_log": [],
            "rp_notes": "",
        }
        self._session_suds.clear()
        self._session_urges.clear()
        self._exposure_elapsed_sec = 0

        self._session_title.setText(str(item.get("title", "")))
        self._timer_arc.set_elapsed(0)
        self._curve.clear()
        self._urge_echo.setText("")

        self._fade_to(1)
        self._exposure_timer.start()
        self._suds_prompt_timer.start()

    def _tick_exposure(self) -> None:
        self._exposure_elapsed_sec += 1
        self._timer_arc.set_elapsed(self._exposure_elapsed_sec)

    def _prompt_suds(self) -> None:
        if not self._active_session:
            return
        # The non-modal in-canvas fade — never a QMessageBox interrupting the work.
        last_t = _score_to_t(self._session_suds[-1]["suds"]) if self._session_suds else 0.6
        self._suds_prompt.reveal(last_t)

    def _record_suds(self, suds_val: int) -> None:
        if not self._active_session:
            return
        entry = {
            "time": datetime.now().isoformat(),
            "elapsed_sec": self._exposure_elapsed_sec,
            "suds": int(suds_val),
        }
        self._session_suds.append(entry)
        self._curve.set_points([(s["elapsed_sec"], s["suds"]) for s in self._session_suds])

    def _record_urge(self) -> None:
        if not self._active_session:
            return
        entry = {
            "time": datetime.now().isoformat(),
            "elapsed_sec": self._exposure_elapsed_sec,
            "urge_strength": 0,
            "resisted": True,
        }
        self._session_urges.append(entry)
        # A quiet confirming glow — that IS the whole point.
        self._urge_echo.setText("Noticed, and not acted on. That's the whole point.")
        self._urge_glow_timer.start(4000)

    def _clear_urge_echo(self) -> None:
        self._urge_echo.setText("")

    def _end_exposure(self) -> None:
        if not self._active_session:
            return

        self._exposure_timer.stop()
        self._suds_prompt_timer.stop()
        self._suds_prompt.hide()

        self._active_session["ended_at"] = datetime.now().isoformat()
        self._active_session["duration_sec"] = self._exposure_elapsed_sec
        self._active_session["suds_log"] = list(self._session_suds)
        self._active_session["urge_log"] = list(self._session_urges)
        self._active_session["rp_notes"] = (
            ""  # response-prevention notes now live in-session as urges
        )
        self._active_session["urges_resisted"] = len(self._session_urges)

        if self._session_suds:
            self._active_session["peak_suds"] = max(s["suds"] for s in self._session_suds)
            self._active_session["final_suds"] = self._session_suds[-1]["suds"]
        else:
            self._active_session["peak_suds"] = 0
            self._active_session["final_suds"] = 0

        finished = self._active_session
        self._sessions.append(finished)
        self.session_completed.emit(finished)

        self._active_session = None
        self._save_data()
        self._refresh_ladder()
        self._fade_to(0)

        # A warm, specific close — witness, not score. Surfaced as a toast.
        self._toast.show_message(self._close_line(finished))

    def _close_line(self, session: dict[str, Any]) -> str:
        mins = max(1, round(session.get("duration_sec", 0) / 60))
        peak = session.get("peak_suds", 0)
        final = session.get("final_suds", 0)
        if peak and final < peak:
            return (
                f"You stayed {mins} minutes, and it fell from {peak} to {final}. "
                "That's you teaching your brain it's safe."
            )
        return f"You stayed {mins} minutes. Staying is the brave part — well done."

    # ------------------------------------------------------------------
    # Mode transitions
    # ------------------------------------------------------------------

    def _fade_to(self, index: int) -> None:
        if self._reduced_motion:
            self._stack.setCurrentIndex(index)
            return
        target = self._stack.widget(index)
        eff = QGraphicsOpacityEffect(target)
        target.setGraphicsEffect(eff)
        eff.setOpacity(0.0)
        self._stack.setCurrentIndex(index)
        anim = QPropertyAnimation(eff, b"opacity", self)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setDuration(480)
        anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        anim.finished.connect(lambda: target.setGraphicsEffect(None))
        anim.start()
        self._page_anim = anim

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def _export_report(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Share with your therapist", "erp_notes.json", "JSON (*.json)"
        )
        if not path:
            return
        report = {
            "exported_at": datetime.now().isoformat(),
            "hierarchy": self._hierarchy,
            "sessions": self._sessions,
            "summary": {
                "total_sessions": len(self._sessions),
                "total_urges_resisted": sum(s.get("urges_resisted", 0) for s in self._sessions),
            },
        }
        try:
            with open(path, "w") as fh:
                json.dump(report, fh, indent=2, default=str)
            self._toast.show_message("Saved. Ready to bring to your next session.")
        except Exception as exc:
            logger.error(f"ERP export failed: {exc}")
            self._toast.show_message("Couldn't save there — try another spot.")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def save_state(self) -> None:
        """Called by main window on close."""
        self._save_data()


# ---------------------------------------------------------------------------
# _Toast — an ambient inline confirmation that fades, never a QMessageBox.
# ---------------------------------------------------------------------------
class _Toast(QWidget):
    """A small warm pill that fades in at the bottom, holds, and fades out."""

    def __init__(self, parent: QWidget, reduced_motion: bool = False):
        super().__init__(parent)
        self._reduced_motion = reduced_motion
        self._text = ""
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMinimumHeight(46)
        self.hide()

        self._eff = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._eff)
        self._eff.setOpacity(0.0)
        self._fade = QPropertyAnimation(self._eff, b"opacity", self)
        self._fade.setDuration(0 if reduced_motion else 420)
        self._fade.setEasingCurve(QEasingCurve.Type.InOutSine)

        self._dwell = QTimer(self)
        self._dwell.setSingleShot(True)
        self._dwell.timeout.connect(self._fade_out)

    def show_message(self, text: str) -> None:
        self._text = text
        self._reposition()
        self.show()
        self.raise_()
        if self._reduced_motion:
            self._eff.setOpacity(1.0)
        else:
            self._fade.stop()
            with contextlib.suppress(TypeError):
                self._fade.finished.disconnect()
            self._fade.setStartValue(0.0)
            self._fade.setEndValue(1.0)
            self._fade.start()
        self._dwell.start(3200)
        self.update()

    def _fade_out(self) -> None:
        if self._reduced_motion:
            self.hide()
            return
        self._fade.stop()
        self._fade.setStartValue(self._eff.opacity())
        self._fade.setEndValue(0.0)
        with contextlib.suppress(TypeError):
            self._fade.finished.disconnect()
        self._fade.finished.connect(self.hide)
        self._fade.start()

    def _reposition(self) -> None:
        par = self.parentWidget()
        if par is None:
            return
        fm = QFontMetrics(sans_font(13))
        w = min(par.width() - 64, fm.horizontalAdvance(self._text) + 56)
        h = 46
        x = (par.width() - w) // 2
        y = par.height() - h - 28
        self.setGeometry(x, max(0, y), w, h)

    def paintEvent(self, _):  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(0.5, 0.5, self.width() - 1, self.height() - 1)
        radius = rect.height() / 2
        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)
        p.fillPath(path, _mix(QColor(_PAL["raised"]), QColor(_PAL["accent"]), 0.12))
        pen = QPen(_mix(QColor(_PAL["border"]), QColor(_PAL["accent"]), 0.35))
        pen.setWidthF(1.0)
        p.setPen(pen)
        p.drawPath(path)
        p.setFont(sans_font(13, QFont.Weight.Medium))
        p.setPen(QColor(_PAL["text"]))
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, self._text)
        p.end()
