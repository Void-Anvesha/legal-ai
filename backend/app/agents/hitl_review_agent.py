"""Human-in-the-loop review control for case files."""
from datetime import datetime

from ..models.intake import CaseFile, CaseStatus, DecisionType, HitlDecision
from ..services.audit_logger import audit_logger


class HitlReviewAgent:
    """Apply officer decisions and maintain an audit trail."""

    def prepare_for_review(self, case_file: CaseFile) -> CaseFile:
        updated = case_file.model_copy(deep=True)
        updated.status = CaseStatus.OFFICER_REVIEW
        updated.updated_at = datetime.utcnow()
        updated.audit_log.append(
            audit_logger.event(
                "prepared_for_hitl_review",
                "Case file prepared for officer review.",
                case_id=updated.case_id,
            )
        )
        return updated

    def apply_decision(self, case_file: CaseFile, decision: HitlDecision) -> CaseFile:
        updated = case_file.model_copy(deep=True)
        if decision.target.value == "legal_section":
            updated.status = CaseStatus.OFFICER_REVIEW
        elif decision.decision_type == DecisionType.APPROVE:
            updated.status = CaseStatus.APPROVED
        elif decision.decision_type == DecisionType.REJECT:
            updated.status = CaseStatus.REJECTED
        elif decision.decision_type == DecisionType.REQUEST_MORE_INFO:
            updated.status = CaseStatus.NEEDS_MORE_INFO
        elif decision.decision_type == DecisionType.ESCALATE:
            updated.status = CaseStatus.ESCALATED
        elif decision.decision_type == DecisionType.EDIT and decision.updated_value:
            if decision.target.value == "statement":
                updated.statement_draft = decision.updated_value
            updated.status = CaseStatus.OFFICER_REVIEW

        if decision.target.value == "legal_section":
            for note in updated.legal_recommendation_notes:
                if decision.original_value in {note.section, f"{note.law} {note.section}"}:
                    note.officer_decision = decision.decision_type.value

        if decision.reason:
            updated.officer_notes.append(decision.reason)

        updated.updated_at = datetime.utcnow()
        updated.audit_log.append(
            audit_logger.officer_event(
                updated.case_id,
                decision.officer_id,
                "hitl_decision",
                "Officer decision recorded.",
                decision_id=decision.decision_id,
                decision_type=decision.decision_type.value,
                target=decision.target.value,
                reason=decision.reason,
            )
        )
        return updated


hitl_review_agent = HitlReviewAgent()
