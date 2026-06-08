"""Voice journal widget — shows a warm "Coming Soon" message when recording
is unavailable, with a gentle path back to text journaling.
"""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from gui.components.hearth_surfaces import HearthButton
from gui.components.state_controls import PALETTE, sans_font, serif_font
from wellness.voice_journal import VoiceJournal


class VoiceJournalWidget(QWidget):
    """A warm placeholder for voice journaling.

    When the ``sounddevice`` backend is unavailable, this widget shows
    a human message and a button that emits ``navigate_to_text_journal``
    so the main window can switch to the text journal tab.
    """

    navigate_to_text_journal = pyqtSignal()

    def __init__(
        self, parent: QWidget | None = None, voice_journal: VoiceJournal | None = None
    ) -> None:
        super().__init__(parent)
        self.voice_journal = voice_journal or VoiceJournal()
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

        if not self.voice_journal.is_available:
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
        else:
            self._record_btn = HearthButton("Record", role="primary")
            self._record_btn.clicked.connect(self._toggle_recording)
            btn_row = QHBoxLayout()
            btn_row.addStretch()
            btn_row.addWidget(self._record_btn)
            btn_row.addStretch()
            layout.addLayout(btn_row)

            self._status_label = QLabel("Ready to record")
            self._status_label.setFont(sans_font(12))
            self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._status_label.setStyleSheet(
                f"color: {PALETTE['text_muted']}; background: transparent;"
            )
            layout.addWidget(self._status_label)

        layout.addStretch()

    def _toggle_recording(self) -> None:
        if self.voice_journal.get_status()["recording"]:
            self.voice_journal.stop_recording()
            self._record_btn.setText("Record")
            self._status_label.setText("Recording saved")
        else:
            self.voice_journal.start_recording()
            self._record_btn.setText("Stop")
            self._status_label.setText("Recording...")
