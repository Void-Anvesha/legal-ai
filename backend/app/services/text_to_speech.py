"""Text-to-speech adapter for follow-up prompts."""


class TextToSpeechService:
    """Return a stable response shape until an audio provider is configured."""

    def synthesize_prompt(self, text: str, language: str = "en-IN") -> dict:
        return {
            "text": text,
            "language": language,
            "audio_url": None,
            "provider": "not_configured",
        }


text_to_speech_service = TextToSpeechService()
