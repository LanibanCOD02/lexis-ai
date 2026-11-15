"""
FAISS Vector Database module.
Handles storing, retrieving, and persisting semantic vector embeddings.
"""
import os
import logging
import hashlib
import json
from typing import List, Tuple, Dict, Any

try:
    import faiss
    import numpy as np
except ImportError:
    faiss = None
    np = None

logger = logging.getLogger(__name__)

# all-mpnet-base-v2 vector dimension
VECTOR_DIMENSION = 768

def _uuid_to_int64(uuid_str: str) -> int:
    """
    Converts a UUID string to a deterministic signed 64-bit integer for FAISS.
    FAISS natively requires int64 for mapped IDs.
    """
    # MD5 is fast and deterministic. We take the first 16 hex chars (64 bits).
    hex_64 = hashlib.md5(str(uuid_str).encode('utf-8')).hexdigest()[:16]
    # Convert to int and shift to signed space (since faiss uses int64)
    return int(hex_64, 16) - (1 << 63)

class VectorStore:
    """
    Wrapper for FAISS vector index.
    """
    def __init__(self, dimension: int = VECTOR_DIMENSION, index_path: str = "storage/vector_store.faiss"):
        """
        Initializes the FAISS index (IndexFlatL2 for exact search).
        
        Args:
            dimension (int): The dimensionality of the vectors.
            index_path (str): The file path to persist the FAISS index on disk.
        """
        if faiss is None:
            raise ImportError("faiss-cpu or numpy is not installed.")
            
        self.dimension = dimension
        self.index_path = index_path
        self.index = None
        self.id_map = {}  # In-memory lookup: FAISS int64 -> SQL UUID
        self._load_or_create_index()

    def _load_or_create_index(self):
        """Loads an existing index from disk or creates a new one."""
        if os.path.exists(self.index_path):
            try:
                self.index = faiss.read_index(self.index_path)
                logger.info(f"Loaded FAISS index from {self.index_path} with {self.index.ntotal} vectors.")
                
                # Load id_map
                map_path = self.index_path + ".map.json"
                if os.path.exists(map_path):
                    with open(map_path, "r") as f:
                        loaded_map = json.load(f)
                        self.id_map = {int(k): v for k, v in loaded_map.items()}
            except Exception as e:
                logger.error(f"Failed to load FAISS index: {e}")
                self._create_new_index()
        else:
            self._create_new_index()

    def _create_new_index(self):
        """Creates a fresh IndexIDMap wrapped around IndexFlatL2."""
        self.index = faiss.IndexIDMap(faiss.IndexFlatL2(self.dimension))
        logger.info(f"Created new FAISS IndexFlatL2 with dimension {self.dimension}.")

    def add_vectors(self, embeddings: List[List[float]], vector_ids: List[str]) -> None:
        """
        Adds multiple vectors to the FAISS index.
        
        Args:
            embeddings (List[List[float]]): A list of dense vector arrays.
            vector_ids (List[str]): Unique string IDs (SQL Primary Keys).
        """
        if not embeddings or not vector_ids:
            return
            
        if len(embeddings) != len(vector_ids):
            raise ValueError("Number of embeddings must match number of vector_ids.")
            
        np_vectors = np.array(embeddings).astype('float32')
        
        int_ids = []
        for vid in vector_ids:
            int_id = _uuid_to_int64(vid)
            int_ids.append(int_id)
            self.id_map[int_id] = vid
            
        np_ids = np.array(int_ids).astype('int64')
        
        self.index.add_with_ids(np_vectors, np_ids)
        logger.info(f"Added {len(embeddings)} vectors to FAISS index.")
        self.save_index()

    def search(self, query_vector: List[float], top_k: int = 50) -> List[Tuple[str, float]]:
        """
        Searches the FAISS index for the Top-K most similar vectors.
        
        Args:
            query_vector (List[float]): The embedded user query.
            top_k (int): Number of results to return.
            
        Returns:
            List[Tuple[str, float]]: A list of tuples containing (Original SQL UUID String, L2 Distance).
        """
        if self.index.ntotal == 0:
            return []
            
        np_query = np.array([query_vector]).astype('float32')
        distances, indices = self.index.search(np_query, top_k)
        
        results = []
        for i in range(len(indices[0])):
            int_id = indices[0][i]
            if int_id != -1:  # -1 means not found (if less than top_k exist)
                # Reverse mapping to original SQL UUID if available
                # In production, the DB should also be queried to verify the FAISS mapping
                str_id = self.id_map.get(int_id, str(int_id))
                results.append((str_id, float(distances[0][i])))
                
        return results

    def save_index(self):
        """Persists the index to disk to prevent re-indexing on reboot."""
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        
        map_path = self.index_path + ".map.json"
        with open(map_path, "w") as f:
            json.dump(self.id_map, f)
            
        logger.info(f"Saved FAISS index to {self.index_path}.")
