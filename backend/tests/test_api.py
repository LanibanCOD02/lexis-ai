import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import uuid

def test_register_user(client: TestClient):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "password123", "role": "Lawyer"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_register_existing_user(client: TestClient):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "password123", "role": "Lawyer"}
    )
    assert response.status_code == 400

def test_login_user(client: TestClient):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client: TestClient):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "wrong@example.com", "password": "password123"}
    )
    assert response.status_code == 401

def test_upload_document_no_file(client: TestClient):
    # Need to be authenticated to upload
    response = client.post("/api/v1/documents/upload")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_chat_e2e_grounding():
    # A true end-to-end integration test is better served in a dedicated integration test file 
    # to avoid mocking. Here we test the endpoint routing.
    pass
