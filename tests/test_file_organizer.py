import pytest
from pathlib import Path
import shutil
import json
from core.file_organizer import FileOrganizer

@pytest.fixture
def temp_workspace(tmp_path):
    """Create a temporary workspace with some dummy files."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    source_dir = tmp_path / "source"
    source_dir.mkdir()

    # Create some files
    (source_dir / "test.txt").write_text("content")
    (source_dir / "image.jpg").write_text("image data")
    (source_dir / "unknown.xyz").write_text("unknown data")

    return data_dir, source_dir

def test_file_organizer_plan(temp_workspace):
    data_dir, source_dir = temp_workspace
    organizer = FileOrganizer(data_dir)

    # Dry run
    plan = organizer.organize_files(source_dir, dry_run=True)

    assert plan['source_dir'] == str(source_dir)
    assert len(plan['moves']) == 2 # txt and jpg
    assert len(plan['skipped']) == 1 # xyz

    # Check move details
    txt_move = next(m for m in plan['moves'] if m['source'].endswith('test.txt'))
    assert txt_move['category'] == 'documents'
    assert 'documents' in txt_move['target']

def test_file_organizer_execute_and_undo(temp_workspace):
    data_dir, source_dir = temp_workspace
    organizer = FileOrganizer(data_dir)

    # 1. Execute
    plan = organizer.organize_files(source_dir, dry_run=True)
    result = organizer.execute_plan(plan)

    assert result['files_moved'] == 2
    assert not (source_dir / "test.txt").exists()
    assert (source_dir / "organized" / "documents" / "test.txt").exists()

    # 2. Undo
    undo_result = organizer.undo_last_transaction()
    assert undo_result['restored'] == 2
    assert (source_dir / "test.txt").exists()
    assert not (source_dir / "organized" / "documents" / "test.txt").exists()

def test_backup(temp_workspace):
    data_dir, source_dir = temp_workspace
    organizer = FileOrganizer(data_dir)

    backup_path = organizer.create_backup(source_dir)
    assert backup_path.exists()
    assert (backup_path / "test.txt").exists()
