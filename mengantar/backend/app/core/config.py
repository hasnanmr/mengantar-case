from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    openrouter_api_key: str
    llm_model: str = "qwen/qwen3-32b"
    embedding_model: str = "Qwen/Qwen3-Embedding-8B"
    sqlite_db_path: str = "./data/chatbot.db"
    faiss_index_path: str = "./data/faiss_index"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
