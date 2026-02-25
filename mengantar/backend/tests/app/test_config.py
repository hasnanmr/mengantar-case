import pytest
from pydantic import ValidationError
from app.core.config import Settings

def test_settings_validation():
    # Valid settings
    settings = Settings(openrouter_api_key="sk-123")
    assert settings.openrouter_api_key == "sk-123"
    assert settings.log_level == "INFO"

    # Missing API key should raise error
    with pytest.raises(ValidationError):
        Settings(openrouter_api_key="")

def test_get_settings_lru():
    from app.core.config import get_settings
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2
