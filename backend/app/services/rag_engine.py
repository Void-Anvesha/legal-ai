"""RAG (Retrieval-Augmented Generation) Engine for LegalAI."""
from typing import List, Dict, Any, Optional
from loguru import logger

from ..database.vector_store import vector_store
from ..core.config import settings
from ..core.exceptions import RAGError
from ..prompts.chat_prompt import ChatPromptBuilder


class RAGEngine:
    """Retrieval-Augmented Generation engine for legal document Q&A."""

    def __init__(self):
        self.prompt_builder = ChatPromptBuilder()

    async def query(
        self,
        question: str,
        document_id: Optional[str] = None,
        chat_history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Process a question using RAG pipeline:
        1. Retrieve relevant context from vector store
        2. Augment prompt with retrieved context
        3. Generate response using LLM
        """
        # Step 1: Retrieve relevant context
        filter_metadata = None
        if document_id:
            filter_metadata = {"document_id": document_id}

        try:
            search_results = await vector_store.search(
                query=question,
                top_k=settings.TOP_K_RESULTS,
                filter_metadata=filter_metadata,
            )
        except Exception as e:
            logger.warning(f"Vector search failed, proceeding without context: {e}")
            search_results = []

        # Step 2: Build context from search results
        context_parts = []
        sources = []
        for result in search_results:
            context_parts.append(result["text"])
            sources.append({
                "text_snippet": result["text"][:200],
                "similarity": result["similarity_score"],
                "metadata": result["metadata"],
            })

        context = "\n\n---\n\n".join(context_parts) if context_parts else "No specific document context found."

        # Step 3: Generate response using LLM
        try:
            answer = await self._generate_response(
                question=question,
                context=context,
                chat_history=chat_history or [],
            )
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            # Fallback: return context-based response
            answer = self._generate_fallback_response(question, search_results)

        return {
            "question": question,
            "answer": answer,
            "sources": sources,
            "context_used": len(search_results),
            "document_id": document_id,
        }

    async def _generate_response(
        self,
        question: str,
        context: str,
        chat_history: List[Dict[str, str]],
    ) -> str:
        """Generate response using LLM with retrieved context."""
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

        if not settings.OPENAI_API_KEY:
            raise RAGError("OpenAI API key not configured")

        llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=0.3,
            max_tokens=1500,
        )

        # Build messages
        messages = [
            SystemMessage(content=self.prompt_builder.rag_system_prompt()),
        ]

        # Add chat history
        for entry in chat_history[-5:]:  # Keep last 5 exchanges
            if entry.get("role") == "user":
                messages.append(HumanMessage(content=entry["content"]))
            elif entry.get("role") == "assistant":
                messages.append(AIMessage(content=entry["content"]))

        # Add current question with context
        user_prompt = self.prompt_builder.rag_user_prompt(
            question=question, context=context
        )
        messages.append(HumanMessage(content=user_prompt))

        response = await llm.ainvoke(messages)
        return response.content

    def _generate_fallback_response(
        self, question: str, search_results: List[Dict[str, Any]]
    ) -> str:
        """Generate a fallback response when LLM is unavailable."""
        if not search_results:
            return (
                "I apologize, but I was unable to find relevant information "
                "in the document database for your question. Please ensure documents "
                "have been uploaded and indexed properly."
            )

        # Construct response from retrieved context
        response_parts = [
            "Based on the available document context:\n",
        ]
        for i, result in enumerate(search_results[:3], 1):
            response_parts.append(
                f"{i}. (Similarity: {result['similarity_score']:.1%}) "
                f"{result['text'][:300]}...\n"
            )

        return "\n".join(response_parts)

    async def explain_judgment(self, document_id: str, text: str) -> str:
        """Explain a judgment in simple terms."""
        search_results = await vector_store.search(
            query="judgment verdict decision holding",
            top_k=3,
            filter_metadata={"document_id": document_id},
        )

        context = "\n".join([r["text"] for r in search_results]) if search_results else text[:2000]

        try:
            return await self._generate_response(
                question="Explain this judgment in simple terms that a non-lawyer can understand.",
                context=context,
                chat_history=[],
            )
        except Exception:
            return "Unable to generate judgment explanation. The LLM service is not configured."

    async def explain_laws(self, text: str) -> str:
        """Explain which laws apply to the given text."""
        search_results = await vector_store.search(
            query="applicable laws sections charges",
            top_k=3,
        )

        context = "\n".join([r["text"] for r in search_results]) if search_results else text[:2000]

        try:
            return await self._generate_response(
                question="Which laws and legal sections apply to this case? Explain each one.",
                context=f"Document text: {text[:1500]}\n\nLegal context: {context}",
                chat_history=[],
            )
        except Exception:
            return "Unable to analyze applicable laws. The LLM service is not configured."

    async def explain_punishment(self, text: str) -> str:
        """Explain possible punishments for the case."""
        try:
            return await self._generate_response(
                question="What are the possible punishments for the offences described in this document?",
                context=text[:2000],
                chat_history=[],
            )
        except Exception:
            return "Unable to analyze punishments. The LLM service is not configured."


# Singleton
rag_engine = RAGEngine()
