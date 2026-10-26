# LegalAI — System Architecture

## Overview

LegalAI is an AI-powered Indian Legal Document Analysis System designed to analyze legal documents, identify applicable laws, generate summaries, and find similar cases. The system follows clean architecture principles with clear separation of concerns.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │Dashboard │ │ Upload   │ │  Chat    │ │  Cases   │  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘  │
│       │             │            │             │         │
│  ┌────┴─────────────┴────────────┴─────────────┴─────┐  │
│  │              API Service Layer (axios)             │  │
│  └────────────────────────┬──────────────────────────┘  │
└───────────────────────────┼─────────────────────────────┘
                            │ HTTP/REST
┌───────────────────────────┼─────────────────────────────┐
│                    BACKEND (FastAPI)                      │
│  ┌────────────────────────┴──────────────────────────┐  │
│  │              API Router Layer                      │  │
│  │  upload.py | summary.py | sections.py | chat.py   │  │
│  │                    cases.py                        │  │
│  └────────────────────────┬──────────────────────────┘  │
│                           │                              │
│  ┌────────────────────────┴──────────────────────────┐  │
│  │              Service Layer                         │  │
│  │  ┌────────────┐ ┌────────────┐ ┌──────────────┐  │  │
│  │  │ PDF Reader │ │ OCR Engine │ │ Legal Parser │  │  │
│  │  └────────────┘ └────────────┘ └──────────────┘  │  │
│  │  ┌────────────┐ ┌────────────┐ ┌──────────────┐  │  │
│  │  │  Section   │ │ Summarizer │ │  RAG Engine  │  │  │
│  │  │ Predictor  │ │            │ │              │  │  │
│  │  └────────────┘ └────────────┘ └──────────────┘  │  │
│  │  ┌────────────┐ ┌────────────┐ ┌──────────────┐  │  │
│  │  │ Embeddings │ │ Similarity │ │  Vector      │  │  │
│  │  │  Service   │ │  Search    │ │  Store       │  │  │
│  │  └────────────┘ └────────────┘ └──────────────┘  │  │
│  └────────────────────────┬──────────────────────────┘  │
│                           │                              │
│  ┌────────────────────────┴──────────────────────────┐  │
│  │              Data Layer                            │  │
│  │  ┌────────────┐ ┌────────────┐ ┌──────────────┐  │  │
│  │  │ ChromaDB   │ │  SQLite    │ │  File System │  │  │
│  │  │ (Vectors)  │ │  (Meta)    │ │  (Uploads)   │  │  │
│  │  └────────────┘ └────────────┘ └──────────────┘  │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────┐
│              EXTERNAL SERVICES                           │
│  ┌────────────┐ ┌────────────┐ ┌──────────────┐        │
│  │ OpenAI API │ │ HuggingFace│ │  Tesseract   │        │
│  │ (GPT-4o)   │ │ (Embedding)│ │  (OCR)       │        │
│  └────────────┘ └────────────┘ └──────────────┘        │
└─────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend Layer

| Component | Technology | Purpose |
|-----------|-----------|---------|
| UI Framework | React 18 + TypeScript | SPA with reactive UI |
| Styling | Tailwind CSS | Utility-first CSS |
| State Management | React Hooks + Context | Component state |
| HTTP Client | Axios | API communication |
| Routing | React Router v6 | Client-side routing |
| File Upload | react-dropzone | Drag-and-drop uploads |
| Markdown | react-markdown | Render AI responses |

### Backend Layer

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Web Framework | FastAPI | Async REST API |
| Data Validation | Pydantic v2 | Request/response schemas |
| Background Tasks | FastAPI BackgroundTasks | Document processing |
| CORS | Starlette middleware | Cross-origin requests |

### AI/ML Layer

| Component | Technology | Purpose |
|-----------|-----------|---------|
| LLM | OpenAI GPT-4o-mini | Summarization, chat, reasoning |
| Embeddings | Sentence Transformers (all-MiniLM-L6-v2) | Vector embeddings |
| Vector DB | ChromaDB | Persistent vector storage |
| OCR | Tesseract + EasyOCR | Text extraction from images |
| RAG | LangChain | Retrieval-Augmented Generation |

### Data Flow

1. **Document Upload**: File → FastAPI → PDF Reader/OCR → Text Extraction → Legal Parser → Entity Extraction → ChromaDB Indexing
2. **Section Prediction**: Text → Keyword Extraction → Section Database Matching → Confidence Scoring → Response
3. **Summarization**: Text → LLM (with prompt) → Short/Detailed Summary → Key Findings → Verdict
4. **Chat**: Question → Embed Query → ChromaDB Search → Context Retrieval → LLM → Response
5. **Similar Cases**: Query → Embed → Vector Search → ChromaDB → Ranked Results

## Design Principles

1. **Clean Architecture**: Separation of API, Service, and Data layers
2. **Dependency Injection**: FastAPI's DI system for service instances
3. **Async-First**: All I/O operations are async for performance
4. **Graceful Degradation**: Fallback to extractive methods when LLM unavailable
5. **Type Safety**: Full Pydantic validation on all API endpoints
6. **Singleton Pattern**: Service instances are shared singletons

## Scalability Considerations

- **Horizontal**: FastAPI supports async, deploy behind Gunicorn with multiple workers
- **Database**: Migrate from SQLite to PostgreSQL for production
- **Vector DB**: ChromaDB can be replaced with Pinecone/Weaviate for cloud scale
- **File Storage**: Replace local filesystem with S3/MinIO
- **Caching**: Add Redis for API response caching
- **Queue**: Replace BackgroundTasks with Celery for heavy processing

## Security

- CORS configured for allowed origins only
- File type and size validation on upload
- API key configuration via environment variables
- No sensitive data in logs (loguru configured)
- Input sanitization on all endpoints
