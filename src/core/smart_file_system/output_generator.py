from typing import Dict, List, Optional
import json
from pathlib import Path
import matplotlib.pyplot as plt
from datetime import datetime

class OutputGenerator:
    def __init__(self, clustering_results: Dict):
        self.clustering_results = clustering_results
        
    def generate_cluster_report(self) -> Dict:
        """Generate a detailed report of file clusters"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_files': len(self.clustering_results['file_paths']),
            'total_clusters': len(set(self.clustering_results['clusters'])) - 1,  # exclude noise
            'cluster_details': []
        }
        
        # Calculate stats for each cluster
        cluster_counts = {}
        for cluster_id in set(self.clustering_results['clusters']):
            count = self.clustering_results['clusters'].count(cluster_id)
            cluster_counts[cluster_id] = count
            
        # Add details for each cluster
        for cluster_id, count in cluster_counts.items():
            report['cluster_details'].append({
                'cluster_id': cluster_id,
                'label': self.clustering_results['cluster_labels'].get(cluster_id, 'Unlabeled'),
                'file_count': count,
                'example_files': self._get_example_files(cluster_id, 3)
            })
            
        return report
        
    def _get_example_files(self, cluster_id: int, count: int = 3) -> List[str]:
        """Get example files from a cluster"""
        examples = []
        for i, cid in enumerate(self.clustering_results['clusters']):
            if cid == cluster_id:
                examples.append(Path(self.clustering_results['file_paths'][i]).name)
                if len(examples) >= count:
                    break
        return examples
        
    def save_report(self, file_path: str, format: str = 'json'):
        """Save cluster report to file"""
        report = self.generate_cluster_report()
        
        if format == 'json':
            with open(file_path, 'w') as f:
                json.dump(report, f, indent=2)
        elif format == 'txt':
            with open(file_path, 'w') as f:
                f.write(self._format_text_report(report))
        else:
            raise ValueError(f"Unsupported format: {format}")
            
    def _format_text_report(self, report: Dict) -> str:
        """Format report as human-readable text"""
        text = f"File Cluster Report - {report['timestamp']}\n"
        text += f"Total Files: {report['total_files']}\n"
        text += f"Total Clusters: {report['total_clusters']}\n\n"
        
        for cluster in report['cluster_details']:
            text += f"Cluster {cluster['cluster_id']}: {cluster['label']}\n"
            text += f"  Files: {cluster['file_count']}\n"
            text += "  Examples:\n"
            for example in cluster['example_files']:
                text += f"    - {example}\n"
            text += "\n"
            
        return text
        
    def generate_cluster_visualization(self, save_path: Optional[str] = None):
        """Generate and optionally save a visualization of clusters"""
        if 'reduced_embeddings' not in self.clustering_results:
            raise ValueError("Clustering results do not contain reduced embeddings")
            
        # Convert to numpy arrays
        embeddings = np.array(self.clustering_results['reduced_embeddings'])
        clusters = np.array(self.clustering_results['clusters'])
        
        # Reduce to 2D for visualization
        tsne = TSNE(n_components=2, random_state=42)
        embeddings_2d = tsne.fit_transform(embeddings)
        
        plt.figure(figsize=(12, 8))
        scatter = plt.scatter(
            embeddings_2d[:, 0], 
            embeddings_2d[:, 1],
            c=clusters,
            cmap='Spectral',
            alpha=0.7
        )
        
        plt.colorbar(scatter)
        plt.title("File Clusters Visualization")
        
        if save_path:
            plt.savefig(save_path)
            plt.close()
        else:
            plt.show()
