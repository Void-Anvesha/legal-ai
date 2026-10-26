"""ChromaDB vector database management for LegalAI."""
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Optional, Dict, Any
from loguru import logger

from ..core.config import settings


class ChromaDBManager:
    """Manages ChromaDB connections and operations."""

    _instance: Optional["ChromaDBManager"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._client = None
            cls._instance._collections: Dict[str, Any] = {}
        return cls._instance

    @property
    def client(self) -> chromadb.ClientAPI:
        """Get or create ChromaDB client."""
        if self._client is None:
            logger.info(f"Initializing ChromaDB at {settings.chroma_path}")
            self._client = chromadb.PersistentClient(
                path=str(settings.chroma_path),
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                ),
            )
            logger.info("ChromaDB client initialized successfully")
        return self._client

    def get_collection(self, collection_name: Optional[str] = None) -> Any:
        """Get or create a collection."""
        name = collection_name or settings.CHROMA_COLLECTION_NAME
        if name not in self._collections:
            self._collections[name] = self.client.get_or_create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"},
            )
            logger.info(f"Collection '{name}' ready with {self._collections[name].count()} documents")
        return self._collections[name]

    def add_documents(
        self,
        ids: List[str],
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        collection_name: Optional[str] = None,
    ) -> None:
        """Add documents to a collection."""
        collection = self.get_collection(collection_name)
        collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas or [{}] * len(ids),
        )
        logger.info(f"Added {len(ids)} documents to collection '{collection_name or settings.CHROMA_COLLECTION_NAME}'")

    def query(
        self,
        query_embeddings: List[List[float]],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        collection_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Query the collection for similar documents."""
        collection = self.get_collection(collection_name)
        results = collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"],
        )
        return results

    def delete_documents(
        self,
        ids: List[str],
        collection_name: Optional[str] = None,
    ) -> None:
        """Delete documents from a collection."""
        collection = self.get_collection(collection_name)
        collection.delete(ids=ids)
        logger.info(f"Deleted {len(ids)} documents from collection '{collection_name or settings.CHROMA_COLLECTION_NAME}'")

    def reset(self, collection_name: Optional[str] = None) -> None:
        """Reset a collection."""
        name = collection_name or settings.CHROMA_COLLECTION_NAME
        try:
            self.client.delete_collection(name)
            logger.info(f"Deleted collection '{name}'")
        except Exception:
            pass
        self._collections.pop(name, None)
        self.get_collection(name)

    def count(self, collection_name: Optional[str] = None) -> int:
        """Count documents in a collection."""
        return self.get_collection(collection_name).count()


# Singleton instance
chroma_manager = ChromaDBManager()
