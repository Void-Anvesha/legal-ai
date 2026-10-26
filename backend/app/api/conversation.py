"""Conversation API aliases for the intake orchestrator."""
from fastapi import APIRouter, HTTPException

from ..agents.orchestrator import intake_orchestrator
from ..models.intake import AddIntakeMessageRequest, AddIntakeMessageResponse, IntakeSessionResponse

router = APIRouter(prefix="/conversation", tags=["Conversation"])


@router.get("/{session_id}", response_model=IntakeSessionResponse)
async def get_conversation(session_id: str):
    """Fetch the conversation and case state for an intake session."""
    try:
        return intake_orchestrator.get_session(session_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{session_id}/message", response_model=AddIntakeMessageResponse)
async def add_conversation_message(session_id: str, request: AddIntakeMessageRequest):
    """Send a transcript message to the conversation orchestrator."""
    try:
        return intake_orchestrator.add_message(
            session_id=session_id,
            content=request.content,
            role=request.role,
            source=request.source,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
