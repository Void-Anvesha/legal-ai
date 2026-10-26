"""Chat API endpoint for LegalAI assistant."""
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from uuid import uuid4

from ..services.rag_engine import rag_engine
from ..api.upload import document_store

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatMessage(BaseModel):
    """A single chat message."""
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str


class ChatRequest(BaseModel):
    """Request for chat completion."""
    message: str = Field(..., min_length=1, max_length=5000)
    document_id: Optional[str] = None
    chat_history: List[ChatMessage] = Field(default_factory=list)


class ChatResponse(BaseModel):
    """Response from chat assistant."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    message: str
    sources: List[dict] = Field(default_factory=list)
    context_used: int = 0
    document_id: Optional[str] = None


# In-memory chat history per session
chat_sessions: dict = {}


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with the LegalAI assistant.
    
    Supports questions like:
    - Explain this judgment
    - Which laws apply?
    - What punishment is possible?
    - Show similar cases
    """
    # Validate document_id if provided
    if request.document_id and request.document_id not in document_store:
        raise HTTPException(status_code=404, detail="Document not found")

    # Process with RAG engine
    result = await rag_engine.query(
        question=request.message,
        document_id=request.document_id,
        chat_history=[msg.model_dump() for msg in request.chat_history],
    )

    return ChatResponse(
        message=result["answer"],
        sources=result["sources"],
        context_used=result["context_used"],
        document_id=result["document_id"],
    )


@router.post("/explain-judgment")
async def explain_judgment(document_id: str):
    """Explain a judgment in simple terms."""
    doc = document_store.get(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    text = doc.get("extracted_text")
    if not text:
        raise HTTPException(status_code=400, detail="No text available")

    explanation = await rag_engine.explain_judgment(document_id, text)
    return {"document_id": document_id, "explanation": explanation}


@router.post("/explain-laws")
async def explain_laws(document_id: str):
    """Explain which laws apply to a document."""
    doc = document_store.get(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    text = doc.get("extracted_text")
    if not text:
        raise HTTPException(status_code=400, detail="No text available")

    explanation = await rag_engine.explain_laws(text)
    return {"document_id": document_id, "explanation": explanation}


@router.post("/explain-punishment")
async def explain_punishment(document_id: str):
    """Explain possible punishments for offences in a document."""
    doc = document_store.get(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    text = doc.get("extracted_text")
    if not text:
        raise HTTPException(status_code=400, detail="No text available")

    explanation = await rag_engine.explain_punishment(text)
    return {"document_id": document_id, "explanation": explanation}
