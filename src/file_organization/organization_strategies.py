"""
File organization strategies adapted for different mental health needs.
"""

import json
import shutil
from datetime import datetime
from enum import Enum, auto
from pathlib import Path


class MentalHealthProfile:
    """Represents different mental health considerations for file organization."""

    def __init__(self) -> None:
        self.has_adhd: bool = False
        self.has_anxiety: bool = False
        self.has_depression: bool = False
        self.needs_structure: bool = False
        self.prefers_visual: bool = False
        self.needs_reminders: bool = False


class OrganizationStrategy(Enum):
    """Available organization strategies."""

    MINIMAL = auto()  # Simple, uncluttered organization
    VISUAL = auto()  # Heavy use of icons and colors
    DETAILED = auto()  # Detailed categorization and metadata
    FLEXIBLE = auto()  # Adaptable hybrid approach


class FileOrganizer:
    """Manages file organization based on mental health needs."""

    def __init__(self, profile: MentalHealthProfile):
        self.profile = profile
        self.strategy = self._determine_strategy()
        self.base_path = Path.home()

    def _determine_strategy(self) -> OrganizationStrategy:
        """Determine the best organization strategy based on profile."""
        if self.profile.has_adhd and self.profile.has_anxiety:
            return (
                OrganizationStrategy.VISUAL
                if self.profile.prefers_visual
                else OrganizationStrategy.FLEXIBLE
            )
        elif self.profile.has_adhd:
            return OrganizationStrategy.MINIMAL
        elif self.profile.has_anxiety:
            return OrganizationStrategy.DETAILED
        elif self.profile.has_depression:
            return OrganizationStrategy.VISUAL
        else:
            return OrganizationStrategy.FLEXIBLE

    def create_organization_structure(self, root_dir: Path) -> dict[str, Path]:
        """Create an organization structure based on the selected strategy."""
        structure = {}

        if self.strategy == OrganizationStrategy.MINIMAL:
            # ADHD-friendly: Simple, clear categories with action-based names
            categories = [
                "NOW - Current Projects",
                "NEXT - Upcoming",
                "DONE - Completed",
                "REFERENCE - Important Info",
            ]

        elif self.strategy == OrganizationStrategy.VISUAL:
            # Visual-heavy organization with emoji markers
            categories = [
                "🎯 Active Projects",
                "📅 Scheduled Tasks",
                "📚 Resources",
                "✨ Inspiration",
                "✅ Completed",
            ]

        elif self.strategy == OrganizationStrategy.DETAILED:
            # Anxiety-friendly: Detailed categorization with clear hierarchy
            categories = [
                "01_Current_Projects",
                "02_Resources",
                "03_Archives",
                "04_Templates",
                "05_Documentation",
                "06_Backups",
            ]

        else:  # FLEXIBLE
            # Adaptable structure with both simple and detailed options
            categories = ["Quick Access", "Projects", "Resources", "Archives"]

        # Create directories
        for category in categories:
            dir_path = root_dir / category
            dir_path.mkdir(parents=True, exist_ok=True)
            structure[category] = dir_path

            # Create metadata file for the directory
            self._create_metadata_file(dir_path, category)

        return structure

    def _create_metadata_file(self, directory: Path, category: str):
        """Create a metadata file with directory information and usage guidelines."""
        metadata = {
            "category": category,
            "created_date": datetime.now().isoformat(),
            "purpose": self._get_category_purpose(category),
            "guidelines": self._get_organization_guidelines(),
            "quick_tips": self._get_quick_tips(),
        }

        with open(directory / ".folder_info.json", "w") as f:
            json.dump(metadata, f, indent=2)

    def _get_category_purpose(self, category: str) -> str:
        """Get the purpose description for a category."""
        purposes = {
            "NOW - Current Projects": "Active projects that need immediate attention",
            "NEXT - Upcoming": "Projects or tasks planned for the near future",
            "DONE - Completed": "Finished projects for reference",
            "REFERENCE - Important Info": "Important information you need to access regularly",
            "🎯 Active Projects": "Projects you're currently working on",
            "📅 Scheduled Tasks": "Tasks with specific deadlines",
            "📚 Resources": "Reference materials and resources",
            "✨ Inspiration": "Inspiring content and ideas",
            "✅ Completed": "Completed projects and tasks",
        }
        return purposes.get(category, "General purpose storage")

    def _get_organization_guidelines(self) -> list[str]:
        """Get organization guidelines based on the current strategy."""
        guidelines = []

        if self.profile.has_adhd:
            guidelines.extend(
                [
                    "Keep file names short and action-oriented",
                    "Use NOW, NEXT, DONE prefixes for clear prioritization",
                    "Limit folder depth to reduce overwhelm",
                    "Set up automatic file sorting when possible",
                ]
            )

        if self.profile.has_anxiety:
            guidelines.extend(
                [
                    "Use detailed, consistent naming conventions",
                    "Include dates in file names (YYYY-MM-DD)",
                    "Maintain regular backups",
                    "Create detailed README files for each project",
                ]
            )

        if self.profile.has_depression:
            guidelines.extend(
                [
                    "Use positive and encouraging folder names",
                    "Include visual elements when possible",
                    "Keep important files easily accessible",
                    "Set up automatic cleanup routines",
                ]
            )

        if not any([self.profile.has_adhd, self.profile.has_anxiety, self.profile.has_depression]):
            guidelines.extend(
                [
                    "Use clear, descriptive names",
                    "Organize by project or category",
                    "Archive completed projects",
                    "Regular maintenance and cleanup",
                ]
            )

        return guidelines

    def _get_quick_tips(self) -> list[str]:
        """Get quick tips based on the user's profile."""
        tips = []

        if self.profile.has_adhd:
            tips.extend(
                [
                    "💡 Use color coding for different project types",
                    "⏰ Set reminders for file cleanup",
                    "📱 Use quick access shortcuts",
                    "🎯 Focus on one folder at a time",
                ]
            )

        if self.profile.has_anxiety:
            tips.extend(
                [
                    "✅ Regular backups are automated",
                    "📋 Use checklists for organization",
                    "🔍 Search function helps find anything",
                    "📝 Keep notes with context",
                ]
            )

        if self.profile.has_depression:
            tips.extend(
                [
                    "🌟 Celebrate completed projects",
                    "🎨 Use inspiring visuals",
                    "👥 Share and collaborate",
                    "🌱 Start small, grow gradually",
                ]
            )

        return tips

    def suggest_file_location(self, file_path: Path) -> Path:
        """Suggest the best location for a file based on its type and content."""
        # Determine the best category based on file analysis
        if self.strategy == OrganizationStrategy.MINIMAL:
            if self._is_active_project_file(file_path):
                return self.base_path / "NOW - Current Projects" / file_path.name
            elif self._is_reference_file(file_path):
                return self.base_path / "REFERENCE - Important Info" / file_path.name
            else:
                return self.base_path / "NEXT - Upcoming" / file_path.name

        elif self.strategy == OrganizationStrategy.VISUAL:
            if self._is_active_project_file(file_path):
                return self.base_path / "🎯 Active Projects" / file_path.name
            elif self._is_scheduled_task(file_path):
                return self.base_path / "📅 Scheduled Tasks" / file_path.name
            else:
                return self.base_path / "📚 Resources" / file_path.name

        elif self.strategy == OrganizationStrategy.DETAILED:
            category = self._determine_detailed_category(file_path)
            return self.base_path / category / self._generate_detailed_filename(file_path)

        else:  # FLEXIBLE
            if self._is_active_project_file(file_path):
                return self.base_path / "Quick Access" / file_path.name
            else:
                return self.base_path / "Projects" / file_path.name

    def _is_active_project_file(self, file_path: Path) -> bool:
        """Check if a file belongs to an active project.

        Currently uses modification time within the last 30 days as a heuristic.
        """
        try:
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            return (datetime.now() - mtime).days <= 30
        except OSError:
            return False

    def _is_reference_file(self, file_path: Path) -> bool:
        """Check if a file is a reference document."""
        reference_types = {".pdf", ".doc", ".docx", ".txt", ".md"}
        return file_path.suffix.lower() in reference_types

    def _is_scheduled_task(self, file_path: Path) -> bool:
        """Check if a file is related to a scheduled task.

        Placeholder: returns False until task-calendar integration is implemented.
        """
        return False

    def _determine_detailed_category(self, file_path: Path) -> str:
        """Determine the detailed category for a file.

        Uses a simple extension-based heuristic. Clients requiring richer
        categorization should subclass and override.
        """
        suffix = file_path.suffix.lower()
        if suffix in {".pdf", ".doc", ".docx", ".txt", ".md"}:
            return "01_Documents"
        if suffix in {".jpg", ".jpeg", ".png", ".gif", ".svg"}:
            return "02_Images"
        if suffix in {".mp4", ".mov", ".avi", ".mkv"}:
            return "03_Videos"
        if suffix in {".mp3", ".wav", ".flac", ".aac"}:
            return "04_Audio"
        if suffix in {".py", ".js", ".ts", ".java", ".cpp", ".c", ".go", ".rs"}:
            return "05_Code"
        return "06_Misc"

    def _generate_detailed_filename(self, file_path: Path) -> str:
        """Generate a detailed filename with metadata."""
        date_prefix = datetime.now().strftime("%Y-%m-%d")
        return f"{date_prefix}_{file_path.name}"

    def organize_directory(self, directory: Path):
        """Organize an entire directory according to the current strategy.

        Raises:
            FileExistsError: If a collision is detected and would overwrite.
        """
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                suggested_location = self.suggest_file_location(file_path)
                suggested_location.parent.mkdir(parents=True, exist_ok=True)
                if suggested_location.exists():
                    raise FileExistsError(
                        f"Collision: {suggested_location} already exists. "
                        "Resolve manually or enable overwrite mode."
                    )
                shutil.move(str(file_path), str(suggested_location))

    def create_quick_access_links(self, directory: Path):
        """Create quick access links for frequently used files and folders.

        Placeholder: not yet implemented.
        """
        raise NotImplementedError("Quick access links are not yet implemented.")
