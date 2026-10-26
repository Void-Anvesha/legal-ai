"""Vector store operations for RAG pipeline."""
from typing import List, Dict, Any, Optional, Tuple
from loguru import logger

from .chroma_db import chroma_manager
from ..services.embeddings import EmbeddingService
from ..core.config import settings


class VectorStore:
    """High-level vector store operations for legal documents."""

    def __init__(self):
        self.embedding_service = EmbeddingService()

    async def index_document(
        self,
        document_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        collection_name: Optional[str] = None,
    ) -> int:
        """Index a document by chunking, embedding, and storing in ChromaDB."""
        chunks = self._chunk_text(text)
        if not chunks:
            logger.warning(f"No chunks generated for document {document_id}")
            return 0

        embeddings = await self.embedding_service.embed_texts(chunks)

        ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]
        metadatas = []
        for i, chunk in enumerate(chunks):
            meta = {
                "document_id": document_id,
                "chunk_index": i,
                "chunk_length": len(chunk),
                **(metadata or {}),
            }
            metadatas.append(meta)

        chroma_manager.add_documents(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
            collection_name=collection_name,
        )

        logger.info(f"Indexed {len(chunks)} chunks for document {document_id}")
        return len(chunks)

    async def search(
        self,
        query: str,
        top_k: int = None,
        min_similarity: float = None,
        filter_metadata: Optional[Dict[str, Any]] = None,
        collection_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Search for similar documents using a query string."""
        top_k = top_k or settings.TOP_K_RESULTS
        min_similarity = min_similarity or settings.SIMILARITY_THRESHOLD

        query_embedding = await self.embedding_service.embed_text(query)

        results = chroma_manager.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_metadata,
            collection_name=collection_name,
        )

        search_results = []
        if results and results["documents"]:
            for i, (doc, metadata, distance) in enumerate(
                zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0],
                )
            ):
                similarity = 1 - distance  # Convert cosine distance to similarity
                if similarity >= min_similarity:
                    search_results.append({
                        "text": doc,
                        "metadata": metadata,
                        "similarity_score": round(similarity, 4),
                        "rank": i + 1,
                    })

        logger.info(f"Found {len(search_results)} results for query (top_k={top_k})")
        return search_results

    async def search_by_embedding(
        self,
        query_embedding: List[float],
        top_k: int = None,
        min_similarity: float = None,
        collection_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Search using a pre-computed embedding."""
        top_k = top_k or settings.TOP_K_RESULTS
        min_similarity = min_similarity or settings.SIMILARITY_THRESHOLD

        results = chroma_manager.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            collection_name=collection_name,
        )

        search_results = []
        if results and results["documents"]:
            for i, (doc, metadata, distance) in enumerate(
                zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0],
                )
            ):
                similarity = 1 - distance
                if similarity >= min_similarity:
                    search_results.append({
                        "text": doc,
                        "metadata": metadata,
                        "similarity_score": round(similarity, 4),
                        "rank": i + 1,
                    })

        return search_results

    def _chunk_text(
        self,
        text: str,
        chunk_size: int = None,
        chunk_overlap: int = None,
    ) -> List[str]:
        """Split text into overlapping chunks."""
        chunk_size = chunk_size or settings.CHUNK_SIZE
        chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

        if not text or len(text.strip()) == 0:
            return []

        # Clean text
        text = " ".join(text.split())

        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]

            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind(". ")
                if last_period > chunk_size // 2:
                    chunk = chunk[: last_period + 1]
                    end = start + last_period + 1

            chunks.append(chunk.strip())
            start = end - chunk_overlap

        return [c for c in chunks if len(c) > 50]  # Filter tiny chunks


vector_store = VectorStore()
