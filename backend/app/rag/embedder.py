"""
Embedding generation module.
Uses SentenceTransformers to vectorize chunked text for FAISS ingestion.
"""
import logging
from typing import List, Dict, Any

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

logger = logging.getLogger(__name__)

# Standard legal RAG model recommendation from architecture
MODEL_NAME = "all-mpnet-base-v2"
DEFAULT_BATCH_SIZE = 32

class DocumentEmbedder:
    """
    Generates dense embeddings for text chunks using SentenceTransformers.
    """
    def __init__(self, model_name: str = MODEL_NAME):
        """
        Initializes the embedding model.
        
        Args:
            model_name (str): The huggingface model identifier.
        """
        if SentenceTransformer is None:
            raise ImportError("sentence-transformers is not installed.")
            
        self.model_name = model_name
        logger.info(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        
    def embed_chunks(self, chunks: List[Dict[str, Any]], batch_size: int = DEFAULT_BATCH_SIZE) -> List[Dict[str, Any]]:
        """
        Generates vectors for a list of text chunks in batches to prevent OOM.
        
        Args:
            chunks (List[Dict[str, Any]]): A list of chunk dictionaries containing 'content'.
            batch_size (int): Number of chunks to process simultaneously.
            
        Returns:
            List[Dict[str, Any]]: The chunks augmented with an 'embedding' array and 'model_used'.
        """
        if not chunks:
            return []
            
        texts = []
        for i, chunk in enumerate(chunks):
            if "content" not in chunk:
                raise ValueError(f"Chunk at index {i} is missing the 'content' field.")
            
            text = chunk["content"]
            if not isinstance(text, str) or not text.strip():
                raise ValueError(f"Chunk at index {i} has empty or invalid 'content'.")
                
            texts.append(text)
        
        try:
            logger.info(f"Generating embeddings for {len(texts)} chunks in batches of {batch_size}...")
            # encode() returns a numpy array or torch tensor, convert to list for generic storage/JSON
            vectors = self.model.encode(texts, batch_size=batch_size, show_progress_bar=False)
            
            for i, chunk in enumerate(chunks):
                chunk["embedding"] = vectors[i].tolist()
                chunk["model_used"] = self.model_name
                
            return chunks
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise
