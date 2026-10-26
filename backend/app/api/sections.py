"""Sections API endpoint for LegalAI."""
from fastapi import APIRouter, HTTPException
from typing import Optional

from ..models.section import (
    SectionPredictionResponse,
    SectionPredictionRequest,
    SectionExplanationResponse,
)
from ..services.section_predictor import section_predictor
from ..api.upload import document_store

router = APIRouter(prefix="/sections", tags=["Sections"])


@router.post("/predict", response_model=SectionPredictionResponse)
async def predict_sections(request: SectionPredictionRequest):
    """Predict applicable legal sections for a document."""
    doc = document_store.get(request.document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    text = request.text or doc.get("extracted_text")
    if not text:
        raise HTTPException(status_code=400, detail="No text available for analysis")

    result = section_predictor.predict_sections(text, request.document_id)
    return result


@router.get("/predict/{document_id}", response_model=SectionPredictionResponse)
async def predict_sections_for_document(document_id: str):
    """Predict applicable legal sections for a document by ID."""
    doc = document_store.get(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    text = doc.get("extracted_text")
    if not text:
        raise HTTPException(status_code=400, detail="No text available for analysis")

    result = section_predictor.predict_sections(text, document_id)
    return result


@router.get("/explain/{act}/{section_number}", response_model=SectionExplanationResponse)
async def explain_section(act: str, section_number: str):
    """
    Get a detailed explanation of a legal section.

    Act codes: BNS, IPC, IT_ACT, BNSS, BSA
    """
    explanation = section_predictor.explain_section(act, section_number)
    if not explanation:
        raise HTTPException(
            status_code=404,
            detail=f"Section {section_number} not found in {act}",
        )

    return SectionExplanationResponse(**explanation)
