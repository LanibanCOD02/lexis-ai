import pytest
import numpy as np
from app.rag.embedder import DocumentEmbedder

def test_embedder_valid_input():
    embedder = DocumentEmbedder()
    chunks = [
        {"content": "The court awarded damages of ₹10 lakh."},
        {"content": "The arbitration agreement was enforceable."}
    ]
    
    results = embedder.embed_chunks(chunks)
    
    assert len(results) == 2
    assert "embedding" in results[0]
    assert "embedding" in results[1]
    
    emb1 = np.array(results[0]["embedding"])
    emb2 = np.array(results[1]["embedding"])
    
    # Ensure they are not identical
    assert not np.allclose(emb1, emb2)
    
    # Check that they aren't the empty string embedding
    empty_result = embedder.model.encode([""])
    assert not np.allclose(emb1, empty_result[0])
    assert not np.allclose(emb2, empty_result[0])

def test_embedder_mismatch_key_fails():
    embedder = DocumentEmbedder()
    
    # This simulates the old bug where "text" was passed instead of "content"
    chunks = [
        {"text": "The court awarded damages of ₹10 lakh."}
    ]
    
    with pytest.raises(ValueError, match="missing the 'content' field"):
        embedder.embed_chunks(chunks)

def test_embedder_empty_content_fails():
    embedder = DocumentEmbedder()
    
    chunks = [
        {"content": "   "}
    ]
    
    with pytest.raises(ValueError, match="empty or invalid 'content'"):
        embedder.embed_chunks(chunks)
