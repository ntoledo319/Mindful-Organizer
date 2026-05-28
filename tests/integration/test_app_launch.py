import subprocess
import sys
from pathlib import Path


def test_app_launch():
    """Test that the application can be launched from command line."""
    process = subprocess.Popen(
        [sys.executable, str(Path(__file__).resolve().parents[2] / "src" / "main.py"), "--help"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate(timeout=5)
    assert process.returncode == 0
    assert b"usage" in stdout.lower()
