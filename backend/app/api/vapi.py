"""Vapi integration endpoints for live voice intake."""
from typing import Any, Dict, Optional

from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel

from ..agents.orchestrator import intake_orchestrator
from ..core.config import settings
from ..models.intake import MessageRole

router = APIRouter(prefix="/vapi", tags=["Vapi"])


class VapiConfigResponse(BaseModel):
    """Public Vapi settings safe for the browser."""

    enabled: bool
    public_key: Optional[str] = None
    assistant_id: Optional[str] = None


class VapiTranscriptRequest(BaseModel):
    """Final transcript captured by the Vapi Web SDK."""

    session_id: str
    transcript: str
    role: str = "user"


@router.get("/config", response_model=VapiConfigResponse)
async def get_vapi_config():
    """Return browser-safe Vapi configuration."""
    enabled = bool(settings.VAPI_PUBLIC_KEY and settings.VAPI_ASSISTANT_ID)
    return VapiConfigResponse(
        enabled=enabled,
        public_key=settings.VAPI_PUBLIC_KEY if enabled else None,
        assistant_id=settings.VAPI_ASSISTANT_ID if enabled else None,
    )


@router.post("/transcript")
async def ingest_vapi_transcript(request: VapiTranscriptRequest):
    """Process a final Vapi browser transcript through the intake agents."""
    if request.role not in {"user", "victim"}:
        return {"processed": False, "reason": "assistant_transcript_ignored"}

    try:
        response = intake_orchestrator.add_message(
            session_id=request.session_id,
            content=request.transcript,
            role=MessageRole.VICTIM,
            source="vapi",
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return {"processed": True, "intake": response}


@router.post("/webhook")
async def receive_vapi_webhook(
    request: Request,
    x_vapi_secret: Optional[str] = Header(default=None),
):
    """Receive Vapi server events for phone or dashboard-configured calls."""
    if settings.VAPI_WEBHOOK_SECRET and x_vapi_secret != settings.VAPI_WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Invalid Vapi webhook secret")

    payload = await request.json()
    message = payload.get("message", payload)
    event_type = message.get("type")

    if event_type != "transcript":
        return {"received": True, "processed": False, "event_type": event_type}

    session_id = _extract_session_id(message, payload)
    transcript = (message.get("transcript") or "").strip()
    role = message.get("role")
    transcript_type = message.get("transcriptType") or message.get("transcript_type")

    if not session_id:
        return {"received": True, "processed": False, "reason": "missing_session_id"}
    if role not in {"user", "victim"} or transcript_type == "partial" or not transcript:
        return {"received": True, "processed": False, "reason": "not_final_user_transcript"}

    try:
        intake_orchestrator.add_message(
            session_id=session_id,
            content=transcript,
            role=MessageRole.VICTIM,
            source="vapi",
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return {"received": True, "processed": True}


def _extract_session_id(message: Dict[str, Any], payload: Dict[str, Any]) -> Optional[str]:
    """Find the BolnaAI session ID across common Vapi metadata locations."""
    candidates = [
        message.get("sessionId"),
        message.get("session_id"),
        payload.get("sessionId"),
        payload.get("session_id"),
    ]

    call = message.get("call") or payload.get("call") or {}
    assistant = message.get("assistant") or payload.get("assistant") or call.get("assistant") or {}
    for container in (call, assistant):
        metadata = container.get("metadata") or {}
        variable_values = container.get("variableValues") or container.get("variable_values") or {}
        candidates.extend(
            [
                metadata.get("sessionId"),
                metadata.get("session_id"),
                variable_values.get("sessionId"),
                variable_values.get("session_id"),
            ]
        )

    for candidate in candidates:
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
    return None
