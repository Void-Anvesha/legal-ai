"""Officer decision service for HITL review actions."""
from ..agents.hitl_review_agent import hitl_review_agent
from ..models.intake import CaseFile, HitlDecision


class OfficerDecisionService:
    """Apply officer decisions through the HITL review agent."""

    def apply(self, case_file: CaseFile, decision: HitlDecision) -> CaseFile:
        return hitl_review_agent.apply_decision(case_file, decision)


officer_decision_service = OfficerDecisionService()
