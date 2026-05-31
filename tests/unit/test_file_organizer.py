"""
Tests for FileOrganizer (src/core/file_organizer.py).

Covers file categorization, organize_files (real + dry-run), undo,
custom rules, duplicate detection, file statistics, archiving,
folder structure setup, search, backup, and history tracking.
"""

import json
import os
import time
from pathlib import Path

import pytest

from core.file_organizer import FileOrganizer


@pytest.fixture
def fo(tmp_data_dir):
    return FileOrganizer(tmp_data_dir)


@pytest.fixture
def source_with_files(tmp_path):
    """Create a source directory with assorted test files."""
    src_dir = tmp_path / "source"
    src_dir.mkdir()

    (src_dir / "report.pdf").write_text("pdf content")
    (src_dir / "notes.txt").write_text("text content")
    (src_dir / "photo.jpg").write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 20)
    (src_dir / "song.mp3").write_bytes(b"\x00" * 50)
    (src_dir / "script.py").write_text("print('hello')")
    (src_dir / "data.csv").write_text("a,b\n1,2\n")
    (src_dir / "unknown.xyz").write_text("mystery file")

    return src_dir


# ---------------------------------------------------------------------------
# File categorization
# ---------------------------------------------------------------------------

class TestFileCategorization:

    def test_categorize_pdf(self, fo, tmp_path):
        f = tmp_path / "doc.pdf"
        f.touch()
        assert fo._get_file_category(f) == "documents"

    def test_categorize_image(self, fo, tmp_path):
        f = tmp_path / "pic.png"
        f.touch()
        assert fo._get_file_category(f) == "images"

    def test_categorize_code(self, fo, tmp_path):
        f = tmp_path / "main.py"
        f.touch()
        assert fo._get_file_category(f) == "code"

    def test_categorize_audio(self, fo, tmp_path):
        f = tmp_path / "track.mp3"
        f.touch()
        assert fo._get_file_category(f) == "audio"

    def test_categorize_video(self, fo, tmp_path):
        f = tmp_path / "clip.mp4"
        f.touch()
        assert fo._get_file_category(f) == "video"

    def test_categorize_spreadsheet(self, fo, tmp_path):
        f = tmp_path / "data.csv"
        f.touch()
        assert fo._get_file_category(f) == "spreadsheets"

    def test_categorize_archive(self, fo, tmp_path):
        f = tmp_path / "bundle.zip"
        f.touch()
        assert fo._get_file_category(f) == "archives"

    def test_unknown_extension_returns_none(self, fo, tmp_path):
        f = tmp_path / "file.xyz"
        f.touch()
        assert fo._get_file_category(f) is None

    def test_case_insensitive_extension(self, fo, tmp_path):
        f = tmp_path / "image.PNG"
        f.touch()
        assert fo._get_file_category(f) == "images"


# ---------------------------------------------------------------------------
# Organize files (real move)
# ---------------------------------------------------------------------------

class TestOrganizeFiles:

    def test_organize_creates_target_dirs(self, fo, source_with_files, tmp_path):
        target = tmp_path / "organized"
        summary = fo.organize_files(source_with_files, target)

        assert summary["moved"] >= 5  # pdf, txt, jpg, mp3, py, csv
        assert summary["errors"] == 0
        assert target.exists()

    def test_organize_moves_files(self, fo, source_with_files, tmp_path):
        target = tmp_path / "organized"
        fo.organize_files(source_with_files, target)

        # Original files should be gone
        assert not (source_with_files / "report.pdf").exists()
        # Category dir should contain the file
        docs = list((target / "documents").glob("*report*"))
        assert len(docs) == 1

    def test_organize_skips_unknown(self, fo, source_with_files, tmp_path):
        target = tmp_path / "organized"
        summary = fo.organize_files(source_with_files, target)

        assert summary["skipped"] >= 1  # unknown.xyz

    def test_organize_skips_hidden_files(self, fo, tmp_path):
        src = tmp_path / "hidden_src"
        src.mkdir()
        (src / ".hidden").write_text("hidden")
        (src / "visible.txt").write_text("visible")

        summary = fo.organize_files(src, tmp_path / "out")
        assert summary["moved"] == 1  # only visible.txt

    def test_organize_default_target(self, fo, tmp_path):
        src = tmp_path / "default_src"
        src.mkdir()
        (src / "file.txt").write_text("content")

        summary = fo.organize_files(src)
        assert summary["moved"] == 1
        assert (src / "organized").exists()

    def test_organize_records_history(self, fo, source_with_files, tmp_path):
        target = tmp_path / "organized"
        fo.organize_files(source_with_files, target)

        assert len(fo.history) >= 5
        assert all(h["action"] == "move" for h in fo.history)


