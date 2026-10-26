"""Safety and escalation checks for intake conversations."""
from typing import List


class SafetyAgent:
    """Detect urgent situations that should move to human attention."""

    emergency_keywords = [
        "right now",
        "currently happening",
        "in danger",
        "weapon",
        "knife",
        "gun",
        "bleeding",
        "unconscious",
        "suicide",
        "kill me",
        "kill myself",
        "minor",
        "child",
        "kidnapped",
        "abducted",
    ]

    def detect_emergency(self, text: str) -> bool:
        lowered = text.lower()
        return any(keyword in lowered for keyword in self.emergency_keywords)

    def safety_notes(self, text: str) -> List[str]:
        if not self.detect_emergency(text):
            return []
        return [
            "Potential emergency detected from victim statement.",
            "Immediate human officer review is recommended.",
        ]


safety_agent = SafetyAgent()
