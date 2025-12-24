"""
File organization and management system.
"""
from pathlib import Path
import shutil
from datetime import datetime
from typing import Dict, List, Optional
import json
import logging
import uuid

class FileOrganizer:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.config_file = data_dir / "file_organizer_config.json"
        self.history_file = data_dir / "transaction_history.json"
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
        """Load the transaction history."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    self.history = json.load(f)
            except json.JSONDecodeError:
                self.history = []
        else:
            self.history = []

    def save_history(self):
        """Save the transaction history."""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=4)

    def generate_plan(self, source_dir: Path, target_dir: Optional[Path] = None) -> Dict:
        """
        Generate a plan for organizing files.
        Does NOT move files.
        """
        if target_dir is None:
            target_dir = source_dir / "organized"

        plan = {
            'source_dir': str(source_dir),
            'target_dir': str(target_dir),
            'timestamp': datetime.now().isoformat(),
            'moves': [],
            'skipped': []
        }

        for file_path in source_dir.glob('*'):
            if file_path.is_file():
                category = self._get_file_category(file_path)
                if category:
                    new_path = self._get_organized_path(file_path, target_dir, category)
                    plan['moves'].append({
                        'source': str(file_path),
                        'target': str(new_path),
                        'category': category
                    })
                else:
                    plan['skipped'].append(str(file_path))

        return plan

    def execute_plan(self, plan: Dict) -> Dict:
        """
        Execute a generated plan and log the transaction.
        """
        transaction_id = str(uuid.uuid4())
        transaction = {
            'id': transaction_id,
            'timestamp': datetime.now().isoformat(),
            'plan_timestamp': plan['timestamp'],
            'operations': [],
            'status': 'completed', # or 'partial'
            'errors': []
        }

        success_count = 0

        for move in plan['moves']:
            src = Path(move['source'])
            dst = Path(move['target'])

            try:
                if not src.exists():
                    transaction['errors'].append(f"Source file not found: {src}")
                    continue

                if dst.exists():
                    # Handle collision: rename
                    stem = dst.stem
                    suffix = dst.suffix
                    dst = dst.parent / f"{stem}_{datetime.now().strftime('%H%M%S')}{suffix}"

                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dst))

                transaction['operations'].append({
                    'type': 'move',
                    'source': str(src),
                    'target': str(dst)
                })
                success_count += 1
            except Exception as e:
                transaction['errors'].append(str(e))
                logging.error(f"Error moving {src} to {dst}: {e}")

        # Save transaction log
        self.history.append(transaction)
        self.save_history()

        return {
            'transaction_id': transaction_id,
            'files_moved': success_count,
            'errors': len(transaction['errors'])
        }

    def undo_last_transaction(self) -> Dict:
        """
        Undo the last completed transaction.
        """
        if not self.history:
            return {'status': 'error', 'message': 'No history to undo'}

        last_transaction = self.history.pop()
        undo_results = {
            'transaction_id': last_transaction['id'],
            'restored': 0,
            'errors': []
        }

        # Reverse operations
        for op in reversed(last_transaction['operations']):
            if op['type'] == 'move':
                src = Path(op['target']) # Current location
                dst = Path(op['source']) # Original location

                try:
                    if src.exists():
                        # Ensure original directory exists
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        if dst.exists():
                             # Collision on restore? Backup rename.
                            dst = dst.parent / f"restored_{dst.name}"

                        shutil.move(str(src), str(dst))
                        undo_results['restored'] += 1
                    else:
                        undo_results['errors'].append(f"File missing: {src}")
                except Exception as e:
                    undo_results['errors'].append(f"Error restoring {src}: {e}")

        self.save_history()
        return undo_results

    def organize_files(self, source_dir: Path, target_dir: Optional[Path] = None, dry_run: bool = True) -> Dict:
        """
        Compatibility wrapper.
        If dry_run is True, returns the Plan.
        If dry_run is False, executes and returns Summary.
        """
        plan = self.generate_plan(source_dir, target_dir)
        if dry_run:
            return plan
        else:
            return self.execute_plan(plan)

    def _get_file_category(self, file_path: Path) -> Optional[str]:
        """Determine the category of a file based on its extension."""
        ext = file_path.suffix.lower()
        for category, extensions in self.config['categories'].items():
            if ext in extensions:
                return category
        return None

    def _get_organized_path(self, file_path: Path, target_dir: Path, category: str) -> Path:
        """Generate the new path for a file based on organization rules."""
        # Simplified naming for V1: Just Category/Filename
        # Could add Date subfolders if configured
        return target_dir / category / file_path.name

    def create_backup(self, source_dir: Path) -> Optional[Path]:
        """Create a backup of the source directory."""
        if not source_dir.exists():
            return None

        backup_dir = self.data_dir / "backups" / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        try:
            shutil.copytree(source_dir, backup_dir)
            return backup_dir
        except Exception as e:
            logging.error(f"Backup failed: {e}")
            return None

    def search_files(self, query: str, search_dir: Optional[Path] = None) -> List[Path]:
        """
        Simple filename search.
        """
        if search_dir is None:
            # Default to scanning the data_dir or a configured root
            # For now, let's just return empty if no dir specified,
            # or maybe search the last organized dir?
            return []

        results = []
        try:
            for file_path in search_dir.rglob(f"*{query}*"):
                results.append(file_path)
        except Exception:
            pass
        return results
