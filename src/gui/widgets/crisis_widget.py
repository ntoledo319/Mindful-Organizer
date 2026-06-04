"""
Crisis -> "Stay" — the live crisis view as the whole room turning toward you.

This is a life-safety surface, reached on the worst night of someone's month,
possibly at 2am, with their cognitive budget near zero and the stakes near
maximum. It is not a database with a UI; it is a hand reaching back.

So it is not a stack of bordered ``QGroupBox`` cards. It is a single warm dark
canvas (painted from theme colors) with a calm Hearthlight presence, one large
serif sentence, and one enormous, dignified, *warm* lifeline button. Crisis Text
Line and SAMHSA are present but quieter. The deterioration checklist (warning
signs) is kept off the live screen entirely — it lives in the calm-state editor.

The signature moment (docs/design/VISION.md, signature C): when the person
reaches for the lifeline, the whole room settles into a slow ~60bpm heartbeat —
the Hearthlight glow easing up and down below their panic rate, "the line is
open." Reduced motion gets a steady warm hold and the same words.

Behavior preserved verbatim from Wave 0 (never weaken a safety path):
  * the 988 / Crisis Text Line / SAMHSA buttons copy the number, fire ``tel:``,
    and now confirm *in-surface and persistently* (not a vanishing tooltip);
  * crisis-plan load / save / edit;
  * seed-placeholder stripping so the live screen never nags "Use Edit to add".
"""

from __future__ import annotations

import contextlib
import json
import logging
from pathlib import Path
from typing import Any

from PyQt6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    QSequentialAnimationGroup,
    Qt,
    QTimer,
    QUrl,
    pyqtSignal,
)
from PyQt6.QtGui import QColor, QDesktopServices, QFont, QPainter, QRadialGradient
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.paths import get_data_dir
from gui.components.hearth_surfaces import HearthButton, HearthCard
from gui.components.hearthlight import Hearthlight
from gui.components.state_controls import sans_font, serif_font

logger = logging.getLogger(__name__)


def _dialable_digits(number: str) -> str:
    """Extract a dialable digit string from a free-form contact number.

    "Text HOME to 741741" -> "741741"; "1-800-662-4357" -> "18006624357".
    Returns "" when the string carries no digits.
    """
    return "".join(ch for ch in number if ch.isdigit())


def _activate_contact(number: str) -> str:
    """Copy a crisis number to the clipboard and attempt to place the call.

    On desktop a `tel:` handler may or may not exist, so the reliable, always-on
    behaviour is putting the number on the clipboard. Returns the digits placed
    on the clipboard so the caller can confirm *in-surface and persistently* —
    a distressed person should never tap a crisis button and get nothing.
    """
    digits = _dialable_digits(number)
    clip = QApplication.clipboard()
    if clip is not None:
        clip.setText(digits or number)
    if digits:
        with contextlib.suppress(Exception):
            QDesktopServices.openUrl(QUrl(f"tel:{digits}"))
    return digits or number


def _real_entries(items: list[str]) -> list[str]:
    """Keep only entries a person actually wrote.

    The seed plan ships placeholder prompts ("Add your safe places here...").
    Those are guidance for the Edit dialog, not content — they must never show
    up as a half-finished line in the live crisis view.
    """
    real: list[str] = []
    for raw in items:
        text = str(raw).strip()
        if not text or text.lower().startswith("add your"):
            continue
        real.append(text)
    return real


def _strip_numbering(text: str) -> str:
    """Drop a leading "1. " / "2) " ordinal so coping lines read as quiet help.

    The seed strategies are numbered for the editor; on the live screen a count
    reads as a checklist to complete, which is the last thing a person in crisis
    needs. "1. Take slow, deep breaths" -> "Take slow, deep breaths".
    """
    s = text.strip()
    i = 0
    while i < len(s) and s[i].isdigit():
        i += 1
    if i > 0 and i < len(s) and s[i] in ".)":
        return s[i + 1 :].strip()
    return s


