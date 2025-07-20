from pathlib import Path
from typing import Dict, List, Optional
from .file_indexer import FileIndexer
from .file_clusterer import FileClusterer
from .hardware_optimizer import HardwareOptimizer
from .output_generator import OutputGenerator
import time
import logging

class SmartFileSystem:
    def __init__(self, db_path: str = "file_index.db"):
        self.logger = logging.getLogger(__name__)
        self.hardware_optimizer = HardwareOptimizer()
        self.file_indexer = FileIndexer(db_path)
        self.file_clusterer = FileClusterer(self.file_indexer)
        self.output_generator = None
        
        # Apply hardware optimizations
        self._apply_hardware_optimizations()
        
    def _apply_hardware_optimizations(self):
        """Apply hardware-specific optimizations"""
        recommendations = self.hardware_optimizer.optimize_for_ai()
        self.logger.info(f"Applied hardware optimizations: {recommendations}")
        
    def index_directory(self, directory_path: str) -> Dict:
        """Index all files in a directory"""
        start_time = time.time()
        path = Path(directory_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
            
        file_count = 0
        for file_path in path.rglob('*'):
            if file_path.is_file():
                if self.file_indexer.index_file(file_path):
                    file_count += 1
                    
        return {
            'status': 'success',
            'files_indexed': file_count,
            'time_elapsed': time.time() - start_time
        }
        
    def cluster_files(self) -> Dict:
        """Cluster all indexed files"""
        start_time = time.time()
        clustering_results = self.file_clusterer.cluster_files()
        
        if clustering_results['status'] == 'error':
            return clustering_results
            
        self.output_generator = OutputGenerator(clustering_results)
        
        return {
            'status': 'success',
            'clusters_found': len(set(clustering_results['clusters'])) - 1,
            'time_elapsed': time.time() - start_time
        }
        
    def generate_report(self, output_path: str, format: str = 'json') -> Dict:
        """Generate a report of file clusters"""
        if not self.output_generator:
            return {'status': 'error', 'message': 'Must cluster files first'}
            
        try:
            self.output_generator.save_report(output_path, format)
            return {'status': 'success', 'output_path': output_path}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
            
    def visualize_clusters(self, output_path: Optional[str] = None) -> Dict:
        """Generate visualization of file clusters"""
        if not self.output_generator:
            return {'status': 'error', 'message': 'Must cluster files first'}
            
        try:
            self.output_generator.generate_cluster_visualization(output_path)
            return {
                'status': 'success',
                'output_path': output_path if output_path else 'displayed'
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
            
    def get_similar_files(self, query: str, top_k: int = 5) -> List[Dict]:
        """Find files similar to the query text"""
        return self.file_indexer.search_similar_files(query, top_k)
        
    def get_file_metadata(self, file_path: str) -> Optional[Dict]:
        """Get metadata for a specific file"""
        return self.file_indexer.get_file_metadata(file_path)
