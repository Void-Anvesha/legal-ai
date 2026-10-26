"""Follow-up question selection for complaint intake."""
from ..models.intake import IncidentFacts


class FollowUpQuestionAgent:
    """Ask one focused question based on missing facts."""

    question_map = {
        "incident description": "Please describe what happened in a little more detail.",
        "incident date": "When did the incident happen?",
        "incident time": "At what time did the incident happen?",
        "incident location": "Where exactly did the incident happen?",
        "accused or suspect details": "Do you know who was involved or can you describe the suspect?",
        "available evidence": "Do you have any evidence such as photos, videos, screenshots, documents, or witnesses?",
    }

    def next_question(self, facts: IncidentFacts, emergency_flag: bool = False) -> str | None:
        if emergency_flag:
            return "This may need immediate attention. Are you currently safe, and do you need urgent police or medical help?"
        for missing in facts.missing_information:
            question = self.question_map.get(missing)
            if question:
                return question
        return None


followup_question_agent = FollowUpQuestionAgent()
