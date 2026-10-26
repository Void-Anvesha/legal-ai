"""Voice helper API.

The browser performs speech recognition in the current implementation. This
endpoint normalizes submitted transcript text so the rest of the intake flow can
use the same backend contract when a server-side speech-to-text provider is
added later.
"""
from pydantic import BaseModel
from fastapi import APIRouter, File, UploadFile

from ..services.speech_to_text import speech_to_text_service
from ..services.text_to_speech import text_to_speech_service

router = APIRouter(prefix="/voice", tags=["Voice"])


class TranscriptRequest(BaseModel):
    """Transcript payload from browser or future STT provider."""
    transcript: str
    language: str = "en-IN"


class TranscriptResponse(BaseModel):
    """Normalized transcript response."""
    transcript: str
    language: str
    confidence: float = 1.0
    audio_path: str | None = None


@router.post("/transcribe", response_model=TranscriptResponse)
async def transcribe_text(request: TranscriptRequest):
    """Return a normalized transcript for the intake workflow."""
    return TranscriptResponse(
        transcript=request.transcript.strip(),
        language=request.language,
        confidence=1.0,
    )


@router.post("/transcribe-audio", response_model=TranscriptResponse)
async def transcribe_audio(file: UploadFile = File(...), language: str = "en-IN"):
    """Store uploaded audio and transcribe it when a provider is configured."""
    result = await speech_to_text_service.transcribe_upload(file, language)
    return TranscriptResponse(
        transcript=result.transcript,
        language=result.language,
        confidence=result.confidence,
        audio_path=result.audio_path,
    )


@router.post("/speak")
async def speak_prompt(request: TranscriptRequest):
    """Return a TTS-ready response for a follow-up prompt."""
    return text_to_speech_service.synthesize_prompt(request.transcript, request.language)
