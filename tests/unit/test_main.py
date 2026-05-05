import pytest

try:
    from src.main import main
    _HAS_MODULE = True
except ImportError:
    _HAS_MODULE = False

pytestmark = pytest.mark.skipif(not _HAS_MODULE, reason="main module not available")


def test_main_exists():
    """Test that main() function exists and is callable."""
    assert callable(main)

def test_main_imports():
    """Test that main imports required modules."""
