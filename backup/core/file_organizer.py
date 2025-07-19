"""
File organization system with mental health focus.
"""
from pathlib import Path
from typing import Dict, List, Optional, Set
import shutil
import json
from datetime import datetime
from .profile_manager import Profile, Condition

class FileOrganizer:
    def __init__(self, root_dir: Path, profile: Profile):
        self.root_dir = root_dir
        self.profile = profile
        self.backup_dir = root_dir / "backups"
        self.metadata_file = root_dir / "file_metadata.json"
        self.metadata: Dict[str, dict] = self._load_metadata()

    def _load_metadata(self) -> Dict[str, dict]:
        """Load file metadata from JSON."""
        if not self.metadata_file.exists():
            return {}
        
        with open(self.metadata_file, 'r') as f:
            return json.load(f)

    def _save_metadata(self):
        """Save file metadata to JSON."""
        self.metadata_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)

    def setup_folder_structure(self):
        """Create folder structure based on profile."""
        for category, subfolders in self.profile.folder_structure.items():
            category_dir = self.root_dir / category
            category_dir.mkdir(parents=True, exist_ok=True)
            
            for subfolder in subfolders:
                subfolder_path = category_dir / subfolder
                subfolder_path.mkdir(parents=True, exist_ok=True)

    def categorize_file(self, file_path: Path) -> Optional[Path]:
        """Categorize a file based on content and filename."""
        if not file_path.exists():
            return None

        # Get file metadata
        file_info = {
            "name": file_path.name,
            "extension": file_path.suffix.lower(),
            "size": file_path.stat().st_size,
            "created": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
        }

        # Determine category based on filename and conditions
        category = self._determine_category(file_path.name, file_info["extension"])
        if not category:
            return None

        # Create target path
        target_dir = self.root_dir / category
        target_path = target_dir / file_path.name

        # Move file
        if target_path != file_path:
            shutil.move(str(file_path), str(target_path))

        # Update metadata
        self.metadata[str(target_path)] = file_info
        self._save_metadata()

        return target_path

    def _determine_category(self, filename: str, extension: str) -> Optional[str]:
        """Determine appropriate category for a file."""
        filename_lower = filename.lower()
        
        # Check condition-specific categories
        if any(condition in self.profile.conditions for condition in [Condition.ADHD, Condition.BIPOLAR]):
            if any(kw in filename_lower for kw in ["mood", "sleep", "energy", "trigger"]):
                return "Tracking"
            if any(kw in filename_lower for kw in ["task", "project", "schedule"]):
                return "Task Management"

        if Condition.OCD in self.profile.conditions:
            if any(kw in filename_lower for kw in ["exposure", "erp", "ritual"]):
                return "ERP Work"

        if Condition.ANXIETY in self.profile.conditions:
            if any(kw in filename_lower for kw in ["anxiety", "panic", "worry"]):
                return "Anxiety Management"

        # Check general categories
        if extension in [".pdf", ".doc", ".docx"]:
            if any(kw in filename_lower for kw in ["report", "record", "plan"]):
                return "Documents"
            if any(kw in filename_lower for kw in ["resource", "guide", "info"]):
                return "Resources"

        if extension in [".txt", ".md", ".rtf"]:
            if any(kw in filename_lower for kw in ["journal", "diary", "note"]):
                return "Personal"
            if any(kw in filename_lower for kw in ["log", "track", "record"]):
                return "Tracking"

        return None

    def create_backup(self):
        """Create a backup of all files."""
        if not self.profile.organization_preferences.get("backup_enabled", True):
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"backup_{timestamp}"
        backup_path.mkdir(parents=True, exist_ok=True)

        # Copy files and folders
        for category in self.profile.folder_structure:
            src_dir = self.root_dir / category
            if src_dir.exists():
                dst_dir = backup_path / category
                shutil.copytree(str(src_dir), str(dst_dir))

        # Save metadata
        with open(backup_path / "metadata.json", 'w') as f:
            json.dump(self.metadata, f, indent=2)

    def search_files(self, query: str, categories: Optional[Set[str]] = None) -> List[Path]:
        """Search for files across categories."""
        results = []
        search_dirs = []

        if categories:
            search_dirs = [self.root_dir / cat for cat in categories]
        else:
            search_dirs = [self.root_dir / cat for cat in self.profile.folder_structure]

        query_lower = query.lower()
        for directory in search_dirs:
            if directory.exists():
                for file_path in directory.rglob("*"):
                    if file_path.is_file() and query_lower in file_path.name.lower():
                        results.append(file_path)

        return results

    def get_category_stats(self) -> Dict[str, dict]:
        """Get statistics for each category."""
        stats = {}
        
        for category in self.profile.folder_structure:
            category_dir = self.root_dir / category
            if not category_dir.exists():
                continue
                
            file_count = 0
            total_size = 0
            last_modified = None
            
            for file_path in category_dir.rglob("*"):
                if file_path.is_file():
                    file_count += 1
                    total_size += file_path.stat().st_size
                    mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if not last_modified or mod_time > last_modified:
                        last_modified = mod_time
            
            stats[category] = {
                "file_count": file_count,
                "total_size": total_size,
                "last_modified": last_modified.isoformat() if last_modified else None
            }
        
        return stats
