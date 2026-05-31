"""Reusable progress bar component."""

from PyQt6.QtWidgets import QProgressBar


class ThemedProgressBar(QProgressBar):
    """Progress bar with theme-aware colors."""

    def __init__(
        self,
        theme: dict[str, str] | None = None,
        *,
        color_key: str = "accent",
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._theme = theme or {}
        self._color_key = color_key
        self.setTextVisible(True)
        self._refresh_style()

    def set_theme(self, theme: dict[str, str]) -> None:
        self._theme = theme
        self._refresh_style()

    def _refresh_style(self) -> None:
        secondary = self._theme.get("secondary", "#cccccc")
        bg = self._theme.get("background", "#f0f0f0")
        chunk = self._theme.get(self._color_key, "#4a90d9")
        self.setStyleSheet(
            f"QProgressBar {{ border: 1px solid {secondary}; "
            f"border-radius: 6px; text-align: center; height: 20px; "
            f"background-color: {bg}; }}"
            f"QProgressBar::chunk {{ background-color: {chunk}; "
            f"border-radius: 6px; }}"
        )
