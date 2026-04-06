"""
Enhanced file organization and management system with dry-run,
undo, duplicate detection, watch folders, and custom rules.
"""
from pathlib import Path
import shutil
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import json


class FileOrganizer:
    """Manages file organization with mental health-aware features."""

    # Expanded file categories (30+ extensions)
    DEFAULT_CATEGORIES = {
        "documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".pages", ".tex", ".md", ".epub"],
        "spreadsheets": [".xls", ".xlsx", ".csv", ".ods", ".numbers"],
        "presentations": [".ppt", ".pptx", ".key", ".odp"],
        "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".tiff", ".ico", ".heic", ".raw"],
        "audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a", ".aiff"],
        "video": [".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".webm", ".m4v"],
        "code": [".py", ".js", ".ts", ".html", ".css", ".java", ".cpp", ".c", ".h", ".go", ".rs", ".rb", ".php", ".swift"],
        "archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
        "design": [".psd", ".ai", ".sketch", ".fig", ".xd", ".indd"],
        "data": [".json", ".xml", ".yaml", ".yml", ".toml", ".sql", ".db", ".sqlite"],
        "fonts": [".ttf", ".otf", ".woff", ".woff2"],
        "executables": [".exe", ".msi", ".dmg", ".app", ".deb", ".rpm"],
    }

    def __init__(self, data_dir: Path, profile=None):
        self.data_dir = data_dir
        self.profile = profile
        self.config_file = data_dir / "file_organizer_config.json"
        self.history_file = data_dir / "file_history.json"
        self.rules_file = data_dir / "organization_rules.json"
        self.config: Dict = {}
        self.history: List[Dict] = []
        self.custom_rules: List[Dict] = []
        self._undo_stack: List[List[Dict]] = []
        self.load_config()
        self.load_history()
        self.load_rules()

    def load_config(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    self.config = json.load(f)
            except (json.JSONDecodeError, Exception):
                self.config = {}

        if not self.config:
            self.config = {
                "categories": self.DEFAULT_CATEGORIES,
                "naming_convention": "date_category_name",
                "organize_by": ["category", "date"],
                "backup_enabled": True,
                "archive_days": 90,
            }
            self.save_config()

    def save_config(self):
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=4)

    def load_history(self):
        if self.history_file.exists():
            try:
                with open(self.history_file, "r") as f:
                    self.history = json.load(f)
            except (json.JSONDecodeError, Exception):
                self.history = []

    def save_history(self):
        with open(self.history_file, "w") as f:
            json.dump(self.history[-1000:], f, indent=2)

    def load_rules(self):
        if self.rules_file.exists():
            try:
                with open(self.rules_file, "r") as f:
                    self.custom_rules = json.load(f)
            except (json.JSONDecodeError, Exception):
                self.custom_rules = []

    def save_rules(self):
        with open(self.rules_file, "w") as f:
            json.dump(self.custom_rules, f, indent=2)

    # === Core Organization ===

    def organize_files(self, source_dir: Path, target_dir: Optional[Path] = None, dry_run: bool = False) -> Dict:
        """Organize files with optional dry-run preview."""
        if target_dir is None:
            target_dir = source_dir / "organized"

        summary = {"moved": 0, "skipped": 0, "errors": 0, "actions": []}

        for file_path in source_dir.glob("*"):
            if file_path.is_file() and not file_path.name.startswith("."):
                try:
                    category = self._get_file_category(file_path)
                    if category:
                        new_path = self._get_organized_path(file_path, target_dir, category)
                        action = {
                            "source": str(file_path),
                            "destination": str(new_path),
                            "category": category,
                            "action": "move",
                        }

                        if dry_run:
                            action["action"] = "preview"
                            summary["actions"].append(action)
                            summary["moved"] += 1
                        else:
                            new_path.parent.mkdir(parents=True, exist_ok=True)
                            shutil.move(str(file_path), str(new_path))
                            summary["moved"] += 1
                            summary["actions"].append(action)
                            self._record_action(file_path, new_path, "move")
                    else:
                        summary["skipped"] += 1
                except Exception as e:
                    summary["errors"] += 1
                    self._record_action(file_path, None, "error", str(e))

        if not dry_run and summary["actions"]:
            self._undo_stack.append(summary["actions"])

        return summary

    def dry_run(self, source_dir: Path, target_dir: Optional[Path] = None) -> Dict:
        """Preview organization without moving files."""
        return self.organize_files(source_dir, target_dir, dry_run=True)

    def undo_last_organization(self) -> Dict:
        """Undo the last organization batch."""
        if not self._undo_stack:
            return {"undone": 0, "errors": 0, "message": "Nothing to undo."}

        actions = self._undo_stack.pop()
        result = {"undone": 0, "errors": 0}

        for action in reversed(actions):
            if action["action"] == "move":
                try:
                    src = Path(action["destination"])
                    dst = Path(action["source"])
                    if src.exists():
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(src), str(dst))
                        result["undone"] += 1
                        self._record_action(src, dst, "undo")
                except Exception:
                    result["errors"] += 1

        result["message"] = f"Undone {result['undone']} file moves."
        return result

    # === File Categorization ===

    def _get_file_category(self, file_path: Path) -> Optional[str]:
        """Determine category, checking custom rules first."""
        # Check custom rules first
        for rule in self.custom_rules:
            if self._matches_rule(file_path, rule):
                return rule.get("category", None)

        # Fall back to extension-based
        ext = file_path.suffix.lower()
        categories = self.config.get("categories", self.DEFAULT_CATEGORIES)
        for category, extensions in categories.items():
            if ext in extensions:
                return category
        return None

    def _matches_rule(self, file_path: Path, rule: Dict) -> bool:
        """Check if a file matches a custom rule."""
        rule_type = rule.get("type", "extension")
        pattern = rule.get("pattern", "")

        if rule_type == "extension" and file_path.suffix.lower() == pattern.lower():
            return True
        elif rule_type == "name_contains" and pattern.lower() in file_path.name.lower():
            return True
        elif rule_type == "name_starts" and file_path.name.lower().startswith(pattern.lower()):
            return True
        return False

    def _get_organized_path(self, file_path: Path, target_dir: Path, category: str) -> Path:
        """Generate organized path for a file."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        return target_dir / category / f"{date_str}_{file_path.name}"

    # === Custom Rules ===

    def add_rule(self, rule_type: str, pattern: str, category: str, destination: Optional[str] = None):
        """Add a custom organization rule."""
        self.custom_rules.append({
            "type": rule_type,
            "pattern": pattern,
            "category": category,
            "destination": destination,
            "created": datetime.now().isoformat(),
        })
        self.save_rules()

    def remove_rule(self, index: int):
        """Remove a custom rule by index."""
        if 0 <= index < len(self.custom_rules):
            self.custom_rules.pop(index)
            self.save_rules()

    def get_rules(self) -> List[Dict]:
        return self.custom_rules.copy()

    # === Duplicate Detection ===

    def find_duplicates(self, directory: Path) -> List[Tuple[Path, Path]]:
        """Find duplicate files by size and hash."""
        size_map: Dict[int, List[Path]] = {}
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                size = file_path.stat().st_size
                size_map.setdefault(size, []).append(file_path)

        duplicates = []
        for size, files in size_map.items():
            if len(files) < 2:
                continue
            # Hash files with same size
            hash_map: Dict[str, List[Path]] = {}
            for fp in files:
                try:
                    file_hash = self._hash_file(fp)
                    hash_map.setdefault(file_hash, []).append(fp)
                except (OSError, PermissionError):
                    continue

            for h, fps in hash_map.items():
                if len(fps) >= 2:
                    for i in range(1, len(fps)):
                        duplicates.append((fps[0], fps[i]))

        return duplicates

    @staticmethod
    def _hash_file(file_path: Path, chunk_size: int = 8192) -> str:
        """Compute SHA256 hash of a file."""
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                hasher.update(chunk)
        return hasher.hexdigest()

    # === File Statistics ===

    def get_file_statistics(self, directory: Path) -> Dict:
        """Get comprehensive file statistics for a directory."""
        stats = {
            "total_files": 0,
            "total_size_bytes": 0,
            "by_category": {},
            "by_extension": {},
            "largest_files": [],
            "oldest_files": [],
            "newest_files": [],
        }

        files_info = []
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                try:
                    fstat = file_path.stat()
                    category = self._get_file_category(file_path) or "uncategorized"
                    ext = file_path.suffix.lower() or "(none)"

                    stats["total_files"] += 1
                    stats["total_size_bytes"] += fstat.st_size
                    stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
                    stats["by_extension"][ext] = stats["by_extension"].get(ext, 0) + 1

                    files_info.append({
                        "path": str(file_path),
                        "size": fstat.st_size,
                        "modified": fstat.st_mtime,
                    })
                except (OSError, PermissionError):
                    continue

        # Top 5 largest files
        files_info.sort(key=lambda x: x["size"], reverse=True)
        stats["largest_files"] = [
            {"path": f["path"], "size_mb": round(f["size"] / (1024 * 1024), 2)}
            for f in files_info[:5]
        ]

        # Sort by age
        files_info.sort(key=lambda x: x["modified"])
        stats["oldest_files"] = [f["path"] for f in files_info[:5]]
        stats["newest_files"] = [f["path"] for f in files_info[-5:]]

        return stats

    def archive_old_files(self, directory: Path, days: int = 90, dry_run: bool = False) -> Dict:
        """Move files not modified in N days to an archive folder."""
        archive_dir = directory / "_archive"
        cutoff = datetime.now().timestamp() - (days * 86400)
        result = {"archived": 0, "files": []}

        for file_path in directory.glob("*"):
            if file_path.is_file() and file_path.stat().st_mtime < cutoff:
                dest = archive_dir / file_path.name
                result["files"].append({"source": str(file_path), "destination": str(dest)})
                if not dry_run:
                    archive_dir.mkdir(exist_ok=True)
                    shutil.move(str(file_path), str(dest))
                    self._record_action(file_path, dest, "archive")
                result["archived"] += 1

        return result

    # === Setup & History ===

    def setup_folder_structure(self):
        """Create default folder structure."""
        for category in self.config.get("categories", self.DEFAULT_CATEGORIES):
            (self.data_dir / "files" / category).mkdir(parents=True, exist_ok=True)

    def _record_action(self, source: Path, target: Optional[Path], action: str, error: Optional[str] = None):
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "source": str(source),
            "target": str(target) if target else None,
            "action": action,
            "error": error,
        })
        self.save_history()

    def get_organization_stats(self) -> Dict:
        stats = {"total_files_moved": 0, "files_by_category": {}, "recent_errors": []}
        for entry in self.history:
            if entry["action"] == "move":
                stats["total_files_moved"] += 1
                if entry.get("target"):
                    category = Path(entry["target"]).parent.name
                    stats["files_by_category"][category] = stats["files_by_category"].get(category, 0) + 1
            elif entry["action"] == "error":
                stats["recent_errors"].append(entry)
        return stats

    def search_files(self, query: str) -> List[str]:
        """Search for files by name in organized directories."""
        results = []
        files_dir = self.data_dir / "files"
        if files_dir.exists():
            for file_path in files_dir.rglob("*"):
                if file_path.is_file() and query.lower() in file_path.name.lower():
                    results.append(str(file_path))
        return results[:50]

    def create_backup(self):
        """Create a backup of the file organizer configuration."""
        backup_dir = self.data_dir / "backups"
        backup_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = {
            "config": self.config,
            "rules": self.custom_rules,
            "timestamp": timestamp,
        }
        with open(backup_dir / f"file_org_backup_{timestamp}.json", "w") as f:
            json.dump(backup, f, indent=2)
