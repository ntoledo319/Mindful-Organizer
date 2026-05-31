"""Reusable card frame component."""

from PyQt6.QtWidgets import QFrame


class CardFrame(QFrame):
    """A styled card container with theme-aware colors.

    Replaces the copy-pasted ``_card_frame()`` helper that existed in
    dashboard, task_manager, mood_tracker, breathing, and journaling widgets.
    """

    def __init__(
        self,
        theme: dict[str, str] | None = None,
        *,
        padding: int = 16,
        radius: int = 6,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._theme = theme or {}
        self._padding = padding
        self._radius = radius
        self.setObjectName("cardFrame")
        self._refresh_style()
        self.setFrameShape(QFrame.Shape.StyledPanel)

    def set_theme(self, theme: dict[str, str]) -> None:
        """Update the card's theme and refresh its appearance."""
        self._theme = theme
        self._refresh_style()

    def _refresh_style(self) -> None:
        bg = self._theme.get("card_bg", "#ffffff")
        border = self._theme.get("border", "#d8d8d8")
        self.setStyleSheet(
            f"QFrame#cardFrame {{ background-color: {bg}; "
            f"border: 1px solid {border}; "
            f"border-radius: {self._radius}px; "
            f"padding: {self._padding}px; }}"
        )
