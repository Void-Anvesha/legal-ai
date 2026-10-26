"""Legal section recommendation agent built on the existing predictor."""
from ..core.exceptions import SectionPredictionError
from ..models.intake import CaseFile
from ..services.legal_retrieval import legal_retrieval_service
from ..services.section_matcher import section_matcher
from .explanation_agent import explanation_confidence_agent


class LegalSectionRecommendationAgent:
    """Recommend sections by reusing the current section predictor."""

    def recommend(self, case_file: CaseFile) -> CaseFile:
        updated = case_file.model_copy(deep=True)
        source_text = legal_retrieval_service.build_query(updated)
        if not source_text.strip():
            updated.legal_recommendations = []
            updated.legal_recommendation_notes = []
            return updated

        try:
            prediction = section_matcher.match(source_text, updated.case_id)
        except SectionPredictionError:
            updated.legal_recommendations = []
            updated.legal_recommendation_notes = []
            return updated

        updated.legal_recommendations = prediction.predicted_sections
        updated.legal_recommendation_notes = [
            explanation_confidence_agent.build_note(section, updated.facts)
            for section in prediction.predicted_sections
        ]
        return updated


legal_section_agent = LegalSectionRecommendationAgent()
