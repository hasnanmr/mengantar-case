import os
from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    openrouter_api_key: str = Field(..., min_length=1)
    llm_model: str = "qwen/qwen3-32b"
    embedding_model: str = "Qwen/Qwen3-Embedding-8B"
    database_url: str = "postgresql://postgres:postgres@localhost:5432/postgres"
    faiss_index_path: str = "./data/faiss_index"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    langfuse_public_key: str = Field(default="")
    langfuse_secret_key: str = Field(default="")
    langfuse_base_url: str = "https://us.cloud.langfuse.com"
    log_level: str = "INFO"
    environment: str = "production"

    model_config = ConfigDict(env_file=".env")


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    
    # Set OpenTelemetry resource attributes before Langfuse is initialized
    os.environ.setdefault(
        "OTEL_RESOURCE_ATTRIBUTES",
        f"service.name=acne-care-chatbot,"
        f"service.version=1.0.0,"
        f"deployment.environment={settings.environment}"
    )
    
    return settings
