# LegalAI — API Documentation

Base URL: `http://localhost:8000/api/v1`

## Health Check

### GET /
Root health check.

**Response:**
```json
{
  "name": "LegalAI",
  "version": "1.0.0",
  "status": "running",
  "docs": "/api/v1/docs"
}
```

### GET /api/v1/health
Detailed health check.

---

## Upload Endpoints

### POST /api/v1/upload/
Upload a legal document for analysis.

**Request:** `multipart/form-data`
- `file`: File (PDF, DOCX, TXT, or image)

**Response:**
```json
{
  "id": "uuid",
  "filename": "stored_filename.pdf",
  "original_filename": "my_document.pdf",
  "file_type": ".pdf",
  "file_size": 1234567,
  "status": "uploaded",
  "message": "Document uploaded successfully. Processing has started."
}
```

### GET /api/v1/upload/
List all uploaded documents.

### GET /api/v1/upload/{document_id}
Get document details including extracted text and metadata.

**Response:**
```json
{
  "id": "uuid",
  "filename": "...",
  "original_filename": "...",
  "file_type": ".pdf",
  "file_size": 1234567,
  "document_type": "court_judgment",
  "status": "completed",
  "extracted_text": "Full text content...",
  "metadata": {
    "case_number": "Crl.A No. 123/2020",
    "court_name": "Supreme Court of India",
    "parties": ["State of Punjab", "Raj Kumar"],
    "crime_category": "murder",
    "keywords": ["murder", "conviction", "appeal"]
  },
  "entities": [
    {
      "entity_type": "party",
      "value": "State of Punjab",
      "confidence": 0.8
    }
  ],
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

### DELETE /api/v1/upload/{document_id}
Delete a document.

---

## Section Prediction Endpoints

### POST /api/v1/sections/predict
Predict legal sections for a document.

**Request:**
```json
{
  "document_id": "uuid",
  "text": "Optional override text"
}
```

**Response:**
```json
{
  "document_id": "uuid",
  "predicted_sections": [
    {
      "section": {
        "act": "Bharatiya Nyaya Sanhita",
        "section_number": "103",
        "section_title": "Punishment for Murder",
        "description": "...",
        "punishment": {
          "punishment_type": "both",
          "minimum_duration": "life imprisonment",
          "maximum_duration": "death penalty",
          "fine_amount": "liable to fine",
          "is_cognizable": true,
          "is_bailable": false
        }
      },
      "confidence": 0.95,
      "reason": "Section 103 of BNS applies because...",
      "relevant_text": "The accused was charged with murder..."
    }
  ],
  "total_sections_found": 5,
  "acts_referenced": ["Bharatiya Nyaya Sanhita", "Bharatiya Nagarik Suraksha Sanhita"]
}
```

### GET /api/v1/sections/predict/{document_id}
Predict sections for a document by ID.

### GET /api/v1/sections/explain/{act}/{section_number}
Get detailed explanation of a legal section.

**Path Parameters:**
- `act`: BNS, IPC, IT_ACT, BNSS, BSA
- `section_number`: e.g., 103, 376, 66

**Response:**
```json
{
  "act": "BNS",
  "section_number": "103",
  "section_title": "Punishment for Murder",
  "simple_explanation": "In simple terms...",
  "legal_implications": "This is a cognizable offence...",
  "punishment_details": { ... },
  "when_applies": "This section applies when: murder, killed, homicide",
  "example_cases": ["Bachan Singh v. State of Punjab (1980)"]
}
```

---

## Summary Endpoints

### POST /api/v1/summary/
Generate a document summary.

**Request:**
```json
{
  "document_id": "uuid",
  "summary_type": "detailed"
}
```

### GET /api/v1/summary/{document_id}
Get summary for a document.

**Response:**
```json
{
  "document_id": "uuid",
  "short_summary": "Brief 2-3 sentence summary...",
  "detailed_summary": "Comprehensive summary...",
  "key_findings": ["Finding 1", "Finding 2"],
  "final_verdict": "The accused was convicted...",
  "legal_principles": ["Principle 1", "Principle 2"]
}
```

---

## Chat Endpoints

### POST /api/v1/chat/
Chat with the LegalAI assistant.

**Request:**
```json
{
  "message": "Which laws apply to this document?",
  "document_id": "uuid",
  "chat_history": [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "How can I help?"}
  ]
}
```

**Response:**
```json
{
  "id": "uuid",
  "message": "Based on the document, the following laws apply...",
  "sources": [
    {
      "text_snippet": "Relevant context...",
      "similarity": 0.89,
      "metadata": {"document_id": "uuid", "chunk_index": 0}
    }
  ],
  "context_used": 3,
  "document_id": "uuid"
}
```

### POST /api/v1/chat/explain-judgment?document_id={id}
Explain a judgment in simple terms.

### POST /api/v1/chat/explain-laws?document_id={id}
Explain applicable laws for a document.

### POST /api/v1/chat/explain-punishment?document_id={id}
Explain possible punishments.

---

## Similar Cases Endpoints

### POST /api/v1/cases/similar
Find similar cases.

**Request:**
```json
{
  "query": "murder conviction death penalty rarest of rare",
  "top_k": 5,
  "min_similarity": 0.5
}
```

**Response:**
```json
{
  "query": "murder conviction...",
  "similar_cases": [
    {
      "id": "sc_001",
      "case_title": "Bachan Singh v. State of Punjab",
      "case_number": "AIR 1980 SC 898",
      "court": "Supreme Court of India",
      "date": "1980-09-09",
      "acts_sections": ["IPC 302"],
      "brief_facts": "...",
      "outcome": "convicted",
      "key_holdings": ["..."],
      "similarity_score": 0.92
    }
  ],
  "total_results": 5
}
```

### GET /api/v1/cases/similar/{document_id}
Find cases similar to a specific document.

---

## Document Types

| Type | Value |
|------|-------|
| Court Judgment | `court_judgment` |
| FIR | `fir` |
| Charge Sheet | `charge_sheet` |
| Petition | `petition` |
| Contract | `contract` |
| Legal Notice | `legal_notice` |
| Affidavit | `affidavit` |
| Bail Application | `bail_application` |
| Writ Petition | `writ_petition` |
| Appeal | `appeal` |
| Other | `other` |

## Processing Status

| Status | Description |
|--------|-------------|
| `uploaded` | File uploaded, processing not started |
| `extracting_text` | Extracting text from document |
| `ocr_processing` | Running OCR on scanned pages |
| `analyzing` | Parsing legal entities and sections |
| `completed` | Processing complete |
| `failed` | Processing failed |

## Error Responses

All errors follow this format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

Common HTTP status codes:
- `400`: Bad request (invalid file, missing parameters)
- `404`: Resource not found
- `422`: Validation error
- `500`: Internal server error
