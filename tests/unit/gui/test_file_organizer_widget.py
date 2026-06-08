"""pytest-qt tests for the FileOrganizerWidget."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from PyQt6.QtWidgets import QAbstractButton

from gui.widgets.file_organizer_widget import FileOrganizerWidget


def _find_button(widget, text: str):
    for btn in widget.findChildren(QAbstractButton):
        if btn.text() == text:
            return btn
    return None


def test_can_be_instantiated(qtbot):
    widget = FileOrganizerWidget(theme={}, file_organizer=None, profile_manager=None)
    qtbot.addWidget(widget)
    assert widget is not None


def test_organize_button_exists(qtbot):
    widget = FileOrganizerWidget(theme={}, file_organizer=None, profile_manager=None)
    qtbot.addWidget(widget)

    btn = _find_button(widget, "Select Folder")
    assert btn is not None
    assert not btn.isHidden()


def test_path_selection_mock_qfiledialog(qtbot, tmp_path):
    organizer = MagicMock()
    organizer.organize_files.return_value = {
        "moved": 3,
        "skipped": 0,
        "errors": 0,
        "actions": [],
    }

    widget = FileOrganizerWidget(theme={}, file_organizer=organizer, profile_manager=None)
    qtbot.addWidget(widget)

    target = tmp_path / "organize_me"
    target.mkdir()

    with patch(
        "gui.widgets.file_organizer_widget.QFileDialog.getExistingDirectory",
        return_value=str(target),
    ):
        btn = _find_button(widget, "Select Folder")
        assert btn is not None
        btn.click()

    assert organizer.organize_files.called
    args, kwargs = organizer.organize_files.call_args
    assert str(args[0]) == str(target)
    assert kwargs.get("dry_run") is False
