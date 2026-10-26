"""Models for victim intake, case drafting, and HITL review."""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from .section import PredictedSection


class IntakeStatus(str, Enum):
    """Lifecycle states for a police intake session."""
    IN_PROGRESS = "in_progress"
    NEEDS_REVIEW = "needs_review"
    COMPLETED = "completed"
    ESCALATED = "escalated"


class CaseStatus(str, Enum):
    """Lifecycle states for generated case files."""
    DRAFT = "draft"
    OFFICER_REVIEW = "officer_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_MORE_INFO = "needs_more_info"
    ESCALATED = "escalated"


class MessageRole(str, Enum):
    """Supported conversation message roles."""
    VICTIM = "victim"
    AGENT = "agent"
    OFFICER = "officer"


class DecisionType(str, Enum):
    """Officer HITL decision types."""
    APPROVE = "approve"
    EDIT = "edit"
    REJECT = "reject"
    REQUEST_MORE_INFO = "request_more_info"
    ESCALATE = "escalate"


class ReviewTarget(str, Enum):
    """Case artifact targeted by a HITL decision."""
    STATEMENT = "statement"
    EXTRACTED_FACT = "extracted_fact"
    LEGAL_SECTION = "legal_section"
    FULL_CASE = "full_case"


class VictimProfile(BaseModel):
    """Victim details collected during intake."""
    name: Optional[str] = None
    age: Optional[str] = None
    gender: Optional[str] = None
    contact: Optional[str] = None
    address: Optional[str] = None


class IncidentFacts(BaseModel):
    """Structured facts extracted from the complaint narrative."""
    type: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    location: Optional[str] = None
    description: str = ""
    sequence_of_events: List[str] = Field(default_factory=list)
    accused: List[str] = Field(default_factory=list)
    witnesses: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    injuries: List[str] = Field(default_factory=list)
    property_loss: List[str] = Field(default_factory=list)
    threats: List[str] = Field(default_factory=list)
    digital_elements: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)


class LegalRecommendationNote(BaseModel):
    """Officer-facing rationale for a predicted legal section."""
    law: str
    section: str
    title: str
    confidence: float
    supporting_facts: List[str] = Field(default_factory=list)
    missing_facts: List[str] = Field(default_factory=list)
    explanation: str
    officer_decision: str = "pending"


class IntakeSession(BaseModel):
    """Victim intake session."""
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    language: str = "en-IN"
    status: IntakeStatus = IntakeStatus.IN_PROGRESS
    consent_given: bool = False
    emergency_flag: bool = False
    current_question: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ConversationMessage(BaseModel):
    """Single intake conversation message."""
    message_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str
    role: MessageRole
    content: str
    source: str = "text"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class CaseFile(BaseModel):
    """Generated case packet for officer review."""
    case_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str
    status: CaseStatus = CaseStatus.DRAFT
    victim: VictimProfile = Field(default_factory=VictimProfile)
    facts: IncidentFacts = Field(default_factory=IncidentFacts)
    summary: str = ""
    statement_draft: str = ""
    legal_recommendations: List[PredictedSection] = Field(default_factory=list)
    legal_recommendation_notes: List[LegalRecommendationNote] = Field(default_factory=list)
    officer_notes: List[str] = Field(default_factory=list)
    audit_log: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class HitlDecision(BaseModel):
    """Officer review decision captured for audit."""
    decision_id: str = Field(default_factory=lambda: str(uuid4()))
    case_id: str
    officer_id: str
    decision_type: DecisionType
    target: ReviewTarget
    original_value: Optional[str] = None
    updated_value: Optional[str] = None
    reason: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class CreateIntakeSessionRequest(BaseModel):
    """Request to create a new intake session."""
    language: str = "en-IN"
    consent_given: bool = True


class AddIntakeMessageRequest(BaseModel):
    """Request to add a victim, agent, or officer message."""
    content: str = Field(..., min_length=1)
    role: MessageRole = MessageRole.VICTIM
    source: str = "text"


class IntakeSessionResponse(BaseModel):
    """Full intake session state."""
    session: IntakeSession
    messages: List[ConversationMessage]
    case_file: CaseFile


class AddIntakeMessageResponse(BaseModel):
    """Response after processing a conversation message."""
    session: IntakeSession
    message: ConversationMessage
    agent_message: Optional[ConversationMessage] = None
    case_file: CaseFile
    next_question: Optional[str] = None
    is_complete_enough: bool = False


class CompleteIntakeResponse(BaseModel):
    """Response after finalizing intake for officer review."""
    session: IntakeSession
    case_file: CaseFile


class HitlDecisionRequest(BaseModel):
    """Request to record an officer decision."""
    officer_id: str = "officer-demo"
    decision_type: DecisionType
    target: ReviewTarget
    original_value: Optional[str] = None
    updated_value: Optional[str] = None
    reason: Optional[str] = None


class HitlDecisionResponse(BaseModel):
    """Response after recording an officer decision."""
    decision: HitlDecision
    case_file: CaseFile
