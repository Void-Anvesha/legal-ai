"""Cases API endpoint for similar case retrieval."""
from fastapi import APIRouter, HTTPException

from ..models.case import SimilarCaseRequest, SimilarCaseResponse
from ..services.similarity_search import similarity_search
from ..api.upload import document_store

router = APIRouter(prefix="/cases", tags=["Cases"])


@router.post("/similar", response_model=SimilarCaseResponse)
async def find_similar_cases(request: SimilarCaseRequest):
    """Find cases similar to a document or query."""
    query = request.query

    if not query and request.document_id:
        doc = document_store.get(request.document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        text = doc.get("extracted_text")
        if not text:
            raise HTTPException(status_code=400, detail="No text available for comparison")
        query = text[:1000]

    if not query:
        raise HTTPException(status_code=400, detail="Either query or document_id must be provided")

    result = await similarity_search.find_similar_cases(
        query=query,
        top_k=request.top_k,
        min_similarity=request.min_similarity,
    )
    return result


@router.get("/similar/{document_id}", response_model=SimilarCaseResponse)
async def find_similar_cases_for_document(document_id: str, top_k: int = 5):
    """Find cases similar to a specific document."""
    doc = document_store.get(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    text = doc.get("extracted_text")
    if not text:
        raise HTTPException(status_code=400, detail="No text available for comparison")

    result = await similarity_search.find_similar_cases(
        query=text[:1000],
        top_k=top_k,
    )
    return result
