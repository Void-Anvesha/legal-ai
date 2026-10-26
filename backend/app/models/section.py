"""Legal section models for LegalAI."""
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class LegalAct(str, Enum):
    """Supported Indian legal acts."""
    BNS = "Bharatiya Nyaya Sanhita"
    IPC = "Indian Penal Code"
    IT_ACT = "Information Technology Act"
    BNSS = "Bharatiya Nagarik Suraksha Sanhita"
    CRPC = "Code of Criminal Procedure"
    BSA = "Bharatiya Sakshya Adhiniyam"
    IEA = "Indian Evidence Act"


class PunishmentType(str, Enum):
    """Types of punishment."""
    IMPRISONMENT = "imprisonment"
    FINE = "fine"
    BOTH = "both"
    DEATH = "death_penalty"
    LIFE_IMPRISONMENT = "life_imprisonment"
    NONE = "none"


class PunishmentDetail(BaseModel):
    """Details about punishment for a legal section."""
    punishment_type: PunishmentType
    minimum_duration: Optional[str] = None
    maximum_duration: Optional[str] = None
    fine_amount: Optional[str] = None
    is_cognizable: Optional[bool] = None
    is_bailable: Optional[bool] = None
    is_compoundable: Optional[bool] = None


class LegalSection(BaseModel):
    """A legal section from an Indian act."""
    act: LegalAct
    section_number: str
    section_title: str
    description: str
    punishment: Optional[PunishmentDetail] = None
    applicability: Optional[str] = None


class PredictedSection(BaseModel):
    """A predicted legal section with confidence and explanation."""
    section: LegalSection
    confidence: float = Field(..., ge=0.0, le=1.0)
    reason: str = Field(..., description="Why this section applies")
    relevant_text: str = Field(..., description="Document text that triggered this prediction")


class SectionPredictionRequest(BaseModel):
    """Request for section prediction."""
    document_id: str
    text: Optional[str] = None


class SectionPredictionResponse(BaseModel):
    """Response for section prediction."""
    document_id: str
    predicted_sections: List[PredictedSection]
    total_sections_found: int
    acts_referenced: List[LegalAct]


class SectionExplanationResponse(BaseModel):
    """Detailed explanation of a legal section."""
    act: LegalAct
    section_number: str
    section_title: str
    simple_explanation: str
    legal_implications: str
    punishment_details: Optional[PunishmentDetail]
    when_applies: str
    example_cases: List[str] = Field(default_factory=list)