# ---------------------------------------------------------------------------
# Default crisis data
# ---------------------------------------------------------------------------

_DEFAULT_CRISIS_PLAN: dict[str, Any] = {
    "emergency_contacts": [
        {
            "name": "988 Suicide & Crisis Lifeline",
            "phone": "988",
            "relationship": "National Hotline",
        },
        {
            "name": "Crisis Text Line",
            "phone": "Text HOME to 741741",
            "relationship": "Text Service",
        },
        {"name": "SAMHSA Helpline", "phone": "1-800-662-4357", "relationship": "Substance Abuse"},
    ],
    "personal_contacts": [],
    "professional_contacts": [],
    "warning_signs": [
        "Withdrawing from others",
        "Difficulty sleeping or sleeping too much",
        "Feeling hopeless or trapped",
        "Increasing substance use",
        "Extreme mood swings",
        "Giving away possessions",
        "Talking about being a burden",
    ],
    "coping_strategies": [
        "1. Take slow, deep breaths -- 4 counts in, 7 hold, 8 out",
        "2. Hold ice cubes or splash cold water on your face",
        "3. Name 5 things you can see, 4 you can touch, 3 you can hear",
        "4. Call a trusted friend or family member",
        "5. Go to a safe place (see list below)",
        "6. Write down your feelings in a journal",
        "7. Remind yourself: this feeling is temporary",
        "8. If in danger, call 988 or go to nearest emergency room",
    ],
    "reasons_for_living": [
        "Add your personal reasons here...",
    ],
    "safe_places": [
        "Add your safe places here...",
    ],
}


# ---------------------------------------------------------------------------
# Edit dialog (calm-state editing — reached from the live screen, never shown
# during the moment itself). Warning signs live here, not on the live canvas.
# ---------------------------------------------------------------------------


