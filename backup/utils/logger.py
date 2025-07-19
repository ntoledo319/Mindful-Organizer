"""Logging utilities for Mindful Organizer."""
import logging
from pathlib import Path
from datetime import datetime


def setup_logger(data_dir: Path) -> logging.Logger:
    """Set up application logger."""
    # Create logs directory
    log_dir = data_dir / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Create log file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    log_file = log_dir / f"mindful_organizer_{timestamp}.log"
    
    # Configure logger
    logger = logging.getLogger("mindful_organizer")
    logger.setLevel(logging.INFO)
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_formatter = logging.Formatter(
        "%(levelname)s: %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger
