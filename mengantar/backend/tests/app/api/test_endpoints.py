from unittest.mock import patch, MagicMock, AsyncMock
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
    with patch("app.api.threads.get_pool") as mock_get_pool:
        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()
        mock_cursor.fetchall.return_value = [("thread1", "check1")]
        
        # cursor() is a sync method that returns an async context manager
        mock_conn.cursor = MagicMock()
        mock_conn.cursor.return_value.__aenter__.return_value = mock_cursor
        
        mock_pool.connection.return_value.__aenter__.return_value = mock_conn
        mock_get_pool.return_value = mock_pool
        
        response = client.get("/api/threads/")
        assert response.status_code == 200
        assert isinstance(response.json()["threads"], list)
        assert response.json()["threads"] == [{"thread_id": "thread1", "last_checkpoint": "check1"}]

# More complex tests for /api/chat/ will requires mocking LangGraph
