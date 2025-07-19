#!/usr/bin/env python3
"""
Cleanup script for Mindful Organizer.
Removes temporary files and checks for stray project files.
"""
import os
import shutil
from pathlib import Path
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cleanup.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class ProjectCleaner:
    def __init__(self):
        self.home = Path.home()
        self.project_patterns = [
            "mindful_organizer*",
            "mindful_optimizer*",
            "MindfulOptimizer*",
            ".mindful_organizer*",
            ".mindful_optimizer*"
        ]
        self.allowed_paths = [
            self.home / "CascadeProjects" / "mindful_organizer"
        ]
        self.temp_extensions = [
            ".pyc", ".pyo", ".pyd", ".so",
            ".coverage", ".pytest_cache",
            "__pycache__", ".DS_Store"
        ]

    def find_stray_files(self):
        """Find files and directories matching project patterns."""
        stray_items = []
        
        # Search in home directory and CascadeProjects
        search_paths = [self.home, self.home / "CascadeProjects"]
        
        for search_path in search_paths:
            if not search_path.exists():
                continue
                
            for pattern in self.project_patterns:
                for item in search_path.glob("**/" + pattern):
                    # Skip allowed paths
                    if any(allowed in item.parents for allowed in self.allowed_paths):
                        continue
                    if item not in self.allowed_paths:
                        stray_items.append(item)
        
        return stray_items

    def cleanup_temp_files(self):
        """Remove temporary files from the project directory."""
        project_dir = self.home / "CascadeProjects" / "mindful_organizer"
        removed = []
        
        if not project_dir.exists():
            logger.warning(f"Project directory not found: {project_dir}")
            return removed
            
        for ext in self.temp_extensions:
            for item in project_dir.glob(f"**/*{ext}"):
                try:
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
                    removed.append(item)
                    logger.info(f"Removed: {item}")
                except Exception as e:
                    logger.error(f"Failed to remove {item}: {e}")
                    
        return removed

    def create_report(self, stray_items, removed_temps):
        """Create a cleanup report."""
        report = []
        report.append("=== Mindful Organizer Cleanup Report ===")
        report.append(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("\n=== Stray Project Files ===")
        
        if stray_items:
            for item in stray_items:
                report.append(f"- {item}")
        else:
            report.append("No stray files found.")
            
        report.append("\n=== Removed Temporary Files ===")
        if removed_temps:
            for item in removed_temps:
                report.append(f"- {item}")
        else:
            report.append("No temporary files removed.")
            
        return "\n".join(report)

def main():
    """Main cleanup function."""
    try:
        cleaner = ProjectCleaner()
        
        # Find stray files
        logger.info("Searching for stray files...")
        stray_items = cleaner.find_stray_files()
        
        # Clean temporary files
        logger.info("Cleaning temporary files...")
        removed_temps = cleaner.cleanup_temp_files()
        
        # Create and save report
        report = cleaner.create_report(stray_items, removed_temps)
        report_path = Path.home() / "CascadeProjects" / "mindful_organizer" / "cleanup_report.txt"
        report_path.write_text(report)
        
        logger.info(f"Cleanup completed. Report saved to: {report_path}")
        
        # Print stray files that need manual review
        if stray_items:
            logger.warning("\nThe following stray files were found and may need manual review:")
            for item in stray_items:
                logger.warning(f"- {item}")
                
    except Exception as e:
        logger.error(f"Cleanup failed: {e}", exc_info=True)

if __name__ == "__main__":
    main()
