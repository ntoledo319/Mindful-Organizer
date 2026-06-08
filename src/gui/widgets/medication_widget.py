"""
The Shelf — Hearth's quiet place for medication.

Hearth doesn't *track* your medication. It keeps a small shelf for you and
gently notices. The metaphor is a bedside windowsill where your bottles live:
warm, personal, low-stakes. You're not filing a compliance report — you're
tending a small routine, and a companion is keeping you company while you do.

This is the rebuild called for in docs/design/audit_06. It replaces the native
checkbox grid, the lifetime "Adherence rate" failure tally, the QGroupBox/
QListWidget CRUD scaffolding, and the bold-italic liability waiver that used to
greet a person about their psych meds. In its place:

  * :class:`DoseCard`        — each of today's doses, the drug name in the
                               reading serif beside a warm capsule glyph, with
                               one calm tap that *blooms warm* on "Took it".
                               Explicit Took / Late / Skipped — never a toggle
                               that quietly records a miss.
  * :class:`SteadinessRibbon`— the last ~14 days as warm marks (filled = taken,
                               half = late, a soft hollow ring = a skip),
                               recent-weighted and self-healing, with one
                               forgiving sentence. Never a percentage, never
                               the word "adherence."

Behavior is preserved exactly: the same constructor ``MedicationWidget(main_window)``,
the same medications.json / adherence.json persistence, the same
``record_status`` mirror into SQLite for the crisis miss-heuristic, the same
``medication_taken`` / ``medication_updated`` signals, the same ``save_state``.
The doctor export stays — reframed as "a note for your doctor."
"""

from __future__ import annotations

import contextlib
import json
import logging
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from PyQt6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    QRectF,
    Qt,
    QTime,
    pyqtProperty,
    pyqtSignal,
)
from PyQt6.QtGui import (
    QColor,
    QFont,
    QPainter,
    QPainterPath,
    QPen,
    QRadialGradient,
)
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QScrollArea,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from core.paths import get_data_dir
from gui.components.hearth_surfaces import ONYX, HearthButton, HearthCard
from gui.components.state_controls import sans_font, serif_font

logger = logging.getLogger(__name__)


# A small palette of natural-material hues so each medication keeps a stable
# visual identity over time — you learn "the clay one is my morning SSRI" by
# colour and shape, not by reading. Drawn warm, never clinical.
_MED_HUES = [
    "#C2703D",  # ember / dried clay
    "#7C8B6F",  # dried sage
    "#A9846B",  # river stone
    "#B0855A",  # banked coal
    "#8C7A9B",  # faded iris
    "#9A6E63",  # terracotta
]


def _hue_for(name: str) -> QColor:
    """A stable warm hue for a medication, keyed off its name."""
    if not name:
        return QColor(_MED_HUES[0])
    return QColor(_MED_HUES[sum(ord(c) for c in name) % len(_MED_HUES)])


def _detect_reduced_motion() -> bool:
    try:
        from utils.accessibility import detect_reduced_motion

        return detect_reduced_motion()
    except Exception:  # accessibility probing must never block the screen
        return False


def _is_prn(med: dict[str, Any]) -> bool:
    """True for an as-needed medication — never a daily obligation."""
    return (med.get("frequency", "") or "").strip().lower() in ("as needed", "as-needed", "prn")


