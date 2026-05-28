"""Reusable button components."""


from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QPushButton


class _ThemedButton(QPushButton):
    """Base class for theme-aware buttons."""

    def __init__(
        self,
        text: str,
        theme: dict[str, str] | None = None,
        *,
        bg_key: str = "accent",
        hover_key: str = "secondary",
        text_color: str = "#ffffff",
        parent=None,
    ) -> None:
        super().__init__(text, parent)
        self._theme = theme or {}
        self._bg_key = bg_key
        self._hover_key = hover_key
        self._text_color = text_color
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(36)
        self.setFont(QFont(self.font().family(), 13, QFont.Weight.Medium))
        self._refresh_style()

    def set_theme(self, theme: dict[str, str]) -> None:
        self._theme = theme
        self._refresh_style()

    def _refresh_style(self) -> None:
        bg = self._theme.get(self._bg_key, "#4a90d9")
        hover = self._theme.get(self._hover_key, "#357abd")
        accent_text = self._theme.get("background", "#18130F")
        self.setStyleSheet(
            f"QPushButton {{ background-color: {bg}; "
            f"color: {accent_text if self._bg_key == 'accent' else self._text_color}; border: none; "
            f"border-radius: 5px; padding: 8px 14px; "
            f"font-weight: 500; font-size: 13px; }}"
            f"QPushButton:hover {{ background-color: {hover}; }}"
        )


class AccentButton(_ThemedButton):
    """Primary action button."""

    def __init__(
        self,
        text: str,
        theme: dict[str, str] | None = None,
        parent=None,
    ) -> None:
        super().__init__(text, theme, bg_key="accent", hover_key="accent_hover", parent=parent)


class DangerButton(_ThemedButton):
    """Destructive action button."""

    def __init__(
        self,
        text: str,
        theme: dict[str, str] | None = None,
        parent=None,
    ) -> None:
        super().__init__(text, theme, bg_key="danger", hover_key="hover", text_color="#ffffff", parent=parent)


class GhostButton(_ThemedButton):
    """Low-emphasis button with transparent background."""

    def __init__(
        self,
        text: str,
        theme: dict[str, str] | None = None,
        parent=None,
    ) -> None:
        super().__init__(
            text,
            theme,
            bg_key="card_bg",
            hover_key="hover",
            text_color=(theme or {}).get("text", "#333333"),
            parent=parent,
        )
        self.setStyleSheet(
            f"QPushButton {{ background-color: transparent; "
            f"color: {(theme or {}).get('text', '#333333')}; "
            f"border: 1px solid {(theme or {}).get('border', '#cccccc')}; "
            f"border-radius: 5px; padding: 8px 14px; "
            f"font-weight: 500; font-size: 13px; }}"
            f"QPushButton:hover {{ background-color: {(theme or {}).get('hover', '#e8f4fd')}; }}"
        )
