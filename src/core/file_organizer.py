"""
File organization and management system.
"""
from pathlib import Path
import shutil
from datetime import datetime
from typing import Dict, List, Optional
import json

class FileOrganizer:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.config_file = data_dir / "file_organizer_config.json"
        self.history_file = data_dir / "file_history.json"
        self.load_config()
        self.load_history()

    def load_config(self):
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                'categories': {
                    'documents': ['.pdf', '.doc', '.docx', '.txt'],
                    'images': ['.jpg', '.jpeg', '.png', '.gif'],
                    'audio': ['.mp3', '.wav', '.flac'],
                    'video': ['.mp4', '.avi', '.mov'],
                    'code': ['.py', '.js', '.html', '.css']
                },
                'naming_convention': 'date_category_name',
                'organize_by': ['category', 'date'],
                'backup_enabled': True,
                'backup_frequency': 'daily'
            }
            self.save_config()

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

    def load_history(self):
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                self.history = json.load(f)
        else:
            self.history = []

    def save_history(self):
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=4)

    def organize_files(self, source_dir: Path, target_dir: Optional[Path] = None) -> Dict:
        """
        Organize files from source directory into categorized structure.
        Returns a summary of actions taken.
        """
        if target_dir is None:
            target_dir = source_dir / "organized"
            
        target_dir.mkdir(exist_ok=True)
        summary = {'moved': 0, 'skipped': 0, 'errors': 0}
        
        for file_path in source_dir.glob('*'):
            if file_path.is_file():
                try:
                    category = self._get_file_category(file_path)
                    if category:
                        new_path = self._get_organized_path(file_path, target_dir, category)
                        new_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(file_path), str(new_path))
                        summary['moved'] += 1
                        self._record_action(file_path, new_path, 'move')
                    else:
                        summary['skipped'] += 1
                except Exception as e:
                    summary['errors'] += 1
                    self._record_action(file_path, None, 'error', str(e))
                    
        return summary

    def _get_file_category(self, file_path: Path) -> Optional[str]:
        """Determine the category of a file based on its extension."""
        ext = file_path.suffix.lower()
        for category, extensions in self.config['categories'].items():
            if ext in extensions:
                return category
        return None

    def _get_organized_path(self, file_path: Path, target_dir: Path, category: str) -> Path:
        """Generate the new path for a file based on organization rules."""
        date_str = datetime.now().strftime('%Y-%m-%d')
        new_name = f"{date_str}_{category}_{file_path.name}"
        return target_dir / category / new_name

    def _record_action(self, source: Path, target: Optional[Path], action: str, error: Optional[str] = None):
        """Record a file operation in the history."""
        self.history.append({
            'timestamp': datetime.now().isoformat(),
            'source': str(source),
            'target': str(target) if target else None,
            'action': action,
            'error': error
        })
        self.save_history()

    def get_organization_stats(self) -> Dict:
        """Get statistics about organized files."""
        stats = {
            'total_files_moved': 0,
            'files_by_category': {},
            'recent_errors': []
        }
        
        for entry in self.history:
            if entry['action'] == 'move':
                stats['total_files_moved'] += 1
                category = Path(entry['target']).parent.name
                stats['files_by_category'][category] = stats['files_by_category'].get(category, 0) + 1
            elif entry['action'] == 'error':
                stats['recent_errors'].append(entry)
                
        return stats
