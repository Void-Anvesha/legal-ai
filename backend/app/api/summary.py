"""Summary API endpoint for LegalAI."""
from fastapi import APIRouter, HTTPException

from ..models.case import SummaryRequest, SummaryResponse
from ..services.summarizer import summarizer
from ..api.upload import document_store

router = APIRouter(prefix="/summary", tags=["Summary"])


@router.post("/", response_model=SummaryResponse)
async def create_summary(request: SummaryRequest):
    """Generate a summary of a legal document."""
    doc = document_store.get(request.document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    text = doc.get("extracted_text")
    if not text:
        raise HTTPException(status_code=400, detail="No text available for summarization")

    result = await summarizer.summarize(text, request.document_id)
    return result


@router.get("/{document_id}", response_model=SummaryResponse)
async def get_summary(document_id: str):
    """Get summary for a document."""
    doc = document_store.get(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    text = doc.get("extracted_text")
    if not text:
        raise HTTPException(status_code=400, detail="No text available for summarization")

    result = await summarizer.summarize(text, document_id)
    return result
