from typing import List, Dict, Optional
from pathlib import Path
import sqlite3


class FileClusterer:
    def __init__(self, file_indexer):
        self.file_indexer = file_indexer
        self.cluster_model = None
        self.embedding_model = None
        
    def _ensure_models(self):
        if self.cluster_model is not None:
            return
        try:
            from sklearn.cluster import HDBSCAN
            from sentence_transformers import SentenceTransformer
            self.cluster_model = HDBSCAN(
                min_cluster_size=5,
                min_samples=2,
                metric='euclidean',
                cluster_selection_method='eom'
            )
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception:
            self.cluster_model = None
            self.embedding_model = None
        
    def cluster_files(self) -> Dict:
        """Cluster files based on their embeddings"""
        self._ensure_models()
        if self.cluster_model is None:
            return {'status': 'skipped', 'reason': 'ml_deps_unavailable', 'clusters_found': 0, 'file_paths': [], 'clusters': []}
        
        embeddings, file_paths = self._get_all_embeddings()
        
        if not embeddings:
            return {'status': 'success', 'clusters_found': 0, 'file_paths': [], 'clusters': []}
        
        try:
            import numpy as np
            embeddings_array = np.array(embeddings)
            
            # Reduce dimensionality for clustering
            if len(embeddings_array) > 10:
                try:
                    import umap.umap_ as umap
                    reducer = umap.UMAP(n_components=5, metric='cosine', n_neighbors=15, min_dist=0.1)
                    reduced_embeddings = reducer.fit_transform(embeddings_array)
                except Exception:
                    reduced_embeddings = embeddings_array
            else:
                reduced_embeddings = embeddings_array
                
            # Perform clustering
            clusters = self.cluster_model.fit_predict(reduced_embeddings)
            
            # Generate labels
            cluster_labels = self._generate_cluster_labels(
                reduced_embeddings, clusters, file_paths
            )
            
            return {
                'status': 'success',
                'clusters_found': len(set(clusters)) - (1 if -1 in clusters else 0),
                'file_paths': file_paths,
                'clusters': clusters.tolist(),
                'reduced_embeddings': reduced_embeddings.tolist(),
                'cluster_labels': cluster_labels
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e), 'clusters_found': 0, 'file_paths': [], 'clusters': []}
        
    def _get_all_embeddings(self):
        """Get all embeddings from the indexer"""
        try:
            import numpy as np
            import sqlite3
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
        except Exception:
            return None, None
            
    def _reduce_dimensionality(self, embeddings):
        """Reduce embedding dimensionality for clustering"""
        try:
            import umap.umap_ as umap
            reducer = umap.UMAP(
                n_components=5,
                metric='cosine',
                n_neighbors=15,
                min_dist=0.1
            )
            return reducer.fit_transform(embeddings)
        except Exception:
            return embeddings
        
    def _generate_cluster_labels(self, embeddings, clusters, file_paths):
        """Generate human-readable labels for each cluster"""
        try:
            import numpy as np
            cluster_labels = {}
            unique_clusters = set(clusters)
            
            for cluster_id in unique_clusters:
                if cluster_id == -1:
                    cluster_labels[cluster_id] = "Uncategorized"
                    continue
                    
                cluster_indices = np.where(clusters == cluster_id)[0]
                cluster_embeddings = embeddings[cluster_indices]
                centroid = np.mean(cluster_embeddings, axis=0)
                distances = np.linalg.norm(cluster_embeddings - centroid, axis=1)
                closest_idx = cluster_indices[np.argmin(distances)]
                representative_file = Path(file_paths[closest_idx]).name
                cluster_labels[cluster_id] = f"Cluster {cluster_id}: {representative_file}"
                
            return cluster_labels
        except Exception:
            return {}
        
    def visualize_clusters(self, clustering_results: Dict, save_path: Optional[str] = None):
        """Visualize clusters in 2D space"""
        try:
            import numpy as np
            from sklearn.manifold import TSNE
            import matplotlib.pyplot as plt
        except Exception:
            return
        reduced_embeddings = np.array(clustering_results['reduced_embeddings'])
        clusters = np.array(clustering_results['clusters'])
        
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
