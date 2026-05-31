"""
Upsell dialog for feature gating.

Displays a tasteful, non-intrusive prompt when a free user tries to access
a premium feature. Includes trial CTA, pricing, and feature highlights.
Designed to feel helpful, not exploitative — this is a mental health app.
"""

from __future__ import annotations

from typing import Any

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)


class UpsellDialog(QDialog):
    """Dialog shown when a gated feature is accessed without the right tier."""

    def __init__(
        self,
        feature_name: str,
        required_tier: str,
        parent: Any = None,
        theme: dict[str, str] | None = None,
    ) -> None:
        super().__init__(parent)
        self._theme = theme or {}
        self.setWindowTitle("Upgrade")
        self.setMinimumWidth(420)
        self.setMaximumWidth(520)
        self.setStyleSheet(self._dialog_stylesheet())

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Header
        header = QLabel("Upgrade for deeper tracking")
        header.setFont(QFont(QFont().defaultFamily(), 16, QFont.Weight.DemiBold))
        header.setStyleSheet(f"color: {self._theme.get('text', '#2C3E50')}; padding-bottom: 4px;")
        layout.addWidget(header)

        # Context message
        context = QLabel(
            f"<b>{feature_name}</b> is available with {required_tier}.\n\n"
            "Hearth can use your local history to prepare reports, surface patterns, "
            "and make reviews with a clinician more concrete."
        )
        context.setWordWrap(True)
        context.setStyleSheet(f"color: {self._theme.get('text', '#333')}; font-size: 13px;")
        layout.addWidget(context)

        # Feature highlights
        highlights = self._tier_highlights(required_tier)
        if highlights:
            card = QFrame()
            card.setStyleSheet(
                f"background-color: {self._theme.get('card_bg', '#F8F9FA')}; "
                f"border: 1px solid {self._theme.get('border', '#D4C7B2')}; "
                "border-radius: 6px; padding: 8px;"
            )
            card_layout = QVBoxLayout(card)
            card_layout.setSpacing(6)
            for h in highlights:
                lbl = QLabel(f"- {h}")
                lbl.setStyleSheet(
                    f"color: {self._theme.get('secondary', '#6B5E50')}; font-size: 12px;"
                )
                card_layout.addWidget(lbl)
            layout.addWidget(card)

        # Pricing
        price_lbl = QLabel(self._pricing_text(required_tier))
        price_lbl.setWordWrap(True)
        price_lbl.setStyleSheet(
            f"color: {self._theme.get('secondary', '#666')}; font-size: 12px; padding-top: 8px;"
        )
        layout.addWidget(price_lbl)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self._trial_btn = QPushButton("Start 14-day trial")
        self._trial_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._trial_btn.setStyleSheet(
            f"QPushButton {{ background-color: {self._theme.get('accent', '#A8845F')}; color: {self._theme.get('background', '#18130F')}; "
            f"border-radius: 5px; padding: 10px 18px; font-weight: 500; font-size: 13px; }}"
            f"QPushButton:hover {{ background-color: {self._theme.get('accent_hover', '#B89472')}; }}"
        )
        self._trial_btn.clicked.connect(self._on_trial)
        btn_row.addWidget(self._trial_btn)

        maybe_btn = QPushButton("Not now")
        maybe_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        maybe_btn.setStyleSheet(
            "QPushButton { background: transparent; color: #888; border: none; padding: 10px; }"
            "QPushButton:hover { color: #555; }"
        )
        maybe_btn.clicked.connect(self.reject)
        btn_row.addWidget(maybe_btn)

        layout.addLayout(btn_row)

        # Trust footer
        footer = QLabel(
            "No credit card required for trial. Cancel anytime. All data stays on your device."
        )
        footer.setWordWrap(True)
        footer.setStyleSheet("color: #999; font-size: 11px; padding-top: 8px;")
        layout.addWidget(footer)

        self._result: str | None = None

    def _dialog_stylesheet(self) -> str:
        return f"QDialog {{ background-color: {self._theme.get('background', '#ffffff')}; }}"

    def _tier_highlights(self, tier: str) -> list[str]:
        if tier.lower() == "premium":
            return [
                "Personal wellness reports for your therapist",
                "Medication adherence heatmaps & values radar",
                "Clinician sharing & priority support",
                "Everything in Pro",
            ]
        return [
            "Unlimited history & trend analytics",
            "Smart notifications based on your patterns",
            "Weekly insights reports",
            "Calendar sync & data export",
        ]

    def _pricing_text(self, tier: str) -> str:
        if tier.lower() == "premium":
            return "<b>Premium</b> — $9.99/month or $79.99/year (save 33%)"
        return "<b>Pro</b> — $4.99/month or $39.99/year (save 33%)"

    def _on_trial(self) -> None:
        self._result = "trial"
        self.accept()

    @property
    def result(self) -> str | None:
        return self._result

    @classmethod
    def prompt(
        cls,
        feature_name: str,
        required_tier: str,
        parent: Any = None,
        theme: dict[str, str] | None = None,
    ) -> str | None:
        """Show the dialog and return the user's choice ('trial' or None)."""
        dlg = cls(feature_name, required_tier, parent, theme)
        dlg.exec()
        return dlg.result
