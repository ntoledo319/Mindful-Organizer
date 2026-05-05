"""Reusable typography components."""


from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel


class SectionTitle(QLabel):
    """Bold section heading with theme-aware color."""

    def __init__(
        self,
        text: str,
        theme: dict[str, str] | None = None,
        *,
        font_size: int = 13,
        parent=None,
    ) -> None:
        super().__init__(text, parent)
        self._theme = theme or {}
        self._font_size = font_size
        self.setFont(QFont(self.font().family(), font_size, QFont.Weight.Bold))
        self._refresh_style()

    def set_theme(self, theme: dict[str, str]) -> None:
        self._theme = theme
        self._refresh_style()

    def _refresh_style(self) -> None:
        color = self._theme.get("text", "#333333")
        self.setStyleSheet(f"color: {color}; padding-bottom: 4px;")


class BodyLabel(QLabel):
    """Word-wrapped body text with theme-aware color."""

    def __init__(
        self,
        text: str = "",
        theme: dict[str, str] | None = None,
        parent=None,
    ) -> None:
        super().__init__(text, parent)
        self._theme = theme or {}
        self.setWordWrap(True)
        self._refresh_style()

    def set_theme(self, theme: dict[str, str]) -> None:
        self._theme = theme
        self._refresh_style()

    def _refresh_style(self) -> None:
        color = self._theme.get("text", "#555555")
        self.setStyleSheet(f"color: {color};")


class Caption(QLabel):
    """Small helper or secondary text."""

    def __init__(
        self,
        text: str = "",
        theme: dict[str, str] | None = None,
        *,
        font_size: int = 11,
        parent=None,
    ) -> None:
        super().__init__(text, parent)
        self._theme = theme or {}
        self.setFont(QFont(self.font().family(), font_size))
        self._refresh_style()

    def set_theme(self, theme: dict[str, str]) -> None:
        self._theme = theme
        self._refresh_style()

    def _refresh_style(self) -> None:
        color = self._theme.get("secondary", "#888888")
        self.setStyleSheet(f"color: {color};")