# ---------------------------------------------------------------------------
# Dry-run
# ---------------------------------------------------------------------------

class TestDryRun:

    def test_dry_run_does_not_move(self, fo, source_with_files, tmp_path):
        target = tmp_path / "dry_target"
        summary = fo.dry_run(source_with_files, target)

        assert summary["moved"] >= 5
        # Files should still exist in source
        assert (source_with_files / "report.pdf").exists()
        # Target should not exist
        assert not target.exists()

    def test_dry_run_actions_are_preview(self, fo, source_with_files, tmp_path):
        target = tmp_path / "dry_target"
        summary = fo.dry_run(source_with_files, target)

        for action in summary["actions"]:
            assert action["action"] == "preview"

    def test_dry_run_does_not_record_history(self, fo, source_with_files, tmp_path):
        initial_history_len = len(fo.history)
        fo.dry_run(source_with_files, tmp_path / "dry_out")
        assert len(fo.history) == initial_history_len


# ---------------------------------------------------------------------------
# Undo
# ---------------------------------------------------------------------------

class TestUndo:

    def test_undo_restores_files(self, fo, source_with_files, tmp_path):
        target = tmp_path / "undo_target"
        fo.organize_files(source_with_files, target)

        result = fo.undo_last_organization()
        assert result["undone"] >= 5
        assert result["errors"] == 0

        # Files should be back in source
        assert (source_with_files / "report.pdf").exists()
        assert (source_with_files / "notes.txt").exists()

    def test_undo_nothing_to_undo(self, fo):
        result = fo.undo_last_organization()
        assert result["undone"] == 0
        assert "Nothing to undo" in result["message"]

    def test_undo_only_undoes_last_batch(self, fo, tmp_path):
        # First batch
        src1 = tmp_path / "batch1"
        src1.mkdir()
        (src1 / "a.txt").write_text("a")
        fo.organize_files(src1, tmp_path / "out1")

        # Second batch
        src2 = tmp_path / "batch2"
        src2.mkdir()
        (src2 / "b.txt").write_text("b")
        fo.organize_files(src2, tmp_path / "out2")

        # Undo should only restore second batch
        result = fo.undo_last_organization()
        assert result["undone"] == 1
        assert (src2 / "b.txt").exists()


# ---------------------------------------------------------------------------
# Custom rules
# ---------------------------------------------------------------------------

class TestCustomRules:

    def test_add_rule(self, fo):
        fo.add_rule("extension", ".log", "logs")
        assert len(fo.custom_rules) == 1
        assert fo.custom_rules[0]["category"] == "logs"

    def test_add_rule_persists(self, tmp_data_dir):
        fo1 = FileOrganizer(tmp_data_dir)
        fo1.add_rule("extension", ".log", "logs")
        del fo1

        fo2 = FileOrganizer(tmp_data_dir)
        assert len(fo2.custom_rules) == 1

    def test_remove_rule(self, fo):
        fo.add_rule("extension", ".log", "logs")
        fo.add_rule("name_contains", "report", "reports")
        fo.remove_rule(0)
        assert len(fo.custom_rules) == 1
        assert fo.custom_rules[0]["category"] == "reports"

    def test_remove_rule_invalid_index(self, fo):
        fo.add_rule("extension", ".log", "logs")
        fo.remove_rule(99)  # should not crash
        assert len(fo.custom_rules) == 1

    def test_custom_rule_overrides_default(self, fo, tmp_path):
        # .txt normally goes to documents; custom rule sends to "notes"
        fo.add_rule("extension", ".txt", "notes")
        f = tmp_path / "file.txt"
        f.touch()
        assert fo._get_file_category(f) == "notes"

    def test_name_contains_rule(self, fo, tmp_path):
        fo.add_rule("name_contains", "invoice", "accounting")
        f = tmp_path / "invoice_2026.pdf"
        f.touch()
        assert fo._get_file_category(f) == "accounting"

    def test_name_starts_rule(self, fo, tmp_path):
        fo.add_rule("name_starts", "backup_", "backups")
        f = tmp_path / "backup_db.sql"
        f.touch()
        assert fo._get_file_category(f) == "backups"

    def test_get_rules(self, fo):
        fo.add_rule("extension", ".log", "logs")
        rules = fo.get_rules()
        assert len(rules) == 1
        # Returned list should be a copy
        rules.clear()
        assert len(fo.custom_rules) == 1


