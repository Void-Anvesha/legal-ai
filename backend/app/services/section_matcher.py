"""Section matching service used by intake recommendations."""
from ..models.section import SectionPredictionResponse
from .section_predictor import section_predictor


class SectionMatcher:
    """Facade over the existing section predictor."""

    def match(self, text: str, case_id: str) -> SectionPredictionResponse:
        return section_predictor.predict_sections(text, case_id)


section_matcher = SectionMatcher()
