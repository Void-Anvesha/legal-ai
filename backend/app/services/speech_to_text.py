"""Speech-to-text adapter for victim intake audio.

This module gives the API a stable contract today and a narrow place to plug in
Whisper, Bhashini, Azure, or another STT provider later.
"""
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from ..core.config import settings


class SpeechToTextResult:
    """Normalized transcription result."""

    def __init__(self, transcript: str, language: str, confidence: float, audio_path: str | None = None):
        self.transcript = transcript
        self.language = language
        self.confidence = confidence
        self.audio_path = audio_path


class SpeechToTextService:
    """Persist uploaded audio and return a transcript when possible."""

    async def transcribe_upload(self, file: UploadFile, language: str = "en-IN") -> SpeechToTextResult:
        audio_dir = settings.upload_path / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)
        suffix = Path(file.filename or "audio.webm").suffix or ".webm"
        stored_path = audio_dir / f"{uuid4()}{suffix}"
        content = await file.read()
        stored_path.write_bytes(content)

        transcript = ""
        if (file.content_type or "").startswith("text/") or suffix.lower() in {".txt", ".vtt"}:
            transcript = content.decode("utf-8", errors="ignore").strip()

        if not transcript:
            transcript = (
                "Audio was received and stored, but server-side speech-to-text is not configured. "
                "Please submit or confirm the transcript text for this recording."
            )

        return SpeechToTextResult(
            transcript=transcript,
            language=language,
            confidence=1.0 if transcript and "not configured" not in transcript else 0.0,
            audio_path=str(stored_path),
        )


speech_to_text_service = SpeechToTextService()
