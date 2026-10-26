"""Embedding service using Sentence Transformers."""
from typing import List, Optional
from loguru import logger
from functools import lru_cache

from ..core.config import settings


class EmbeddingService:
    """Service for generating text embeddings using Sentence Transformers."""

    _instance: Optional["EmbeddingService"] = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def model(self):
        """Lazy-load the embedding model."""
        if self._model is None:
            logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(settings.EMBEDDING_MODEL)
            logger.info(f"Embedding model loaded: {settings.EMBEDDING_MODEL}")
        return self._model

    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        embedding = self.model.encode(text, show_progress_bar=False)
        return embedding.tolist()

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        embeddings = self.model.encode(
            texts,
            show_progress_bar=False,
            batch_size=32,
        )
        return embeddings.tolist()

    def embed_text_sync(self, text: str) -> List[float]:
        """Synchronous embedding generation."""
        embedding = self.model.encode(text, show_progress_bar=False)
        return embedding.tolist()

    def embed_texts_sync(self, texts: List[str]) -> List[List[float]]:
        """Synchronous batch embedding generation."""
        embeddings = self.model.encode(
            texts,
            show_progress_bar=False,
            batch_size=32,
        )
        return embeddings.tolist()

    def get_dimension(self) -> int:
        """Get the dimension of the embedding vectors."""
        return self.model.get_sentence_embedding_dimension()
