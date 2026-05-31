"""
Enhanced file organization and management system with dry-run,
undo, duplicate detection, watch folders, custom rules, batch rename,
recency scoring, and archive support.
"""

import hashlib
import json
import logging
import shutil
import threading
import time
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

_SECONDS_PER_DAY = 86400


class FileOrganizer:
    """Manages file organization with mental health-aware features."""

    # Expanded file categories (30+ extensions)
    DEFAULT_CATEGORIES = {
        "documents": [
            ".pdf",
            ".doc",
            ".docx",
            ".txt",
            ".rtf",
            ".odt",
            ".pages",
            ".tex",
            ".md",
            ".epub",
        ],
        "spreadsheets": [".xls", ".xlsx", ".csv", ".ods", ".numbers"],
        "presentations": [".ppt", ".pptx", ".key", ".odp"],
        "images": [
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",
            ".svg",
            ".webp",
            ".tiff",
            ".ico",
            ".heic",
            ".raw",
        ],
        "audio": [
            ".mp3",
            ".wav",
            ".flac",
            ".aac",
            ".ogg",
            ".wma",
            ".m4a",
            ".aiff",
        ],
        "video": [
            ".mp4",
            ".avi",
            ".mov",
            ".mkv",
            ".wmv",
            ".flv",
            ".webm",
            ".m4v",
        ],
        "code": [
            ".py",
            ".js",
            ".ts",
            ".html",
            ".css",
            ".java",
            ".cpp",
            ".c",
            ".h",
            ".go",
            ".rs",
            ".rb",
            ".php",
            ".swift",
        ],
        "archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
        "design": [".psd", ".ai", ".sketch", ".fig", ".xd", ".indd"],
        "data": [
            ".json",
            ".xml",
            ".yaml",
            ".yml",
            ".toml",
            ".sql",
            ".db",
            ".sqlite",
        ],
        "fonts": [".ttf", ".otf", ".woff", ".woff2"],
        "executables": [".exe", ".msi", ".dmg", ".app", ".deb", ".rpm"],
    }

    # Content-based hints: map first bytes (magic numbers) to categories
    MAGIC_BYTES: dict[bytes, str] = {
        b"%PDF": "documents",
        b"\x89PNG": "images",
        b"\xff\xd8\xff": "images",
        b"GIF8": "images",
        b"PK\x03\x04": "archives",  # zip / docx / xlsx
        b"Rar!": "archives",
        b"\x1f\x8b": "archives",  # gzip
        b"ID3": "audio",
        b"\xff\xfb": "audio",  # mp3
        b"\x00\x00\x00\x1c": "video",  # mp4 ftyp
        b"\x00\x00\x00\x18": "video",
    }

    def __init__(self, data_dir: Path, profile: object | None = None):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.profile = profile
        self.config_file = data_dir / "file_organizer_config.json"
        self.history_file = data_dir / "file_history.json"
        self.rules_file = data_dir / "organization_rules.json"
        self.config: dict[str, Any] = {}
        self.history: list[dict] = []
        self.custom_rules: list[dict] = []
        self._undo_stack: list[list[dict]] = []
        self._watch_thread: threading.Thread | None = None
        self._watch_stop_event = threading.Event()
        self.load_config()
        self.load_history()
        self.load_rules()

    # ── Configuration Persistence ─────────────────────────────────

    def load_config(self) -> None:
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
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

    def save_config(self) -> None:
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=4)

    def load_history(self) -> None:
        if self.history_file.exists():
            try:
                with open(self.history_file) as f:
                    self.history = json.load(f)
            except (json.JSONDecodeError, Exception):
                self.history = []

    def save_history(self) -> None:
        with open(self.history_file, "w") as f:
            json.dump(self.history[-1000:], f, indent=2)

    def load_rules(self) -> None:
        if self.rules_file.exists():
            try:
                with open(self.rules_file) as f:
                    self.custom_rules = json.load(f)
            except (json.JSONDecodeError, Exception):
                self.custom_rules = []

    def save_rules(self) -> None:
        with open(self.rules_file, "w") as f:
            json.dump(self.custom_rules, f, indent=2)

    # ── Core Organization ─────────────────────────────────────────

    def organize_files(
        self,
        source_dir: Path,
        target_dir: Path | None = None,
        dry_run: bool = False,
    ) -> dict:
        """Organize files from source directory into categorized structure.

        Args:
            source_dir: Directory containing files to organize.
            target_dir: Destination root. Defaults to source_dir/organized.
            dry_run: If True, preview changes without moving files.

        Returns:
            Summary dict with keys: moved, skipped, errors, actions.
        """
        if target_dir is None:
            target_dir = source_dir / "organized"

        summary: dict = {"moved": 0, "skipped": 0, "errors": 0, "actions": []}

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
                            "action": "preview" if dry_run else "move",
                        }
                        if not dry_run:
                            new_path.parent.mkdir(parents=True, exist_ok=True)
                            shutil.move(str(file_path), str(new_path))
                            self._record_action(file_path, new_path, "move")
                        summary["moved"] += 1
                        summary["actions"].append(action)
                    else:
                        summary["skipped"] += 1
                except (OSError, PermissionError, shutil.Error) as e:
                    summary["errors"] += 1
                    self._record_action(file_path, None, "error", str(e))

        if not dry_run and summary["actions"]:
            self._undo_stack.append(summary["actions"])

        return summary

    def dry_run(self, source_dir: Path, target_dir: Path | None = None) -> dict:
        """Preview organization without moving files.

        Returns the same summary structure as organize_files but with
        action type 'preview' instead of 'move'.
        """
        return self.organize_files(source_dir, target_dir, dry_run=True)

    def undo_last_organization(self) -> dict:
        """Undo the most recent organization batch, restoring files to
        their original locations.

        Returns:
            Dict with undone count, errors, and message.
        """
        if not self._undo_stack:
            return {"undone": 0, "errors": 0, "message": "Nothing to undo."}

        actions = self._undo_stack.pop()
        result: dict = {"undone": 0, "errors": 0, "message": ""}

        for action in reversed(actions):
            if action.get("action") == "move":
                try:
                    src = Path(action["destination"])
                    dst = Path(action["source"])
                    if src.exists():
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(src), str(dst))
                        result["undone"] += 1
                        self._record_action(src, dst, "undo")
                except (OSError, PermissionError, shutil.Error):
                    result["errors"] += 1

        result["message"] = f"Undone {result['undone']} file moves."
        return result

    # ── File Categorization ───────────────────────────────────────

    def _get_file_category(self, file_path: Path) -> str | None:
        """Determine category using custom rules, extension, then content hints."""
        # Custom rules first
        for rule in self.custom_rules:
            if self._matches_rule(file_path, rule):
                category = rule.get("category")
                if isinstance(category, str):
                    return category

        # Extension-based lookup
        ext = file_path.suffix.lower()
        categories: dict[str, list[str]] = self.config.get("categories", self.DEFAULT_CATEGORIES)
        for category, extensions in categories.items():
            if ext in extensions:
                return category

        # Content-based fallback (magic bytes)
        return self._detect_category_by_content(file_path)

    def _detect_category_by_content(self, file_path: Path) -> str | None:
        """Attempt to detect file category from the first bytes of the file."""
        try:
            with open(file_path, "rb") as f:
                header = f.read(8)
            for magic, category in self.MAGIC_BYTES.items():
                if header.startswith(magic):
                    return category
        except (OSError, PermissionError):
            pass
        return None

    def _matches_rule(self, file_path: Path, rule: dict[str, Any]) -> bool:
        """Check if a file matches a custom organization rule."""
        rule_type = str(rule.get("type", "extension"))
        pattern = str(rule.get("pattern", ""))

        if rule_type == "extension":
            return file_path.suffix.lower() == pattern.lower()
        elif rule_type == "name_contains":
            return pattern.lower() in file_path.name.lower()
        elif rule_type == "name_starts":
            return file_path.name.lower().startswith(pattern.lower())
        elif rule_type == "name_ends":
            stem = file_path.stem.lower()
            return stem.endswith(pattern.lower())
        elif rule_type == "size_gt":
            try:
                return file_path.stat().st_size > int(pattern)
            except (OSError, ValueError):
                return False
        return False

    def _get_organized_path(self, file_path: Path, target_dir: Path, category: str) -> Path:
        """Generate the organized destination path for a file."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        return target_dir / category / f"{date_str}_{file_path.name}"

    # ── Custom Rules Engine ───────────────────────────────────────

    def add_rule(
        self,
        rule_type: str,
        pattern: str,
        category: str,
        destination: str | None = None,
    ) -> None:
        """Add a custom organization rule.

        Args:
            rule_type: One of 'extension', 'name_contains', 'name_starts',
                       'name_ends', 'size_gt'.
            pattern: The value to match (e.g. '.psd', 'project', '1048576').
            category: Target category name (e.g. 'Design').
            destination: Optional specific destination directory override.
        """
        self.custom_rules.append(
            {
                "type": rule_type,
                "pattern": pattern,
                "category": category,
                "destination": destination,
                "created": datetime.now().isoformat(),
            }
        )
        self.save_rules()

    def remove_rule(self, index: int) -> bool:
        """Remove a custom rule by index. Returns True if removed."""
        if 0 <= index < len(self.custom_rules):
            self.custom_rules.pop(index)
            self.save_rules()
            return True
        return False

    def get_rules(self) -> list[dict]:
        """Return a copy of all custom rules."""
        return self.custom_rules.copy()

    # ── Batch Rename ──────────────────────────────────────────────

    def batch_rename(
        self,
        directory: Path,
        template: str,
        dry_run: bool = False,
    ) -> list[dict]:
        """Rename files in a directory using a template string.

        Template placeholders:
            {name}     - original filename without extension
            {ext}      - original extension (including dot)
            {date}     - current date YYYY-MM-DD
            {n}        - sequential number (zero-padded to 3 digits)
            {category} - detected file category

        Args:
            directory: Directory containing files to rename.
            template: Naming template string.
            dry_run: If True, return proposed renames without executing.

        Returns:
            List of dicts with 'original', 'new_name', and 'action' keys.
        """
        results: list[dict] = []
        files = sorted(
            [f for f in directory.iterdir() if f.is_file()],
            key=lambda p: p.name,
        )

        for idx, file_path in enumerate(files):
            category = self._get_file_category(file_path) or "other"
            new_name = template.format(
                name=file_path.stem,
                ext=file_path.suffix,
                date=datetime.now().strftime("%Y-%m-%d"),
                n=f"{idx + 1:03d}",
                category=category,
            )
            new_path = file_path.parent / new_name
            entry = {
                "original": str(file_path),
                "new_name": str(new_path),
                "action": "preview" if dry_run else "rename",
            }
            if not dry_run and new_path != file_path:
                try:
                    file_path.rename(new_path)
                    self._record_action(file_path, new_path, "rename")
                except OSError as e:
                    entry["action"] = "error"
                    entry["error"] = str(e)
            results.append(entry)

        return results

    # ── Duplicate Detection ───────────────────────────────────────

    def find_duplicates(self, directory: Path) -> list[tuple[Path, Path]]:
        """Find duplicate files by size and SHA-256 hash.

        Returns:
            List of (original, duplicate) path pairs.
        """
        size_map: dict[int, list[Path]] = {}
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                try:
                    size = file_path.stat().st_size
                    size_map.setdefault(size, []).append(file_path)
                except (OSError, PermissionError):
                    continue

        duplicates: list[tuple[Path, Path]] = []
        for _size, files in size_map.items():
            if len(files) < 2:
                continue
            hash_map: dict[str, list[Path]] = {}
            for fp in files:
                try:
                    file_hash = self._hash_file(fp)
                    hash_map.setdefault(file_hash, []).append(fp)
                except (OSError, PermissionError):
                    continue
            for _h, fps in hash_map.items():
                if len(fps) >= 2:
                    for i in range(1, len(fps)):
                        duplicates.append((fps[0], fps[i]))

        return duplicates

    def find_duplicates_by_name(self, directory: Path) -> dict[str, list[Path]]:
        """Find files with identical names across subdirectories.

        Returns:
            Dict mapping filename to list of paths where it appears.
        """
        name_map: dict[str, list[Path]] = {}
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                name_map.setdefault(file_path.name, []).append(file_path)
        return {k: v for k, v in name_map.items() if len(v) > 1}

    @staticmethod
    def _hash_file(file_path: Path, chunk_size: int = 8192) -> str:
        """Compute SHA-256 hash of a file."""
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                hasher.update(chunk)
        return hasher.hexdigest()

    # ── Watch Folder Mode ─────────────────────────────────────────

    def start_watching(
        self,
        directory: Path,
        target_dir: Path | None = None,
        poll_interval: float = 5.0,
        callback: Callable[[dict], None] | None = None,
    ) -> None:
        """Start monitoring a directory for new files.

        New files are organized automatically. Runs in a background thread.

        Args:
            directory: Directory to watch.
            target_dir: Where organized files go. Defaults to directory/organized.
            poll_interval: Seconds between directory scans.
            callback: Optional function called with each move summary.
        """
        if self._watch_thread and self._watch_thread.is_alive():
            return  # Already watching

        self._watch_stop_event.clear()
        seen: set = set()

        # Seed with existing files
        if directory.exists():
            for fp in directory.iterdir():
                if fp.is_file():
                    seen.add(str(fp))

        def _watch_loop() -> None:
            while not self._watch_stop_event.is_set():
                if directory.exists():
                    for fp in directory.iterdir():
                        if fp.is_file() and str(fp) not in seen:
                            seen.add(str(fp))
                            category = self._get_file_category(fp)
                            if category:
                                dest_dir = target_dir or (directory / "organized")
                                new_path = self._get_organized_path(fp, dest_dir, category)
                                try:
                                    new_path.parent.mkdir(parents=True, exist_ok=True)
                                    shutil.move(str(fp), str(new_path))
                                    self._record_action(fp, new_path, "watch_move")
                                    if callback:
                                        callback(
                                            {
                                                "source": str(fp),
                                                "destination": str(new_path),
                                                "category": category,
                                            }
                                        )
                                except (OSError, PermissionError, shutil.Error):
                                    logger = logging.getLogger(__name__)
                                    logger.exception("Watch folder move failed")
                self._watch_stop_event.wait(poll_interval)

        self._watch_thread = threading.Thread(target=_watch_loop, daemon=True, name="file-watcher")
        self._watch_thread.start()

    def stop_watching(self) -> None:
        """Stop the watch folder thread."""
        self._watch_stop_event.set()
        if self._watch_thread:
            self._watch_thread.join(timeout=10)
            self._watch_thread = None

    @property
    def is_watching(self) -> bool:
        return self._watch_thread is not None and self._watch_thread.is_alive()

    # ── Recency Scoring ───────────────────────────────────────────

    def get_recency_scores(self, directory: Path) -> list[dict]:
        """Score files by how recently they were accessed/modified.

        Returns a list sorted by recency (most recent first), each with:
            path, last_accessed, last_modified, recency_score (0-100).
        """
        now = time.time()
        scored: list[dict] = []

        for fp in directory.rglob("*"):
            if not fp.is_file():
                continue
            try:
                stat = fp.stat()
                last_access = stat.st_atime
                last_modify = stat.st_mtime
                most_recent = max(last_access, last_modify)
                age_days = (now - most_recent) / _SECONDS_PER_DAY
                # Exponential decay: score 100 for today, ~37 after 30 days
                score = max(0.0, 100.0 * (0.97**age_days))
                scored.append(
                    {
                        "path": str(fp),
                        "last_accessed": datetime.fromtimestamp(last_access).isoformat(),
                        "last_modified": datetime.fromtimestamp(last_modify).isoformat(),
                        "age_days": round(age_days, 1),
                        "recency_score": round(score, 1),
                    }
                )
            except (OSError, PermissionError):
                continue

        scored.sort(key=lambda x: x["recency_score"], reverse=True)
        return scored

    # ── Archive Old Files ─────────────────────────────────────────

    def archive_old_files(
        self,
        directory: Path,
        days: int = 90,
        dry_run: bool = False,
    ) -> dict:
        """Move files not modified in *days* to an archive sub-folder.

        Args:
            directory: Source directory.
            days: Age threshold in days.
            dry_run: Preview only.

        Returns:
            Dict with archived count and file list.
        """
        archive_dir = directory / "_archive"
        cutoff = datetime.now().timestamp() - (days * _SECONDS_PER_DAY)
        result: dict = {"archived": 0, "files": []}

        for fp in directory.glob("*"):
            if fp.is_file():
                try:
                    if fp.stat().st_mtime < cutoff:
                        dest = archive_dir / fp.name
                        result["files"].append({"source": str(fp), "destination": str(dest)})
                        if not dry_run:
                            archive_dir.mkdir(exist_ok=True)
                            shutil.move(str(fp), str(dest))
                            self._record_action(fp, dest, "archive")
                        result["archived"] += 1
                except (OSError, PermissionError):
                    continue

        return result

    # ── File Statistics ───────────────────────────────────────────

    def get_file_statistics(self, directory: Path) -> dict:
        """Comprehensive file statistics for a directory tree.

        Returns counts by type, size distribution, age analysis, and
        top largest / oldest / newest files.
        """
        stats: dict = {
            "total_files": 0,
            "total_size_bytes": 0,
            "by_category": {},
            "by_extension": {},
            "size_distribution": {
                "tiny_lt_1kb": 0,
                "small_1kb_100kb": 0,
                "medium_100kb_10mb": 0,
                "large_10mb_100mb": 0,
                "huge_gt_100mb": 0,
            },
            "age_distribution": {
                "today": 0,
                "this_week": 0,
                "this_month": 0,
                "this_year": 0,
                "older": 0,
            },
            "largest_files": [],
            "oldest_files": [],
            "newest_files": [],
        }

        now = time.time()
        files_info: list[dict] = []

        for fp in directory.rglob("*"):
            if not fp.is_file():
                continue
            try:
                fstat = fp.stat()
            except (OSError, PermissionError):
                continue

            size = fstat.st_size
            mtime = fstat.st_mtime
            category = self._get_file_category(fp) or "uncategorized"
            ext = fp.suffix.lower() or "(none)"

            stats["total_files"] += 1
            stats["total_size_bytes"] += size
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
            stats["by_extension"][ext] = stats["by_extension"].get(ext, 0) + 1

            # Size distribution
            if size < 1024:
                stats["size_distribution"]["tiny_lt_1kb"] += 1
            elif size < 102400:
                stats["size_distribution"]["small_1kb_100kb"] += 1
            elif size < 10485760:
                stats["size_distribution"]["medium_100kb_10mb"] += 1
            elif size < 104857600:
                stats["size_distribution"]["large_10mb_100mb"] += 1
            else:
                stats["size_distribution"]["huge_gt_100mb"] += 1

            # Age distribution
            age_days = (now - mtime) / 86400
            if age_days < 1:
                stats["age_distribution"]["today"] += 1
            elif age_days < 7:
                stats["age_distribution"]["this_week"] += 1
            elif age_days < 30:
                stats["age_distribution"]["this_month"] += 1
            elif age_days < 365:
                stats["age_distribution"]["this_year"] += 1
            else:
                stats["age_distribution"]["older"] += 1

            files_info.append({"path": str(fp), "size": size, "modified": mtime})

        # Top 5 largest
        files_info.sort(key=lambda x: x["size"], reverse=True)
        stats["largest_files"] = [
            {
                "path": f["path"],
                "size_mb": round(f["size"] / (1024 * 1024), 2),
            }
            for f in files_info[:5]
        ]

        # Oldest / newest
        files_info.sort(key=lambda x: x["modified"])
        stats["oldest_files"] = [f["path"] for f in files_info[:5]]
        stats["newest_files"] = [f["path"] for f in files_info[-5:]]

        return stats

    # ── History & Stats Helpers ───────────────────────────────────

    def _record_action(
        self,
        source: Path,
        target: Path | None,
        action: str,
        error: str | None = None,
    ) -> None:
        """Record a file operation in the history log."""
        self.history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "source": str(source),
                "target": str(target) if target else None,
                "action": action,
                "error": error,
            }
        )
        self.save_history()

    def get_organization_stats(self) -> dict:
        """Get statistics about organized files from history."""
        stats: dict = {
            "total_files_moved": 0,
            "files_by_category": {},
            "recent_errors": [],
        }
        for entry in self.history:
            if entry["action"] == "move":
                stats["total_files_moved"] += 1
                if entry.get("target"):
                    category = Path(entry["target"]).parent.name
                    stats["files_by_category"][category] = (
                        stats["files_by_category"].get(category, 0) + 1
                    )
            elif entry["action"] == "error":
                stats["recent_errors"].append(entry)
        return stats

    def search_files(self, query: str) -> list[str]:
        """Search for files by name in organized directories."""
        results: list[str] = []
        files_dir = self.data_dir / "files"
        if files_dir.exists():
            for fp in files_dir.rglob("*"):
                if fp.is_file() and query.lower() in fp.name.lower():
                    results.append(str(fp))
        return results[:50]

    def setup_folder_structure(self) -> None:
        """Create the default category folder structure."""
        for category in self.config.get("categories", self.DEFAULT_CATEGORIES):
            (self.data_dir / "files" / category).mkdir(parents=True, exist_ok=True)

    def create_backup(self) -> None:
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
