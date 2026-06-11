"""Tests for src/file_organization/organization_strategies.py."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from file_organization.organization_strategies import (
    FileOrganizer,
    MentalHealthProfile,
    OrganizationStrategy,
)


class TestMentalHealthProfile:
    def test_default_profile(self):
        p = MentalHealthProfile()
        assert p.has_adhd is False
        assert p.has_anxiety is False
        assert p.has_depression is False
        assert p.needs_structure is False
        assert p.prefers_visual is False
        assert p.needs_reminders is False


class TestDetermineStrategy:
    def test_adhd_and_anxiety_prefers_visual(self):
        p = MentalHealthProfile()
        p.has_adhd = True
        p.has_anxiety = True
        p.prefers_visual = True
        o = FileOrganizer(p)
        assert o.strategy == OrganizationStrategy.VISUAL

    def test_adhd_and_anxiety_flexible(self):
        p = MentalHealthProfile()
        p.has_adhd = True
        p.has_anxiety = True
        p.prefers_visual = False
        o = FileOrganizer(p)
        assert o.strategy == OrganizationStrategy.FLEXIBLE

    def test_adhd_only(self):
        p = MentalHealthProfile()
        p.has_adhd = True
        o = FileOrganizer(p)
        assert o.strategy == OrganizationStrategy.MINIMAL

    def test_anxiety_only(self):
        p = MentalHealthProfile()
        p.has_anxiety = True
        o = FileOrganizer(p)
        assert o.strategy == OrganizationStrategy.DETAILED

    def test_depression_only(self):
        p = MentalHealthProfile()
        p.has_depression = True
        o = FileOrganizer(p)
        assert o.strategy == OrganizationStrategy.VISUAL

    def test_default_flexible(self):
        p = MentalHealthProfile()
        o = FileOrganizer(p)
        assert o.strategy == OrganizationStrategy.FLEXIBLE


class TestCreateOrganizationStructure:
    def test_minimal_structure(self, tmp_path):
        p = MentalHealthProfile()
        p.has_adhd = True
        o = FileOrganizer(p)
        structure = o.create_organization_structure(tmp_path)
        assert "NOW - Current Projects" in structure
        assert structure["NOW - Current Projects"].exists()

    def test_visual_structure(self, tmp_path):
        p = MentalHealthProfile()
        p.has_depression = True
        o = FileOrganizer(p)
        structure = o.create_organization_structure(tmp_path)
        assert "🎯 Active Projects" in structure
        assert structure["🎯 Active Projects"].exists()

    def test_detailed_structure(self, tmp_path):
        p = MentalHealthProfile()
        p.has_anxiety = True
        o = FileOrganizer(p)
        structure = o.create_organization_structure(tmp_path)
        assert "01_Current_Projects" in structure
        assert structure["01_Current_Projects"].exists()

    def test_flexible_structure(self, tmp_path):
        p = MentalHealthProfile()
        o = FileOrganizer(p)
        structure = o.create_organization_structure(tmp_path)
        assert "Quick Access" in structure
        assert structure["Quick Access"].exists()

    def test_metadata_created(self, tmp_path):
        p = MentalHealthProfile()
        o = FileOrganizer(p)
        o.create_organization_structure(tmp_path)
        meta = tmp_path / "Quick Access" / ".folder_info.json"
        assert meta.exists()
        data = __import__("json").loads(meta.read_text())
        assert "category" in data
        assert "guidelines" in data


class TestSuggestFileLocation:
    def test_minimal_active_file(self, tmp_path):
        p = MentalHealthProfile()
        p.has_adhd = True
        o = FileOrganizer(p)
        f = tmp_path / "active.txt"
        f.write_text("test")
        loc = o.suggest_file_location(f)
        assert "NOW - Current Projects" in str(loc)

    def test_minimal_reference_file(self, tmp_path):
        p = MentalHealthProfile()
        p.has_adhd = True
        o = FileOrganizer(p)
        f = tmp_path / "doc.pdf"
        f.write_text("test")
        loc = o.suggest_file_location(f)
        assert "REFERENCE" in str(loc)

    def test_visual_active_file(self, tmp_path):
        p = MentalHealthProfile()
        p.has_depression = True
        o = FileOrganizer(p)
        f = tmp_path / "active.txt"
        f.write_text("test")
        loc = o.suggest_file_location(f)
        assert "🎯 Active Projects" in str(loc)

    def test_detailed_category(self, tmp_path):
        p = MentalHealthProfile()
        p.has_anxiety = True
        o = FileOrganizer(p)
        f = tmp_path / "photo.png"
        f.write_text("test")
        loc = o.suggest_file_location(f)
        assert "02_Images" in str(loc)
        assert loc.name.startswith("20")  # date prefix

    def test_detailed_code_category(self, tmp_path):
        p = MentalHealthProfile()
        p.has_anxiety = True
        o = FileOrganizer(p)
        f = tmp_path / "script.py"
        f.write_text("test")
        loc = o.suggest_file_location(f)
        assert "05_Code" in str(loc)

    def test_flexible_default(self, tmp_path):
        p = MentalHealthProfile()
        o = FileOrganizer(p)
        f = tmp_path / "random.bin"
        f.write_text("test")
        loc = o.suggest_file_location(f)
        assert "Projects" in str(loc)

    def test_oserror_handling(self, tmp_path):
        p = MentalHealthProfile()
        o = FileOrganizer(p)
        f = tmp_path / "nonexistent.txt"
        assert o._is_active_project_file(f) is False


class TestGuidelines:
    def test_adhd_guidelines(self):
        p = MentalHealthProfile()
        p.has_adhd = True
        o = FileOrganizer(p)
        g = o._get_organization_guidelines()
        assert any("NOW" in line for line in g)

    def test_anxiety_guidelines(self):
        p = MentalHealthProfile()
        p.has_anxiety = True
        o = FileOrganizer(p)
        g = o._get_organization_guidelines()
        assert any("backups" in line for line in g)

    def test_depression_guidelines(self):
        p = MentalHealthProfile()
        p.has_depression = True
        o = FileOrganizer(p)
        g = o._get_organization_guidelines()
        assert any("positive" in line for line in g)

    def test_default_guidelines(self):
        p = MentalHealthProfile()
        o = FileOrganizer(p)
        g = o._get_organization_guidelines()
        assert any("descriptive" in line for line in g)


class TestQuickTips:
    def test_adhd_tips(self):
        p = MentalHealthProfile()
        p.has_adhd = True
        o = FileOrganizer(p)
        tips = o._get_quick_tips()
        assert len(tips) > 0

    def test_anxiety_tips(self):
        p = MentalHealthProfile()
        p.has_anxiety = True
        o = FileOrganizer(p)
        tips = o._get_quick_tips()
        assert len(tips) > 0

    def test_depression_tips(self):
        p = MentalHealthProfile()
        p.has_depression = True
        o = FileOrganizer(p)
        tips = o._get_quick_tips()
        assert len(tips) > 0

    def test_no_tips_default(self):
        p = MentalHealthProfile()
        o = FileOrganizer(p)
        tips = o._get_quick_tips()
        assert tips == []


class TestOrganizeDirectory:
    def test_organize_directory(self, tmp_path):
        p = MentalHealthProfile()
        p.has_adhd = True
        o = FileOrganizer(p)
        source = tmp_path / "source"
        source.mkdir()
        (source / "file.txt").write_text("hello")
        # Patch base_path so files land inside tmp_path
        o.base_path = tmp_path
        o.organize_directory(source)
        assert not (source / "file.txt").exists()

    def test_organize_directory_collision(self, tmp_path):
        p = MentalHealthProfile()
        p.has_adhd = True
        o = FileOrganizer(p)
        source = tmp_path / "source"
        source.mkdir()
        (source / "file.txt").write_text("hello")
        o.base_path = tmp_path
        o.organize_directory(source)
        # Second run should raise FileExistsError
        (source / "file.txt").write_text("hello again")
        with pytest.raises(FileExistsError):
            o.organize_directory(source)


class TestQuickAccessLinks:
    def test_not_implemented(self, tmp_path):
        p = MentalHealthProfile()
        o = FileOrganizer(p)
        with pytest.raises(NotImplementedError):
            o.create_quick_access_links(tmp_path)
