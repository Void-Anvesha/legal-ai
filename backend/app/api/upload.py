"""Upload API endpoint for LegalAI."""
import os
import shutil
from pathlib import Path
from typing import Optional
from uuid import uuid4
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from loguru import logger

from ..models.document import (
    DocumentResponse,
    DocumentType,
    ProcessingStatus,
    UploadResponse,
)
from ..core.config import settings
from ..core.exceptions import FileValidationError, DocumentProcessingError
from ..services.pdf_reader import pdf_reader
from ..services.legal_parser import legal_parser
from ..database.vector_store import vector_store

router = APIRouter(prefix="/upload", tags=["Upload"])

# In-memory document store (replace with database in production)
document_store: dict = {}


@router.post("/", response_model=UploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    """Upload a legal document for analysis."""
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = Path(file.filename).suffix.lower()
    if ext not in settings.allowed_extensions_list:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{ext}' not allowed. Allowed: {settings.allowed_extensions_list}",
        )

    # Check file size
    contents = await file.read()
    if len(contents) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE_MB}MB",
        )

    # Save file
    doc_id = str(uuid4())
    safe_filename = f"{doc_id}{ext}"
    file_path = settings.upload_path / safe_filename

    with open(file_path, "wb") as f:
        f.write(contents)

    # Create document record
    document_store[doc_id] = {
        "id": doc_id,
        "filename": safe_filename,
        "original_filename": file.filename,
        "file_type": ext,
        "file_size": len(contents),
        "document_type": DocumentType.OTHER,
        "status": ProcessingStatus.UPLOADED,
        "extracted_text": None,
        "metadata": None,
        "entities": [],
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }

    # Process document in background
    background_tasks.add_task(process_document, doc_id, str(file_path))

    return UploadResponse(
        id=doc_id,
        filename=safe_filename,
        original_filename=file.filename,
        file_type=ext,
        file_size=len(contents),
        status=ProcessingStatus.UPLOADED,
        message="Document uploaded successfully. Processing has started.",
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str):
    """Get document details by ID."""
    doc = document_store.get(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    return DocumentResponse(**doc)


@router.get("/", response_model=list[DocumentResponse])
async def list_documents():
    """List all uploaded documents."""
    return [DocumentResponse(**doc) for doc in document_store.values()]


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """Delete a document."""
    doc = document_store.get(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete file
    file_path = settings.upload_path / doc["filename"]
    if file_path.exists():
        file_path.unlink()

    # Remove from store
    del document_store[document_id]

    return {"message": "Document deleted successfully", "id": document_id}


async def process_document(doc_id: str, file_path: str):
    """Background task to process uploaded document."""
    try:
        doc = document_store[doc_id]
        doc["status"] = ProcessingStatus.EXTRACTING_TEXT
        doc["updated_at"] = datetime.utcnow().isoformat()

        # Extract text
        text, used_ocr = pdf_reader.extract_text(file_path)
        doc["extracted_text"] = text

        if used_ocr:
            doc["status"] = ProcessingStatus.OCR_PROCESSING
            doc["updated_at"] = datetime.utcnow().isoformat()

        # Parse legal entities
        doc["status"] = ProcessingStatus.ANALYZING
        doc["updated_at"] = datetime.utcnow().isoformat()

        metadata, entities, doc_type = legal_parser.parse(text)
        doc["metadata"] = metadata.model_dump()
        doc["entities"] = [e.model_dump() for e in entities]
        doc["document_type"] = doc_type

        # Index in vector store
        try:
            await vector_store.index_document(
                document_id=doc_id,
                text=text,
                metadata={
                    "filename": doc["original_filename"],
                    "document_type": doc_type.value,
                    "case_number": metadata.case_number or "",
                    "court": metadata.court_name or "",
                },
            )
        except Exception as e:
            logger.warning(f"Vector indexing failed for {doc_id}: {e}")

        doc["status"] = ProcessingStatus.COMPLETED
        doc["updated_at"] = datetime.utcnow().isoformat()
        logger.info(f"Document {doc_id} processed successfully")

    except Exception as e:
        logger.error(f"Document processing failed for {doc_id}: {e}")
        if doc_id in document_store:
            document_store[doc_id]["status"] = ProcessingStatus.FAILED
            document_store[doc_id]["updated_at"] = datetime.utcnow().isoformat()
