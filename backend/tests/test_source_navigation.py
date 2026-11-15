import pytest
from fastapi.testclient import TestClient
import uuid
import os
import asyncio
from app.db.session import AsyncSessionLocal
from app.models.core import Case, User
from app.models.rag import Document, Chunk
from app.core.security import get_password_hash

# Synchronous test functions using the provided 'client' fixture

def get_auth_token(client: TestClient):
    # Ensure user exists (ignoring errors if already exists)
    client.post("/api/v1/auth/register", json={
        "email": "navtest@example.com",
        "password": "password123",
        "role": "Lawyer"
    })
    resp = client.post("/api/v1/auth/login", data={"username": "navtest@example.com", "password": "password123"})
    if resp.status_code == 200:
        return resp.json()["access_token"]
    return ""

def test_citation_unauthorized(client: TestClient):
    """Test C: Unauthorized citation request -> 401/403"""
    chunk_id = str(uuid.uuid4())
    response = client.get(f"/api/v1/citations/{chunk_id}")
    assert response.status_code == 401

def test_pdf_unauthorized(client: TestClient):
    """Test F: Unauthorized PDF request -> 401/403"""
    doc_id = str(uuid.uuid4())
    response = client.get(f"/api/v1/documents/{doc_id}/file")
    assert response.status_code == 401

def test_citation_invalid_chunk(client: TestClient):
    """Test B: Invalid chunk UUID -> 404"""
    token = get_auth_token(client)
    chunk_id = str(uuid.uuid4())
    response = client.get(f"/api/v1/citations/{chunk_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404

def test_pdf_invalid_document(client: TestClient):
    """Test E: Invalid document -> 404"""
    token = get_auth_token(client)
    doc_id = str(uuid.uuid4())
    response = client.get(f"/api/v1/documents/{doc_id}/file", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404

def test_pdf_path_traversal(client: TestClient):
    """Test G: Path traversal attempt -> rejected (404/422)"""
    token = get_auth_token(client)
    response = client.get("/api/v1/documents/../../../etc/passwd/file", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code in (404, 422)

@pytest.mark.asyncio
async def test_valid_citation_and_pdf(client: TestClient):
    """
    Test A: Valid citation -> 200
    Test D: Valid document PDF -> 200 PDF response
    Test H: Correct mapping (citation UUID -> Chunk -> Document -> Case -> page_number)
    Test I: Source content corresponds to actual Chunk.content.
    """
    # Create test data directly with a fresh DB session
    from tests.conftest import TestingSessionLocal
    
    import tempfile
    fd, temp_path = tempfile.mkstemp(suffix=".pdf")
    with os.fdopen(fd, 'w') as f:
        f.write("%PDF-1.4 dummy content")
    
    from datetime import date
    from app.models.core import Court
    import uuid
    async with TestingSessionLocal() as session:
        court = Court(name=f"Court {uuid.uuid4()}")
        session.add(court)
        await session.commit()
        await session.refresh(court)
        test_case = Case(title="Test Case Navigation", case_number="TEST-123", decision_date=date(2024, 1, 1), court_id=court.id)
        session.add(test_case)
        await session.commit()
        await session.refresh(test_case)
        
        test_doc = Document(case_id=test_case.id, file_path=temp_path, checksum="test", document_type="judgment")
        session.add(test_doc)
        await session.commit()
        await session.refresh(test_doc)
        
        chunk_content = "Case: Test, Court: SC, Page: 48\n---\nHere is the actual passage."
        test_chunk = Chunk(document_id=test_doc.id, content=chunk_content, chunk_index=0, token_count=10)
        session.add(test_chunk)
        await session.commit()
        await session.refresh(test_chunk)
        
        chunk_id = str(test_chunk.id)
        doc_id = str(test_doc.id)
        case_id = str(test_case.id)

    token = get_auth_token(client)
    
    # Test A, H, I: Citation lookup
    response = client.get(f"/api/v1/citations/{chunk_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["chunk_id"] == chunk_id
    assert data["document_id"] == doc_id
    assert data["case_id"] == case_id
    assert data["page_number"] == 48  # Parsed correctly
    assert data["content"] == chunk_content # Corresponds exactly
    
    # Test D: Document file download
    response_pdf = client.get(f"/api/v1/documents/{doc_id}/file", headers={"Authorization": f"Bearer {token}"})
    assert response_pdf.status_code == 200
    assert response_pdf.headers["content-type"] == "application/pdf"
    assert "%PDF-1.4 dummy content" in response_pdf.text
    
    os.remove(temp_path)
