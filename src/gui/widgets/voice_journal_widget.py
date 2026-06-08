"""Voice journal widget — shows a warm "Coming Soon" message when recording
is unavailable, with a gentle path back to text journaling.
"""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from gui.components.hearth_surfaces import HearthButton
from gui.components.state_controls import PALETTE, sans_font, serif_font


class VoiceJournalWidget(QWidget):
    """A warm placeholder for voice journaling.

    When the ``sounddevice`` backend is unavailable, this widget shows
    a human message and a button that emits ``navigate_to_text_journal``
    so the main window can switch to the text journal tab.
    """

    navigate_to_text_journal = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        layout.addStretch()

        title = QLabel("Voice Journal")
        title.setFont(serif_font(24))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: {PALETTE['text']}; background: transparent;")
        layout.addWidget(title)

        msg = QLabel("Voice journaling is coming soon. For now, try text journaling.")
        msg.setFont(sans_font(14))
        msg.setWordWrap(True)
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg.setStyleSheet(f"color: {PALETTE['text_muted']}; background: transparent;")
        layout.addWidget(msg)

        btn = HearthButton("Go to Text Journal", role="primary")
        btn.clicked.connect(self.navigate_to_text_journal.emit)
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        layout.addStretch()
