"""The task list — Hearth's quiet, energy-aware to-do.

This is the highest-traffic utility in the app, and it used to read like a
spreadsheet: a list/table with priority hex dots, an energy spinbox, a
checkbox tick, a five-column filter bar, and a separate detail pane full of
``--`` walls (docs/design/audit_07). For someone with ADHD or depression a
long ranked list of obligations is not neutral — it is the thing that
freezes you. So the rebuild does the opposite of a productivity app:

  * It opens **low-energy-first** — the gentlest thing you could do, on top —
    so the page meets you where you are instead of leading with the urgent.
  * Each task is a warm :class:`HearthCard` row, not a list item: a soft
    energy reading on the left ("one spoon" / "a few spoons"), the title in
    the reading serif, and a quiet line of when-and-where beneath it.
  * **Finishing a task is a warm bloom, not a checkbox.** You press "Done"
    and the card lights ember and settles away — the room acknowledges it,
    rather than ticking a box and moving on.
  * One warm "add" line at the top, in plain language, through the same NLP
    parser. No dropdown grid, no spinbox, no separate dialog.
  * The empty state invites instead of nagging.

Behavior is unchanged. The constructor signature, the ``nlp_parser`` add
path, every ``TaskManager`` call (add / complete / delete / undo / redo),
and the ``task_added`` / ``task_completed`` signals are all preserved, so
the app still constructs and saves exactly as before.
"""

from __future__ import annotations

import logging
from datetime import date, datetime
from typing import Any

from PyQt6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    Qt,
    QTimer,
    pyqtProperty,
    pyqtSignal,
)
from PyQt6.QtGui import QColor, QFont, QPainter, QPainterPath, QRadialGradient
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from gui.components.hearth_surfaces import ONYX, HearthButton, HearthCard
from gui.components.state_controls import sans_font, serif_font, warmth_color

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Energy, in human words. The data stores 0–100; nobody feels in percentages.
# Low energy reads cool and small; a heavy task reads warmer and weightier —
# but the warmth here means "this will cost you," not "this is good."
# ---------------------------------------------------------------------------
def _energy_word(energy: int) -> str:
    if energy <= 20:
        return "barely a spoon"
    if energy <= 40:
        return "one spoon"
    if energy <= 60:
        return "a few spoons"
    if energy <= 80:
        return "a real lift"
    return "a heavy one"


def _energy_t(energy: int) -> float:
    """Map stored energy 0–100 onto the warmth ramp [0, 1]."""
    return max(0.0, min(1.0, energy / 100.0))


def _due_phrase(due: str | None) -> str:
    """A plain, forgiving line about when — never a red 'OVERDUE' badge."""
    if not due:
        return ""
    try:
        d = date.fromisoformat(str(due)[:10])
    except (ValueError, TypeError):
        return f"by {due}"
    today = date.today()
    delta = (d - today).days
    if delta < -1:
        return f"was for {abs(delta)} days ago — whenever you can"
    if delta == -1:
        return "was for yesterday — no rush"
    if delta == 0:
        return "for today, if it fits"
    if delta == 1:
        return "for tomorrow"
    if delta <= 7:
        return f"in {delta} days"
    return f"for {d.strftime('%a %d %b')}"


