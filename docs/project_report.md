# LegalAI — Project Report

## Project Overview

**LegalAI** is an AI-powered Indian Legal Document Analysis System that automates the analysis of legal documents, identifies applicable laws and sections, generates summaries, and retrieves similar cases from a legal knowledge base.

## Problem Statement

Indian legal professionals deal with massive volumes of documents — judgments, FIRs, charge sheets, petitions, and contracts. Manual analysis is:
- **Time-consuming**: Reading and understanding complex legal text takes hours
- **Error-prone**: Missing applicable sections or relevant precedents
- **Inaccessible**: Legal jargon makes documents incomprehensible for common citizens
- **Disconnected**: Finding similar cases requires extensive manual research

## Solution

LegalAI addresses these challenges through:

1. **Automated Text Extraction**: OCR + PDF parsing for any document format
2. **Entity Recognition**: Extract parties, dates, courts, crime categories, evidence
3. **Legal Section Prediction**: Identify applicable sections from BNS, IPC, IT Act, BNSS, BSA
4. **Plain English Explanations**: Convert legal jargon to accessible language
5. **AI Summarization**: Generate short and detailed summaries with key findings
6. **Similar Case Retrieval**: Find landmark judgments using semantic search
7. **Conversational Interface**: Ask questions about documents in natural language

## Technology Decisions

### Frontend: React + TypeScript + Tailwind CSS
- **React**: Component-based architecture, rich ecosystem
- **TypeScript**: Type safety, better IDE support, fewer runtime errors
- **Tailwind CSS**: Rapid UI development, consistent design system
- **Vite**: Fast development server and build tool

### Backend: FastAPI + Python
- **FastAPI**: High-performance async framework, automatic OpenAPI docs
- **Pydantic v2**: Fast data validation with type hints
- **Python**: Dominant language for AI/ML ecosystem
- **Background Tasks**: Non-blocking document processing

### AI Stack
- **LangChain**: Orchestration of LLM calls and RAG pipeline
- **Sentence Transformers**: Local embedding generation (all-MiniLM-L6-v2)
- **ChromaDB**: Persistent, lightweight vector database
- **OpenAI GPT-4o-mini**: Cost-effective LLM for reasoning tasks
- **Tesseract + EasyOCR**: Dual OCR approach for maximum coverage

## Key Features Implemented

### 1. Document Processing Pipeline
```
File Upload → Format Detection → Text Extraction → OCR (if needed) → 
Entity Parsing → Section Matching → Vector Indexing
```

### 2. Legal Section Database
Comprehensive database covering:
- **BNS**: 30+ sections (replacing IPC from July 2024)
- **IPC**: 15+ commonly referenced sections (legacy cases)
- **IT Act**: 12 sections covering cybercrime
- **BNSS**: 12 procedural sections (replacing CrPC)
- **BSA**: 9 evidence law sections (replacing Evidence Act)

### 3. Dual Prediction Strategy
- **Direct Reference Extraction** (95% confidence): Sections explicitly mentioned in text
- **Keyword-Based Prediction** (50-90% confidence): Contextual matching from crime descriptions

### 4. RAG Pipeline
```
User Question → Query Embedding → ChromaDB Search → Context Retrieval → 
Prompt Augmentation → LLM Generation → Response
```

### 5. Similarity Search
- 16 landmark cases indexed in vector store
- Semantic similarity using cosine distance
- Keyword-based fallback when vector search unavailable
- Outcome and key holdings display

## Performance Considerations

| Operation | Estimated Time |
|-----------|---------------|
| PDF Text Extraction | 1-5 seconds |
| OCR Processing | 5-30 seconds per page |
| Entity Extraction | < 1 second |
| Section Prediction | < 2 seconds |
| Summary Generation | 5-15 seconds (LLM) |
| Similar Case Search | < 2 seconds |
| Chat Response | 3-10 seconds (LLM) |

## Testing Strategy

### Unit Tests
- Legal parser entity extraction
- Section prediction accuracy
- Text chunking logic
- Embedding generation

### Integration Tests
- Full upload → process → analyze pipeline
- RAG pipeline end-to-end
- API endpoint validation

### Manual Testing
- Upload various document formats
- Verify OCR quality
- Test chat responses
- Validate section explanations

## Deployment Architecture

### Development
```bash
# Backend
cd backend && uvicorn app.main:app --reload

# Frontend
cd frontend && npm run dev
```

### Production (Docker)
```yaml
services:
  backend:
    build: ./backend
    ports: ["8000:8000"]
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - uploads:/app/uploads
      - vector_db:/app/vector_db

  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    depends_on: [backend]
```

### Production Checklist
- [ ] Replace SQLite with PostgreSQL
- [ ] Add authentication (JWT)
- [ ] Configure Redis for caching
- [ ] Set up Celery for background tasks
- [ ] Add rate limiting
- [ ] Configure HTTPS
- [ ] Set up monitoring (Prometheus + Grafana)
- [ ] Add logging aggregation
- [ ] Implement backup strategy for vector DB

## Known Limitations

1. **In-Memory Document Store**: Current implementation uses in-memory storage; data lost on restart
2. **OpenAI Dependency**: LLM features require OpenAI API key
3. **OCR Quality**: Depends on document image quality
4. **Section Database**: Limited to most common sections; comprehensive coverage requires full act data
5. **No Authentication**: No user authentication or authorization
6. **Single Language**: Currently supports English documents only
7. **No Batch Processing**: One document at a time

## Future Enhancements

1. **Full Database Migration**: SQLAlchemy models with PostgreSQL
2. **User Authentication**: JWT-based auth with role-based access
3. **Multi-language Support**: Hindi and regional language documents
4. **Batch Processing**: Upload and analyze multiple documents
5. **Fine-tuned Models**: Train custom models on Indian legal corpus
6. **Real-time Collaboration**: Multiple users analyzing same document
7. **Legal Research API**: Public API for legal research integration
8. **Mobile Application**: React Native mobile client
9. **Citation Network**: Build and visualize case citation networks
10. **Compliance Checker**: Automated compliance checking for contracts

## Conclusion

LegalAI demonstrates the potential of AI in transforming legal document analysis in India. The system successfully combines modern AI techniques (LLMs, embeddings, RAG) with domain-specific legal knowledge to provide actionable insights for legal professionals and citizens alike.

---

**Built with**: Python, FastAPI, React, TypeScript, LangChain, ChromaDB, Sentence Transformers, Tailwind CSS

**Developed for**: Indian Legal System Analysis

**Date**: June 2026
