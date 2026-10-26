"""Document models for LegalAI."""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from uuid import uuid4


class DocumentType(str, Enum):
    """Types of legal documents supported."""
    COURT_JUDGMENT = "court_judgment"
    FIR = "fir"
    CHARGE_SHEET = "charge_sheet"
    PETITION = "petition"
    CONTRACT = "contract"
    LEGAL_NOTICE = "legal_notice"
    AFFIDAVIT = "affidavit"
    BAIL_APPLICATION = "bail_application"
    WRIT_PETITION = "writ_petition"
    APPEAL = "appeal"
    OTHER = "other"


class ProcessingStatus(str, Enum):
    """Document processing status."""
    UPLOADED = "uploaded"
    EXTRACTING_TEXT = "extracting_text"
    OCR_PROCESSING = "ocr_processing"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


class ExtractedEntity(BaseModel):
    """An extracted entity from a legal document."""
    entity_type: str = Field(..., description="Type: party, date, location, crime, evidence, keyword")
    value: str = Field(..., description="Extracted value")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    context: Optional[str] = Field(None, description="Surrounding context")


class DocumentMetadata(BaseModel):
    """Metadata extracted from a legal document."""
    case_number: Optional[str] = None
    court_name: Optional[str] = None
    judge_name: Optional[str] = None
    date_of_filing: Optional[str] = None
    date_of_judgment: Optional[str] = None
    parties: List[str] = Field(default_factory=list)
    location: Optional[str] = None
    crime_category: Optional[str] = None
    evidence_list: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)


class DocumentBase(BaseModel):
    """Base document model."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    document_type: DocumentType = DocumentType.OTHER
    status: ProcessingStatus = ProcessingStatus.UPLOADED
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DocumentCreate(BaseModel):
    """Schema for creating a document."""
    filename: str
    original_filename: str
    file_type: str
    file_size: int


class DocumentResponse(BaseModel):
    """Schema for document API response."""
    id: str
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    document_type: DocumentType
    status: ProcessingStatus
    extracted_text: Optional[str] = None
    metadata: Optional[DocumentMetadata] = None
    entities: List[ExtractedEntity] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class DocumentTextResponse(BaseModel):
    """Schema for extracted text response."""
    id: str
    filename: str
    extracted_text: str
    metadata: Optional[DocumentMetadata] = None
    entities: List[ExtractedEntity] = Field(default_factory=list)


class UploadResponse(BaseModel):
    """Schema for file upload response."""
    id: str
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    status: ProcessingStatus
    message: str
