"""Case models for LegalAI."""
from enum import Enum
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from uuid import uuid4


class CaseOutcome(str, Enum):
    """Possible case outcomes."""
    CONVICTED = "convicted"
    ACQUITTED = "acquitted"
    DISMISSED = "dismissed"
    SETTLED = "settled"
    PENDING = "pending"
    BAIL_GRANTED = "bail_granted"
    BAIL_DENIED = "bail_denied"
    APPEAL_ALLOWED = "appeal_allowed"
    APPEAL_DISMISSED = "appeal_dismissed"


class SimilarCase(BaseModel):
    """A similar legal case from the knowledge base."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    case_title: str
    case_number: Optional[str] = None
    court: str
    date: Optional[str] = None
    acts_sections: List[str] = Field(default_factory=list)
    brief_facts: str
    outcome: CaseOutcome
    key_holdings: List[str] = Field(default_factory=list)
    similarity_score: float = Field(..., ge=0.0, le=1.0)


class SimilarCaseRequest(BaseModel):
    """Request for similar case retrieval."""
    document_id: Optional[str] = None
    query: Optional[str] = None
    top_k: int = Field(default=5, ge=1, le=20)
    min_similarity: float = Field(default=0.5, ge=0.0, le=1.0)


class SimilarCaseResponse(BaseModel):
    """Response for similar case retrieval."""
    query: str
    similar_cases: List[SimilarCase]
    total_results: int


class CaseSummary(BaseModel):
    """Summary of a legal case."""
    short_summary: str = Field(..., description="2-3 sentence summary")
    detailed_summary: str = Field(..., description="Comprehensive summary")
    key_findings: List[str] = Field(default_factory=list)
    final_verdict: str
    legal_principles: List[str] = Field(default_factory=list)


class SummaryRequest(BaseModel):
    """Request for judgment summarization."""
    document_id: str
    summary_type: str = Field(default="detailed", pattern="^(short|detailed|key_findings)$")


class SummaryResponse(BaseModel):
    """Response for judgment summarization."""
    document_id: str
    short_summary: str
    detailed_summary: str
    key_findings: List[str]
    final_verdict: str
    legal_principles: List[str]
