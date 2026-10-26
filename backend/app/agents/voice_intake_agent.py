"""Voice intake agent for consent, opening prompts, and transcript normalization."""


class VoiceIntakeAgent:
    """Owns the victim-facing opening flow for voice or text intake."""

    opening_prompt = (
        "Please tell me what happened in your own words. I will listen first, "
        "then I may ask a few questions to make sure important details are not missed."
    )

    consent_notice = (
        "This system will help record your complaint as a draft for police review. "
        "Please continue only if you consent to processing this statement."
    )

    def normalize_transcript(self, transcript: str) -> str:
        return " ".join(transcript.split()).strip()


voice_intake_agent = VoiceIntakeAgent()
