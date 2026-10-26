"""Victim intake API for the BolnaAI workflow."""
from typing import List

from fastapi import APIRouter, File, HTTPException, UploadFile

from ..agents.orchestrator import intake_orchestrator
from ..models.intake import (
    AddIntakeMessageRequest,
    AddIntakeMessageResponse,
    CaseFile,
    CompleteIntakeResponse,
    CreateIntakeSessionRequest,
    IntakeSessionResponse,
    MessageRole,
)
from ..services.speech_to_text import speech_to_text_service

router = APIRouter(prefix="/intake", tags=["Intake"])


@router.post("/sessions", response_model=IntakeSessionResponse)
async def create_intake_session(request: CreateIntakeSessionRequest):
    """Create a new victim intake session."""
    return intake_orchestrator.create_session(request)


@router.get("/sessions/{session_id}", response_model=IntakeSessionResponse)
async def get_intake_session(session_id: str):
    """Fetch the full state for an intake session."""
    try:
        return intake_orchestrator.get_session(session_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/sessions/{session_id}/message", response_model=AddIntakeMessageResponse)
async def add_intake_message(session_id: str, request: AddIntakeMessageRequest):
    """Add a conversation message and run intake agents."""
    try:
        return intake_orchestrator.add_message(
            session_id=session_id,
            content=request.content,
            role=request.role,
            source=request.source,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{session_id}/message", response_model=AddIntakeMessageResponse)
async def add_intake_message_alias(session_id: str, request: AddIntakeMessageRequest):
    """Compatibility alias for the architecture-documented intake route."""
    return await add_intake_message(session_id, request)


@router.post("/{session_id}/audio", response_model=AddIntakeMessageResponse)
async def add_intake_audio(session_id: str, file: UploadFile = File(...), language: str = "en-IN"):
    """Upload victim audio, transcribe it, and process it through the intake agents."""
    try:
        transcript = await speech_to_text_service.transcribe_upload(file, language)
        return intake_orchestrator.add_message(
            session_id=session_id,
            content=transcript.transcript,
            role=MessageRole.VICTIM,
            source="voice",
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/sessions/{session_id}/next-question")
async def get_next_question(session_id: str):
    """Return the next follow-up question for a session."""
    try:
        return {"next_question": intake_orchestrator.next_question(session_id)}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{session_id}/next-question")
async def get_next_question_alias(session_id: str):
    """Compatibility alias for the architecture-documented intake route."""
    return await get_next_question(session_id)


@router.post("/sessions/{session_id}/complete", response_model=CompleteIntakeResponse)
async def complete_intake_session(session_id: str):
    """Finalize intake, draft the complaint, recommend sections, and send to review."""
    try:
        return intake_orchestrator.complete_session(session_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{session_id}/complete", response_model=CompleteIntakeResponse)
async def complete_intake_session_alias(session_id: str):
    """Compatibility alias for the architecture-documented intake route."""
    return await complete_intake_session(session_id)


@router.get("/cases", response_model=List[CaseFile])
async def list_intake_cases():
    """List case files generated through intake."""
    return intake_orchestrator.list_cases()


@router.get("/cases/{case_id}", response_model=CaseFile)
async def get_intake_case(case_id: str):
    """Fetch a generated case file."""
    try:
        return intake_orchestrator.get_case(case_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/cases/{case_id}/recommend-sections", response_model=CaseFile)
async def recommend_sections_for_case(case_id: str):
    """Regenerate legal section recommendations for an intake case."""
    try:
        case_file = intake_orchestrator.get_case(case_id)
        updated = intake_orchestrator.complete_session(case_file.session_id).case_file
        return updated
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