class _CrisisPlanEditDialog(QDialog):
    """Dialog for editing the crisis plan."""

    def __init__(
        self,
        plan: dict[str, Any],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Edit Crisis Plan")
        self.setMinimumSize(700, 600)
        self._plan = {k: (list(v) if isinstance(v, list) else v) for k, v in plan.items()}

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Personal contacts
        layout.addWidget(
            _edit_header("Personal Contacts (name | phone | relationship, one per line)")
        )
        self._personal_edit = QTextEdit()
        self._personal_edit.setPlainText(
            "\n".join(
                f"{c.get('name', '')} | {c.get('phone', '')} | {c.get('relationship', '')}"
                for c in self._plan.get("personal_contacts", [])
            )
        )
        self._personal_edit.setMaximumHeight(100)
        layout.addWidget(self._personal_edit)

        # Professional contacts
        layout.addWidget(_edit_header("Professional Contacts (name | phone | role)"))
        self._prof_edit = QTextEdit()
        self._prof_edit.setPlainText(
            "\n".join(
                f"{c.get('name', '')} | {c.get('phone', '')} | {c.get('relationship', '')}"
                for c in self._plan.get("professional_contacts", [])
            )
        )
        self._prof_edit.setMaximumHeight(100)
        layout.addWidget(self._prof_edit)

        # Warning signs (calm-state only — never on the live screen)
        layout.addWidget(_edit_header("Warning Signs (one per line)"))
        self._warnings_edit = QTextEdit()
        self._warnings_edit.setPlainText("\n".join(self._plan.get("warning_signs", [])))
        self._warnings_edit.setMaximumHeight(100)
        layout.addWidget(self._warnings_edit)

        # Coping strategies
        layout.addWidget(_edit_header("Coping Strategies (one per line)"))
        self._coping_edit = QTextEdit()
        self._coping_edit.setPlainText("\n".join(self._plan.get("coping_strategies", [])))
        self._coping_edit.setMaximumHeight(100)
        layout.addWidget(self._coping_edit)

        # Reasons for living
        layout.addWidget(_edit_header("Reasons for Living (one per line)"))
        self._reasons_edit = QTextEdit()
        self._reasons_edit.setPlainText("\n".join(self._plan.get("reasons_for_living", [])))
        self._reasons_edit.setMaximumHeight(80)
        layout.addWidget(self._reasons_edit)

        # Safe places
        layout.addWidget(_edit_header("Safe Places (one per line)"))
        self._safe_edit = QTextEdit()
        self._safe_edit.setPlainText("\n".join(self._plan.get("safe_places", [])))
        self._safe_edit.setMaximumHeight(80)
        layout.addWidget(self._safe_edit)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _parse_contacts(self, text: str) -> list[dict[str, str]]:
        contacts: list[dict[str, str]] = []
        for line in text.strip().split("\n"):
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 2 and parts[0]:
                contacts.append(
                    {
                        "name": parts[0],
                        "phone": parts[1] if len(parts) > 1 else "",
                        "relationship": parts[2] if len(parts) > 2 else "",
                    }
                )
        return contacts

    def get_plan(self) -> dict[str, Any]:
        return {
            "emergency_contacts": self._plan.get("emergency_contacts", []),
            "personal_contacts": self._parse_contacts(self._personal_edit.toPlainText()),
            "professional_contacts": self._parse_contacts(self._prof_edit.toPlainText()),
            "warning_signs": [
                s.strip() for s in self._warnings_edit.toPlainText().split("\n") if s.strip()
            ],
            "coping_strategies": [
                s.strip() for s in self._coping_edit.toPlainText().split("\n") if s.strip()
            ],
            "reasons_for_living": [
                s.strip() for s in self._reasons_edit.toPlainText().split("\n") if s.strip()
            ],
            "safe_places": [
                s.strip() for s in self._safe_edit.toPlainText().split("\n") if s.strip()
            ],
        }


def _edit_header(text: str) -> QLabel:
    label = QLabel(text)
    label.setTextFormat(Qt.TextFormat.PlainText)
    label.setFont(sans_font(13, weight=QFont.Weight.DemiBold))
    return label


# ---------------------------------------------------------------------------
# The "Stay" canvas
# ---------------------------------------------------------------------------


class CrisisWidget(QWidget):
    """Crisis -> "Stay": one warm room, one sentence, one human."""

    plan_updated = pyqtSignal()

    # The heartbeat that opens when someone reaches for the lifeline: ~60bpm,
    # one full ease up + down per second, paced *below* panic to pull them down.
    _HEARTBEAT_MS = 1000
    _GLOW_REST = 0.46  # the room at rest — a banked, watchful coal
    _GLOW_BEAT_HI = 0.92  # the held-open line, brightest of the beat
    _GLOW_BEAT_LO = 0.58  # the trough — never dark, the line never drops

    def __init__(self, main_window: Any, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.main_window = main_window
        self._plan: dict[str, Any] = dict(_DEFAULT_CRISIS_PLAN)
        self._theme = self._resolve_theme()
        self._reduced_motion = self._resolve_reduced_motion()
        self._reason_idx = 0
        self._reasons: list[str] = []

        # Crisis plan manager (optional)
        self._crisis_manager = None
        with contextlib.suppress(Exception):
            self._crisis_manager = main_window.crisis_plan_manager

        self._data_dir = self._resolve_data_dir()
        self._load_plan()
        self._build_ui()

    # ------------------------------------------------------------------
    # Theme / motion
    # ------------------------------------------------------------------

    def _resolve_theme(self) -> dict[str, str]:
        with contextlib.suppress(Exception):
            return dict(self.main_window.theme_manager.get_colors())
        return {}

    def _resolve_reduced_motion(self) -> bool:
        with contextlib.suppress(Exception):
            return bool(self.main_window.theme_manager.reduced_motion)
        return False

    def _color(self, key: str, fallback: str) -> str:
        return self._theme.get(key, fallback)

    # ------------------------------------------------------------------
    # Persistence (unchanged from Wave 0)
    # ------------------------------------------------------------------

    def _resolve_data_dir(self) -> Path:
        try:
            return Path(self.main_window.data_dir)
        except (AttributeError, TypeError):
            p = get_data_dir()
            p.mkdir(parents=True, exist_ok=True)
            return p

    def _plan_file(self) -> Path:
        self._data_dir.mkdir(parents=True, exist_ok=True)
        return self._data_dir / "crisis_plan.json"

    def _load_plan(self) -> None:
        if self._crisis_manager and hasattr(self._crisis_manager, "get_quick_access"):
            try:
                self._plan.update(
                    self._quick_access_to_plan(self._crisis_manager.get_quick_access())
                )
                return
            except Exception as exc:
                logger.debug(f"Crisis manager load error: {exc}")
        path = self._plan_file()
        if path.exists():
            try:
                with open(path) as fh:
                    loaded = json.load(fh)
                self._plan.update(loaded)
            except (json.JSONDecodeError, OSError) as exc:
                logger.debug(f"Crisis plan load error: {exc}")

    def _quick_access_to_plan(self, quick: dict[str, Any]) -> dict[str, Any]:
        """Adapt CrisisPlanManager quick-access data to this widget's plan shape."""
        emergency_contacts = []
        for contact in quick.get("crisis_lines", []):
            emergency_contacts.append(
                {
                    "name": contact.get("name", ""),
                    "phone": contact.get("phone", "") or contact.get("instructions", ""),
                    "relationship": "Crisis line",
                }
            )
        professional_contacts = []
        for contact in quick.get("professionals", []):
            professional_contacts.append(
                {
                    "name": contact.get("name", ""),
                    "phone": contact.get("phone", ""),
                    "relationship": contact.get("role", "Professional"),
                }
            )
        personal_contacts = []
        for contact in quick.get("call_someone", []):
            personal_contacts.append(
                {
                    "name": contact.get("name", ""),
                    "phone": contact.get("phone", ""),
                    "relationship": contact.get("relationship", ""),
                }
            )
        return {
            "emergency_contacts": emergency_contacts or _DEFAULT_CRISIS_PLAN["emergency_contacts"],
            "personal_contacts": personal_contacts,
            "professional_contacts": professional_contacts,
            "warning_signs": list(_DEFAULT_CRISIS_PLAN["warning_signs"]),
            "coping_strategies": quick.get("try_first", [])
            or _DEFAULT_CRISIS_PLAN["coping_strategies"],
            "reasons_for_living": quick.get("reasons_for_living", []),
            "safe_places": quick.get("safe_places", []),
        }

    def _save_plan(self) -> None:
        if self._crisis_manager and hasattr(self._crisis_manager, "update_plan"):
            try:
                from wellness.crisis_plan import CrisisPlan

                self._crisis_manager.update_plan(
                    CrisisPlan(
                        warning_signs=self._plan.get("warning_signs", []),
                        coping_strategies=self._plan.get("coping_strategies", []),
                        safe_places=self._plan.get("safe_places", []),
                        reasons_for_living=self._plan.get("reasons_for_living", []),
                    )
                )
                return
            except Exception as exc:
                logger.debug(f"Crisis manager save error: {exc}")
        try:
            with open(self._plan_file(), "w") as fh:
                json.dump(self._plan, fh, indent=2)
        except (OSError, TypeError) as exc:
            logger.debug(f"Crisis plan save error: {exc}")

    # ------------------------------------------------------------------
    # The warm room — painted, not a card stack
    # ------------------------------------------------------------------

    def paintEvent(self, _event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        bg = QColor(self._color("background", "#0F0F11"))
        p.fillRect(self.rect(), bg)

        # Warmth rises from the ember at the top — the room lit from one corner,
        # the last warm room in a cold house. It pools behind the lifeline so the
        # eye is drawn down toward the one action, not scattered across cards.
        accent = QColor(self._color("accent", "#D9A05B"))
        cx = self.width() / 2
        top = QRadialGradient(cx, self.height() * 0.20, self.width() * 0.62)
        warm = QColor(accent)
        warm.setAlpha(34)
        top.setColorAt(0.0, warm)
        top.setColorAt(1.0, QColor(accent.red(), accent.green(), accent.blue(), 0))
        p.fillRect(self.rect(), top)

        # A second, lower bloom under the lifeline so it feels held in light.
        low = QRadialGradient(cx, self.height() * 0.56, self.width() * 0.5)
        warm2 = QColor(accent)
        warm2.setAlpha(20)
        low.setColorAt(0.0, warm2)
        low.setColorAt(1.0, QColor(accent.red(), accent.green(), accent.blue(), 0))
        p.fillRect(self.rect(), low)
        p.end()

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        text = self._color("text", "#F2EDE6")
        accent = self._color("accent", "#D9A05B")
        muted = self._color("text_muted", "#A99B88")

        root = QVBoxLayout(self)
        root.setContentsMargins(40, 30, 40, 30)
        root.setSpacing(0)
        root.addStretch(2)

        # A column that stays a calm reading width, centered in the room.
        column = QWidget()
        column.setMaximumWidth(620)
        col = QVBoxLayout(column)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(0)
        col.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # The ember — the room's calm presence, watching.
        ember_row = QHBoxLayout()
        ember_row.addStretch()
        self._ember = Hearthlight(
            glow=self._GLOW_REST,
            reduced_motion=self._reduced_motion,
            transparent_bg=True,
        )
        self._ember.setFixedSize(116, 116)
        ember_row.addWidget(self._ember)
        ember_row.addStretch()
        col.addLayout(ember_row)
        col.addSpacing(18)

        # The one sentence — large, serif, the first and maybe only thing read.
        self._sentence = QLabel("You don't have to get through\nthis alone right now.")
        self._sentence.setFont(serif_font(27))
        self._sentence.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._sentence.setWordWrap(True)
        self._sentence.setStyleSheet(f"color: {text}; background: transparent;")
        col.addWidget(self._sentence)
        col.addSpacing(26)

        # The one true action — the 988 lifeline, big, warm, dignified.
        self._lifeline = self._build_lifeline()
        col.addWidget(self._lifeline)
        col.addSpacing(14)

        # The persistent, calm in-surface confirmation (hidden until tapped).
        self._confirm = self._build_confirmation()
        self._confirm.setVisible(False)
        col.addWidget(self._confirm)

        # The quieter, secondary lines — text + a person, if they have one.
        self._build_secondary_lines(col)
        col.addSpacing(22)

        # Reasons for living — surfaced gently, one at a time, only if real.
        self._build_reasons(col)

        # A few calm coping steps, most-accessible first.
        self._build_coping(col)
        col.addSpacing(20)

        # Edit (calm-state) + disclaimer — quiet, at the foot of the room.
        edit_row = QHBoxLayout()
        edit_row.addStretch()
        edit_btn = HearthButton(
            "Edit your safety plan", role="ghost", reduced_motion=self._reduced_motion
        )
        edit_btn.clicked.connect(self._edit_plan)
        edit_row.addWidget(edit_btn)
        edit_row.addStretch()
        col.addLayout(edit_row)
        col.addSpacing(8)

        self._disclaimer = QLabel(
            "Hearth sits with you, but it can't be your doctor. If you're in danger "
            "right now, please call 988 — they're awake, and they're for exactly this."
        )
        self._disclaimer.setFont(sans_font(11))
        self._disclaimer.setWordWrap(True)
        self._disclaimer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._disclaimer.setStyleSheet(f"color: {muted}; background: transparent;")
        col.addWidget(self._disclaimer)

        column_row = QHBoxLayout()
        column_row.addStretch()
        column_row.addWidget(column)
        column_row.addStretch()
        root.addLayout(column_row)
        root.addStretch(3)

        # The heartbeat that opens when the lifeline is reached for.
        self._build_heartbeat()
        _ = accent  # accent flows through painted surfaces; referenced for clarity

    def _build_lifeline(self) -> QWidget:
        """The 988 line, as the single largest, warmest action on the screen."""
        contacts = self._plan.get("emergency_contacts", [])
        primary = contacts[0] if contacts else _DEFAULT_CRISIS_PLAN["emergency_contacts"][0]
        name = primary.get("name", "988 Suicide & Crisis Lifeline")
        number = primary.get("phone", "988")
        self._primary_number = number

        card = HearthCard(elevation=2, radius=20)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(28, 24, 28, 24)
        lay.setSpacing(6)

        label = QLabel("Call 988 — talk to someone now")
        label.setFont(serif_font(23, weight=QFont.Weight.DemiBold))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(f"color: {self._color('text', '#F2EDE6')}; background: transparent;")

        sub = QLabel(_clean_lifeline_name(name))
        sub.setFont(sans_font(13))
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(
            f"color: {self._color('text_muted', '#A99B88')}; background: transparent;"
        )

        btn = HearthButton("Call 988", role="primary", reduced_motion=self._reduced_motion)
        btn.setMinimumHeight(64)
        font = btn.font()
        font.setPointSize(17)
        btn.setFont(font)
        btn.clicked.connect(lambda: self._reach_out(number))

        lay.addWidget(label)
        lay.addWidget(sub)
        lay.addSpacing(10)
        lay.addWidget(btn)
        return card

    def _build_confirmation(self) -> QLabel:
        """A persistent, calm confirmation — never a vanishing tooltip."""
        label = QLabel("")
        label.setFont(sans_font(13))
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        accent = self._color("accent", "#D9A05B")
        label.setStyleSheet(f"color: {accent}; background: transparent;")
        return label

    def _build_secondary_lines(self, col: QVBoxLayout) -> None:
        """Crisis Text Line, SAMHSA, and a trusted person — present but quieter."""
        contacts = self._plan.get("emergency_contacts", [])
        row = QHBoxLayout()
        row.setSpacing(10)
        row.addStretch()
        # The remaining emergency lines (text line, SAMHSA) ride quieter as ghosts.
        for contact in contacts[1:]:
            number = contact.get("phone", "")
            label = _secondary_label(contact.get("name", ""), number)
            if not number.strip():
                continue
            btn = HearthButton(label, role="ghost", reduced_motion=self._reduced_motion)
            btn.clicked.connect(lambda _checked=False, num=number: self._reach_out(num))
            row.addWidget(btn)

        # A person they trust — only if they wrote one. Never an empty "add" slot.
        personal = self._plan.get("personal_contacts", [])
        for c in personal[:1]:
            number = c.get("phone", "")
            if not number.strip():
                continue
            name = c.get("name", "")
            btn = HearthButton(f"Call {name}", role="ghost", reduced_motion=self._reduced_motion)
            btn.clicked.connect(lambda _checked=False, num=number: self._reach_out(num))
            row.addWidget(btn)
        row.addStretch()
        wrap = QWidget()
        wrap.setLayout(row)
        col.addWidget(wrap)

    def _build_reasons(self, col: QVBoxLayout) -> None:
        """The person's own reasons for living — the emotional core, one at a time."""
        self._reasons = _real_entries(self._plan.get("reasons_for_living", []))
        if not self._reasons:
            self._reason_label = None
            return

        intro = QLabel("Some of what you wanted to stay for")
        intro.setFont(sans_font(11, weight=QFont.Weight.DemiBold))
        intro.setAlignment(Qt.AlignmentFlag.AlignCenter)
        intro.setStyleSheet(
            f"color: {self._color('text_muted', '#A99B88')}; background: transparent;"
        )
        col.addWidget(intro)
        col.addSpacing(6)

        self._reason_label = QLabel(self._reasons[0])
        self._reason_label.setFont(serif_font(21))
        self._reason_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._reason_label.setWordWrap(True)
        self._reason_label.setStyleSheet(
            f"color: {self._color('text', '#F2EDE6')}; background: transparent;"
        )
        self._reason_opacity = QGraphicsOpacityEffect(self._reason_label)
        self._reason_opacity.setOpacity(1.0)
        self._reason_label.setGraphicsEffect(self._reason_opacity)
        col.addWidget(self._reason_label)
        col.addSpacing(22)

        # Cycle gently between reasons, one at a time, with a slow crossfade.
        if len(self._reasons) > 1 and not self._reduced_motion:
            self._reason_fade = QPropertyAnimation(self._reason_opacity, b"opacity", self)
            self._reason_fade.setDuration(900)
            self._reason_fade.setEasingCurve(QEasingCurve.Type.InOutSine)
            self._reason_timer = QTimer(self)
            self._reason_timer.setInterval(7000)
            self._reason_timer.timeout.connect(self._next_reason)
            self._reason_timer.start()

    def _next_reason(self) -> None:
        if not self._reasons or self._reason_label is None:
            return
        # Fade out, swap text at the trough, fade back in.
        self._reason_fade.stop()
        self._reason_fade.setStartValue(1.0)
        self._reason_fade.setEndValue(0.0)

        def _swap() -> None:
            self._reason_idx = (self._reason_idx + 1) % len(self._reasons)
            self._reason_label.setText(self._reasons[self._reason_idx])
            self._reason_fade.stop()
            self._reason_fade.setStartValue(0.0)
            self._reason_fade.setEndValue(1.0)
            self._reason_fade.start()

        with contextlib.suppress(TypeError):
            self._reason_fade.finished.disconnect()
        self._reason_fade.finished.connect(_swap, Qt.ConnectionType.SingleShotConnection)
        self._reason_fade.start()

    def _build_coping(self, col: QVBoxLayout) -> None:
        """A few calm steps, most-accessible first — quiet, never a checklist."""
        raw = self._plan.get("coping_strategies", [])
        steps = [_strip_numbering(str(s)) for s in raw if str(s).strip()]
        # Keep it short — a drowning person reads one or two lines, not eight.
        steps = steps[:3]
        if not steps:
            return

        intro = QLabel("Or stay here a moment, and try one small thing")
        intro.setFont(sans_font(11, weight=QFont.Weight.DemiBold))
        intro.setAlignment(Qt.AlignmentFlag.AlignCenter)
        intro.setStyleSheet(
            f"color: {self._color('text_muted', '#A99B88')}; background: transparent;"
        )
        col.addWidget(intro)
        col.addSpacing(6)

        for step in steps:
            line = QLabel(step)
            line.setFont(serif_font(15))
            line.setAlignment(Qt.AlignmentFlag.AlignCenter)
            line.setWordWrap(True)
            line.setStyleSheet(f"color: {self._color('text', '#F2EDE6')}; background: transparent;")
            col.addWidget(line)
            col.addSpacing(4)

    # ------------------------------------------------------------------
    # Signature moment — "the line is open"
    # ------------------------------------------------------------------

    def _build_heartbeat(self) -> None:
        """A ~60bpm glow pulse on the ember — the room settling, the line open."""
        rest = self._GLOW_BEAT_LO
        self._heartbeat = QSequentialAnimationGroup(self)
        up = QPropertyAnimation(self._ember, b"glow")
        up.setStartValue(self._GLOW_BEAT_LO)
        up.setEndValue(self._GLOW_BEAT_HI)
        up.setDuration(self._HEARTBEAT_MS // 2)
        up.setEasingCurve(QEasingCurve.Type.InOutSine)
        down = QPropertyAnimation(self._ember, b"glow")
        down.setStartValue(self._GLOW_BEAT_HI)
        down.setEndValue(self._GLOW_BEAT_LO)
        down.setDuration(self._HEARTBEAT_MS // 2)
        down.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._heartbeat.addAnimation(up)
        self._heartbeat.addAnimation(down)
        self._heartbeat.setLoopCount(-1)
        _ = rest

    def _reach_out(self, number: str) -> None:
        """Copy + tel: the lifeline, then turn the room toward the person."""
        placed = _activate_contact(number)
        is_988 = "988" in placed

        # The persistent, calm confirmation — replaces the vanishing tooltip.
        if is_988:
            self._confirm.setText(
                "The line is open. 988 is on your clipboard too. "
                "If the call didn't start, dial it — we're not going anywhere."
            )
        else:
            self._confirm.setText(
                f"{placed} is on your clipboard. Reach out when you're ready — we're right here."
            )
        self._confirm.setVisible(True)
        self._update_sentence("Stay. Help is on the way to you.")

        # The room settles into a slow heartbeat, paced below panic to pull down.
        if self._reduced_motion:
            self._ember.set_glow(self._GLOW_BEAT_HI, animate=False)
        else:
            self._ember.stop_breathing()
            self._heartbeat.stop()
            self._ember.set_glow(self._GLOW_BEAT_LO, animate=False)
            self._heartbeat.start()

    def _update_sentence(self, text: str) -> None:
        self._sentence.setText(text)

    # ------------------------------------------------------------------
    # Edit (calm-state)
    # ------------------------------------------------------------------

    def _edit_plan(self) -> None:
        dialog = _CrisisPlanEditDialog(self._plan, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._plan = dialog.get_plan()
            self._save_plan()
            self.plan_updated.emit()
            self._rebuild()

    def _rebuild(self) -> None:
        """Clear and rebuild the entire surface."""
        if hasattr(self, "_reason_timer"):
            self._reason_timer.stop()
        if hasattr(self, "_heartbeat"):
            self._heartbeat.stop()
        old = self.layout()
        if old is not None:
            # Detach the old layout from self so _build_ui can install a fresh
            # one — Qt refuses to set a second layout on a widget that still
            # owns one, which silently leaves the rebuilt content un-managed.
            # Reparenting the layout onto a throwaway widget hands Qt ownership
            # to delete it *and everything still nested in it*, so no orphaned
            # child of self survives to paint over the new room.
            QWidget().setLayout(old)
        # Belt-and-braces: any direct child widget that slipped its layout is
        # deleted now, so a stale label can never ghost over the new surface.
        for child in self.findChildren(QWidget):
            if child.parent() is self:
                child.setParent(None)
                child.deleteLater()
        self._theme = self._resolve_theme()
        self._reduced_motion = self._resolve_reduced_motion()
        self._reason_idx = 0
        self._build_ui()
        self.update()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def save_state(self) -> None:
        """Called by main window on close."""
        self._save_plan()


# ---------------------------------------------------------------------------
# Small, local helpers
# ---------------------------------------------------------------------------


def _clean_lifeline_name(name: str) -> str:
    """The hotline's real name, intact (the & survives — QLabel plain text)."""
    return name.strip() or "988 Suicide & Crisis Lifeline"


def _secondary_label(name: str, number: str) -> str:
    """A short, calm label for the quieter lines."""
    n = name.strip()
    if "text" in n.lower():
        return "Text instead"
    if "samhsa" in n.lower():
        return "SAMHSA helpline"
    return n or number


def _clear_layout(layout) -> None:
    if layout is None:
        return
    while layout.count():
        item = layout.takeAt(0)
        if item is None:
            continue
        w = item.widget()
        if w:
            w.deleteLater()
        else:
            _clear_layout(item.layout())
