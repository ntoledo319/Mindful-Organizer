import sqlite3
from pathlib import Path
import hashlib
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
import numpy as np
import json

class FileIndexer:
    def __init__(self, db_path: str = "file_index.db"):
        self.db_path = db_path
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self._init_db()
        
    def _init_db(self):
        """Initialize the SQLite database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create files table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT UNIQUE,
                    file_hash TEXT,
                    last_modified REAL,
                    size INTEGER,
                    file_type TEXT,
                    metadata TEXT,
                    embedding BLOB
                )
            ''')
            
            # Create indexes for faster queries
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_path ON files(path)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_file_type ON files(file_type)')
            conn.commit()
            
    def index_file(self, file_path: Path) -> bool:
        """Index a single file, storing its metadata and content embedding"""
        try:
            file_hash = self._calculate_file_hash(file_path)
            last_modified = file_path.stat().st_mtime
            size = file_path.stat().st_size
            file_type = file_path.suffix.lower()
            
            # Read and embed text content if it's a text file
            embedding = None
            metadata = {}
            
            if file_type in ['.txt', '.md', '.py', '.js', '.html', '.css', '.json']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    embedding = self._generate_embedding(content)
                    metadata['content_length'] = len(content)
                    metadata['lines'] = content.count('\n') + 1
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO files 
                    (path, file_hash, last_modified, size, file_type, metadata, embedding)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    str(file_path),
                    file_hash,
                    last_modified,
                    size,
                    file_type,
                    json.dumps(metadata),
                    embedding.tobytes() if embedding is not None else None
                ))
                conn.commit()
            return True
        except Exception as e:
            print(f"Error indexing file {file_path}: {e}")
            return False
            
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file contents"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()
        
    def _generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding vector for text content"""
        return self.embedding_model.encode(text)
        
    def get_file_embedding(self, file_path: str) -> Optional[np.ndarray]:
        """Retrieve embedding for a file"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT embedding FROM files WHERE path = ?', (file_path,))
            result = cursor.fetchone()
            if result and result[0]:
                return np.frombuffer(result[0], dtype=np.float32)
        return None
        
    def search_similar_files(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for files similar to the query text"""
        query_embedding = self._generate_embedding(query)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.create_function("cosine_sim", 2, self._cosine_similarity)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT path, cosine_sim(embedding, ?) as similarity 
                FROM files 
                WHERE embedding IS NOT NULL
                ORDER BY similarity DESC
                LIMIT ?
            ''', (query_embedding.tobytes(), top_k))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'path': row[0],
                    'similarity': row[1]
                })
            return results
            
    def _cosine_similarity(self, blob1: bytes, blob2: bytes) -> float:
        """SQLite function to calculate cosine similarity between embeddings"""
        vec1 = np.frombuffer(blob1, dtype=np.float32)
        vec2 = np.frombuffer(blob2, dtype=np.float32)
        return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))
