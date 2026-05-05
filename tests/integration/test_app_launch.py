import subprocess


def test_app_launch():
    """Test that the application can be launched from command line."""
    process = subprocess.Popen(
        ["mindful-organizer", "--help"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate(timeout=5)
    assert process.returncode == 0
    assert b"usage" in stdout.lower()
