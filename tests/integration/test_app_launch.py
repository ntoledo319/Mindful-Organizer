import subprocess
import time
import pytest

def test_app_launch():
    """Test that the application can be launched from command line."""
    process = subprocess.Popen(
        ["mindful-organizer"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(2)  # Give app time to start
    process.terminate()
    assert process.poll() is None  # Process was running
