"""
Crisis plan quick-access widget -- large, calm, distress-friendly UI.

Provides emergency contacts, coping strategies, warning signs, reasons
for living, safe places, and professional contacts in a minimal, readable
layout designed for use during emotional crises.
"""

from __future__ import annotations

import contextlib
import json
import logging
from pathlib import Path
from typing import Any

from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QCursor, QDesktopServices, QFont
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTextEdit,
    QToolTip,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)


def _dialable_digits(number: str) -> str:
    """Extract a dialable digit string from a free-form contact number.

    "Text HOME to 741741" -> "741741"; "1-800-662-4357" -> "18006624357".
    Returns "" when the string carries no digits.
    """
    return "".join(ch for ch in number if ch.isdigit())


def _activate_contact(number: str) -> None:
    """Copy a crisis number to the clipboard and attempt to place the call.

    On desktop a `tel:` handler may or may not exist, so the reliable, always-on
    behaviour is putting the number on the clipboard with visible confirmation —
    a distressed user should never tap a crisis button and get nothing.
    """
    digits = _dialable_digits(number)
    clip = QApplication.clipboard()
    if clip is not None:
        clip.setText(digits or number)
    if digits:
        with contextlib.suppress(Exception):
            QDesktopServices.openUrl(QUrl(f"tel:{digits}"))
    QToolTip.showText(
        QCursor.pos(),
        f"Copied {number} to your clipboard.\nCall it from your phone if dialing isn't available here.",
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _crisis_card() -> QFrame:
    frame = QFrame()
    frame.setObjectName("crisisCard")
    frame.setFrameShape(QFrame.Shape.StyledPanel)
    frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
    return frame


def _large_label(text: str, size: int = 16) -> QLabel:
    label = QLabel(text)
    label.setFont(QFont("Segoe UI", size))
    label.setWordWrap(True)
    return label


def _header_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
    return label


def _contact_button(name: str, number: str) -> QPushButton:
    btn = QPushButton(f"{name}\n{number}")
    btn.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
    btn.setMinimumHeight(70)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setProperty("class", "crisisContact")
    if number.strip():
        btn.setToolTip(f"Click to copy {number} and try to call it")
        btn.clicked.connect(lambda _=False, num=number: _activate_contact(num))
    return btn


def _calm_button(text: str) -> QPushButton:
    btn = QPushButton(text)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
    btn.setProperty("class", "outline")
    return btn


# ---------------------------------------------------------------------------
# Default crisis data
# ---------------------------------------------------------------------------

_DEFAULT_CRISIS_PLAN: dict[str, Any] = {
    "emergency_contacts": [
        {"name": "988 Suicide & Crisis Lifeline", "phone": "988", "relationship": "National Hotline"},
        {"name": "Crisis Text Line", "phone": "Text HOME to 741741", "relationship": "Text Service"},
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
# Edit dialog
# ---------------------------------------------------------------------------

class _CrisisPlanEditDialog(QDialog):
    """Dialog for editing the crisis plan."""

    def __init__(
        self, plan: dict[str, Any],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Edit Crisis Plan")
        self.setMinimumSize(700, 600)
        self._plan = {k: (list(v) if isinstance(v, list) else v) for k, v in plan.items()}

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Personal contacts
        layout.addWidget(_header_label("Personal Contacts (name | phone | relationship, one per line)"))
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
        layout.addWidget(_header_label("Professional Contacts (name | phone | role)"))
        self._prof_edit = QTextEdit()
        self._prof_edit.setPlainText(
            "\n".join(
                f"{c.get('name', '')} | {c.get('phone', '')} | {c.get('relationship', '')}"
                for c in self._plan.get("professional_contacts", [])
            )
        )
        self._prof_edit.setMaximumHeight(100)
        layout.addWidget(self._prof_edit)

        # Warning signs
        layout.addWidget(_header_label("Warning Signs (one per line)"))
        self._warnings_edit = QTextEdit()
        self._warnings_edit.setPlainText("\n".join(self._plan.get("warning_signs", [])))
        self._warnings_edit.setMaximumHeight(100)
        layout.addWidget(self._warnings_edit)

        # Coping strategies
        layout.addWidget(_header_label("Coping Strategies (one per line)"))
        self._coping_edit = QTextEdit()
        self._coping_edit.setPlainText("\n".join(self._plan.get("coping_strategies", [])))
        self._coping_edit.setMaximumHeight(100)
        layout.addWidget(self._coping_edit)

        # Reasons for living
        layout.addWidget(_header_label("Reasons for Living (one per line)"))
        self._reasons_edit = QTextEdit()
        self._reasons_edit.setPlainText("\n".join(self._plan.get("reasons_for_living", [])))
        self._reasons_edit.setMaximumHeight(80)
        layout.addWidget(self._reasons_edit)

        # Safe places
        layout.addWidget(_header_label("Safe Places (one per line)"))
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
                contacts.append({
                    "name": parts[0],
                    "phone": parts[1] if len(parts) > 1 else "",
                    "relationship": parts[2] if len(parts) > 2 else "",
                })
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


# ---------------------------------------------------------------------------
# Widget
# ---------------------------------------------------------------------------

class CrisisWidget(QWidget):
    """Crisis plan quick-access tab -- minimal, calm, large fonts."""

    plan_updated = pyqtSignal()

    def __init__(self, main_window: Any, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.main_window = main_window
        self._plan: dict[str, Any] = dict(_DEFAULT_CRISIS_PLAN)

        # Try to get crisis plan manager
        self._crisis_manager = None
        with contextlib.suppress(Exception):
            self._crisis_manager = main_window.crisis_plan_manager

        self._data_dir = self._resolve_data_dir()
        self._load_plan()
        self._build_ui()
        self._apply_theme()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _resolve_data_dir(self) -> Path:
        try:
            return Path(self.main_window.data_dir)
        except (AttributeError, TypeError):
            p = Path.home() / ".mindful_organizer"
            p.mkdir(parents=True, exist_ok=True)
            return p

    def _plan_file(self) -> Path:
        self._data_dir.mkdir(parents=True, exist_ok=True)
        return self._data_dir / "crisis_plan.json"

    def _load_plan(self) -> None:
        if self._crisis_manager and hasattr(self._crisis_manager, "get_quick_access"):
            try:
                self._plan.update(self._quick_access_to_plan(self._crisis_manager.get_quick_access()))
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
            emergency_contacts.append({
                "name": contact.get("name", ""),
                "phone": contact.get("phone", "") or contact.get("instructions", ""),
                "relationship": "Crisis line",
            })
        professional_contacts = []
        for contact in quick.get("professionals", []):
            professional_contacts.append({
                "name": contact.get("name", ""),
                "phone": contact.get("phone", ""),
                "relationship": contact.get("role", "Professional"),
            })
        personal_contacts = []
        for contact in quick.get("call_someone", []):
            personal_contacts.append({
                "name": contact.get("name", ""),
                "phone": contact.get("phone", ""),
                "relationship": contact.get("relationship", ""),
            })
        return {
            "emergency_contacts": emergency_contacts or _DEFAULT_CRISIS_PLAN["emergency_contacts"],
            "personal_contacts": personal_contacts,
            "professional_contacts": professional_contacts,
            "warning_signs": list(_DEFAULT_CRISIS_PLAN["warning_signs"]),
            "coping_strategies": quick.get("try_first", []) or _DEFAULT_CRISIS_PLAN["coping_strategies"],
            "reasons_for_living": quick.get("reasons_for_living", []),
            "safe_places": quick.get("safe_places", []),
        }

    def _save_plan(self) -> None:
        if self._crisis_manager and hasattr(self._crisis_manager, "update_plan"):
            try:
                from wellness.crisis_plan import CrisisPlan
                self._crisis_manager.update_plan(CrisisPlan(
                    warning_signs=self._plan.get("warning_signs", []),
                    coping_strategies=self._plan.get("coping_strategies", []),
                    safe_places=self._plan.get("safe_places", []),
                    reasons_for_living=self._plan.get("reasons_for_living", []),
                ))
                return
            except Exception as exc:
                logger.debug(f"Crisis manager save error: {exc}")
        try:
            with open(self._plan_file(), "w") as fh:
                json.dump(self._plan, fh, indent=2)
        except (OSError, TypeError) as exc:
            logger.debug(f"Crisis plan save error: {exc}")

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        outer.addWidget(scroll)

        container = QWidget()
        container.setMaximumWidth(920)
        self._root = QVBoxLayout(container)
        self._root.setSpacing(16)
        self._root.setContentsMargins(32, 32, 32, 40)
        scroll.setWidget(container)

        # Header
        header = QLabel("Crisis resources")
        header.setObjectName("crisisHeader")
        header.setFont(QFont("Segoe UI", 26, QFont.Weight.DemiBold))
        self._root.addWidget(header)

        self._build_emergency_contacts()
        self._build_personal_contacts()
        self._build_professional_contacts()
        self._build_warning_signs()
        self._build_coping_strategies()
        self._build_reasons_for_living()
        self._build_safe_places()

        # Edit button
        edit_btn = _calm_button("Edit Crisis Plan")
        edit_btn.clicked.connect(self._edit_plan)
        self._root.addWidget(edit_btn)

        # Disclaimer
        disclaimer = QLabel(
            "This is a supplement to professional care, not a replacement. "
            "If you are in immediate danger, please call 988 or go to your nearest emergency room."
        )
        disclaimer.setFont(QFont("Segoe UI", 12))
        disclaimer.setWordWrap(True)
        disclaimer.setObjectName("crisisDisclaimer")
        self._root.addWidget(disclaimer)
        self._root.addStretch()

    def _apply_theme(self) -> None:
        theme = {}
        with contextlib.suppress(Exception):
            theme = self.main_window.theme_manager.get_colors()
        background = theme.get("background", "#18130F")
        card_bg = theme.get("card_bg", "#221C16")
        border = theme.get("border", "#3D3128")
        text = theme.get("text", "#F2E8D9")
        secondary = theme.get("secondary", "#BCAE9C")
        accent = theme.get("accent", "#A8845F")
        danger = theme.get("danger", "#C66860")
        self.setStyleSheet(
            f"""
            QWidget {{ background-color: {background}; color: {text}; }}
            QLabel {{ background-color: transparent; color: {text}; }}
            QScrollArea {{ border: none; background-color: {background}; }}
            QLabel#crisisHeader {{
                color: {text};
                font-size: 28px;
                font-weight: 600;
                padding-bottom: 8px;
            }}
            QLabel#crisisDisclaimer {{
                color: {secondary};
                font-size: 12px;
                padding: 8px 0;
            }}
            QFrame#crisisCard {{
                background-color: {card_bg};
                border: 1px solid {border};
                border-radius: 6px;
                padding: 16px;
            }}
            QPushButton[class="crisisContact"] {{
                background-color: transparent;
                color: {text};
                border: 1px solid {danger};
                border-radius: 6px;
                padding: 12px;
                font-size: 14px;
                font-weight: 600;
                text-align: left;
            }}
            QPushButton[class="crisisContact"]:hover {{
                background-color: {danger};
                color: {background};
            }}
            QPushButton[class="outline"] {{
                background-color: transparent;
                color: {accent};
                border: 1px solid {border};
                border-radius: 6px;
                padding: 10px 14px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton[class="outline"]:hover {{
                background-color: {card_bg};
                color: {text};
            }}
            """
        )

    def _build_emergency_contacts(self) -> None:
        card = _crisis_card()
        layout = QVBoxLayout(card)
        layout.addWidget(_header_label("Emergency Resources"))

        for contact in self._plan.get("emergency_contacts", []):
            btn = _contact_button(
                contact.get("name", ""), contact.get("phone", "")
            )
            layout.addWidget(btn)
        self._root.addWidget(card)

    def _build_personal_contacts(self) -> None:
        contacts = self._plan.get("personal_contacts", [])
        card = _crisis_card()
        layout = QVBoxLayout(card)
        layout.addWidget(_header_label("Personal Contacts"))

        if not contacts:
            layout.addWidget(
                _large_label("No personal contacts added yet. Use Edit to add.", 14)
            )
        else:
            for c in contacts:
                btn = _contact_button(
                    f"{c.get('name', '')} ({c.get('relationship', '')})",
                    c.get("phone", ""),
                )
                layout.addWidget(btn)
        self._root.addWidget(card)

    def _build_professional_contacts(self) -> None:
        contacts = self._plan.get("professional_contacts", [])
        card = _crisis_card()
        layout = QVBoxLayout(card)
        layout.addWidget(_header_label("Professional Contacts"))

        if not contacts:
            layout.addWidget(
                _large_label(
                    "No professional contacts added yet. Add your therapist or psychiatrist.",
                    14,
                )
            )
        else:
            for c in contacts:
                btn = _contact_button(
                    f"{c.get('name', '')} ({c.get('relationship', '')})",
                    c.get("phone", ""),
                )
                layout.addWidget(btn)
        self._root.addWidget(card)

    def _build_warning_signs(self) -> None:
        card = _crisis_card()
        layout = QVBoxLayout(card)
        layout.addWidget(_header_label("Warning Signs Checklist"))

        for sign in self._plan.get("warning_signs", []):
            label = _large_label(f"  {sign}", 14)
            layout.addWidget(label)
        self._root.addWidget(card)

    def _build_coping_strategies(self) -> None:
        card = _crisis_card()
        layout = QVBoxLayout(card)
        layout.addWidget(_header_label("Coping Strategies"))

        for strategy in self._plan.get("coping_strategies", []):
            label = _large_label(strategy, 15)
            layout.addWidget(label)
        self._root.addWidget(card)

    def _build_reasons_for_living(self) -> None:
        card = _crisis_card()
        layout = QVBoxLayout(card)
        layout.addWidget(_header_label("Reasons for Living"))

        for reason in self._plan.get("reasons_for_living", []):
            label = _large_label(f"  {reason}", 15)
            layout.addWidget(label)
        self._root.addWidget(card)

    def _build_safe_places(self) -> None:
        card = _crisis_card()
        layout = QVBoxLayout(card)
        layout.addWidget(_header_label("Safe Places"))

        for place in self._plan.get("safe_places", []):
            label = _large_label(f"  {place}", 14)
            layout.addWidget(label)
        self._root.addWidget(card)

    # ------------------------------------------------------------------
    # Edit
    # ------------------------------------------------------------------

    def _edit_plan(self) -> None:
        dialog = _CrisisPlanEditDialog(self._plan, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._plan = dialog.get_plan()
            self._save_plan()
            self.plan_updated.emit()
            self._rebuild()

    def _rebuild(self) -> None:
        """Clear and rebuild the entire widget."""
        layout = self.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                if item is None:
                    continue
                widget = item.widget()  # type: ignore[union-attr]
                if widget:
                    widget.deleteLater()
        self._build_ui()
        self._apply_theme()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def save_state(self) -> None:
        """Called by main window on close."""
        self._save_plan()
