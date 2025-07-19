import pytest
from src.main import main

def test_main_exists():
    """Test that main() function exists and is callable."""
    assert callable(main)

def test_main_imports():
    """Test that main imports required modules."""
    import src.gui.main_window
    import src.core.task_manager
    import src.core.system_optimizer
    import src.profile.mental_health_profile_builder
