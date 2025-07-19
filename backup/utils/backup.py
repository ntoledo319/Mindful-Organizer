"""Backup utilities for Mindful Organizer."""
import shutil
from pathlib import Path
from datetime import datetime
import json
from typing import List


class BackupManager:
    """Manage data backups for Mindful Organizer."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.backup_dir = data_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self) -> Path:
        """Create a backup of all data."""
        # Create timestamp for backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"backup_{timestamp}"
        
        # Create backup directory
        backup_path.mkdir(exist_ok=True)
        
        # Copy all data files
        for item in self.data_dir.glob("*"):
            if item.name != "backups":  # Skip backup directory
                if item.is_file():
                    shutil.copy2(item, backup_path)
                elif item.is_dir():
                    shutil.copytree(item, backup_path / item.name)
        
        # Create backup info
        info = {
            "timestamp": timestamp,
            "created": datetime.now().isoformat(),
            "files": [f.name for f in backup_path.rglob("*") if f.is_file()]
        }
        
        with open(backup_path / "backup_info.json", "w") as f:
            json.dump(info, f, indent=4)
        
        return backup_path
    
    def restore_backup(self, backup_path: Path):
        """Restore data from a backup."""
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup not found: {backup_path}")
        
        # Clear current data (except backups)
        for item in self.data_dir.glob("*"):
            if item.name != "backups":
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
        
        # Restore from backup
        for item in backup_path.glob("*"):
            if item.name != "backup_info.json":
                if item.is_file():
                    shutil.copy2(item, self.data_dir)
                elif item.is_dir():
                    shutil.copytree(item, self.data_dir / item.name)
    
    def list_backups(self) -> List[dict]:
        """List all available backups."""
        backups = []
        for backup_dir in self.backup_dir.glob("backup_*"):
            info_file = backup_dir / "backup_info.json"
            if info_file.exists():
                with open(info_file, "r") as f:
                    info = json.load(f)
                    info["path"] = str(backup_dir)
                    backups.append(info)
        
        return sorted(backups, key=lambda x: x["timestamp"], reverse=True)
    
    def cleanup_old_backups(self, keep_days: int = 30):
        """Remove backups older than specified days."""
        cutoff = datetime.now().timestamp() - (keep_days * 86400)
        
        for backup_dir in self.backup_dir.glob("backup_*"):
            if backup_dir.stat().st_mtime < cutoff:
                shutil.rmtree(backup_dir)
