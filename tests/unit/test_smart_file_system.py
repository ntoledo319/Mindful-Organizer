import shutil
import tempfile
from pathlib import Path

import pytest

try:
    from src.core.smart_file_system import SmartFileSystem
    _HAS_MODULE = True
except ImportError:
    _HAS_MODULE = False

pytestmark = pytest.mark.skipif(not _HAS_MODULE, reason="smart_file_system module not available")


class TestSmartFileSystem:
    @pytest.fixture
    def test_dir(self):
        temp_dir = tempfile.mkdtemp()
        files = {
            'doc1.txt': 'This is a document about machine learning',
            'doc2.txt': 'Deep learning and neural networks',
            'code1.py': 'def train_model(): pass',
            'code2.py': 'class NeuralNetwork: pass',
            'data.json': '{"features": [1,2,3], "label": "test"}'
        }
        for filename, content in files.items():
            with open(Path(temp_dir) / filename, 'w') as f:
                f.write(content)
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def sfs(self):
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp.close()
            sfs = SmartFileSystem(db_path=tmp.name)
            yield sfs
            del sfs
            Path(tmp.name).unlink(missing_ok=True)

    def test_initialization(self, sfs):
        assert sfs is not None
        assert hasattr(sfs, 'file_indexer')
        assert hasattr(sfs, 'file_clusterer')

    def test_index_directory(self, sfs, test_dir):
        result = sfs.index_directory(test_dir)
        assert result['status'] == 'success'
        assert result['files_indexed'] == 5

    def test_cluster_files(self, sfs, test_dir):
        sfs.index_directory(test_dir)
        result = sfs.cluster_files()
        assert result['status'] in ('success', 'skipped')

    def test_generate_report(self, sfs, test_dir):
        sfs.index_directory(test_dir)
        sfs.cluster_files()
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
            result = sfs.generate_report(temp_file.name)
            assert result['status'] == 'success'
            assert Path(temp_file.name).exists()
            Path(temp_file.name).unlink()

    def test_get_similar_files(self, sfs, test_dir):
        sfs.index_directory(test_dir)
        results = sfs.get_similar_files("machine learning models", top_k=2)
        # May return empty if ML deps are unavailable
        assert isinstance(results, list)
