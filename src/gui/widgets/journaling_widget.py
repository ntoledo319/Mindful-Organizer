"""
Journal -> a warm notebook. The writing is the hero.

The old surface (docs/design/audit_04 §3.3) buried the one thing that matters —
the act of writing — beneath a prompt card, a category combo, a "Get New Prompt"
button, two mood sliders, a tags field, and two equal amber buttons: a five-
instrument cockpit for typing a sentence. This rebuild inverts the priority. You
open it and a calm, full-width reading-serif page is already waiting, a single
quiet serif prompt resting above it that you can take or ignore (a gentle
"another?" cycles it, never a loud button). Mood-before/after, if kept at all,
are tiny optional word-valued StateSliders tucked at the foot — never a gate to
writing. Setting an entry down is met with an ambient inline fade ("Set down."),
never a QMessageBox.

The load-bearing safety path is preserved verbatim: every entry is quietly read
by ``JournalAnalyzer`` for self-harm / ideation language, and a flagged entry
makes the room turn toward you — the page recedes and a warm panel rises from the
bottom with one human sentence and one calm door to help — then emits
``crisis_requested``, which the main window already routes to the crisis tab.

Behavior preserved for the integrator:
  * constructor signature ``(theme, journal_manager=None, profile_manager=None,
    parent=None)``;
  * the ``entry_saved(dict)`` and ``crisis_requested()`` signals, with the same
    saved-entry payload shape;
  * the persistence path (``journal_manager.save_entry`` else the JSON fallback);
  * ``_check_risk`` -> ``JournalAnalyzer().analyze().risk_flagged`` -> crisis;
  * ``apply_theme``.

Color and type come only from the component helpers (PALETTE, serif_font,
sans_font) — no hardcoded hex, no "Segoe UI".
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import logging
from datetime import date, datetime
from pathlib import Path
from typing import Any

from PyQt6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    QRect,
    Qt,
    QTimer,
    pyqtProperty,
    pyqtSignal,
)
from PyQt6.QtGui import QColor, QFont, QPainter, QRadialGradient
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.paths import get_data_dir
from gui.components.hearth_surfaces import HearthButton, HearthCard
from gui.components.state_controls import (
    PALETTE,
    StateSlider,
    sans_font,
    serif_font,
    warmth_color,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Prompts — quiet serif invitations, never a "Prompt of the Day" card.
# A few warm, plain openers for everyone, with condition-aware ones folded in.
# These are offered, not assigned: you write over them or cycle past them.
# ---------------------------------------------------------------------------

_PROMPTS: dict[str, list[str]] = {
    "General": [
        "What's loud right now?",
        "What's one thing today asked of you?",
        "What would you say if no one were reading?",
        "What are you carrying that you could set down here?",
        "What small thing went right?",
        "Where did your mind keep wandering back to?",
        "If today had a weather, what was it?",
        "What do you want to remember about right now?",
    ],
    "Anxiety": [
        "What's the worry underneath the worry?",
        "What's true right now, not what might happen?",
        "If a friend felt this, what would you tell them?",
        "When did the fear last loosen its grip, even a little?",
    ],
    "Depression": [
        "What got you out of bed, or what made it hard?",
        "Name one thing that took effort today. It counts.",
        "Who, or what, still feels like yours?",
        "What would 'enough' look like tonight?",
    ],
    "ADHD": [
        "Where did your attention actually go today?",
        "Empty your head here — no order, just out.",
        "What slipped through the cracks, and is that okay?",
        "What pulled you in, and what pushed you off?",
    ],
    "OCD": [
        "What did you let stay uncertain today?",
        "What would the extra time be for, if the loop let go?",
        "Where did you choose the discomfort over the ritual?",
        "What's the thought asking of you, really?",
    ],
    "PTSD": [
        "Where did you feel safe, even for a moment?",
        "What's solid and here, in this room, right now?",
        "What helped you come back when you drifted?",
        "What does steady ground feel like for you?",
    ],
    "Bipolar Disorder": [
        "What pace is today moving at?",
        "What's true regardless of how fast things feel?",
        "What would 'steady' ask of you tonight?",
    ],
    "Panic Disorder": [
        "What does your body know that words don't yet?",
        "What helped the wave pass, last time?",
    ],
}


def _prompt_pool(conditions: list[str]) -> list[str]:
    pool: list[str] = list(_PROMPTS.get("General", []))
    for cond in conditions:
        pool.extend(_PROMPTS.get(cond, []))
    if not pool:
        pool = ["Write about anything on your mind."]
    return pool


def _daily_prompt(conditions: list[str]) -> str:
    """Pick a deterministic opener for today (stable across re-opens)."""
    pool = _prompt_pool(conditions)
    seed = int(hashlib.md5(date.today().isoformat().encode()).hexdigest(), 16)
    return pool[seed % len(pool)]


# A felt reads as a word. The optional sliders carry that word back to the 1–10
# scores the rest of the app stores, so persistence is unchanged.
def _slider_to_score(t: float) -> int:
    return max(1, min(10, round(1 + t * 9)))


def _score_to_slider(score: float) -> float:
    return max(0.0, min(1.0, (float(score) - 1.0) / 9.0))


# ---------------------------------------------------------------------------
# A quiet ember acknowledgement — the room saying "Set down.", then receding.
# (Mirrors the mood tracker's _EmberConfirm; never a popup, just a warm word.)
# ---------------------------------------------------------------------------
class _EmberConfirm(QLabel):
    """An inline, fading acknowledgement in the reading serif."""

    def __init__(self, reduced_motion: bool = False, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._reduced_motion = reduced_motion
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFont(serif_font(17))
        self._opacity = 0.0
        self.setStyleSheet(f"color: {PALETTE['accent']}; background: transparent;")
        self.setVisible(False)

        self._fade = QPropertyAnimation(self, b"glow", self)
        self._fade.setEasingCurve(QEasingCurve.Type.InOutSine)

    def _get_glow(self) -> float:
        return self._opacity

    def _set_glow(self, v: float) -> None:
        self._opacity = v
        c = QColor(PALETTE["accent"])
        c.setAlphaF(max(0.0, min(1.0, v)))
        self.setStyleSheet(
            f"color: rgba({c.red()}, {c.green()}, {c.blue()}, {c.alphaF():.3f}); "
            f"background: transparent;"
        )
        if v <= 0.01:
            self.setVisible(False)

    glow = pyqtProperty(float, fget=_get_glow, fset=_set_glow)

    def acknowledge(self, text: str) -> None:
        self.setText(text)
        self.setVisible(True)
        if self._reduced_motion:
            self._set_glow(1.0)
            return
        self._fade.stop()
        self._fade.setDuration(2800)
        self._fade.setKeyValueAt(0.0, 0.0)
        self._fade.setKeyValueAt(0.16, 1.0)
        self._fade.setKeyValueAt(0.72, 1.0)
        self._fade.setKeyValueAt(1.0, 0.0)
        self._fade.start()


# ---------------------------------------------------------------------------
# The crisis panel that rises from the bottom — the room turning toward you.
# Replaces the QMessageBox.Warning risk path (audit_04 §3.3, signature 2).
# ---------------------------------------------------------------------------
class _CrisisPanel(QWidget):
    """A warm, full-width panel that slides up over the foot of the page.

    No triangle icon, no "Warning", no OK/Cancel. One human sentence, one large
    calm door to help (which emits the wired ``crisis_requested``), and the 988
    line in plain reach. It feels like a hand reaching back, not an OS alert.
    """

    open_plan = pyqtSignal()

    def __init__(self, reduced_motion: bool = False, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._reduced_motion = reduced_motion
        self.setVisible(False)
        # Painted, soft, warm — sits above the page during the moment.
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)

        col = QVBoxLayout(self)
        col.setContentsMargins(44, 30, 44, 34)
        col.setSpacing(14)
        col.addStretch()

        line = QLabel("That sounds really heavy. You don't have to hold it alone right now.")
        line.setFont(serif_font(23))
        line.setAlignment(Qt.AlignmentFlag.AlignCenter)
        line.setWordWrap(True)
        line.setStyleSheet(f"color: {PALETTE['text']}; background: transparent;")
        col.addWidget(line)

        sub = QLabel("988 is awake, and it's for exactly this. I can open it, and your plan, now.")
        sub.setFont(sans_font(13))
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setWordWrap(True)
        sub.setStyleSheet(f"color: {PALETTE['text_muted']}; background: transparent;")
        col.addWidget(sub)
        col.addSpacing(6)

        row = QHBoxLayout()
        row.addStretch()
        open_btn = HearthButton(
            "Open 988 and your crisis plan", role="primary", reduced_motion=reduced_motion
        )
        open_btn.setMinimumHeight(54)
        open_btn.clicked.connect(self.open_plan.emit)
        row.addWidget(open_btn)

        stay_btn = HearthButton("Stay with my writing", role="ghost", reduced_motion=reduced_motion)
        stay_btn.clicked.connect(self.dismiss)
        row.addWidget(stay_btn)
        row.addStretch()
        col.addLayout(row)
        col.addStretch()

        self._slide = QPropertyAnimation(self, b"geometry", self)
        self._slide.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._slide.setDuration(0 if reduced_motion else 520)

    def paintEvent(self, _event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()
        # The warmer raised surface, so the panel reads as the room leaning in.
        p.fillRect(rect, QColor(PALETTE["raised"]))
        # Warmth rising from the bottom edge — the hand reaching back.
        accent = QColor(PALETTE["accent"])
        bloom = QRadialGradient(rect.center().x(), rect.bottom(), rect.width() * 0.7)
        warm = QColor(accent)
        warm.setAlpha(40)
        bloom.setColorAt(0.0, warm)
        bloom.setColorAt(1.0, QColor(accent.red(), accent.green(), accent.blue(), 0))
        p.fillRect(rect, bloom)
        # A single soft warm hairline along the top, so it sits in front cleanly.
        edge = QColor(PALETTE["accent"])
        edge.setAlpha(60)
        p.fillRect(QRect(0, 0, rect.width(), 1), edge)
        p.end()

    def rise(self) -> None:
        """Slide up to cover the lower portion of the parent page."""
        parent = self.parentWidget()
        if parent is None:
            self.setVisible(True)
            return
        pw, ph = parent.width(), parent.height()
        h = max(220, int(ph * 0.46))
        end = QRect(0, ph - h, pw, h)
        start = QRect(0, ph, pw, h)
        self.setGeometry(start)
        self.setVisible(True)
        self.raise_()
        if self._reduced_motion:
            self.setGeometry(end)
            return
        self._slide.stop()
        self._slide.setStartValue(start)
        self._slide.setEndValue(end)
        self._slide.start()

    def dismiss(self) -> None:
        if self._reduced_motion or not self.isVisible():
            self.setVisible(False)
            return
        geo = self.geometry()
        end = QRect(geo.x(), self.parentWidget().height(), geo.width(), geo.height())
        self._slide.stop()
        self._slide.setStartValue(geo)
        self._slide.setEndValue(end)
        with contextlib.suppress(TypeError):
            self._slide.finished.disconnect()
        self._slide.finished.connect(
            lambda: self.setVisible(False), Qt.ConnectionType.SingleShotConnection
        )
        self._slide.start()


# ---------------------------------------------------------------------------
# A label that quietly elides its line to fit, so a long first line tapers to
# an ellipsis rather than running off the edge of the page.
# ---------------------------------------------------------------------------
class _ElidedLabel(QLabel):
    def __init__(self, text: str, color: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._full = text
        self._color = QColor(color)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)

    def paintEvent(self, _event) -> None:  # noqa: N802
        p = QPainter(self)
        fm = self.fontMetrics()
        elided = fm.elidedText(self._full, Qt.TextElideMode.ElideRight, self.width())
        p.setPen(self._color)
        p.setFont(self.font())
        p.drawText(self.rect(), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, elided)
        p.end()


# ---------------------------------------------------------------------------
# An entry leaf — one past entry as a quiet warm row, not a database cell.
# Date, the first line, and a single warmth dot encoding the "after" feeling.
# ---------------------------------------------------------------------------
class _EntryLeaf(QWidget):
    """A single past entry, rendered as a calm leaf you can reopen."""

    reopen = pyqtSignal(dict)

    def __init__(self, entry: dict[str, Any], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._entry = entry
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(58)

        row = QHBoxLayout(self)
        row.setContentsMargins(2, 8, 2, 8)
        row.setSpacing(14)

        # The warmth dot — sized small, colored by the "after" feeling if known.
        self._dot = QLabel("")
        self._dot.setFixedSize(14, 58)
        row.addWidget(self._dot, alignment=Qt.AlignmentFlag.AlignVCenter)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)

        raw = entry.get("text", "")
        first = raw.strip().split("\n", 1)[0]
        line = _ElidedLabel(first or "(a quiet one)", PALETTE["text"])
        line.setFont(serif_font(15))
        line.setStyleSheet("background: transparent;")
        text_col.addWidget(line)

        when = entry.get("date", (entry.get("timestamp", "") or "")[:10])
        meta = QLabel(_pretty_date(when))
        meta.setFont(sans_font(11))
        meta.setStyleSheet(f"color: {PALETTE['text_muted']}; background: transparent;")
        text_col.addWidget(meta)

        row.addLayout(text_col, stretch=1)

    def paintEvent(self, _event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        # A soft warm dot down the left, colored by the "after" feeling.
        after = self._entry.get("mood_after")
        t = _score_to_slider(after) if isinstance(after, int | float) else 0.5
        col = warmth_color(t)
        bloom = QRadialGradient(7, self.height() / 2, 9)
        c0 = QColor(col)
        c0.setAlpha(220)
        bloom.setColorAt(0.0, c0)
        bloom.setColorAt(1.0, QColor(col.red(), col.green(), col.blue(), 0))
        p.setBrush(bloom)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(2, int(self.height() / 2 - 7), 14, 14)
        # A quiet hairline beneath, so leaves rest in a column without boxing.
        edge = QColor(PALETTE["border"])
        p.fillRect(QRect(28, self.height() - 1, self.width() - 28, 1), edge)
        p.end()

    def mouseReleaseEvent(self, _event) -> None:  # noqa: N802
        self.reopen.emit(self._entry)


def _pretty_date(iso: str) -> str:
    try:
        d = date.fromisoformat(iso)
    except (ValueError, TypeError):
        return iso or ""
    today = date.today()
    delta = (today - d).days
    if delta == 0:
        return "Today"
    if delta == 1:
        return "Yesterday"
    return d.strftime("%a %d %b")


# ---------------------------------------------------------------------------
# Widget
# ---------------------------------------------------------------------------
class JournalingWidget(QWidget):
    """The notebook: a calm page, a quiet prompt, your words — then set down."""

    entry_saved = pyqtSignal(dict)
    crisis_requested = pyqtSignal()  # emitted when an entry trips risk-language detection

    def __init__(
        self,
        theme: dict[str, str],
        journal_manager: Any = None,
        profile_manager: Any = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._theme = theme
        self._journal_manager = journal_manager
        self._profile_manager = profile_manager

        self._reduced_motion = self._detect_reduced_motion()
        self._bg = QColor(PALETTE["bg"])

        # The optional felt-sliders are tucked away until the writer asks for them.
        self._felt_revealed = False
        self._prompt_pool = _prompt_pool(self._get_conditions())
        self._prompt_idx = 0

        # In-memory entries if no manager
        self._entries: list[dict[str, Any]] = []
        self._load_entries()

        self._build_ui()
        self._refresh_prompt()
        self._refresh_history()

    # ------------------------------------------------------------------
    # Persistence fallback (UNCHANGED — same paths the app already relies on)
    # ------------------------------------------------------------------

    def _data_file(self) -> Path | None:
        if self._journal_manager and hasattr(self._journal_manager, "data_dir"):
            return Path(self._journal_manager.data_dir) / "journal_entries.json"
        home = get_data_dir() / "journal_entries.json"
        home.parent.mkdir(parents=True, exist_ok=True)
        return home

    def _load_entries(self) -> None:
        if self._journal_manager and hasattr(self._journal_manager, "entries"):
            self._entries = list(self._journal_manager.entries)
            return
        path = self._data_file()
        if path and path.exists():
            try:
                with open(path) as fh:
                    self._entries = json.load(fh)
            except (json.JSONDecodeError, OSError):
                self._entries = []

    def _save_entries(self) -> None:
        if self._journal_manager and hasattr(self._journal_manager, "save_entry"):
            return  # manager handles persistence
        path = self._data_file()
        if path:
            try:
                with open(path, "w") as fh:
                    json.dump(self._entries, fh, indent=2, default=str)
            except (OSError, TypeError) as exc:
                logger.warning(f"Failed to save journal entries: {exc}")

    # ------------------------------------------------------------------
    # The warm room behind the page
    # ------------------------------------------------------------------

    def paintEvent(self, _event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), self._bg)
        # A faint warmth pooled near the top, the same off-screen hearth that
        # warms Today and the check-in — the page is lit from one corner.
        grad = QRadialGradient(self.width() / 2, self.height() * 0.10, self.width() * 0.62)
        warm = QColor(PALETTE["accent"])
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
        root = QVBoxLayout(container)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)
        scroll.setWidget(container)

        # A centered reading column — a page, not a dashboard.
        page_row = QHBoxLayout()
        page_row.setContentsMargins(0, 0, 0, 0)
        page_row.addStretch()

        page = QWidget()
        page.setMaximumWidth(680)
        page.setStyleSheet("background: transparent;")
        col = QVBoxLayout(page)
        col.setContentsMargins(36, 40, 36, 44)
        col.setSpacing(0)

        col.addWidget(self._build_writing_card())
        col.addSpacing(30)
        col.addWidget(self._build_history())
        col.addStretch()

        page_row.addWidget(page)
        page_row.addStretch()
        root.addLayout(page_row)

        # The crisis panel lives on top of the whole widget, rising on demand.
        self._crisis_panel = _CrisisPanel(reduced_motion=self._reduced_motion, parent=self)
        self._crisis_panel.open_plan.connect(self._open_crisis)

    # -- the writing card (the hero) ------------------------------------

    def _build_writing_card(self) -> QWidget:
        card = HearthCard(elevation=2, radius=24)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(40, 34, 40, 32)
        layout.setSpacing(0)

        # The quiet prompt — a serif line you can take or ignore, with a gentle
        # "another?" beside it. No "Prompt of the Day" card, no category combo.
        prompt_row = QHBoxLayout()
        prompt_row.setContentsMargins(0, 0, 0, 0)
        prompt_row.setSpacing(10)

        self._prompt_label = QLabel("")
        self._prompt_label.setFont(serif_font(20))
        self._prompt_label.setWordWrap(True)
        self._prompt_label.setStyleSheet(f"color: {PALETTE['text']}; background: transparent;")
        prompt_row.addWidget(self._prompt_label, stretch=1)

        self._another_btn = HearthButton(
            "another?", role="ghost", reduced_motion=self._reduced_motion
        )
        self._another_btn.clicked.connect(self._next_prompt)
        prompt_row.addWidget(self._another_btn, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addLayout(prompt_row)
        layout.addSpacing(18)

        # The editor — borderless, generously leaded, on the card surface. This
        # is the page; it should feel like a notebook, not a textarea.
        self._editor = QTextEdit()
        self._editor.setMinimumHeight(240)
        self._editor.setFrameShape(QTextEdit.Shape.NoFrame)
        self._editor.setPlaceholderText("")  # the prompt above is the invitation
        self._editor.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        edit_font = serif_font(16)
        self._editor.setFont(edit_font)
        self._editor.document().setDocumentMargin(2)
        self._editor.setStyleSheet(
            "QTextEdit { background: transparent; border: none; "
            f"color: {PALETTE['text']}; "
            f"selection-background-color: {PALETTE['raised']}; "
            f"selection-color: {PALETTE['text']}; }}"
        )
        self._editor.textChanged.connect(self._on_text_changed)
        layout.addWidget(self._editor)
        layout.addSpacing(8)

        # The foot of the page: a faint word-count (only after the page has
        # something on it), the optional felt-affordance, then one warm door.
        foot = QHBoxLayout()
        foot.setContentsMargins(0, 0, 0, 0)
        foot.setSpacing(12)

        self._wordcount = QLabel("")
        self._wordcount.setFont(sans_font(11))
        self._wordcount.setStyleSheet(f"color: {PALETTE['text_muted']}; background: transparent;")
        foot.addWidget(self._wordcount)
        foot.addStretch()

        # The felt-affordance — a tiny, optional way to note how the writing
        # moved you, tucked at the edge. Never a gate; revealed only on ask.
        self._felt_toggle = HearthButton(
            "note how this felt", role="ghost", reduced_motion=self._reduced_motion
        )
        self._felt_toggle.clicked.connect(self._reveal_felt)
        foot.addWidget(self._felt_toggle)

        self._save_btn = HearthButton(
            "Set it down", role="primary", reduced_motion=self._reduced_motion
        )
        self._save_btn.clicked.connect(self._save_entry)
        foot.addWidget(self._save_btn)
        layout.addLayout(foot)

        # The optional felt-sliders — hidden until asked for; word-valued, small.
        self._felt_host = self._build_felt_row()
        self._felt_host.setVisible(False)
        layout.addWidget(self._felt_host)

        # The ambient confirmation — "Set down." — fading in place of a popup.
        self._confirm = _EmberConfirm(reduced_motion=self._reduced_motion)
        layout.addWidget(self._confirm)

        return card

    def _build_felt_row(self) -> QWidget:
        host = QWidget()
        host.setStyleSheet("background: transparent;")
        v = QVBoxLayout(host)
        v.setContentsMargins(0, 14, 0, 0)
        v.setSpacing(6)

        rule = QWidget()
        rule.setFixedHeight(1)
        rule.setStyleSheet(f"background: {PALETTE['border']};")
        v.addWidget(rule)
        v.addSpacing(6)

        before_lbl = QLabel("Before you started")
        before_lbl.setFont(sans_font(11))
        before_lbl.setStyleSheet(f"color: {PALETTE['text_muted']}; background: transparent;")
        v.addWidget(before_lbl)
        self._mood_before = StateSlider(value=0.5, reduced_motion=self._reduced_motion)
        self._mood_before.setMinimumHeight(78)
        v.addWidget(self._mood_before)

        after_lbl = QLabel("And after")
        after_lbl.setFont(sans_font(11))
        after_lbl.setStyleSheet(f"color: {PALETTE['text_muted']}; background: transparent;")
        v.addWidget(after_lbl)
        self._mood_after = StateSlider(value=0.5, reduced_motion=self._reduced_motion)
        self._mood_after.setMinimumHeight(78)
        v.addWidget(self._mood_after)

        return host

    # -- history (kept, quieted to a warm stream of leaves) -------------

    def _build_history(self) -> QWidget:
        card = HearthCard(elevation=0, radius=20)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(30, 24, 30, 22)
        layout.setSpacing(6)

        title = QLabel("Pages before this")
        title.setFont(serif_font(17, QFont.Weight.Medium))
        title.setStyleSheet(f"color: {PALETTE['text']}; background: transparent;")
        layout.addWidget(title)

        self._history_empty = QLabel(
            "Nothing here yet. The first thing you write stays between us."
        )
        self._history_empty.setFont(sans_font(12))
        self._history_empty.setWordWrap(True)
        self._history_empty.setStyleSheet(
            f"color: {PALETTE['text_muted']}; background: transparent;"
        )
        layout.addWidget(self._history_empty)
        layout.addSpacing(4)

        self._history_host = QWidget()
        self._history_host.setStyleSheet("background: transparent;")
        self._history_col = QVBoxLayout(self._history_host)
        self._history_col.setContentsMargins(0, 0, 0, 0)
        self._history_col.setSpacing(0)
        layout.addWidget(self._history_host)

        return card

    # ------------------------------------------------------------------
    # Prompt
    # ------------------------------------------------------------------

    def _refresh_prompt(self) -> None:
        self._prompt_pool = _prompt_pool(self._get_conditions())
        prompt = _daily_prompt(self._get_conditions())
        if prompt in self._prompt_pool:
            self._prompt_idx = self._prompt_pool.index(prompt)
        self._prompt_label.setText(prompt)

    def _next_prompt(self) -> None:
        if not self._prompt_pool:
            return
        self._prompt_idx = (self._prompt_idx + 1) % len(self._prompt_pool)
        self._prompt_label.setText(self._prompt_pool[self._prompt_idx])

    def _get_conditions(self) -> list[str]:
        conditions: list[str] = []
        if self._profile_manager and hasattr(self._profile_manager, "current_profile"):
            profile = self._profile_manager.current_profile
            if profile and hasattr(profile, "conditions") and profile.conditions:
                for c in profile.conditions:
                    conditions.append(c.value if hasattr(c, "value") else str(c))
        return conditions

    # ------------------------------------------------------------------
    # Editor
    # ------------------------------------------------------------------

    def _on_text_changed(self) -> None:
        text = self._editor.toPlainText().strip()
        count = len(text.split()) if text else 0
        # The count fades in only once there's a page going — never "Words: 0"
        # scolding an empty page (audit_04 §3.3).
        if count >= 20:
            self._wordcount.setText(f"{count} words")
        else:
            self._wordcount.setText("")

    def _reveal_felt(self) -> None:
        self._felt_revealed = True
        self._felt_host.setVisible(True)
        self._felt_toggle.setVisible(False)

    # ------------------------------------------------------------------
    # Save — same payload, same signals, same risk routing
    # ------------------------------------------------------------------

    def _save_entry(self) -> None:
        text = self._editor.toPlainText().strip()
        if not text:
            # An empty page isn't an error worth a popup — a quiet nudge in place.
            self._confirm.acknowledge("Nothing to set down yet. The page is yours.")
            return

        before_score = _slider_to_score(self._mood_before.value()) if self._felt_revealed else 5
        after_score = _slider_to_score(self._mood_after.value()) if self._felt_revealed else 5

        entry: dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "date": date.today().isoformat(),
            "text": text,
            "mood_before": before_score,
            "mood_after": after_score,
            "tags": [],
            "word_count": len(text.split()),
            "prompt": self._prompt_label.text(),
        }

        # SAME persistence the widget has always used.
        if self._journal_manager and hasattr(self._journal_manager, "save_entry"):
            with contextlib.suppress(Exception):
                self._journal_manager.save_entry(entry)

        self._entries.append(entry)
        self._save_entries()
        self.entry_saved.emit(entry)

        # Read the entry for explicit self-harm / ideation language BEFORE the
        # routine acknowledgement, so a flagged entry turns the room toward help
        # rather than ending in a "set down" and nothing else.
        risk_flagged = self._check_risk(text)

        # Clear the page for the next one.
        self._editor.clear()
        if self._felt_revealed:
            self._mood_before.setValue(0.5)
            self._mood_after.setValue(0.5)
        self._wordcount.setText("")
        self._next_prompt()
        self._refresh_history()

        if risk_flagged:
            self._surface_crisis_resources()
        else:
            self._confirm.acknowledge("Set down. It's safe here.")

    def _check_risk(self, text: str) -> bool:
        """Return True if the entry contains explicit self-harm/ideation language.

        Unchanged: the JournalAnalyzer risk detection the safety net depends on.
        """
        try:
            from wellness.journal_analyzer import JournalAnalyzer

            return JournalAnalyzer().analyze(text).risk_flagged
        except Exception as exc:  # analysis must never block saving
            logger.debug("Journal risk analysis failed: %s", exc)
            return False

    def _surface_crisis_resources(self) -> None:
        """The room turns toward the writer — a rising warm panel, never a popup.

        The panel's primary action emits ``crisis_requested`` (via _open_crisis),
        which the main window already routes to the crisis tab.
        """
        self._crisis_panel.rise()

    def _open_crisis(self) -> None:
        self._crisis_panel.dismiss()
        self.crisis_requested.emit()

    # ------------------------------------------------------------------
    # History (warm stream of leaves)
    # ------------------------------------------------------------------

    def _refresh_history(self) -> None:
        # Clear the column.
        while self._history_col.count():
            item = self._history_col.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        entries = sorted(self._entries, key=lambda e: e.get("timestamp", ""), reverse=True)
        has_any = bool(entries)
        self._history_empty.setVisible(not has_any)
        self._history_host.setVisible(has_any)

        for entry in entries[:40]:
            leaf = _EntryLeaf(entry)
            leaf.reopen.connect(self._reopen_entry)
            self._history_col.addWidget(leaf)

    def _reopen_entry(self, entry: dict[str, Any]) -> None:
        self._editor.setPlainText(entry.get("text", ""))
        if entry.get("prompt"):
            self._prompt_label.setText(entry["prompt"])
        before = entry.get("mood_before")
        after = entry.get("mood_after")
        if isinstance(before, int | float) or isinstance(after, int | float):
            self._reveal_felt()
            if isinstance(before, int | float):
                self._mood_before.setValue(_score_to_slider(before))
            if isinstance(after, int | float):
                self._mood_after.setValue(_score_to_slider(after))
        # Bring the page back into view.
        QTimer.singleShot(0, lambda: self._editor.setFocus())

    # ------------------------------------------------------------------
    # Misc
    # ------------------------------------------------------------------

    def _detect_reduced_motion(self) -> bool:
        try:
            from utils.accessibility import detect_reduced_motion

            return detect_reduced_motion()
        except Exception:  # accessibility probing must never block the screen
            return False

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        # Keep the crisis panel anchored to the foot of the page if it's up.
        if getattr(self, "_crisis_panel", None) is not None and self._crisis_panel.isVisible():
            ph, pw = self.height(), self.width()
            h = max(220, int(ph * 0.46))
            self._crisis_panel.setGeometry(0, ph - h, pw, h)

    # ------------------------------------------------------------------
    # Theme
    # ------------------------------------------------------------------

    def apply_theme(self, theme: dict[str, str]) -> None:
        self._theme = theme
        self.update()
