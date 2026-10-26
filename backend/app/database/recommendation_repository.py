"""Repository boundary for legal recommendations and HITL decisions."""
from typing import Dict, List

from ..models.intake import HitlDecision


class RecommendationRepository:
    """In-memory decision storage, replaceable with SQL storage."""

    def __init__(self):
        self.decisions: Dict[str, List[HitlDecision]] = {}

    def add_decision(self, decision: HitlDecision) -> HitlDecision:
        self.decisions.setdefault(decision.case_id, []).append(decision)
        return decision

    def list_decisions(self, case_id: str) -> List[HitlDecision]:
        return self.decisions.get(case_id, [])
