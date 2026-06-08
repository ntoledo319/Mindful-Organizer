"""
Integration tests for the File Organization workflow.

Validates condition-aware strategy selection, file organization execution,
duplicate detection, and dry-run mode across the strategy engine, core
organizer, and UI configuration layers.
"""

from pathlib import Path

import pytest

from core.file_organizer import FileOrganizer as CoreFileOrganizer
from file_organization.organization_strategies import (
    FileOrganizer as StrategyOrganizer,
)
from file_organization.organization_strategies import (
    MentalHealthProfile,
    OrganizationStrategy,
)
from gui.widgets.file_organizer_widget import _CONDITION_CONFIGS


@pytest.fixture
def core_organizer(tmp_data_dir):
    """Core file organizer backed by a temp data directory."""
    return CoreFileOrganizer(tmp_data_dir)


@pytest.fixture
def mixed_source_dir(tmp_path):
    """Create a temp directory with assorted file types (docs, images, code, etc.)."""
    src = tmp_path / "mixed_source"
    src.mkdir()
    (src / "report.pdf").write_text("PDF report content")
    (src / "notes.txt").write_text("Plain text notes")
    (src / "photo.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 20)
    (src / "song.mp3").write_bytes(b"\x00" * 50)
    (src / "script.py").write_text("print('hello')")
    (src / "data.csv").write_text("a,b\n1,2\n")
    return src


# ---------------------------------------------------------------------------
# 1. Organization strategy selection
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestOrganizationStrategySelection:
    def test_adhd_profile_produces_action_based_emoji_folders(self, tmp_path):
        """ADHD maps to MINIMAL strategy; UI layer adds action-based emoji names."""
        profile = MentalHealthProfile()
        profile.has_adhd = True
        organizer = StrategyOrganizer(profile)

        assert organizer.strategy == OrganizationStrategy.MINIMAL

        structure = organizer.create_organization_structure(tmp_path)
        folders = set(structure.keys())
        assert "NOW - Current Projects" in folders
        assert "NEXT - Upcoming" in folders
        assert "DONE - Completed" in folders
        assert "REFERENCE - Important Info" in folders

        ui_folders = _CONDITION_CONFIGS["ADHD"]["folder_names"]
        assert any("🚀" in f for f in ui_folders)
        assert any("DO NOW" in f for f in ui_folders)
        assert any("✅" in f for f in ui_folders)

    def test_ocd_profile_produces_numbered_structure(self, tmp_path):
        """OCD falls through to FLEXIBLE strategy; UI layer provides numbered folders."""
        profile = MentalHealthProfile()
        profile.needs_structure = True
        organizer = StrategyOrganizer(profile)

        assert organizer.strategy == OrganizationStrategy.FLEXIBLE

        structure = organizer.create_organization_structure(tmp_path)
        folders = set(structure.keys())
        assert "Quick Access" in folders
        assert "Projects" in folders
        assert "Resources" in folders
        assert "Archives" in folders

        ui_folders = _CONDITION_CONFIGS["OCD"]["folder_names"]
        assert all(f[0].isdigit() for f in ui_folders)
        assert "01_Current" in ui_folders
        assert "02_Review" in ui_folders
        assert "03_Archive" in ui_folders
        assert "04_Scratch" in ui_folders

    def test_depression_profile_produces_energy_tiered_folders(self, tmp_path):
        """Depression maps to VISUAL strategy; UI layer uses energy-tiered names."""
        profile = MentalHealthProfile()
        profile.has_depression = True
        organizer = StrategyOrganizer(profile)

        assert organizer.strategy == OrganizationStrategy.VISUAL

        structure = organizer.create_organization_structure(tmp_path)
        folders = set(structure.keys())
        assert any("🎯" in f for f in folders)
        assert any("📚" in f for f in folders)

        ui_folders = _CONDITION_CONFIGS["Depression"]["folder_names"]
        assert "Gentle — Low Effort" in ui_folders
        assert "Steady — Medium Effort" in ui_folders
        assert "Strong — High Effort" in ui_folders
        assert "Rest — No Action Needed" in ui_folders

    def test_anxiety_profile_produces_detailed_hierarchy(self, tmp_path):
        """Anxiety maps to DETAILED strategy with numbered hierarchy."""
        profile = MentalHealthProfile()
        profile.has_anxiety = True
        organizer = StrategyOrganizer(profile)

        assert organizer.strategy == OrganizationStrategy.DETAILED

        structure = organizer.create_organization_structure(tmp_path)
        folders = list(structure.keys())
        expected = [
            "01_Current_Projects",
            "02_Resources",
            "03_Archives",
            "04_Templates",
            "05_Documentation",
            "06_Backups",
        ]
        assert folders == expected
        assert _CONDITION_CONFIGS["Anxiety"]["folder_names"] == expected


# ---------------------------------------------------------------------------
# 2. File organization execution
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestFileOrganizationExecution:
    def test_organize_mixed_files_into_categories(self, core_organizer, mixed_source_dir, tmp_path):
        """Mixed files should be categorized and moved into the correct folders."""
        target = tmp_path / "organized"
        summary = core_organizer.organize_files(mixed_source_dir, target)

        assert summary["moved"] == 6
        assert summary["errors"] == 0
        assert summary["skipped"] == 0

        # Files should have moved out of source
        assert not (mixed_source_dir / "report.pdf").exists()
        assert not (mixed_source_dir / "photo.png").exists()
        assert not (mixed_source_dir / "script.py").exists()

        # Files should be in category subdirectories with date prefix
        assert list((target / "documents").glob("*report.pdf"))
        assert list((target / "documents").glob("*notes.txt"))
        assert list((target / "images").glob("*photo.png"))
        assert list((target / "audio").glob("*song.mp3"))
        assert list((target / "code").glob("*script.py"))
        assert list((target / "spreadsheets").glob("*data.csv"))

    def test_organize_with_profile_folder_structure(
        self, core_organizer, mixed_source_dir, tmp_path
    ):
        """Creating a mental-health-aware structure should not interfere with file organization."""
        profile = MentalHealthProfile()
        profile.has_anxiety = True
        strategy_org = StrategyOrganizer(profile)
        strategy_org.create_organization_structure(tmp_path)

        # Core organizer should still function independently
        target = tmp_path / "organized"
        summary = core_organizer.organize_files(mixed_source_dir, target)
        assert summary["moved"] == 6
        assert summary["errors"] == 0
        assert target.exists()


# ---------------------------------------------------------------------------
# 3. Duplicate detection
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestDuplicateDetection:
    def test_find_duplicates_by_content(self, core_organizer, tmp_path):
        """Duplicate files with identical content should be detected."""
        dup_dir = tmp_path / "duplicates"
        dup_dir.mkdir()
        content = b"identical file content"
        (dup_dir / "original.txt").write_bytes(content)
        (dup_dir / "copy.txt").write_bytes(content)
        (dup_dir / "different.txt").write_bytes(b"something else")

        duplicates = core_organizer.find_duplicates(dup_dir)
        assert len(duplicates) == 1
        pair = {str(duplicates[0][0]), str(duplicates[0][1])}
        assert str(dup_dir / "original.txt") in pair
        assert str(dup_dir / "copy.txt") in pair

    def test_organize_with_duplicates_in_source(self, core_organizer, tmp_path):
        """Organizing a directory with duplicate files should complete without crashes."""
        src = tmp_path / "src_dupes"
        src.mkdir()
        content = b"same content"
        (src / "file_a.pdf").write_bytes(content)
        (src / "file_b.pdf").write_bytes(content)
        (src / "unique.pdf").write_bytes(b"unique content")

        # Verify duplicates are detected first
        dups = core_organizer.find_duplicates(src)
        assert len(dups) == 1

        # Organize should handle them gracefully (date prefix prevents collision)
        summary = core_organizer.organize_files(src, tmp_path / "out")
        assert summary["moved"] == 3
        assert summary["errors"] == 0

        # All files should exist in the target
        target_docs = list((tmp_path / "out" / "documents").glob("*.pdf"))
        assert len(target_docs) == 3


# ---------------------------------------------------------------------------
# 4. Dry-run mode
# ---------------------------------------------------------------------------


@pytest.mark.integration
class TestDryRunMode:
    def test_dry_run_does_not_move_files(self, core_organizer, mixed_source_dir, tmp_path):
        """Dry-run should preview changes without moving any files."""
        target = tmp_path / "dry_target"
        summary = core_organizer.dry_run(mixed_source_dir, target)

        assert summary["moved"] == 6
        assert not target.exists()

        # Source files untouched
        assert (mixed_source_dir / "report.pdf").exists()
        assert (mixed_source_dir / "photo.png").exists()
        assert (mixed_source_dir / "script.py").exists()

        for action in summary["actions"]:
            assert action["action"] == "preview"

    def test_dry_run_generates_correct_plan(self, core_organizer, mixed_source_dir, tmp_path):
        """Dry-run report should contain all expected files and categories."""
        summary = core_organizer.dry_run(mixed_source_dir, tmp_path / "plan_target")

        actions = summary["actions"]
        categories = {a["category"] for a in actions}
        assert "documents" in categories
        assert "images" in categories
        assert "code" in categories
        assert "audio" in categories
        assert "spreadsheets" in categories

        sources = {Path(a["source"]).name for a in actions}
        assert "report.pdf" in sources
        assert "photo.png" in sources
        assert "script.py" in sources
        assert "song.mp3" in sources
        assert "data.csv" in sources

        # No history should be recorded for dry-run
        assert len(core_organizer.history) == 0
