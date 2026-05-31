"""Reusable container components."""

from PyQt6.QtWidgets import QFrame, QScrollArea, QVBoxLayout, QWidget


class ScrollContainer(QScrollArea):
    """Standard scroll area with theme-aware background.

    Eliminates the repeated scroll-area setup in every widget module.
    """

    def __init__(
        self,
        theme: dict[str, str] | None = None,
        *,
        margins: tuple = (24, 24, 24, 24),
        spacing: int = 16,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._theme = theme or {}
        self._margins = margins
        self._spacing = spacing

        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self._refresh_style()

        # Inner container with standard layout
        self._container = QWidget()
        self._layout = QVBoxLayout(self._container)
        self._layout.setSpacing(spacing)
        self._layout.setContentsMargins(*margins)
        self.setWidget(self._container)

    @property
    def layout(self) -> QVBoxLayout:  # type: ignore[override]
        """Access the inner container's layout."""
        return self._layout

    def set_theme(self, theme: dict[str, str]) -> None:
        self._theme = theme
        self._refresh_style()

    def _refresh_style(self) -> None:
        bg = self._theme.get("background", "#f5f5f5")
        self.setStyleSheet(f"QScrollArea {{ background-color: {bg}; }}")
