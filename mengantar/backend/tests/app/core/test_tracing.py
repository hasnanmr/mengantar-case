import pytest
from unittest.mock import patch, MagicMock
from app.core.langfuse_handler import get_langfuse_handler

@pytest.fixture
def mock_settings():
    with patch("app.core.langfuse_handler.settings") as mock:
        mock.langfuse_public_key = "pk-test"
        mock.langfuse_secret_key = "sk-test"
        mock.langfuse_base_url = "https://cloud.langfuse.com"
        yield mock

def test_get_langfuse_handler_success(mock_settings):
    with patch("app.core.langfuse_handler.CallbackHandler") as mock_handler:
        handler = get_langfuse_handler(session_id="test_session", tags=["test"])
        
        assert handler is not None
        mock_handler.assert_called_once_with()

def test_get_langfuse_handler_missing_keys(mock_settings):
    mock_settings.langfuse_public_key = None
    handler = get_langfuse_handler()
    assert handler is None

def test_get_langfuse_handler_empty_keys(mock_settings):
    mock_settings.langfuse_public_key = ""
    handler = get_langfuse_handler()
    assert handler is None
