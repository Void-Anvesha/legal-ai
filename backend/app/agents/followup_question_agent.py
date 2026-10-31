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
    hindi_question_map = {
        "Please describe what happened in a little more detail.": "कृपया थोड़ा और विस्तार से बताइए कि क्या हुआ।",
        "When did the incident happen?": "यह घटना कब हुई?",
        "At what time did the incident happen?": "यह घटना किस समय हुई?",
        "Where exactly did the incident happen?": "यह घटना ठीक किस जगह हुई?",
        "Do you know who was involved or can you describe the suspect?": "क्या आप जानते हैं कि इसमें कौन शामिल था, या आप संदिग्ध व्यक्ति का वर्णन कर सकते हैं?",
        "Do you have any evidence such as photos, videos, screenshots, documents, or witnesses?": "क्या आपके पास कोई सबूत है, जैसे फोटो, वीडियो, स्क्रीनशॉट, दस्तावेज़ या गवाह?",
        "This may need immediate attention. Are you currently safe, and do you need urgent police or medical help?": "इसमें तुरंत ध्यान देने की ज़रूरत हो सकती है। क्या आप अभी सुरक्षित हैं, और क्या आपको तुरंत पुलिस या मेडिकल मदद चाहिए?",
    }

    def next_question(self, facts: IncidentFacts, emergency_flag: bool = False) -> str | None:
        if emergency_flag:
            return "This may need immediate attention. Are you currently safe, and do you need urgent police or medical help?"
        for missing in facts.missing_information:
            question = self.question_map.get(missing)
            if question:
                return question
        return None

    def localize_question(self, question: str | None, language: str) -> str | None:
        if not question or language != "hi-IN":
            return question
        return self.hindi_question_map.get(question, question)

    def missing_key_for_question(self, question: str | None) -> str | None:
        """Return the missing-information key that a follow-up question asks for."""
        if not question:
            return None
        for missing_key, english_question in self.question_map.items():
            if question == english_question:
                return missing_key
            if question == self.hindi_question_map.get(english_question):
                return missing_key
        return None


followup_question_agent = FollowUpQuestionAgent()
