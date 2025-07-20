import pytest
from pathlib import Path
import tempfile
import shutil
from src.core.smart_file_system import SmartFileSystem

class TestSmartFileSystem:
    @pytest.fixture
    def test_dir(self):
        # Create a temporary directory with test files
        temp_dir = tempfile.mkdtemp()
        
        # Create some test files with different content
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
        return SmartFileSystem(db_path=":memory:")
        
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
        assert result['status'] == 'success'
        assert result['clusters_found'] > 0
        
    def test_generate_report(self, sfs, test_dir):
        sfs.index_directory(test_dir)
        sfs.cluster_files()
        
        with tempfile.NamedTemporaryFile(suffix='.json') as temp_file:
            result = sfs.generate_report(temp_file.name)
            assert result['status'] == 'success'
            assert Path(temp_file.name).exists()
            
    def test_get_similar_files(self, sfs, test_dir):
        sfs.index_directory(test_dir)
        results = sfs.get_similar_files("machine learning models", top_k=2)
        assert len(results) == 2
        assert any('doc1.txt' in r['path'] for r in results)
