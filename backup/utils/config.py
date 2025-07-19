"""Configuration utilities for Mindful Organizer."""
import json
from pathlib import Path
from typing import Dict, Any


class Config:
    """Configuration manager for Mindful Organizer."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.config_file = data_dir / "config.json"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if self.config_file.exists():
            with open(self.config_file, "r") as f:
                return json.load(f)
        return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default configuration."""
        config = {
            "optimization": {
                "auto_optimize": True,
                "optimization_interval": 300,  # 5 minutes
                "resource_threshold": 80,  # percentage
            },
            "mindfulness": {
                "break_interval": 1800,  # 30 minutes
                "meditation_reminder": True,
                "breathing_reminder": True,
            },
            "ui": {
                "theme": "light",
                "font_size": 12,
                "show_system_tray": True,
            },
            "data": {
                "backup_enabled": True,
                "backup_interval": 86400,  # 24 hours
                "max_history": 365,  # days
            }
        }
        self.save_config(config)
        return config
    
    def save_config(self, config: Dict[str, Any] = None):
        """Save configuration to file."""
        if config is not None:
            self.config = config
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=4)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        try:
            parts = key.split(".")
            value = self.config
            for part in parts:
                value = value[part]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """Set configuration value."""
        parts = key.split(".")
        config = self.config
        for part in parts[:-1]:
            if part not in config:
                config[part] = {}
            config = config[part]
        config[parts[-1]] = value
        self.save_config()
