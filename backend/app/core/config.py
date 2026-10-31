"""Core configuration for BolnaAI backend."""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    APP_NAME: str = "BolnaAI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_PREFIX: str = "/api/v1"

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    DATABASE_URL: str = "sqlite:///./legalai.db"
    CHROMA_PERSIST_DIR: str = "../vector_db"
    CHROMA_COLLECTION_NAME: str = "legal_documents"

    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    LLM_PROVIDER: str = "gemini"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    HUGGINGFACE_API_KEY: str = ""
    VAPI_API_KEY: str = ""
    VAPI_PUBLIC_KEY: str = ""
    VAPI_ASSISTANT_ID: str = ""
    VAPI_WEBHOOK_SECRET: str = ""

    TESSERACT_CMD: str = "tesseract"
    OCR_LANGUAGE: str = "eng"

    MAX_UPLOAD_SIZE_MB: int = 50
    UPLOAD_DIR: str = "../uploads"
    ALLOWED_EXTENSIONS: str = ".pdf,.docx,.txt,.png,.jpg,.jpeg,.tiff,.bmp"

    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RESULTS: int = 5
    SIMILARITY_THRESHOLD: float = 0.3

    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, value):
        """Accept common bool strings and ignore unrelated host log-level values."""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {"true", "1", "yes", "on"}:
                return True
            if lowered in {"false", "0", "no", "off"}:
                return False
            return True
        return value

    @property
    def allowed_extensions_list(self) -> List[str]:
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(",")]

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def upload_path(self) -> Path:
        path = self._resolve_project_path(self.UPLOAD_DIR)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def chroma_path(self) -> Path:
        path = self._resolve_project_path(self.CHROMA_PERSIST_DIR)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _resolve_project_path(self, value: str) -> Path:
        path = Path(value)
        if path.is_absolute():
            return path
        project_root = Path(__file__).resolve().parents[3]
        clean_parts = [part for part in path.parts if part not in {".", ".."}]
        return project_root.joinpath(*clean_parts)


settings = Settings()
