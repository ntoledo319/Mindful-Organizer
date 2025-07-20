import numpy as np
from typing import List, Dict, Optional
from sklearn.cluster import HDBSCAN
from sklearn.manifold import TSNE
from sentence_transformers import SentenceTransformer
from .file_indexer import FileIndexer
import umap.umap_ as umap
import matplotlib.pyplot as plt
import json
from pathlib import Path

class FileClusterer:
    def __init__(self, file_indexer: FileIndexer):
        self.file_indexer = file_indexer
        self.cluster_model = HDBSCAN(
            min_cluster_size=5,
            min_samples=2,
            metric='euclidean',
            cluster_selection_method='eom'
        )
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
    def cluster_files(self) -> Dict:
        """Cluster files based on their embeddings"""
        # Get all embeddings from the indexer
        embeddings, file_paths = self._get_all_embeddings()
        
        if not embeddings:
            return {'status': 'error', 'message': 'No embeddings found'}
            
        # Reduce dimensionality for clustering
        reduced_embeddings = self._reduce_dimensionality(embeddings)
        
        # Perform clustering
        clusters = self.cluster_model.fit_predict(reduced_embeddings)
        
        # Generate cluster labels
        cluster_labels = self._generate_cluster_labels(embeddings, clusters, file_paths)
        
        # Save clustering results
        clustering_results = {
            'file_paths': file_paths,
            'clusters': clusters.tolist(),
            'cluster_labels': cluster_labels,
            'reduced_embeddings': reduced_embeddings.tolist()
        }
        
        return clustering_results
        
    def _get_all_embeddings(self):
        """Retrieve all embeddings and corresponding file paths from indexer"""
        with sqlite3.connect(self.file_indexer.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT path, embedding FROM files WHERE embedding IS NOT NULL')
            results = cursor.fetchall()
            
            if not results:
                return None, None
                
            file_paths = []
            embeddings = []
            for path, embedding_blob in results:
                file_paths.append(path)
                embeddings.append(np.frombuffer(embedding_blob, dtype=np.float32))
                
            return np.array(embeddings), file_paths
            
    def _reduce_dimensionality(self, embeddings: np.ndarray) -> np.ndarray:
        """Reduce embedding dimensionality for clustering"""
        reducer = umap.UMAP(
            n_components=5,
            metric='cosine',
            n_neighbors=15,
            min_dist=0.1
        )
        return reducer.fit_transform(embeddings)
        
    def _generate_cluster_labels(self, embeddings: np.ndarray, 
                               clusters: np.ndarray, 
                               file_paths: List[str]) -> Dict[int, str]:
        """Generate human-readable labels for each cluster"""
        # Get representative samples for each cluster
        cluster_labels = {}
        unique_clusters = set(clusters)
        
        for cluster_id in unique_clusters:
            if cluster_id == -1:
                cluster_labels[cluster_id] = "Uncategorized"
                continue
                
            # Get indices of files in this cluster
            cluster_indices = np.where(clusters == cluster_id)[0]
            cluster_embeddings = embeddings[cluster_indices]
            
            # Calculate centroid
            centroid = np.mean(cluster_embeddings, axis=0)
            
            # Find file closest to centroid
            distances = np.linalg.norm(cluster_embeddings - centroid, axis=1)
            closest_idx = cluster_indices[np.argmin(distances)]
            representative_file = Path(file_paths[closest_idx]).name
            
            # Generate label based on representative file
            cluster_labels[cluster_id] = f"Cluster {cluster_id}: {representative_file}"
            
        return cluster_labels
        
    def visualize_clusters(self, clustering_results: Dict, save_path: Optional[str] = None):
        """Visualize clusters in 2D space"""
        reduced_embeddings = np.array(clustering_results['reduced_embeddings'])
        clusters = np.array(clustering_results['clusters'])
        
        # Reduce to 2D for visualization
        tsne = TSNE(n_components=2, random_state=42)
        embeddings_2d = tsne.fit_transform(reduced_embeddings)
        
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
