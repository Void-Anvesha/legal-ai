"""Legal retrieval query preparation for intake case files."""
from ..models.intake import CaseFile


class LegalRetrievalService:
    """Build legal-search text from structured complaint facts."""

    def build_query(self, case_file: CaseFile) -> str:
        facts = case_file.facts
        parts = [
            facts.type or "",
            facts.description,
            case_file.summary,
            case_file.statement_draft,
            " ".join(facts.injuries),
            " ".join(facts.property_loss),
            " ".join(facts.threats),
            " ".join(facts.digital_elements),
            " ".join(facts.evidence),
        ]
        return "\n".join(part for part in parts if part).strip()


legal_retrieval_service = LegalRetrievalService()