# ---------------------------------------------------------------------------
# A quiet ember that fades up, holds, and recedes — never a popup.
# ---------------------------------------------------------------------------
class _EmberLine(QLabel):
    """An inline, fading acknowledgement in the reading serif.

    It says one plain thing ("Logged — 8:02am."), glows up, holds, and recedes.
    Under reduced motion it simply appears and lingers without the fade.
    """

    def __init__(self, reduced_motion: bool = False, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._reduced_motion = reduced_motion
        self.setFont(serif_font(15))
        self.setWordWrap(True)
        self._opacity = 0.0
        self._apply(0.0)
        self.setVisible(False)

        self._fade = QPropertyAnimation(self, b"glow", self)
        self._fade.setEasingCurve(QEasingCurve.Type.InOutSine)

    def _apply(self, v: float) -> None:
        c = QColor(ONYX["accent"])
        self.setStyleSheet(
            f"color: rgba({c.red()}, {c.green()}, {c.blue()}, {max(0.0, min(1.0, v)):.3f}); "
            f"background: transparent;"
        )

    def _get_glow(self) -> float:
        return self._opacity

    def _set_glow(self, v: float) -> None:
        self._opacity = v
        self._apply(v)
        if v <= 0.01:
            self.setVisible(False)

    glow = pyqtProperty(float, fget=_get_glow, fset=_set_glow)

    def say(self, text: str) -> None:
        self.setText(text)
        self.setVisible(True)
        if self._reduced_motion:
            self._set_glow(1.0)
            return
        self._fade.stop()
        self._fade.setDuration(3200)
        self._fade.setKeyValueAt(0.0, 0.0)
        self._fade.setKeyValueAt(0.12, 1.0)
        self._fade.setKeyValueAt(0.74, 1.0)
        self._fade.setKeyValueAt(1.0, 0.0)
        self._fade.start()


# ---------------------------------------------------------------------------
# DoseCard — one of today's doses, as an object on a shelf.
# ---------------------------------------------------------------------------
class DoseCard(HearthCard):
    """A wide, low card for a single medication's dose today.

    Left: a custom-painted capsule glyph in the med's own warm hue. Center: the
    drug name in the reading serif, dose + time tucked beneath in muted sans.
    Right: one calm action. Tapping "Took it" runs a slow eased ``warmth`` bloom
    — the capsule and a thin left edge catch hearthlight, the way a lamp on the
    shelf catches the pill. A skip dims to a resting tone; never alarm-red.

    Three honest states, all explicit choices (no toggle-implies-missed):
        "taken", "late", "skipped". An unset day is simply "pending" — quiet,
        not a failure.
    """

    # status -> (request_status, signal_name) emitted upward
    taken = pyqtSignal(str)  # med name
    statusChanged = pyqtSignal(str, str)  # noqa: N815  (med name, status)

    def __init__(
        self,
        med: dict[str, Any],
        status: str = "pending",
        *,
        reduced_motion: bool = False,
        prn: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        # All dose cards stand at one calm elevation; warmth, not lift, is how a
        # taken dose announces itself.
        super().__init__(parent, elevation=1, radius=18)
        self._med = med
        self._status = status
        self._prn = prn
        self._reduced_motion = reduced_motion
        self._hue = _hue_for(med.get("name", ""))
        # warmth 0 = resting stone, 1 = caught the hearthlight
        self._warmth = 1.0 if status in ("taken", "late") else 0.0
        self.setMinimumHeight(96)

        self._anim = QPropertyAnimation(self, b"warmth", self)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.setDuration(0 if reduced_motion else 440)

        self._build()
        self._reflect_status()

    # -- the warm bloom property ---------------------------------------
    def _get_warmth(self) -> float:
        return self._warmth

    def _set_warmth(self, v: float) -> None:
        self._warmth = v
        self.update()

    warmth = pyqtProperty(float, fget=_get_warmth, fset=_set_warmth)

    # -- layout ---------------------------------------------------------
    def _build(self) -> None:
        row = QHBoxLayout(self)
        # Leave room on the left for the painted capsule glyph + warming edge.
        row.setContentsMargins(70, 16, 22, 16)
        row.setSpacing(16)

        # Name + the numbers tucked beneath.
        text_col = QVBoxLayout()
        text_col.setSpacing(3)
        name = self._med.get("name", "this one")
        self._name_label = QLabel(name)
        self._name_label.setFont(serif_font(20, QFont.Weight.Medium))
        self._name_label.setStyleSheet(f"color: {ONYX['text']}; background: transparent;")
        text_col.addWidget(self._name_label)

        self._sub_label = QLabel(self._subtitle())
        self._sub_label.setFont(sans_font(12))
        self._sub_label.setStyleSheet(f"color: {ONYX['text_muted']}; background: transparent;")
        text_col.addWidget(self._sub_label)
        row.addLayout(text_col, stretch=1)

        # The action(s) on the right. One calm primary tap; the honest
        # alternatives (late / skip) live as recessive ghosts beside it.
        self._action_wrap = QWidget()
        self._action_wrap.setStyleSheet("background: transparent;")
        self._action_row = QHBoxLayout(self._action_wrap)
        self._action_row.setContentsMargins(0, 0, 0, 0)
        self._action_row.setSpacing(8)
        row.addWidget(self._action_wrap, alignment=Qt.AlignmentFlag.AlignRight)

        self._take_btn = HearthButton(
            "Took it", role="primary", reduced_motion=self._reduced_motion
        )
        self._take_btn.clicked.connect(lambda: self._set_status("taken"))

        self._late_btn = HearthButton("Late", role="ghost", reduced_motion=self._reduced_motion)
        self._late_btn.clicked.connect(lambda: self._set_status("late"))

        self._skip_btn = HearthButton("Skip", role="ghost", reduced_motion=self._reduced_motion)
        self._skip_btn.clicked.connect(lambda: self._set_status("skipped"))

        # Once a dose is settled, a single quiet "Change" reopens the choice —
        # so a misclick is always undoable, but never an accidental "missed".
        self._change_btn = HearthButton("Change", role="ghost", reduced_motion=self._reduced_motion)
        self._change_btn.clicked.connect(self._reopen)

        for b in (self._take_btn, self._late_btn, self._skip_btn, self._change_btn):
            self._action_row.addWidget(b)

    def _subtitle(self) -> str:
        dose = (self._med.get("dosage", "") or "").strip()
        time_str = (self._med.get("time", "") or "").strip()
        if self._prn:
            bits = [b for b in (dose, "if you need it") if b]
            return "  ·  ".join(bits) if bits else "if you need it"
        bits = [b for b in (dose, _pretty_time(time_str)) if b]
        return "  ·  ".join(bits)

    # -- status transitions --------------------------------------------
    def _set_status(self, status: str) -> None:
        self._status = status
        self._reflect_status()
        target = 1.0 if status in ("taken", "late") else 0.32 if status == "skipped" else 0.0
        if self._reduced_motion:
            self._set_warmth(target)
        else:
            self._anim.stop()
            self._anim.setStartValue(self._warmth)
            self._anim.setEndValue(target)
            self._anim.start()
        if status == "taken":
            self.taken.emit(self._med.get("name", ""))
        self.statusChanged.emit(self._med.get("name", ""), status)

    def _reopen(self) -> None:
        # Return to the open choice without recording anything — an undo, never
        # a "missed". The day goes back to pending.
        self._set_status("pending")

    def _reflect_status(self) -> None:
        settled = self._status in ("taken", "late", "skipped")
        # When settled, the loud "Took it" recedes; only a quiet "Change" remains
        # plus the warm confirmation line painted on the card itself.
        self._take_btn.setVisible(not settled)
        self._late_btn.setVisible(not settled)
        self._skip_btn.setVisible(not settled)
        self._change_btn.setVisible(settled)
        self._sub_label.setText(self._confirm_subtitle() if settled else self._subtitle())

    def _confirm_subtitle(self) -> str:
        if self._status == "taken":
            return f"Logged — {_now_clock()}."
        if self._status == "late":
            return f"Took it late — {_now_clock()}. No penalty here."
        if self._status == "skipped":
            return "Noted. Tomorrow's a fresh one."
        return self._subtitle()

    # -- paint: the capsule glyph + warming left edge -------------------
    def paintEvent(self, event):  # noqa: N802 (Qt naming)
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        w = self._warmth
        hue = QColor(self._hue)
        accent = QColor(ONYX["accent"])
        # The glyph warms from the med's own resting hue toward hearthlight as
        # the dose is taken.
        glyph = QColor(
            int(hue.red() + (accent.red() - hue.red()) * w),
            int(hue.green() + (accent.green() - hue.green()) * w),
            int(hue.blue() + (accent.blue() - hue.blue()) * w),
        )

        full = QRectF(self.rect()).adjusted(2, 2, -2, -2)

        # 1) A thin left edge that blooms warm when the dose is taken.
        if w > 0.001:
            edge_path = QPainterPath()
            edge_path.addRoundedRect(QRectF(full.left(), full.top(), 6, full.height()), 3, 3)
            ec = QColor(accent)
            ec.setAlpha(int(190 * w))
            p.fillPath(edge_path, ec)
            # A soft pool of warmth spilling rightward from that edge.
            pool = QRadialGradient(full.left() + 4, full.center().y(), full.width() * 0.5)
            pc = QColor(accent)
            pc.setAlpha(int(34 * w))
            pool.setColorAt(0.0, pc)
            pool.setColorAt(1.0, QColor(accent.red(), accent.green(), accent.blue(), 0))
            clip = QPainterPath()
            clip.addRoundedRect(full, 18, 18)
            p.save()
            p.setClipPath(clip)
            p.fillRect(full, pool)
            p.restore()

        # 2) The capsule glyph, centred in the left margin.
        cx = full.left() + 34
        cy = full.center().y()
        cap_w = 30.0
        cap_h = 15.0
        cap = QRectF(cx - cap_w / 2, cy - cap_h / 2, cap_w, cap_h)

        # Soft halo behind it when warm.
        if w > 0.001:
            halo = QRadialGradient(cx, cy, cap_w)
            hc = QColor(glyph)
            hc.setAlpha(int(120 * w))
            halo.setColorAt(0.0, hc)
            halo.setColorAt(1.0, QColor(glyph.red(), glyph.green(), glyph.blue(), 0))
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(halo)
            p.drawEllipse(QRectF(cx - cap_w, cy - cap_w, cap_w * 2, cap_w * 2))

        # The capsule body: two-tone, the way a real capsule is, in the med hue.
        capsule = QPainterPath()
        capsule.addRoundedRect(cap, cap_h / 2, cap_h / 2)
        # When skipped, the glyph rests dim and hollow rather than alarmed.
        if self._status == "skipped":
            p.setPen(Qt.PenStyle.NoPen)
            ring = QColor(self._hue)
            ring.setAlpha(70)
            p.setBrush(ring)
            p.drawPath(capsule)
        else:
            p.setClipPath(capsule)
            left_half = QColor(glyph).lighter(112)
            right_half = QColor(glyph).darker(118)
            p.fillRect(QRectF(cap.left(), cap.top(), cap.width() / 2, cap.height()), left_half)
            p.fillRect(
                QRectF(cap.center().x(), cap.top(), cap.width() / 2, cap.height()), right_half
            )
            # A small soft highlight along the top, like light on a smooth shell.
            sheen = QColor(255, 248, 238, 60)
            p.fillRect(QRectF(cap.left(), cap.top(), cap.width(), cap.height() * 0.32), sheen)
            p.setClipping(False)
        p.end()


def _pretty_time(time_str: str) -> str:
    """'08:00' -> '8:00am'. Falls back to the raw string on any surprise."""
    try:
        h, m = (int(x) for x in time_str.split(":")[:2])
        suffix = "am" if h < 12 else "pm"
        h12 = h % 12 or 12
        return f"{h12}:{m:02d}{suffix}"
    except (ValueError, IndexError):
        return time_str


def _now_clock() -> str:
    n = datetime.now()
    suffix = "am" if n.hour < 12 else "pm"
    h12 = n.hour % 12 or 12
    return f"{h12}:{n.minute:02d}{suffix}"


# ---------------------------------------------------------------------------
# SteadinessRibbon — the recent rhythm, forgiving and self-healing.
# ---------------------------------------------------------------------------
class SteadinessRibbon(QWidget):
    """The last ~14 days as a warm row of marks — never a percentage.

    A filled warm dot for a day you took your doses, a half-warm dot for a late
    one, a soft hollow ring for a skip, and a faint quiet dot for a day that
    simply passed unmarked (not a failure — just quiet). Recent days glow a
    touch brighter than old ones, so a rough patch fades on its own and the row
    can never become a growing "Missed: 47."
    """

    WINDOW_DAYS = 14

    def __init__(self, reduced_motion: bool = False, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._marks: list[str] = ["none"] * self.WINDOW_DAYS  # taken/late/skip/none
        self.setMinimumHeight(54)

    def set_marks(self, marks: list[str]) -> None:
        """marks oldest-first, length WINDOW_DAYS; each in taken/late/skip/none."""
        self._marks = (marks or [])[-self.WINDOW_DAYS :]
        if len(self._marks) < self.WINDOW_DAYS:
            self._marks = ["none"] * (self.WINDOW_DAYS - len(self._marks)) + self._marks
        self.update()

    def paintEvent(self, _event):  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        n = len(self._marks)
        if n == 0:
            p.end()
            return
        accent = QColor(ONYX["accent"])
        muted = QColor(ONYX["text_muted"])

        pad = 4.0
        avail = self.width() - 2 * pad
        slot = avail / n
        r = min(slot * 0.34, 9.0)
        cy = self.height() / 2

        for i, mark in enumerate(self._marks):
            cx = pad + slot * (i + 0.5)
            # Recent days glow a touch warmer; old ones fade — self-healing.
            recency = 0.55 + 0.45 * (i / max(1, n - 1))

            if mark == "taken":
                self._dot(p, cx, cy, r, accent, alpha=int(235 * recency), fill=1.0)
            elif mark == "late":
                # Half-warm: a filled lower half, the upper a faint glow.
                self._dot(p, cx, cy, r, accent, alpha=int(150 * recency), fill=0.55)
            elif mark == "skip":
                # A soft hollow ring — a small gap in the fire's glow, not a mark.
                self._ring(p, cx, cy, r, muted, alpha=int(185 * recency))
            else:
                # A quiet, barely-there dot — the day just passed.
                self._dot(p, cx, cy, r * 0.5, muted, alpha=int(70 * recency), fill=1.0)
        p.end()

    @staticmethod
    def _dot(
        p: QPainter, cx: float, cy: float, r: float, color: QColor, *, alpha: int, fill: float
    ):
        c = QColor(color)
        if fill >= 0.999:
            # A soft warm halo, then the solid coal.
            halo = QRadialGradient(cx, cy, r * 2.2)
            hc = QColor(color)
            hc.setAlpha(int(alpha * 0.38))
            halo.setColorAt(0.0, hc)
            halo.setColorAt(1.0, QColor(color.red(), color.green(), color.blue(), 0))
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(halo)
            p.drawEllipse(QRectF(cx - r * 2.2, cy - r * 2.2, r * 4.4, r * 4.4))
            c.setAlpha(alpha)
            p.setBrush(c)
            p.drawEllipse(QRectF(cx - r, cy - r, 2 * r, 2 * r))
        else:
            # Late: faint full disc + a warmer lower crescent.
            faint = QColor(color)
            faint.setAlpha(int(alpha * 0.5))
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(faint)
            p.drawEllipse(QRectF(cx - r, cy - r, 2 * r, 2 * r))
            warm = QColor(color)
            warm.setAlpha(alpha)
            path = QPainterPath()
            path.addEllipse(QRectF(cx - r, cy - r, 2 * r, 2 * r))
            p.setClipPath(path)
            p.setBrush(warm)
            p.drawRect(QRectF(cx - r, cy, 2 * r, r))
            p.setClipping(False)

    @staticmethod
    def _ring(p: QPainter, cx: float, cy: float, r: float, color: QColor, *, alpha: int):
        p.save()
        c = QColor(color)
        c.setAlpha(alpha)
        pen = QPen(c)
        pen.setWidthF(2.0)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QRectF(cx - r, cy - r, 2 * r, 2 * r))
        p.restore()


# ---------------------------------------------------------------------------
# ShelfTile — a medication as an object on the shelf, with in-context edit/remove.
# ---------------------------------------------------------------------------
class ShelfTile(QWidget):
    """A small row for one medication in the shelf, edit/remove living in place.

    No global Add/Edit/Remove button bar — the actions live on the tile itself
    as recessive ghosts, so they're there when you reach for them and quiet
    otherwise.
    """

    editRequested = pyqtSignal(dict)  # noqa: N815
    removeRequested = pyqtSignal(dict)  # noqa: N815

    def __init__(
        self, med: dict[str, Any], reduced_motion: bool = False, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._med = med
        self._reduced_motion = reduced_motion
        self._hue = _hue_for(med.get("name", ""))
        self.setMinimumHeight(46)
        self._confirming = False
        self._build()

    def _build(self) -> None:
        row = QHBoxLayout(self)
        row.setContentsMargins(34, 6, 8, 6)
        row.setSpacing(12)

        name = self._med.get("name", "this one")
        # Name on top, the numbers tucked beneath — so the actions never crowd
        # the text and nothing has to clip.
        text_col = QVBoxLayout()
        text_col.setSpacing(1)
        self._name_label = QLabel(name)
        self._name_label.setFont(sans_font(13, QFont.Weight.DemiBold))
        self._name_label.setStyleSheet(f"color: {ONYX['text']}; background: transparent;")
        text_col.addWidget(self._name_label)
        self._meta_label = QLabel(self._meta())
        self._meta_label.setFont(sans_font(11))
        self._meta_label.setStyleSheet(f"color: {ONYX['text_muted']}; background: transparent;")
        text_col.addWidget(self._meta_label)
        row.addLayout(text_col, stretch=1)

        self._edit_btn = HearthButton("Edit", role="ghost", reduced_motion=self._reduced_motion)
        self._edit_btn.clicked.connect(lambda: self.editRequested.emit(self._med))
        row.addWidget(self._edit_btn)

        self._remove_btn = HearthButton(
            "Take off the shelf", role="ghost", reduced_motion=self._reduced_motion
        )
        self._remove_btn.clicked.connect(self._ask_remove)
        row.addWidget(self._remove_btn)

        # The inline confirm — no QMessageBox. Two quiet ghosts that replace the
        # remove control until the choice is made.
        self._confirm_label = QLabel(f"Take {name} off the shelf?")
        self._confirm_label.setFont(sans_font(12))
        self._confirm_label.setStyleSheet(f"color: {ONYX['text_muted']}; background: transparent;")
        self._yes_btn = HearthButton("Yes", role="ghost", reduced_motion=self._reduced_motion)
        self._yes_btn.clicked.connect(lambda: self.removeRequested.emit(self._med))
        self._no_btn = HearthButton("Keep it", role="ghost", reduced_motion=self._reduced_motion)
        self._no_btn.clicked.connect(self._cancel_remove)
        for w in (self._confirm_label, self._yes_btn, self._no_btn):
            w.setVisible(False)
            row.addWidget(w)

    def _meta(self) -> str:
        dose = (self._med.get("dosage", "") or "").strip()
        freq = (self._med.get("frequency", "") or "").strip()
        time_str = (self._med.get("time", "") or "").strip()
        when = "as needed" if _is_prn(self._med) else _pretty_time(time_str)
        bits = [b for b in (dose, when) if b]
        if freq and not _is_prn(self._med) and freq.lower() not in ("daily", ""):
            bits.append(freq.lower())
        return "   ·   ".join(bits)

    def _ask_remove(self) -> None:
        self._confirming = True
        self._edit_btn.setVisible(False)
        self._remove_btn.setVisible(False)
        for w in (self._confirm_label, self._yes_btn, self._no_btn):
            w.setVisible(True)

    def _cancel_remove(self) -> None:
        self._confirming = False
        self._edit_btn.setVisible(True)
        self._remove_btn.setVisible(True)
        for w in (self._confirm_label, self._yes_btn, self._no_btn):
            w.setVisible(False)

    def paintEvent(self, _event):  # noqa: N802
        # A tiny resting hue mark at the left, so the shelf reads as a row of
        # distinct little objects rather than a list.
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        c = QColor(self._hue)
        c.setAlpha(180)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(c)
        cy = self.height() / 2
        p.drawEllipse(QRectF(12, cy - 4, 8, 8))
        p.end()


# ---------------------------------------------------------------------------
# Add / edit sheet
# ---------------------------------------------------------------------------
class _MedicationDialog(QDialog):
    """A calm sheet for adding or editing a medication.

    Same data contract as before (name / dosage / frequency / time) so
    persistence is untouched; the labels are reframed as questions a thoughtful
    person would ask, and the chrome is warmed off the native form look.
    """

    def __init__(self, med: dict[str, Any] | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Add to the shelf" if not med else "Edit")
        self.setMinimumWidth(420)
        self.setStyleSheet(
            f"QDialog {{ background: {ONYX['background']}; }}"
            f"QLabel {{ color: {ONYX['text']}; background: transparent; }}"
            f"QLineEdit, QComboBox, QTimeEdit {{"
            f"  background: {ONYX['surface']}; color: {ONYX['text']};"
            f"  border: 1px solid {ONYX['border']}; border-radius: 10px;"
            f"  padding: 9px 11px; selection-background-color: {ONYX['accent']};"
            f"}}"
            f"QComboBox QAbstractItemView {{"
            f"  background: {ONYX['surface']}; color: {ONYX['text']};"
            f"  selection-background-color: {ONYX['surface_raised']};"
            f"}}"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 26, 28, 24)
        layout.setSpacing(14)

        heading = QLabel("What's on the shelf?" if not med else f"{med.get('name', '')}")
        heading.setFont(serif_font(22, QFont.Weight.Medium))
        layout.addWidget(heading)

        layout.addWidget(self._field("What is it?"))
        self._name = QLineEdit(med.get("name", "") if med else "")
        self._name.setPlaceholderText("e.g. Sertraline")
        self._name.setFont(sans_font(13))
        layout.addWidget(self._name)

        layout.addWidget(self._field("How much?"))
        self._dosage = QLineEdit(med.get("dosage", "") if med else "")
        self._dosage.setPlaceholderText("e.g. 50mg")
        self._dosage.setFont(sans_font(13))
        layout.addWidget(self._dosage)

        layout.addWidget(self._field("How often?"))
        self._frequency = QComboBox()
        self._frequency.setFont(sans_font(13))
        self._frequency.addItems(["Daily", "Twice daily", "Weekly", "As needed"])
        if med and med.get("frequency"):
            idx = self._frequency.findText(med["frequency"])
            if idx >= 0:
                self._frequency.setCurrentIndex(idx)
        layout.addWidget(self._frequency)

        layout.addWidget(self._field("When do you usually take it?"))
        self._time = QTimeEdit()
        self._time.setFont(sans_font(13))
        self._time.setDisplayFormat("HH:mm")
        if med and med.get("time"):
            try:
                parts = med["time"].split(":")
                self._time.setTime(QTime(int(parts[0]), int(parts[1])))
            except (ValueError, IndexError):
                self._time.setTime(QTime(8, 0))
        else:
            self._time.setTime(QTime(8, 0))
        layout.addWidget(self._time)

        layout.addSpacing(6)
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel = HearthButton("Not now", role="ghost")
        cancel.clicked.connect(self.reject)
        btn_row.addWidget(cancel)
        save = HearthButton("Put it on the shelf" if not med else "Save", role="primary")
        save.clicked.connect(self.accept)
        btn_row.addWidget(save)
        layout.addLayout(btn_row)

    @staticmethod
    def _field(text: str) -> QLabel:
        label = QLabel(text)
        label.setFont(sans_font(11, QFont.Weight.DemiBold))
        label.setStyleSheet(f"color: {ONYX['text_muted']}; background: transparent;")
        return label

    def get_data(self) -> dict[str, Any]:
        return {
            "name": self._name.text().strip(),
            "dosage": self._dosage.text().strip(),
            "frequency": self._frequency.currentText(),
            "time": self._time.time().toString("HH:mm"),
        }


# ---------------------------------------------------------------------------
# Widget
# ---------------------------------------------------------------------------
class MedicationWidget(QWidget):
    """The Shelf — today's doses, a forgiving rhythm, and the shelf itself."""

    medication_taken = pyqtSignal(str)  # med name
    medication_updated = pyqtSignal()

    # Recent window the ribbon summarises. Long enough to see a rhythm, short
    # enough that a rough patch from a month ago never haunts the present.
    _RHYTHM_WINDOW_DAYS = 14

    def __init__(self, main_window: Any, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.main_window = main_window

        self._medication_tracker = None
        with contextlib.suppress(Exception):
            self._medication_tracker = main_window.medication_tracker

        self._reduced_motion = _detect_reduced_motion()
        self._medications: list[dict[str, Any]] = []
        self._adherence: dict[str, dict[str, str]] = {}  # date -> {med_name: status}

        self._bg = QColor(ONYX["background"])

        self._load_data()
        self._build_ui()
        self._refresh_all()

    # ------------------------------------------------------------------
    # The warm room behind the cards
    # ------------------------------------------------------------------
    def paintEvent(self, _event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), self._bg)
        grad = QRadialGradient(self.width() / 2, self.height() * 0.08, self.width() * 0.7)
        warm = QColor(ONYX["accent"])
        warm.setAlpha(20)
        grad.setColorAt(0.0, warm)
        grad.setColorAt(1.0, QColor(warm.red(), warm.green(), warm.blue(), 0))
        p.fillRect(self.rect(), grad)
        p.end()

    # ------------------------------------------------------------------
    # Persistence (unchanged contract)
    # ------------------------------------------------------------------
    def _data_dir(self) -> Path:
        try:
            base = Path(self.main_window.data_dir)
        except (AttributeError, TypeError):
            base = get_data_dir()
        p = base / "medication"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def _load_data(self) -> None:
        dd = self._data_dir()
        meds_file = dd / "medications.json"
        adherence_file = dd / "adherence.json"

        if meds_file.exists():
            try:
                with open(meds_file) as fh:
                    self._medications = json.load(fh)
            except (json.JSONDecodeError, OSError) as exc:
                logger.debug(f"Medication load error: {exc}")

        if adherence_file.exists():
            try:
                with open(adherence_file) as fh:
                    self._adherence = json.load(fh)
            except (json.JSONDecodeError, OSError) as exc:
                logger.debug(f"Adherence load error: {exc}")

    def _save_data(self) -> None:
        dd = self._data_dir()
        dd.mkdir(parents=True, exist_ok=True)
        try:
            with open(dd / "medications.json", "w") as fh:
                json.dump(self._medications, fh, indent=2, default=str)
            with open(dd / "adherence.json", "w") as fh:
                json.dump(self._adherence, fh, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save medication data: {e}")

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
        self._root = QVBoxLayout(container)
        self._root.setSpacing(22)
        self._root.setContentsMargins(40, 34, 40, 32)
        # A reading column, not a dashboard sprawl.
        container.setMaximumWidth(720)
        scroll.setWidget(container)

        # Header — warm, in the reading voice. No "Tracker."
        header = QLabel("Your shelf")
        header.setFont(serif_font(27, QFont.Weight.Medium))
        header.setStyleSheet(f"color: {ONYX['text']}; background: transparent;")
        self._root.addWidget(header)

        # 1) Today's doses — the only thing that matters on arrival.
        self._today_section = QVBoxLayout()
        self._today_section.setSpacing(12)
        self._today_caption = QLabel("Today")
        self._today_caption.setFont(sans_font(11, QFont.Weight.DemiBold))
        self._today_caption.setStyleSheet(
            f"color: {ONYX['text_muted']}; background: transparent; letter-spacing: 1px;"
        )
        self._today_section.addWidget(self._today_caption)

        self._doses_host = QWidget()
        self._doses_host.setStyleSheet("background: transparent;")
        self._doses_layout = QVBoxLayout(self._doses_host)
        self._doses_layout.setContentsMargins(0, 0, 0, 0)
        self._doses_layout.setSpacing(12)
        self._today_section.addWidget(self._doses_host)

        self._dose_confirm = _EmberLine(reduced_motion=self._reduced_motion)
        self._today_section.addWidget(self._dose_confirm)
        self._root.addLayout(self._today_section)

        # 2) The steadiness ribbon — recent, forgiving rhythm.
        self._ribbon_card = HearthCard(elevation=0, radius=20)
        ribbon_layout = QVBoxLayout(self._ribbon_card)
        ribbon_layout.setContentsMargins(26, 20, 26, 22)
        ribbon_layout.setSpacing(12)
        self._ribbon_line = QLabel("")
        self._ribbon_line.setFont(serif_font(17))
        self._ribbon_line.setWordWrap(True)
        self._ribbon_line.setStyleSheet(f"color: {ONYX['text']}; background: transparent;")
        ribbon_layout.addWidget(self._ribbon_line)
        self._ribbon = SteadinessRibbon(reduced_motion=self._reduced_motion)
        ribbon_layout.addWidget(self._ribbon)
        self._root.addWidget(self._ribbon_card)

        # 3) The shelf — your medications, as objects, add/edit in context.
        shelf_caption = QLabel("On the shelf")
        shelf_caption.setFont(sans_font(11, QFont.Weight.DemiBold))
        shelf_caption.setStyleSheet(
            f"color: {ONYX['text_muted']}; background: transparent; letter-spacing: 1px;"
        )
        self._root.addWidget(shelf_caption)

        self._shelf_card = HearthCard(elevation=1, radius=20)
        self._shelf_layout = QVBoxLayout(self._shelf_card)
        self._shelf_layout.setContentsMargins(18, 14, 18, 16)
        self._shelf_layout.setSpacing(4)
        self._root.addWidget(self._shelf_card)

        # 4) For your doctor — the export, tucked at the foot.
        export_row = QHBoxLayout()
        self._export_btn = HearthButton(
            "Put together a note for your doctor",
            role="ghost",
            reduced_motion=self._reduced_motion,
        )
        self._export_btn.clicked.connect(self._export_for_doctor)
        export_row.addWidget(self._export_btn)
        export_row.addStretch()
        self._root.addLayout(export_row)

        self._export_confirm = _EmberLine(reduced_motion=self._reduced_motion)
        self._root.addWidget(self._export_confirm)

        # The quiet bottom line — present for honesty, invisible to emotion.
        disclaimer = QLabel("Hearth keeps the record. Your doctor makes the calls.")
        disclaimer.setFont(sans_font(11))
        disclaimer.setWordWrap(True)
        disclaimer.setStyleSheet(
            f"color: {ONYX['text_muted']}; background: transparent; font-style: italic;"
        )
        self._root.addWidget(disclaimer)

        self._root.addStretch()

    # ------------------------------------------------------------------
    # Refresh
    # ------------------------------------------------------------------
    def _refresh_all(self) -> None:
        self._refresh_doses()
        self._refresh_shelf()
        self._refresh_ribbon()

    def _clear_layout(self, layout: QVBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            if item is None:
                continue
            w = item.widget()
            if w is not None:
                w.deleteLater()

    # -- today's doses --------------------------------------------------
    def _refresh_doses(self) -> None:
        self._clear_layout(self._doses_layout)

        if not self._medications:
            empty = QLabel(
                "Nothing on the shelf yet. Add the first one when you're ready, "
                "and today's doses will wait for you here."
            )
            empty.setFont(serif_font(16))
            empty.setWordWrap(True)
            empty.setStyleSheet(f"color: {ONYX['text_muted']}; background: transparent;")
            self._doses_layout.addWidget(empty)
            return

        today_str = date.today().isoformat()
        today_adherence = self._adherence.get(today_str, {})

        scheduled = [m for m in self._medications if not _is_prn(m)]
        prn = [m for m in self._medications if _is_prn(m)]

        if not scheduled and not prn:
            return

        # The scheduled doses, the next-undone one lifted gently.
        first_open_done = False
        for med in scheduled:
            name = med.get("name", "?")
            status = today_adherence.get(name, "pending")
            card = DoseCard(
                med,
                status=status,
                reduced_motion=self._reduced_motion,
                prn=False,
            )
            if status == "pending" and not first_open_done:
                first_open_done = True
            card.taken.connect(lambda n: self.medication_taken.emit(n))
            card.statusChanged.connect(self._on_dose_status)
            self._doses_layout.addWidget(card)

        # PRN meds, surfaced gently and contextually — never a daily obligation.
        if prn:
            prn_caption = QLabel("If you need it, it's here")
            prn_caption.setFont(sans_font(11, QFont.Weight.DemiBold))
            prn_caption.setStyleSheet(
                f"color: {ONYX['text_muted']}; background: transparent; letter-spacing: 1px;"
            )
            self._doses_layout.addSpacing(4)
            self._doses_layout.addWidget(prn_caption)
            for med in prn:
                name = med.get("name", "?")
                status = today_adherence.get(name, "pending")
                card = DoseCard(
                    med,
                    status=status,
                    reduced_motion=self._reduced_motion,
                    prn=True,
                )
                card.taken.connect(lambda n: self.medication_taken.emit(n))
                card.statusChanged.connect(self._on_dose_status)
                self._doses_layout.addWidget(card)

    def _on_dose_status(self, med_name: str, status: str) -> None:
        """A dose card was set to taken / late / skipped / pending — record it.

        Every transition is an explicit, intentional choice. Returning to
        ``pending`` is an undo: it clears the day back to neutral and never
        records a "missed" that would feed the crisis miss-heuristic a false
        alarm. A real miss is inferred elsewhere, not by a stray tap.
        """
        today_str = date.today().isoformat()
        if today_str not in self._adherence:
            self._adherence[today_str] = {}
        if status == "pending":
            self._adherence[today_str].pop(med_name, None)
        else:
            self._adherence[today_str][med_name] = status
        self._save_data()
        self._sync_status_to_db(med_name, today_str, status)

        # A warm, plain line — never a popup.
        if status == "taken":
            self._dose_confirm.say(f"Logged — {_now_clock()}. Good.")
        elif status == "late":
            self._dose_confirm.say("Took it late, and that still counts.")
        elif status == "skipped":
            self._dose_confirm.say("Noted. Tomorrow's a fresh one.")

        self._refresh_ribbon()

    def _sync_status_to_db(self, med_name: str, day: str, status: str) -> None:
        """Mirror an adherence change into MEDICATION_LOGS (SQLite).

        The widget keeps a JSON model for its own display, but adherence must
        also reach the database so the wellness orchestrator's medication-miss
        crisis heuristic can see it. Best-effort: a DB hiccup must never block
        the user from logging a dose.
        """
        tracker = self._medication_tracker
        if tracker is None or not hasattr(tracker, "record_status"):
            return
        # 'pending' (an undo) carries no dose status to the DB — clearing a
        # mistaken tap should not write a row.
        if status == "pending":
            return
        dosage = ""
        for med in self._medications:
            if med.get("name") == med_name:
                dosage = med.get("dosage", "") or ""
                break
        try:
            tracker.record_status(med_name, day, status, dosage=dosage)
        except Exception as exc:  # noqa: BLE001 - persistence must not crash the UI
            logger.debug("Medication DB sync failed for %s: %s", med_name, exc)

    # -- the shelf ------------------------------------------------------
    def _refresh_shelf(self) -> None:
        self._clear_layout(self._shelf_layout)

        if not self._medications:
            empty = QLabel("The shelf is empty for now.")
            empty.setFont(sans_font(12))
            empty.setStyleSheet(f"color: {ONYX['text_muted']}; background: transparent;")
            empty.setContentsMargins(16, 4, 0, 4)
            self._shelf_layout.addWidget(empty)
        else:
            for i, med in enumerate(self._medications):
                tile = ShelfTile(med, reduced_motion=self._reduced_motion)
                tile.editRequested.connect(self._edit_medication)
                tile.removeRequested.connect(self._remove_medication)
                self._shelf_layout.addWidget(tile)
                if i < len(self._medications) - 1:
                    rule = QWidget()
                    rule.setFixedHeight(1)
                    rule.setStyleSheet(f"background: {ONYX['border']};")
                    self._shelf_layout.addWidget(rule)

        # The one warm way to add — a single ghost at the end of the shelf.
        self._shelf_layout.addSpacing(6)
        add_btn = HearthButton(
            "+  Add a medication", role="ghost", reduced_motion=self._reduced_motion
        )
        add_btn.clicked.connect(self._add_medication)
        add_row = QHBoxLayout()
        add_row.setContentsMargins(0, 0, 0, 0)
        add_row.addWidget(add_btn)
        add_row.addStretch()
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent;")
        wrap.setLayout(add_row)
        self._shelf_layout.addWidget(wrap)

    # -- the steadiness ribbon ------------------------------------------
    def _recent_window_days(self) -> list[str]:
        """ISO dates for the last RHYTHM_WINDOW_DAYS, oldest first, today last."""
        today = date.today()
        return [
            (today - timedelta(days=offset)).isoformat()
            for offset in range(self._RHYTHM_WINDOW_DAYS - 1, -1, -1)
        ]

    def _day_mark(self, day: str) -> str:
        """A single day's mark for the ribbon: taken / late / skip / none.

        A day reads as 'taken' if any dose was taken, 'late' if the warmest
        thing that happened was a late dose, 'skip' if the only thing recorded
        was a skip, and 'none' if the day simply passed unmarked.
        """
        statuses = list(self._adherence.get(day, {}).values())
        if not statuses:
            return "none"
        if "taken" in statuses:
            return "taken"
        if "late" in statuses:
            return "late"
        if "skipped" in statuses:
            return "skip"
        return "none"

    def _refresh_ribbon(self) -> None:
        recent = self._recent_window_days()
        marks = [self._day_mark(d) for d in recent]
        self._ribbon.set_marks(marks)
        self._ribbon_line.setText(self._ribbon_text(recent, marks))

    def _ribbon_text(self, recent: list[str], marks: list[str]) -> str:
        if not self._medications:
            return "Add a medication and the days you keep will gather here, gently."

        kept = sum(1 for m in marks if m in ("taken", "late"))
        if kept == 0:
            return "No pressure — log one whenever you take it, and we'll start keeping the rhythm."

        window = len(marks)
        # The live streak: consecutive kept days ending today.
        streak = 0
        for m in reversed(marks):
            if m in ("taken", "late"):
                streak += 1
            else:
                break

        today_kept = marks[-1] in ("taken", "late")
        yesterday_kept = window >= 2 and marks[-2] in ("taken", "late")

        if not yesterday_kept and window >= 2 and streak >= 1 and today_kept:
            return f"{kept} kept days these two weeks. Yesterday slipped by — it happens."
        if streak >= 5:
            return f"{streak} steady days in a row. This rhythm is holding."
        if streak >= 2:
            return f"{streak} steady days in a row."
        if today_kept and not yesterday_kept:
            return "Back on it today. One day at a time is plenty."
        if today_kept:
            return "Marked today. That's the one that counts."
        return f"{kept} of the last {window} days kept. Picking it back up is the whole game."

    # ------------------------------------------------------------------
    # Medication add / edit / remove
    # ------------------------------------------------------------------
    def _add_medication(self) -> None:
        dialog = _MedicationDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if not data["name"]:
                return
            self._medications.append(data)
            self._save_data()
            self.medication_updated.emit()
            self._refresh_all()

    def _edit_medication(self, med: dict[str, Any]) -> None:
        try:
            row = self._medications.index(med)
        except ValueError:
            return
        dialog = _MedicationDialog(med=med, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if not data["name"]:
                return
            self._medications[row] = data
            self._save_data()
            self.medication_updated.emit()
            self._refresh_all()

    def _remove_medication(self, med: dict[str, Any]) -> None:
        try:
            self._medications.remove(med)
        except ValueError:
            return
        self._save_data()
        self.medication_updated.emit()
        self._refresh_all()

    # ------------------------------------------------------------------
    # The note for your doctor
    # ------------------------------------------------------------------
    def _export_for_doctor(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "A note for your doctor", "medication_note.json", "JSON (*.json)"
        )
        if not path:
            return

        # A recent, honest summary per medication — kept to the same window the
        # ribbon shows, so nothing here grows into a lifetime failure tally.
        recent = self._recent_window_days()
        summary: dict[str, Any] = {}
        for med in self._medications:
            name = med.get("name", "?")
            taken = late = skipped = 0
            for day in recent:
                status = self._adherence.get(day, {}).get(name)
                if status == "taken":
                    taken += 1
                elif status == "late":
                    late += 1
                elif status == "skipped":
                    skipped += 1
            summary[name] = {
                "window_days": len(recent),
                "taken": taken,
                "late": late,
                "skipped": skipped,
            }

        report = {
            "exported_at": datetime.now().isoformat(),
            "window_days": len(recent),
            "medications": self._medications,
            "recent_summary": summary,
        }
        try:
            with open(path, "w") as fh:
                json.dump(report, fh, indent=2, default=str)
            self._export_confirm.say(f"Saved for your doctor — {Path(path).name}.")
        except Exception as exc:
            logger.error(f"Medication export failed: {exc}")
            self._export_confirm.say("Couldn't save the note just now. Try once more?")

    # ------------------------------------------------------------------
    # Public API (unchanged)
    # ------------------------------------------------------------------
    def save_state(self) -> None:
        """Called by the main window on close."""
        self._save_data()
