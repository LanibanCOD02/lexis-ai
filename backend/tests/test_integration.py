import pytest
import os
import uuid
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from app.main import app
from tests.conftest import TestingSessionLocal
from app.models.core import User, Case, Court
from app.models.rag import Document, Chunk, Embedding
from app.rag.embedder import DocumentEmbedder
from app.rag.faiss_index import VectorStore
import datetime

def test_full_rag_grounding_integration(client: TestClient):
    """
    End-to-End integration test covering:
    - User Registration & Login
    - Manual Chunk insertion mimicking a processed PDF
    - Embedding and FAISS indexing
    - Chat querying mapping FAISS -> SQL -> Gemini
    """
    # 1. Register User
    res = client.post(
        "/api/v1/auth/register",
        json={"email": "ragtest@example.com", "password": "password123", "role": "Lawyer"}
    )
    assert res.status_code == 200
    
    # 2. Login User
    res = client.post(
        "/api/v1/auth/login",
        data={"username": "ragtest@example.com", "password": "password123"}
    )
    assert res.status_code == 200
    token = res.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    async def _setup_db():
        async with TestingSessionLocal() as session:
            court = Court(name="Test Court", jurisdiction="Test")
            session.add(court)
            await session.flush()
            
            case = Case(
                title="Test Commercial Contract Case",
                case_number="TEST-001",
                decision_date=datetime.date(2026, 1, 1),
                court_id=court.id,
                status="Processed"
            )
            session.add(case)
            await session.flush()
            
            doc = Document(
                id=uuid.uuid4(),
                case_id=case.id,
                file_path="dummy/path.pdf",
                checksum="dummy_checksum_123",
                document_type="PDF"
            )
            session.add(doc)
            await session.flush()
            
            chunk = Chunk(
                document_id=doc.id,
                content="The court awarded damages of ₹10 lakh.",
                chunk_index=0,
                token_count=10
            )
            session.add(chunk)
            await session.flush()
            
            # 4. Generate Embedding and add to FAISS
            embedder = DocumentEmbedder()
            embedded_chunk = embedder.embed_chunks([{"content": chunk.content, "metadata": {}}])[0]
            
            faiss_id = str(uuid.uuid4())
            vstore = VectorStore()
            vstore.add_vectors([embedded_chunk["embedding"]], [faiss_id])
            
            embedding = Embedding(
                chunk_id=chunk.id,
                model_used="test-embedder",
                faiss_vector_id=faiss_id
            )
            session.add(embedding)
            await session.commit()
            
    asyncio.run(_setup_db())
    
    # 5. Execute Chat Query mapping FAISS -> SQL Chunk -> LLM
    with patch("app.rag.providers.genai.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "The court awarded damages of ₹10 lakh based on the provided document. [citations]"
        mock_response.usage_metadata.prompt_token_count = 10
        mock_response.usage_metadata.candidates_token_count = 10
        mock_response.usage_metadata.total_token_count = 20
        mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client
        
        res = client.post(
            "/api/v1/chat/",
            json={"query": "What damages were awarded?"},
            headers=headers
        )
        assert res.status_code == 200
        data = res.json()
        
        # 6. Verify retrieved context
        call_kwargs = mock_client.aio.models.generate_content.call_args.kwargs
        assert "The court awarded damages of ₹10 lakh." in call_kwargs["contents"]
        
        # Verify answer and citation
        assert "₹10 lakh" in data["answer"]
