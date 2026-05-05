import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

try:
    from src.core.smart_file_system.cli import main
    _HAS_MODULE = True
except ImportError:
    _HAS_MODULE = False

pytestmark = pytest.mark.skipif(not _HAS_MODULE, reason="smart_file_system.cli module not available")


class TestCLI:
    @pytest.fixture
    def test_dir(self):
        # Create temporary directory with test files
        temp_dir = tempfile.mkdtemp()
        (Path(temp_dir) / "test1.txt").write_text("Machine learning document")
        (Path(temp_dir) / "test2.txt").write_text("Deep learning research")
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_index_command(self, test_dir, capsys):
        test_args = ["cli.py", "index", test_dir]
        with patch.object(sys, 'argv', test_args):
            main()

        captured = capsys.readouterr()
        assert "Indexed 2 files" in captured.out

    def test_cluster_command(self, test_dir, capsys):
        # First index files
        test_args = ["cli.py", "index", test_dir]
        with patch.object(sys, 'argv', test_args):
            main()

        # Then test clustering
        test_args = ["cli.py", "cluster"]
        with patch.object(sys, 'argv', test_args):
            main()

        captured = capsys.readouterr()
        assert "clusters" in captured.out

    def test_report_command(self, test_dir, capsys):
        # Setup: index and cluster first
        test_args = ["cli.py", "index", test_dir]
        with patch.object(sys, 'argv', test_args):
            main()

        test_args = ["cli.py", "cluster"]
        with patch.object(sys, 'argv', test_args):
            main()

        # Test report generation
        with tempfile.NamedTemporaryFile() as temp_file:
            test_args = ["cli.py", "report", "--output", temp_file.name]
            with patch.object(sys, 'argv', test_args):
                main()

            captured = capsys.readouterr()
            assert temp_file.name in captured.out
            assert Path(temp_file.name).exists()

    def test_search_command(self, test_dir, capsys):
        # Setup: index files first
        test_args = ["cli.py", "index", test_dir]
        with patch.object(sys, 'argv', test_args):
            main()

        # Test search (may return empty if ML deps unavailable)
        test_args = ["cli.py", "search", "machine learning"]
        with patch.object(sys, 'argv', test_args):
            main()

        captured = capsys.readouterr()
        assert "Similar files:" in captured.out

    def test_error_handling(self, capsys):
        test_args = ["cli.py", "index", "/nonexistent/directory"]
        with patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1