# ---------------------------------------------------------------------------
# Duplicate detection
# ---------------------------------------------------------------------------

class TestDuplicateDetection:

    def test_find_duplicates(self, fo, tmp_path):
        d = tmp_path / "dupes"
        d.mkdir()
        content = b"identical content"
        (d / "orig.txt").write_bytes(content)
        (d / "copy.txt").write_bytes(content)
        (d / "different.txt").write_bytes(b"something else")

        dupes = fo.find_duplicates(d)
        assert len(dupes) == 1
        paths = {str(dupes[0][0]), str(dupes[0][1])}
        assert str(d / "orig.txt") in paths
        assert str(d / "copy.txt") in paths

    def test_no_duplicates(self, fo, tmp_path):
        d = tmp_path / "no_dupes"
        d.mkdir()
        (d / "a.txt").write_bytes(b"aaa")
        (d / "b.txt").write_bytes(b"bbb")

        dupes = fo.find_duplicates(d)
        assert len(dupes) == 0

    def test_empty_directory(self, fo, tmp_path):
        d = tmp_path / "empty"
        d.mkdir()
        dupes = fo.find_duplicates(d)
        assert len(dupes) == 0

    def test_duplicate_in_subdirectory(self, fo, tmp_path):
        d = tmp_path / "nested"
        d.mkdir()
        sub = d / "sub"
        sub.mkdir()
        content = b"same"
        (d / "file.txt").write_bytes(content)
        (sub / "file.txt").write_bytes(content)

        dupes = fo.find_duplicates(d)
        assert len(dupes) == 1


# ---------------------------------------------------------------------------
# File statistics
# ---------------------------------------------------------------------------

class TestFileStatistics:

    def test_get_statistics(self, fo, source_with_files):
        stats = fo.get_file_statistics(source_with_files)

        assert stats["total_files"] >= 7
        assert stats["total_size_bytes"] > 0
        assert "documents" in stats["by_category"]
        assert ".pdf" in stats["by_extension"]
        assert len(stats["largest_files"]) >= 1

    def test_empty_directory_stats(self, fo, tmp_path):
        d = tmp_path / "empty_stats"
        d.mkdir()
        stats = fo.get_file_statistics(d)

        assert stats["total_files"] == 0
        assert stats["total_size_bytes"] == 0

    def test_largest_files_ordered(self, fo, tmp_path):
        d = tmp_path / "sized"
        d.mkdir()
        (d / "small.txt").write_bytes(b"x" * 10)
        (d / "big.txt").write_bytes(b"x" * 10000)
        (d / "medium.txt").write_bytes(b"x" * 1000)

        stats = fo.get_file_statistics(d)
        sizes = [f["size_mb"] for f in stats["largest_files"]]
        assert sizes == sorted(sizes, reverse=True)


# ---------------------------------------------------------------------------
# Archive old files
# ---------------------------------------------------------------------------

class TestArchiveOldFiles:

    def test_archive_old_files(self, fo, tmp_path):
        d = tmp_path / "archive_src"
        d.mkdir()
        old_file = d / "old.txt"
        old_file.write_text("old")
        # Set modification time to 100 days ago
        old_time = time.time() - (100 * 86400)
        os.utime(old_file, (old_time, old_time))

        new_file = d / "new.txt"
        new_file.write_text("new")

        result = fo.archive_old_files(d, days=90)
        assert result["archived"] == 1
        assert not old_file.exists()
        assert new_file.exists()

    def test_archive_dry_run(self, fo, tmp_path):
        d = tmp_path / "archive_dry"
        d.mkdir()
        old_file = d / "old.txt"
        old_file.write_text("old")
        old_time = time.time() - (100 * 86400)
        os.utime(old_file, (old_time, old_time))

        result = fo.archive_old_files(d, days=90, dry_run=True)
        assert result["archived"] == 1
        # File should still exist
        assert old_file.exists()

    def test_archive_nothing_old(self, fo, tmp_path):
        d = tmp_path / "archive_new"
        d.mkdir()
        (d / "recent.txt").write_text("recent")

        result = fo.archive_old_files(d, days=90)
        assert result["archived"] == 0


