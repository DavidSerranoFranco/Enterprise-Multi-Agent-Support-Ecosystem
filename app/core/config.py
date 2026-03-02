from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List

class Settings(BaseSettings):
    # Database
    database_url: str

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # LLM APIs
    google_api_key: str
    openai_api_key: str | None = None
    anthropic_api_key: str = ""

    # ChromaDB
    chroma_persist_directory: str = "./chroma_data"
    chroma_collection_name: str = "support_docs"

    # App Config
    secret_key: str
    debug: bool = False
    cors_origins: str = "http://localhost:3000"

    # Agent Config
    default_llm_model: str = "gpt-4-turbo-preview"
    embedding_model: str = "text-embedding-3-small"
    max_tokens: int = 4096
    temperature: float = 0.7

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"
        extra = "ignore"

@lru_cache()
def get_settings() -> Settings:
    return Settings()