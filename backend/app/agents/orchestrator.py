"""Conversation orchestrator for the BolnaAI intake workflow."""
from datetime import datetime
from typing import Dict, List, Optional

from ..models.intake import (
    AddIntakeMessageResponse,
    CaseFile,
    CaseStatus,
    CompleteIntakeResponse,
    ConversationMessage,
    CreateIntakeSessionRequest,
    HitlDecision,
    HitlDecisionRequest,
    HitlDecisionResponse,
    IntakeSession,
    IntakeSessionResponse,
    IntakeStatus,
    MessageRole,
)
from ..database.case_repository import CaseRepository
from ..database.recommendation_repository import RecommendationRepository
from ..database.session_repository import SessionRepository
from .fact_extraction_agent import fact_extraction_agent
from .followup_question_agent import followup_question_agent
from .hitl_review_agent import hitl_review_agent
from .legal_section_agent import legal_section_agent
from .safety_agent import safety_agent
from .statement_drafting_agent import statement_drafting_agent
from .voice_intake_agent import voice_intake_agent
from ..services.audit_logger import audit_logger
from ..services.officer_decision_service import officer_decision_service


class IntakeOrchestrator:
    """Coordinate intake messages, agents, case files, and HITL review."""

    def __init__(self):
        self.session_repository = SessionRepository()
        self.case_repository = CaseRepository()
        self.recommendation_repository = RecommendationRepository()
        self.sessions: Dict[str, IntakeSession] = self.session_repository.sessions
        self.messages: Dict[str, List[ConversationMessage]] = self.session_repository.messages
        self.cases: Dict[str, CaseFile] = self.case_repository.cases
        self.session_to_case: Dict[str, str] = self.case_repository.session_to_case
        self.decisions: Dict[str, List[HitlDecision]] = self.recommendation_repository.decisions

    def create_session(self, request: CreateIntakeSessionRequest) -> IntakeSessionResponse:
        opening_prompt = voice_intake_agent.opening_prompt
        if request.language == "hi-IN":
            opening_prompt = (
                "कृपया अपने शब्दों में बताइए कि क्या हुआ। मैं पहले सुनूँगा, "
                "फिर ज़रूरी जानकारी पूरी करने के लिए कुछ सवाल पूछ सकता हूँ।"
            )
        session = IntakeSession(
            language=request.language,
            consent_given=request.consent_given,
            current_question=opening_prompt,
        )
        case_file = CaseFile(session_id=session.session_id)
        case_file.facts.missing_information = fact_extraction_agent.missing_information(case_file.facts)
        case_file.audit_log.append(
            audit_logger.session_event(
                session.session_id,
                "intake_session_created",
                "Victim intake session created.",
            )
        )
        self.session_repository.save_session(session)
        self.case_repository.save_case(case_file)
        return self.get_session(session.session_id)

    def get_session(self, session_id: str) -> IntakeSessionResponse:
        session = self._get_session(session_id)
        case_file = self._get_case_for_session(session_id)
        return IntakeSessionResponse(
            session=session,
            messages=self.messages.get(session_id, []),
            case_file=case_file,
        )

    def list_cases(self) -> List[CaseFile]:
        return sorted(self.cases.values(), key=lambda case: case.created_at, reverse=True)

    def get_case(self, case_id: str) -> CaseFile:
        if case_id not in self.cases:
            raise KeyError("Case not found")
        return self.cases[case_id]

    def add_message(
        self,
        session_id: str,
        content: str,
        role: MessageRole = MessageRole.VICTIM,
        source: str = "text",
    ) -> AddIntakeMessageResponse:
        session = self._get_session(session_id)
        case_file = self._get_case_for_session(session_id)
        message = ConversationMessage(
            session_id=session_id,
            role=role,
            content=voice_intake_agent.normalize_transcript(content) if role == MessageRole.VICTIM else content,
            source=source,
        )
        self.messages[session_id].append(message)

        if role == MessageRole.VICTIM:
            if self._looks_like_hindi(content):
                session.language = "hi-IN"
            followup_key = followup_question_agent.missing_key_for_question(session.current_question)
            case_file.victim, case_file.facts = fact_extraction_agent.update_case_details(
                case_file.victim,
                case_file.facts,
                content,
                session.language,
                followup_key,
            )
            if safety_agent.detect_emergency(content):
                session.emergency_flag = True
                session.status = IntakeStatus.ESCALATED
                case_file.status = CaseStatus.ESCALATED
                case_file.officer_notes.extend(safety_agent.safety_notes(content))
                case_file.audit_log.append(
                    audit_logger.session_event(
                        session_id,
                        "emergency_flag_detected",
                        "Safety agent detected possible urgent risk.",
                    )
                )

        case_file = statement_drafting_agent.update_case_draft(case_file)
        next_question = followup_question_agent.next_question(case_file.facts, session.emergency_flag)
        localized_question = followup_question_agent.localize_question(next_question, session.language)
        is_complete_enough = fact_extraction_agent.is_complete_enough(case_file.facts)

        session.current_question = localized_question
        session.updated_at = datetime.utcnow()
        case_file.updated_at = datetime.utcnow()
        case_file.audit_log.append(
            audit_logger.session_event(
                session_id,
                "conversation_message_processed",
                "Conversation message processed by intake agents.",
            )
        )
        self.sessions[session_id] = session
        self.cases[case_file.case_id] = case_file

        agent_message = None
        if localized_question:
            agent_message = ConversationMessage(
                session_id=session_id,
                role=MessageRole.AGENT,
                content=localized_question,
                source="system",
            )
            self.messages[session_id].append(agent_message)

        return AddIntakeMessageResponse(
            session=session,
            message=message,
            agent_message=agent_message,
            case_file=case_file,
            next_question=localized_question,
            is_complete_enough=is_complete_enough,
        )

    def next_question(self, session_id: str) -> Optional[str]:
        session = self._get_session(session_id)
        case_file = self._get_case_for_session(session_id)
        question = followup_question_agent.next_question(case_file.facts, session.emergency_flag)
        question = followup_question_agent.localize_question(question, session.language)
        session.current_question = question
        session.updated_at = datetime.utcnow()
        return question

    def complete_session(self, session_id: str) -> CompleteIntakeResponse:
        session = self._get_session(session_id)
        case_file = self._get_case_for_session(session_id)
        case_file = statement_drafting_agent.update_case_draft(case_file)
        case_file = legal_section_agent.recommend(case_file)
        case_file = hitl_review_agent.prepare_for_review(case_file)
        session.status = IntakeStatus.NEEDS_REVIEW
        session.current_question = None
        session.updated_at = datetime.utcnow()
        self.sessions[session_id] = session
        self.cases[case_file.case_id] = case_file
        return CompleteIntakeResponse(session=session, case_file=case_file)

    def record_hitl_decision(self, case_id: str, request: HitlDecisionRequest) -> HitlDecisionResponse:
        case_file = self.get_case(case_id)
        decision = HitlDecision(case_id=case_id, **request.model_dump())
        self.recommendation_repository.add_decision(decision)
        case_file = officer_decision_service.apply(case_file, decision)
        self.cases[case_id] = case_file
        return HitlDecisionResponse(decision=decision, case_file=case_file)

    def get_decisions(self, case_id: str) -> List[HitlDecision]:
        self.get_case(case_id)
        return self.decisions.get(case_id, [])

    def _get_session(self, session_id: str) -> IntakeSession:
        if session_id not in self.sessions:
            raise KeyError("Intake session not found")
        return self.sessions[session_id]

    def _get_case_for_session(self, session_id: str) -> CaseFile:
        case_id = self.session_to_case.get(session_id)
        if not case_id or case_id not in self.cases:
            raise KeyError("Case file not found")
        return self.cases[case_id]

    def _looks_like_hindi(self, text: str) -> bool:
        """Detect Devanagari/Hindi speech and keep the session in Hindi."""
        devanagari_count = sum(1 for char in text if "\u0900" <= char <= "\u097f")
        return devanagari_count >= 2


intake_orchestrator = IntakeOrchestrator()