# ---------------------------------------------------------------------------
# Folder structure setup
# ---------------------------------------------------------------------------

class TestFolderStructure:

    def test_setup_folder_structure(self, fo):
        fo.setup_folder_structure()
        files_dir = fo.data_dir / "files"
        assert files_dir.exists()

        for category in fo.DEFAULT_CATEGORIES:
            assert (files_dir / category).exists()


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

class TestSearch:

    def test_search_files(self, fo):
        # Set up organized directory with files
        files_dir = fo.data_dir / "files" / "documents"
        files_dir.mkdir(parents=True)
        (files_dir / "report_2026.pdf").write_text("content")
        (files_dir / "notes.txt").write_text("content")

        results = fo.search_files("report")
        assert len(results) == 1
        assert "report_2026.pdf" in results[0]

    def test_search_no_results(self, fo):
        fo.setup_folder_structure()
        results = fo.search_files("nonexistent_file_xyz")
        assert len(results) == 0

    def test_search_case_insensitive(self, fo):
        files_dir = fo.data_dir / "files" / "documents"
        files_dir.mkdir(parents=True)
        (files_dir / "Report.PDF").write_text("content")

        results = fo.search_files("report")
        assert len(results) == 1


# ---------------------------------------------------------------------------
# Configuration backup
# ---------------------------------------------------------------------------

class TestBackup:

    def test_create_backup(self, fo):
        fo.add_rule("extension", ".log", "logs")
        fo.create_backup()

        backup_dir = fo.data_dir / "backups"
        assert backup_dir.exists()
        backups = list(backup_dir.glob("file_org_backup_*.json"))
        assert len(backups) == 1

        data = json.loads(backups[0].read_text())
        assert "config" in data
        assert "rules" in data
        assert len(data["rules"]) == 1


# ---------------------------------------------------------------------------
# Organization stats
# ---------------------------------------------------------------------------

class TestOrganizationStats:

    def test_stats_from_history(self, fo, source_with_files, tmp_path):
        fo.organize_files(source_with_files, tmp_path / "org_out")
        stats = fo.get_organization_stats()

        assert stats["total_files_moved"] >= 5
        assert len(stats["files_by_category"]) >= 1
        assert len(stats["recent_errors"]) == 0

    def test_stats_empty_history(self, fo):
        stats = fo.get_organization_stats()
        assert stats["total_files_moved"] == 0

    def test_stats_track_errors(self, fo, tmp_data_dir):
        # Record an error manually
        fo._record_action(Path("/nonexistent"), None, "error", "test error")
        stats = fo.get_organization_stats()
        assert len(stats["recent_errors"]) == 1


# ---------------------------------------------------------------------------
# Persistence (config & history)
# ---------------------------------------------------------------------------

class TestPersistence:

    def test_config_saved_and_loaded(self, tmp_data_dir):
        fo1 = FileOrganizer(tmp_data_dir)
        fo1.config["archive_days"] = 30
        fo1.save_config()
        del fo1

        fo2 = FileOrganizer(tmp_data_dir)
        assert fo2.config["archive_days"] == 30

    def test_history_saved_and_loaded(self, tmp_data_dir):
        fo1 = FileOrganizer(tmp_data_dir)
        fo1._record_action(Path("/src"), Path("/dst"), "move")
        del fo1

        fo2 = FileOrganizer(tmp_data_dir)
        assert len(fo2.history) == 1
        assert fo2.history[0]["action"] == "move"

    def test_history_capped_at_1000(self, tmp_data_dir):
        fo = FileOrganizer(tmp_data_dir)
        for i in range(1050):
            fo.history.append({"action": "move", "source": f"/s{i}", "target": f"/t{i}", "timestamp": ""})
        fo.save_history()
        del fo

        fo2 = FileOrganizer(tmp_data_dir)
        assert len(fo2.history) <= 1000

    def test_corrupt_config_handled(self, tmp_data_dir):
        (tmp_data_dir / "file_organizer_config.json").write_text("{bad json")
        fo = FileOrganizer(tmp_data_dir)
        # Should fall back to defaults
        assert "categories" in fo.config

    def test_corrupt_history_handled(self, tmp_data_dir):
        (tmp_data_dir / "file_history.json").write_text("{bad json")
        fo = FileOrganizer(tmp_data_dir)
        assert fo.history == []
