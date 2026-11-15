import asyncio
import numpy as np
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.rag import Embedding, Chunk
from app.rag.faiss_index import VectorStore
import faiss

async def run_diagnostic():
    async with AsyncSessionLocal() as session:
        # Get all chunks
        result = await session.execute(select(Chunk))
        chunks = result.scalars().all()
        
        # Get all embeddings
        result = await session.execute(select(Embedding))
        embeddings_records = result.scalars().all()
        
        empty_chunks = sum(1 for c in chunks if not c.content or not c.content.strip())
        print(f"Total Chunks: {len(chunks)}")
        print(f"Empty Text Chunks: {empty_chunks}")
        
        faiss_index = VectorStore()
        
        print(f"FAISS Index Count: {faiss_index.index.ntotal}")
        print(f"FAISS Index Dimension: {faiss_index.index.d}")
        
        # Extract vectors to check uniqueness and norms
        vectors = []
        try:
            # For IndexIDMap, the underlying index is .index
            # Let's extract all vectors directly if possible
            if hasattr(faiss_index.index, 'index'):
                for i in range(faiss_index.index.ntotal):
                    vec = faiss_index.index.index.reconstruct(i)
                    vectors.append(vec)
            else:
                for i in range(faiss_index.index.ntotal):
                    vec = faiss_index.index.reconstruct(i)
                    vectors.append(vec)
        except Exception as e:
            print(f"Error extracting vectors: {e}")
        
        if not vectors:
            print("Could not reconstruct vectors directly. Assuming standard dim and norm.")
        else:
            vectors_arr = np.array(vectors)
            
            # Dimension
            print(f"Dimension (from vectors): {vectors_arr.shape[1]}")
            
            # Norms
            norms = np.linalg.norm(vectors_arr, axis=1)
            print(f"Average Norm: {np.mean(norms):.4f}")
            
            # Uniqueness
            unique_vectors = np.unique(vectors_arr, axis=0)
            print(f"Unique Embeddings: {len(unique_vectors)}")
            print(f"Duplicate Embeddings: {len(vectors_arr) - len(unique_vectors)}")
        
if __name__ == "__main__":
    asyncio.run(run_diagnostic())
