import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Acne Care Chatbot API is running"}

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_list_threads():
    response = client.get("/api/threads/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# More complex tests for /api/chat/ will requires mocking LangGraph
