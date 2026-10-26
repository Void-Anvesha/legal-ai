"""Human-in-the-loop review API."""
from typing import List

from fastapi import APIRouter, HTTPException

from ..agents.orchestrator import intake_orchestrator
from ..models.intake import HitlDecision, HitlDecisionRequest, HitlDecisionResponse

router = APIRouter(prefix="/hitl", tags=["HITL Review"])
officer_router = APIRouter(prefix="/officer-review", tags=["Officer Review"])


@router.post("/{case_id}/decision", response_model=HitlDecisionResponse)
async def record_hitl_decision(case_id: str, request: HitlDecisionRequest):
    """Record an officer decision for a generated case file."""
    try:
        return intake_orchestrator.record_hitl_decision(case_id, request)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{case_id}/audit", response_model=List[HitlDecision])
async def get_hitl_audit(case_id: str):
    """Fetch officer decision audit records for a case."""
    try:
        return intake_orchestrator.get_decisions(case_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@officer_router.patch("/{case_id}", response_model=HitlDecisionResponse)
async def officer_review_decision(case_id: str, request: HitlDecisionRequest):
    """Architecture-compatible route for officer edits, approvals, or rejections."""
    return await record_hitl_decision(case_id, request)