# ---------------------------------------------------------------------------
# _ElidedLabel — one-line text that gracefully trails off (…) instead of
# wrapping into the row below or clipping mid-word against a hard edge.
# ---------------------------------------------------------------------------
class _ElidedLabel(QLabel):
    """A QLabel that elides to a single line at whatever width it is given."""

    def __init__(self, text: str, font: QFont, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._full = text
        self.setFont(font)
        from PyQt6.QtWidgets import QSizePolicy

        # Claim the stretch space of its column, but allow shrinking below the
        # natural text width (at which point we elide rather than overflow).
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumWidth(0)
        fm = self.fontMetrics()
        self.setFixedHeight(fm.height() + 2)

    def setText(self, text: str) -> None:  # noqa: N802
        self._full = text
        self.update()

    def minimumSizeHint(self):  # noqa: N802
        from PyQt6.QtCore import QSize

        fm = self.fontMetrics()
        return QSize(0, fm.height() + 2)

    def paintEvent(self, _event):  # noqa: N802
        p = QPainter(self)
        p.setFont(self.font())
        col = self.palette().windowText().color()
        # Honor the stylesheet color set on the label.
        ss = self.styleSheet()
        if "color:" in ss:
            frag = ss.split("color:")[1].split(";")[0].strip()
            c = QColor(frag)
            if c.isValid():
                col = c
        p.setPen(col)
        fm = p.fontMetrics()
        elided = fm.elidedText(self._full, Qt.TextElideMode.ElideRight, self.width())
        p.drawText(self.rect(), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, elided)
        p.end()


# ---------------------------------------------------------------------------
# TaskRow — one task as a warm card. Completing it is a slow ember bloom.
# ---------------------------------------------------------------------------
class TaskRow(HearthCard):
    """A single task, drawn as a warm row rather than a list line.

    Left: a small warmth dot + the cost in spoons. Middle: the title in the
    reading serif with a quiet when/where line beneath. Right: a recessive
    "Done" that, when pressed, blooms the whole card ember-warm and settles
    it away — the soft warm acknowledgement instead of a checkbox tick.
    """

    done_requested = pyqtSignal()
    remove_requested = pyqtSignal()

    def __init__(
        self,
        task: Any,
        *,
        completed_view: bool = False,
        reduced_motion: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        # Resting elevation; the warmth lives in the energy dot, not the box.
        super().__init__(parent, elevation=0, radius=18)
        self._task = task
        self._completed_view = completed_view
        self._reduced_motion = reduced_motion
        self._bloom = 0.0  # 0..1 ember bloom on completion
        self._energy = int(getattr(task, "energy_required", 50) or 0)

        self._build(task)

        self._bloom_anim = QPropertyAnimation(self, b"bloom", self)
        self._bloom_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._bloom_anim.setDuration(0 if reduced_motion else 620)

    # -- the bloom property: ember warmth washing across the card ---------
    def _get_bloom(self) -> float:
        return self._bloom

    def _set_bloom(self, v: float) -> None:
        self._bloom = v
        self.update()

    bloom = pyqtProperty(float, fget=_get_bloom, fset=_set_bloom)

    def _build(self, task: Any) -> None:
        # A steady row height so the list reads as a calm, even stack rather
        # than a ragged grid — titles elide to one line instead of colliding,
        # and the stacked Done / Let go on the right both have room.
        self.setMinimumHeight(94)

        row = QHBoxLayout(self)
        row.setContentsMargins(40, 16, 18, 16)  # left inset clears the energy dot
        row.setSpacing(12)

        # Left: the energy reading, the page's organizing idea made small. A
        # fixed-width gutter keeps every title starting on the same line.
        left = QVBoxLayout()
        left.setSpacing(0)
        self._spoons = QLabel(_energy_word(self._energy))
        self._spoons.setFont(sans_font(11, QFont.Weight.DemiBold))
        self._spoons.setWordWrap(True)
        self._spoons.setFixedWidth(80)
        spoon_color = (
            QColor(ONYX["text_muted"])
            if self._completed_view
            else warmth_color(_energy_t(self._energy))
        )
        self._spoons.setStyleSheet(f"color: {spoon_color.name()}; background: transparent;")
        left.addStretch()
        left.addWidget(self._spoons)
        left.addStretch()
        row.addLayout(left)

        # Middle: the title (reading voice) + a quiet when/where line. The
        # title rides one line and elides; the page is calmer for it.
        mid = QVBoxLayout()
        mid.setSpacing(4)
        mid.addStretch()
        title = getattr(task, "title", "Untitled") or "Untitled"
        self._title = _ElidedLabel(title, serif_font(18, QFont.Weight.Medium))
        title_color = ONYX["text_muted"] if self._completed_view else ONYX["text"]
        self._title.setStyleSheet(f"color: {title_color}; background: transparent;")
        mid.addWidget(self._title)

        sub = self._subtitle(task)
        if sub:
            self._sub = _ElidedLabel(sub, sans_font(11))
            self._sub.setStyleSheet(f"color: {ONYX['text_muted']}; background: transparent;")
            mid.addWidget(self._sub)
        mid.addStretch()
        row.addLayout(mid, stretch=1)

        # Right: the actions, stacked in one slim column so the title keeps the
        # room. "Done" is the warm gesture; a recessive "Let go" below it removes
        # a task you no longer need — never a loud red delete.
        if self._completed_view:
            done_mark = QLabel("done")
            done_mark.setFont(sans_font(11, QFont.Weight.DemiBold))
            done_mark.setStyleSheet(f"color: {ONYX['accent']}; background: transparent;")
            row.addWidget(done_mark, alignment=Qt.AlignmentFlag.AlignVCenter)
        else:
            actions = QVBoxLayout()
            actions.setSpacing(0)
            actions.addStretch()
            self._done_btn = HearthButton("Done", role="ghost", reduced_motion=self._reduced_motion)
            self._done_btn.clicked.connect(self._on_done)
            actions.addWidget(self._done_btn, alignment=Qt.AlignmentFlag.AlignRight)

            self._let_go = HearthButton("Let go", role="ghost", reduced_motion=self._reduced_motion)
            self._let_go.setFont(sans_font(11))
            self._let_go.clicked.connect(lambda: self.remove_requested.emit())
            actions.addWidget(self._let_go, alignment=Qt.AlignmentFlag.AlignRight)
            actions.addStretch()
            row.addLayout(actions)

    def _subtitle(self, task: Any) -> str:
        parts: list[str] = []
        due = _due_phrase(getattr(task, "due_date", None))
        if due:
            parts.append(due)
        category = getattr(task, "category", None)
        cat = getattr(category, "value", None) or getattr(task, "custom_category", None)
        if cat and cat != "Other":
            parts.append(str(cat).lower())
        recurrence = getattr(task, "recurrence", None)
        if recurrence is not None:
            parts.append("comes around again")
        if self._completed_view:
            done_at = getattr(task, "completed_at", None)
            if done_at:
                try:
                    dt = datetime.fromisoformat(str(done_at))
                    return f"set down {dt.strftime('%a %d %b')}"
                except (ValueError, TypeError):
                    return "set down"
        return "  ·  ".join(parts)

    # -- the warm-bloom completion --------------------------------------
    def _on_done(self) -> None:
        # Acknowledge with a slow ember bloom, then tell the surface to commit.
        # Even under reduced motion we light it briefly so the gesture lands.
        if hasattr(self, "_done_btn"):
            self._done_btn.setEnabled(False)
        if hasattr(self, "_let_go"):
            self._let_go.setEnabled(False)
        if self._reduced_motion:
            self._set_bloom(1.0)
            self.done_requested.emit()
            return
        self._bloom_anim.stop()
        self._bloom_anim.setStartValue(0.0)
        self._bloom_anim.setEndValue(1.0)
        self._bloom_anim.start()
        # Let the bloom be felt before the list re-reads and this row dissolves.
        QTimer.singleShot(560, self.done_requested.emit)

    def paintEvent(self, event):  # noqa: N802
        super().paintEvent(event)
        # An energy dot pinned to the left edge — the row's warmth at a glance.
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        glow = warmth_color(_energy_t(self._energy))
        if self._completed_view:
            glow = QColor(ONYX["text_muted"])
        cy = self.height() / 2
        cx = 20.0
        halo = QRadialGradient(cx, cy, 13)
        h0 = QColor(glow)
        h0.setAlpha(150)
        halo.setColorAt(0.0, h0)
        halo.setColorAt(1.0, QColor(glow.red(), glow.green(), glow.blue(), 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(halo)
        p.drawEllipse(int(cx - 13), int(cy - 13), 26, 26)
        p.setBrush(glow)
        p.drawEllipse(int(cx - 4), int(cy - 4), 8, 8)

        # The completion bloom: ember warmth washing the whole card, rising
        # from the centre as the task is set down.
        if self._bloom > 0.001:
            rect = self.rect().adjusted(2, 2, -2, -2)
            path = QPainterPath()
            path.addRoundedRect(
                float(rect.x()), float(rect.y()), rect.width(), rect.height(), 18, 18
            )
            p.setClipPath(path)
            wash = QRadialGradient(self.width() / 2, cy, self.width() * 0.7)
            warm = QColor(ONYX["accent"])
            warm.setAlpha(int(120 * self._bloom))
            wash.setColorAt(0.0, warm)
            warm2 = QColor(warm)
            warm2.setAlpha(0)
            wash.setColorAt(1.0, warm2)
            p.fillPath(path, wash)
        p.end()


# ---------------------------------------------------------------------------
# Widget
# ---------------------------------------------------------------------------
class TaskManagerWidget(QWidget):
    """The warm task list: gentlest-first, add in plain words, finish by bloom."""

    task_added = pyqtSignal()
    task_completed = pyqtSignal()

    def __init__(
        self,
        theme: dict[str, str],
        task_manager: Any = None,
        nlp_parser: Any = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._theme = theme
        self._task_manager = task_manager
        self._nlp_parser = nlp_parser
        # Kept for behavior parity with the prior widget's local undo path.
        self._undo_stack: list[dict[str, Any]] = []
        self._redo_stack: list[dict[str, Any]] = []
        self._show_done = False
        self._reduced_motion = self._detect_reduced_motion()
        self._bg = QColor(ONYX["background"])
        self._rows: list[TaskRow] = []

        self._build_ui()
        self._refresh_task_list()

    # ------------------------------------------------------------------
    # The warm room behind the cards
    # ------------------------------------------------------------------
    def paintEvent(self, _event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), self._bg)
        grad = QRadialGradient(self.width() / 2, self.height() * 0.1, self.width() * 0.6)
        warm = QColor(ONYX["accent"])
        warm.setAlpha(20)
        grad.setColorAt(0.0, warm)
        warm2 = QColor(warm)
        warm2.setAlpha(0)
        grad.setColorAt(1.0, warm2)
        p.fillRect(self.rect(), grad)
        p.end()

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
        # A steady reading-column width (DESIGN_SYSTEM §3: closer to a page than
        # a dashboard), centered by the stretches in ``hold`` below.
        container.setFixedWidth(620)
        self._root = QVBoxLayout(container)
        self._root.setSpacing(14)
        self._root.setContentsMargins(40, 38, 40, 40)

        # Center the reading column rather than letting it stretch wide.
        hold = QWidget()
        hold.setStyleSheet("background: transparent;")
        hold_row = QHBoxLayout(hold)
        hold_row.setContentsMargins(0, 0, 0, 0)
        hold_row.addStretch()
        hold_row.addWidget(container)
        hold_row.addStretch()
        scroll.setWidget(hold)

        self._build_header()
        self._build_add_line()

        # Undo / redo — kept for behavior parity
        undo_row = QHBoxLayout()
        undo_row.addStretch()
        self._undo_btn = HearthButton("Undo", role="ghost", reduced_motion=self._reduced_motion)
        self._undo_btn.clicked.connect(self._undo)
        undo_row.addWidget(self._undo_btn)
        self._redo_btn = HearthButton("Redo", role="ghost", reduced_motion=self._reduced_motion)
        self._redo_btn.clicked.connect(self._redo)
        undo_row.addWidget(self._redo_btn)
        undo_row.addStretch()
        self._root.addLayout(undo_row)

        # The list itself lives in a column we rebuild on refresh.
        self._list_box = QVBoxLayout()
        self._list_box.setSpacing(10)
        self._root.addLayout(self._list_box)

        # The quiet way to look back at what's been set down.
        self._done_toggle = HearthButton(
            "Show what you've set down", role="ghost", reduced_motion=self._reduced_motion
        )
        self._done_toggle.clicked.connect(self._toggle_done)
        toggle_row = QHBoxLayout()
        toggle_row.addStretch()
        toggle_row.addWidget(self._done_toggle)
        toggle_row.addStretch()
        self._root.addSpacing(6)
        self._root.addLayout(toggle_row)

        self._root.addStretch()

    def _build_header(self) -> None:
        title = QLabel("What's on you")
        title.setFont(serif_font(28, QFont.Weight.Medium))
        title.setStyleSheet(f"color: {ONYX['text']}; background: transparent;")
        self._root.addWidget(title)

        self._lede = QLabel("")
        self._lede.setFont(serif_font(16))
        self._lede.setWordWrap(True)
        self._lede.setStyleSheet(f"color: {ONYX['text_muted']}; background: transparent;")
        self._root.addWidget(self._lede)
        self._root.addSpacing(6)

    def _build_add_line(self) -> None:
        # One warm line, plain language, straight through the NLP parser.
        card = HearthCard(elevation=1, radius=18)
        row = QHBoxLayout(card)
        row.setContentsMargins(20, 12, 14, 12)
        row.setSpacing(12)

        self._nlp_input = QLineEdit()
        self._nlp_input.setPlaceholderText("Name one thing… 'email the clinic friday, gentle'")
        self._nlp_input.setFont(serif_font(16))
        self._nlp_input.setStyleSheet(
            "QLineEdit { background: transparent; border: none; "
            f"color: {ONYX['text']}; padding: 6px 2px; }}"
            f"QLineEdit::placeholder {{ color: {ONYX['text_muted']}; }}"
        )
        self._nlp_input.returnPressed.connect(self._add_task_from_nlp)
        row.addWidget(self._nlp_input, stretch=1)

        add_btn = HearthButton("Add it", role="primary", reduced_motion=self._reduced_motion)
        add_btn.clicked.connect(self._add_task_from_nlp)
        row.addWidget(add_btn)

        self._root.addWidget(card)

        # A quiet inline acknowledgement when something is added.
        self._add_echo = QLabel("")
        self._add_echo.setFont(serif_font(14))
        self._add_echo.setStyleSheet(f"color: {ONYX['accent']}; background: transparent;")
        self._add_echo.setVisible(False)
        self._root.addWidget(self._add_echo)

    # ------------------------------------------------------------------
    # Data
    # ------------------------------------------------------------------
    def _get_tasks(self) -> list:
        if not self._task_manager:
            return []
        try:
            return list(self._task_manager.tasks)
        except (AttributeError, TypeError):
            return []

    def _open_tasks(self) -> list:
        """Incomplete tasks, gentlest (lowest-energy) first.

        The energy-aware ordering is the whole point: the page leads with the
        thing that costs you least, so a low day still has somewhere to start.
        Ties fall back to due-date, then priority — quietly, underneath.
        """
        tasks = [t for t in self._get_tasks() if not getattr(t, "completed", False)]
        tasks.sort(
            key=lambda t: (
                int(getattr(t, "energy_required", 50) or 0),
                str(getattr(t, "due_date", "") or "9999"),
                -getattr(getattr(t, "priority", None), "value", 0),
            )
        )
        return tasks

    def _done_tasks(self) -> list:
        tasks = [t for t in self._get_tasks() if getattr(t, "completed", False)]
        tasks.sort(key=lambda t: str(getattr(t, "completed_at", "") or ""), reverse=True)
        return tasks

    def _clear_list(self) -> None:
        while self._list_box.count():
            item = self._list_box.takeAt(0)
            w = item.widget()
            if w is not None:
                # Reparent out immediately so it can't linger over the rebuild
                # while deleteLater waits for the event loop.
                w.setParent(None)
                w.deleteLater()
        self._rows.clear()

    def _refresh_task_list(self) -> None:
        self._clear_list()

        open_tasks = self._open_tasks()
        done_tasks = self._done_tasks()

        # The lede speaks to where you are: empty, light, or carrying a lot.
        self._lede.setText(self._lede_text(len(open_tasks)))

        if not open_tasks:
            # The gentle invitation shows whenever the active list is clear,
            # even when the finished drawer is open below it.
            self._add_empty_state()
        else:
            for task in open_tasks:
                roww = TaskRow(task, reduced_motion=self._reduced_motion)
                roww.done_requested.connect(lambda t=task: self._complete(t))
                roww.remove_requested.connect(lambda t=task: self._let_go(t))
                self._list_box.addWidget(roww)
                self._rows.append(roww)

        if self._show_done:
            if done_tasks:
                cap = QLabel("Set down")
                cap.setFont(sans_font(11, QFont.Weight.DemiBold))
                cap.setStyleSheet(
                    f"color: {ONYX['text_muted']}; background: transparent; letter-spacing: 1px;"
                )
                wrap = QWidget()
                wrap.setStyleSheet("background: transparent;")
                wl = QVBoxLayout(wrap)
                wl.setContentsMargins(2, 14, 2, 4)
                wl.addWidget(cap)
                self._list_box.addWidget(wrap)
            for task in done_tasks:
                roww = TaskRow(task, completed_view=True, reduced_motion=self._reduced_motion)
                self._list_box.addWidget(roww)
                self._rows.append(roww)

        self._done_toggle.setText(
            "Tuck the finished away" if self._show_done else "Show what you've set down"
        )
        self._done_toggle.setVisible(bool(done_tasks) or self._show_done)

    def _lede_text(self, open_count: int) -> str:
        if open_count == 0:
            return "Nothing pressing. The lightest first, whenever you're ready."
        if open_count == 1:
            return "Just the one. Start where it's easiest — it's right here."
        if open_count <= 4:
            return "The gentlest is on top. You don't have to take them in order."
        return "Plenty here, so it's sorted by what costs you least. One is enough for today."

    def _add_empty_state(self) -> None:
        card = HearthCard(elevation=0, radius=20)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(30, 34, 30, 34)
        layout.setSpacing(8)

        line = QLabel("Clear, for now.")
        line.setFont(serif_font(20, QFont.Weight.Medium))
        line.setAlignment(Qt.AlignmentFlag.AlignCenter)
        line.setStyleSheet(f"color: {ONYX['text']}; background: transparent;")
        layout.addWidget(line)

        sub = QLabel(
            "When something starts circling in your head, set it down up there "
            "and let it rest with me instead."
        )
        sub.setFont(serif_font(15))
        sub.setWordWrap(True)
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(f"color: {ONYX['text_muted']}; background: transparent;")
        layout.addWidget(sub)

        self._list_box.addWidget(card)

    def _acknowledge(self, text: str) -> None:
        self._add_echo.setText(text)
        self._add_echo.setVisible(True)
        QTimer.singleShot(2600, lambda: self._add_echo.setVisible(False))

    # ------------------------------------------------------------------
    # Actions — unchanged data paths, warmed gestures
    # ------------------------------------------------------------------
    def _add_task_from_nlp(self) -> None:
        text = self._nlp_input.text().strip()
        if not text:
            return

        added_title = text
        if self._nlp_parser and hasattr(self._nlp_parser, "parse"):
            try:
                parsed = self._nlp_parser.parse(text)
                if self._task_manager and hasattr(self._task_manager, "add_task"):
                    from core.task_manager import Task, TaskCategory, TaskPriority

                    priority_map = {
                        "urgent": TaskPriority.Urgent,
                        "high": TaskPriority.High,
                        "medium": TaskPriority.Medium,
                        "low": TaskPriority.Low,
                    }
                    category_map = {c.value: c for c in TaskCategory}
                    p = getattr(parsed, "priority", None)
                    p_val = (
                        p.value
                        if p is not None and hasattr(p, "value")
                        else str(p).lower()
                        if p
                        else "medium"
                    )
                    added_title = getattr(parsed, "title", text)
                    task = Task(
                        title=added_title,
                        priority=priority_map.get(p_val, TaskPriority.Medium),
                        category=category_map.get(
                            getattr(parsed, "category", "Other"), TaskCategory.Other
                        ),
                        energy_required=getattr(parsed, "energy", 50),
                        due_date=getattr(parsed, "due_date", None),
                    )
                    self._push_undo("add", task)
                    self._task_manager.add_task(task)
                    self.task_added.emit()
            except (AttributeError, TypeError):
                self._add_task_simple(text)
        else:
            self._add_task_simple(text)

        self._nlp_input.clear()
        self._acknowledge(f"Got it. “{added_title}” is with me now.")
        self._refresh_task_list()

    def _add_task_simple(self, text: str) -> None:
        if not self._task_manager:
            return
        try:
            from core.task_manager import Task, TaskCategory, TaskPriority

            task = Task(
                title=text,
                priority=TaskPriority.Medium,
                category=TaskCategory.Other,
                energy_required=50,
            )
            self._push_undo("add", task)
            self._task_manager.add_task(task)
            self.task_added.emit()
        except (AttributeError, TypeError) as exc:
            logger.debug(f"Add task error: {exc}")

    def _complete(self, task: Any) -> None:
        self._push_undo("complete", task)
        if self._task_manager and hasattr(self._task_manager, "complete_task"):
            self._task_manager.complete_task(task)
        else:
            task.completed = True
            task.completed_at = datetime.now()
        self.task_completed.emit()
        self._refresh_task_list()

    def _let_go(self, task: Any) -> None:
        # Removing a task you no longer need. No confirm modal in a tender
        # surface — it goes quietly, and Undo can always bring it back.
        self._push_undo("delete", task)
        if self._task_manager:
            try:
                if hasattr(self._task_manager, "delete_task"):
                    self._task_manager.delete_task(getattr(task, "id", task))
                else:
                    self._task_manager.tasks.remove(task)
                    if hasattr(self._task_manager, "_save_tasks"):
                        self._task_manager._save_tasks()
            except (ValueError, AttributeError):
                pass
        self._refresh_task_list()

    def _toggle_done(self) -> None:
        self._show_done = not self._show_done
        self._refresh_task_list()

    # -- undo / redo (kept for behavior parity) -------------------------
    def _push_undo(self, action: str, task: Any) -> None:
        self._undo_stack.append({"action": action, "task": task})
        self._redo_stack.clear()

    def _undo(self) -> None:
        if not self._undo_stack:
            return
        entry = self._undo_stack.pop()
        self._redo_stack.append(entry)
        action = entry["action"]
        task = entry["task"]
        if action == "add" and self._task_manager:
            try:
                self._task_manager.tasks.remove(task)
                if hasattr(self._task_manager, "_save_tasks"):
                    self._task_manager._save_tasks()
            except ValueError:
                pass
        elif action == "delete" and self._task_manager:
            self._task_manager.tasks.append(task)
            if hasattr(self._task_manager, "_save_tasks"):
                self._task_manager._save_tasks()
        elif action == "complete":
            task.completed = False
            task.completed_at = None
            if self._task_manager and hasattr(self._task_manager, "_save_tasks"):
                self._task_manager._save_tasks()
        self._refresh_task_list()

    def _redo(self) -> None:
        if not self._redo_stack:
            return
        entry = self._redo_stack.pop()
        self._undo_stack.append(entry)
        action = entry["action"]
        task = entry["task"]
        if action == "add" and self._task_manager:
            self._task_manager.tasks.append(task)
            if hasattr(self._task_manager, "_save_tasks"):
                self._task_manager._save_tasks()
        elif action == "delete" and self._task_manager:
            try:
                self._task_manager.tasks.remove(task)
                if hasattr(self._task_manager, "_save_tasks"):
                    self._task_manager._save_tasks()
            except ValueError:
                pass
        elif action == "complete":
            task.completed = True
            task.completed_at = datetime.now()
            if self._task_manager and hasattr(self._task_manager, "_save_tasks"):
                self._task_manager._save_tasks()
        self._refresh_task_list()

    # ------------------------------------------------------------------
    # Misc
    # ------------------------------------------------------------------
    def _detect_reduced_motion(self) -> bool:
        try:
            from utils.accessibility import detect_reduced_motion

            return detect_reduced_motion()
        except Exception:  # accessibility probing must never block the screen
            return False

    def apply_theme(self, theme: dict[str, str]) -> None:
        self._theme = theme
        self.update()
