import pytest
from fastapi.testclient import TestClient
import uuid
import os

from app.db.session import AsyncSessionLocal
from app.models.core import Case
from app.models.rag import Document, Chunk, Embedding
from app.rag.faiss_index import _uuid_to_int64

def get_auth_token(client: TestClient):
    client.post("/api/v1/auth/register", json={
        "email": "similartest@example.com",
        "password": "password123",
        "role": "Lawyer"
    })
    resp = client.post("/api/v1/auth/login", data={"username": "similartest@example.com", "password": "password123"})
    if resp.status_code == 200:
        return resp.json()["access_token"]
    return ""

@pytest.mark.asyncio
async def test_similar_cases(client: TestClient):
    # Setup Data
    from tests.conftest import TestingSessionLocal
    from datetime import date
    from app.models.core import Court
    import uuid
    
    async with TestingSessionLocal() as session:
        court = Court(name=f"Court {uuid.uuid4()}")
        session.add(court)
        await session.commit()
        await session.refresh(court)
        
        case_a = Case(title="Case A", case_number="A-1", decision_date=date(2024, 1, 1), court_id=court.id)
        case_b = Case(title="Case B", case_number="B-1", decision_date=date(2024, 1, 2), court_id=court.id)
        case_c = Case(title="Case C", case_number="C-1", decision_date=date(2024, 1, 3), court_id=court.id)
        session.add_all([case_a, case_b, case_c])
        await session.commit()
        await session.refresh(case_a)
        await session.refresh(case_b)
        await session.refresh(case_c)
        
        doc_a = Document(case_id=case_a.id, file_path="a.pdf", checksum="a", document_type="judgment")
        doc_b = Document(case_id=case_b.id, file_path="b.pdf", checksum="b", document_type="judgment")
        doc_c = Document(case_id=case_c.id, file_path="c.pdf", checksum="c", document_type="judgment")
        session.add_all([doc_a, doc_b, doc_c])
        await session.commit()
        
        chunk_a1 = Chunk(document_id=doc_a.id, content="Page: 1\n---\nApple banana orange.", chunk_index=0, token_count=3)
        chunk_b1 = Chunk(document_id=doc_b.id, content="Page: 2\n---\nApple banana pear.", chunk_index=0, token_count=3)
        chunk_b2 = Chunk(document_id=doc_b.id, content="Page: 3\n---\nApple banana grape.", chunk_index=1, token_count=3)
        chunk_c1 = Chunk(document_id=doc_c.id, content="Page: 4\n---\nCar truck vehicle.", chunk_index=0, token_count=3)
        session.add_all([chunk_a1, chunk_b1, chunk_b2, chunk_c1])
        await session.commit()
        
        # We manually add FAISS embeddings to simulate FAISS index matches
        emb_a1 = Embedding(chunk_id=chunk_a1.id, faiss_vector_id=_uuid_to_int64(str(chunk_a1.id)), model_used="all-mpnet-base-v2")
        emb_b1 = Embedding(chunk_id=chunk_b1.id, faiss_vector_id=_uuid_to_int64(str(chunk_b1.id)), model_used="all-mpnet-base-v2")
        emb_b2 = Embedding(chunk_id=chunk_b2.id, faiss_vector_id=_uuid_to_int64(str(chunk_b2.id)), model_used="all-mpnet-base-v2")
        emb_c1 = Embedding(chunk_id=chunk_c1.id, faiss_vector_id=_uuid_to_int64(str(chunk_c1.id)), model_used="all-mpnet-base-v2")
        session.add_all([emb_a1, emb_b1, emb_b2, emb_c1])
        await session.commit()
        
        # Need to mock VectorStore to return specific matches since we don't really want to run real FAISS logic here
        from unittest.mock import patch
        with patch('app.api.endpoints.cases.VectorStore') as MockVectorStore:
            mock_vstore_instance = MockVectorStore.return_value
            # We pretend the query for case_a matches chunk_b1, chunk_b2, and chunk_c1
            # FAISS results are list of (faiss_vector_id, distance)
            mock_vstore_instance.search.return_value = [
                (str(_uuid_to_int64(str(chunk_b1.id))), 0.2), # Best match for B
                (str(_uuid_to_int64(str(chunk_b2.id))), 0.4), # Worse match for B
                (str(_uuid_to_int64(str(chunk_a1.id))), 0.1), # Match for A (should be excluded)
                (str(_uuid_to_int64(str(chunk_c1.id))), 1.0)  # Match for C
            ]
            
            token = get_auth_token(client)
            headers = {"Authorization": f"Bearer {token}"}
            
            # 1. Valid case returns 200
            res = client.get(f"/api/v1/cases/{str(case_a.id)}/similar?limit=5", headers=headers)
            assert res.status_code == 200
            data = res.json()
            
            # 4. Current case is excluded (Case A shouldn't be here)
            similar = data["similar_cases"]
            assert not any(c["case_id"] == str(case_a.id) for c in similar)
            
            # 5. Multiple chunks from one case become one result (Case B should appear once)
            assert sum(1 for c in similar if c["case_id"] == str(case_b.id)) == 1
            
            # 6. Best matching chunk is retained (Chunk B1 is the best for B)
            b_case = next(c for c in similar if c["case_id"] == str(case_b.id))
            assert b_case["matched_chunks"][0]["chunk_id"] == str(chunk_b1.id)
            assert b_case["matched_chunks"][0]["page_number"] == 2
            
            # 12. Excerpts exactly correspond to stored SQL chunk content (metadata stripped)
            assert b_case["matched_chunks"][0]["excerpt"] == "Apple banana pear."
            
            # 10. Similarity score calculation is correct
            # dist = 0.2 -> score = 1.0 - (0.2 / 2.0) = 0.9
            assert b_case["similarity_score"] == 0.9
            assert b_case["distance"] == 0.2
            
            # Ranking follows distance
            assert similar[0]["case_id"] == str(case_b.id)
            assert similar[1]["case_id"] == str(case_c.id)
            
            # 7 & 8 & 9 Limit testing
            res = client.get(f"/api/v1/cases/{str(case_a.id)}/similar?limit=1", headers=headers)
            assert len(res.json()["similar_cases"]) == 1
            
            res = client.get(f"/api/v1/cases/{str(case_a.id)}/similar?limit=20", headers=headers)
            assert len(res.json()["similar_cases"]) <= 10 # Enforced max 10
            
            # 2. Invalid case returns 404
            res = client.get(f"/api/v1/cases/{str(uuid.uuid4())}/similar", headers=headers)
            assert res.status_code == 404
            
            # 3. Authentication is enforced
            res = client.get(f"/api/v1/cases/{str(case_a.id)}/similar")
            assert res.status_code == 401
            
            # 11. Empty corpus safely returns
            mock_vstore_instance.search.return_value = []
            res = client.get(f"/api/v1/cases/{str(case_a.id)}/similar", headers=headers)
            assert res.status_code == 200
            assert res.json()["similar_cases"] == []
