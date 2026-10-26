"""Explanation and confidence agent for officer-facing legal recommendations."""
from ..models.intake import IncidentFacts, LegalRecommendationNote
from ..models.section import PredictedSection


class ExplanationConfidenceAgent:
    """Convert raw section predictions into reviewable legal recommendation notes."""

    def build_note(self, prediction: PredictedSection, facts: IncidentFacts) -> LegalRecommendationNote:
        supporting_facts = self._supporting_facts(prediction, facts)
        missing_facts = self._missing_facts(prediction, facts)
        title = prediction.section.section_title
        return LegalRecommendationNote(
            law=prediction.section.act.value,
            section=prediction.section.section_number,
            title=title,
            confidence=prediction.confidence,
            supporting_facts=supporting_facts,
            missing_facts=missing_facts,
            explanation=(
                f"{title} may apply because the complaint contains facts matching this section. "
                "This is only a draft recommendation and must be verified by an authorized officer."
            ),
        )

    def _supporting_facts(self, prediction: PredictedSection, facts: IncidentFacts) -> list[str]:
        support = []
        if facts.type:
            support.append(f"Complaint classified as {facts.type.replace('_', ' ')}.")
        if facts.location:
            support.append(f"Incident location captured as {facts.location}.")
        if facts.injuries:
            support.append(f"Injuries mentioned: {', '.join(facts.injuries)}.")
        if facts.property_loss:
            support.append(f"Property or loss mentioned: {', '.join(facts.property_loss)}.")
        if facts.threats:
            support.append(f"Threat-related terms mentioned: {', '.join(facts.threats)}.")
        if facts.digital_elements:
            support.append(f"Digital elements mentioned: {', '.join(facts.digital_elements)}.")
        if prediction.relevant_text:
            support.append(f"Relevant victim text: {prediction.relevant_text[:180]}.")
        return support[:5]

    def _missing_facts(self, prediction: PredictedSection, facts: IncidentFacts) -> list[str]:
        missing = list(facts.missing_information)
        title = prediction.section.section_title.lower()
        if any(word in title for word in ["hurt", "assault", "rape", "injury"]) and not facts.injuries:
            missing.append("injury or medical details")
        if any(word in title for word in ["theft", "robbery", "cheating", "fraud"]) and not facts.property_loss:
            missing.append("property, amount, or loss details")
        if "computer" in title or "technology" in prediction.section.act.value.lower():
            if not facts.digital_elements:
                missing.append("digital account, device, transaction, or evidence details")
        if "criminal intimidation" in title and not facts.threats:
            missing.append("exact words or nature of the threat")

        deduped = []
        for item in missing:
            if item not in deduped:
                deduped.append(item)
        return deduped[:6]


explanation_confidence_agent = ExplanationConfidenceAgent()
