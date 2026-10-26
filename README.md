# ⚖️ LegalAI — Intelligent Legal Document Analysis System

> AI-powered Indian Legal Document Analysis System that identifies applicable laws, sections, and relevant case information from legal documents.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)
![React](https://img.shields.io/badge/React-18-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-5-blue)
![LangChain](https://img.shields.io/badge/LangChain-0.2-green)

---

## 🌟 Features

| Feature | Description |
|---------|-------------|
| 📄 **Document Upload** | Support for PDF, DOCX, TXT, and scanned images with OCR |
| 🔍 **Entity Extraction** | Parties, dates, courts, crime categories, evidence, keywords |
| ⚖️ **Section Prediction** | Identify applicable sections from BNS, IPC, IT Act, BNSS, BSA |
| 📝 **Legal Explanations** | Plain English explanations of legal sections |
| 📋 **Summarization** | Short & detailed summaries, key findings, final verdict |
| 🔎 **Similar Cases** | Semantic search for landmark judgments |
| 💬 **Chat Assistant** | Ask questions about your documents |
| 🧠 **RAG Pipeline** | Retrieval-Augmented Generation with vector database |

---

## 📁 Project Structure

```
BolnaAI/
├── frontend/                # React + TypeScript + Tailwind
│   ├── src/
│   │   ├── pages/          # Dashboard, Upload, Chat, Summary, Cases
│   │   ├── components/     # Navbar, FileUploader, ChatBox, SectionCard, etc.
│   │   ├── services/       # API client
│   │   └── App.tsx
│   └── package.json
│
├── backend/                 # FastAPI + Python
│   ├── app/
│   │   ├── api/            # Upload, Summary, Sections, Chat, Cases routes
│   │   ├── services/       # PDF Reader, OCR, Legal Parser, Section Predictor,
│   │   │                   # Summarizer, RAG Engine, Embeddings, Similarity Search
│   │   ├── models/         # Document, Section, Case Pydantic models
│   │   ├── database/       # ChromaDB, SQL database, Vector store
│   │   ├── prompts/        # Summary, Section, Chat prompt templates
│   │   └── main.py         # FastAPI application entry point
│   ├── requirements.txt
│   └── .env
│
├── legal_dataset/           # Legal knowledge base
│   ├── BNS/                # Bharatiya Nyaya Sanhita sections
│   ├── IT_ACT/             # IT Act sections
│   ├── BNSS/               # Bharatiya Nagarik Suraksha Sanhita sections
│   ├── BSA/                # Bharatiya Sakshya Adhiniyam sections
│   ├── Supreme_Court/      # Landmark SC judgments
│   └── High_Court/         # Notable HC judgments
│
├── vector_db/               # ChromaDB persistent storage
├── uploads/                 # Uploaded documents
├── docs/                    # Architecture, API docs, Project report
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Tesseract OCR (for scanned documents)

### 1. Clone & Setup

```bash
git clone <repository-url>
cd BolnaAI
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 4. Start Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### 5. Access Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/v1/docs

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for LLM features | Required |
| `EMBEDDING_MODEL` | Sentence Transformer model | all-MiniLM-L6-v2 |
| `CHROMA_PERSIST_DIR` | ChromaDB storage path | ../vector_db |
| `MAX_UPLOAD_SIZE_MB` | Max file upload size | 50 |
| `CHUNK_SIZE` | Text chunk size for RAG | 1000 |
| `TOP_K_RESULTS` | Number of search results | 5 |

---

## 📚 Legal Knowledge Base

### Supported Acts

| Act | Abbreviation | Effective |
|-----|-------------|-----------|
| Bharatiya Nyaya Sanhita | BNS | July 1, 2024 |
| Indian Penal Code | IPC | 1860 (legacy) |
| Information Technology Act | IT Act | 2000 |
| Bharatiya Nagarik Suraksha Sanhita | BNSS | July 1, 2024 |
| Bharatiya Sakshya Adhiniyam | BSA | July 1, 2024 |

### IPC → BNS Mapping

| IPC Section | BNS Section | Offence |
|-------------|-------------|---------|
| 302 | 103 | Murder |
| 307 | 109 | Attempt to Murder |
| 376 | 63 | Rape |
| 379 | 221 | Theft |
| 420 | 245 | Cheating |
| 498A | 300 | Cruelty by Husband |
| 304B | 299 | Dowry Death |
| 354 | 304 | Outraging Modesty |
| 34 | 387 | Common Intention |

---

## 🏗️ Architecture

```
React Frontend ←→ FastAPI Backend ←→ AI Services
                                    ←→ ChromaDB (Vectors)
                                    ←→ OpenAI (LLM)
                                    ←→ Tesseract (OCR)
```

See [Architecture Documentation](docs/architecture.md) for detailed diagrams.

---

## 📖 API Documentation

Full API documentation available at:
- **Swagger UI**: `http://localhost:8000/api/v1/docs`
- **ReDoc**: `http://localhost:8000/api/v1/redoc`
- **Markdown**: [API Docs](docs/api_docs.md)

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/upload/` | Upload document |
| GET | `/api/v1/upload/{id}` | Get document details |
| GET | `/api/v1/sections/predict/{id}` | Predict legal sections |
| GET | `/api/v1/sections/explain/{act}/{section}` | Explain a section |
| GET | `/api/v1/summary/{id}` | Generate summary |
| POST | `/api/v1/chat/` | Chat with AI assistant |
| POST | `/api/v1/cases/similar` | Find similar cases |

---

## 🛠️ Technology Stack

### Frontend
- React 18 + TypeScript
- Tailwind CSS
- React Router v6
- Axios
- react-dropzone
- react-markdown

### Backend
- FastAPI 0.111
- Pydantic v2
- LangChain
- Sentence Transformers
- ChromaDB
- PyPDF2 + pdfplumber
- pytesseract + EasyOCR

### AI
- OpenAI GPT-4o-mini (LLM)
- all-MiniLM-L6-v2 (Embeddings)
- Tesseract OCR

---

## 📋 Development Roadmap

- [x] Document upload and text extraction
- [x] OCR for scanned documents
- [x] Legal entity extraction
- [x] Section prediction (BNS, IPC, IT Act, BNSS, BSA)
- [x] Summarization engine
- [x] Similar case retrieval
- [x] Chat assistant with RAG
- [x] Frontend dashboard
- [ ] User authentication (JWT)
- [ ] PostgreSQL migration
- [ ] Redis caching
- [ ] Celery background tasks
- [ ] Multi-language support (Hindi)
- [ ] Mobile application
- [ ] Deployment (Docker + K8s)

---

## 📄 License

This project is for educational and research purposes. Legal analysis provided by this system should not be considered as professional legal advice.

---

## 🙏 Acknowledgments

- Supreme Court of India — for landmark judgments that form our knowledge base
- Indian Law Institute — for legal research resources
- Ministry of Law & Justice — for BNS, BNSS, BSA act texts
- OpenAI — for GPT models
- HuggingFace — for Sentence Transformers

---

**⚖️ LegalAI — Making Indian Law Accessible Through AI**
