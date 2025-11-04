# Clarity Architecture

## Overview

Clarity is a **100% local-first, privacy-focused personal learning assistant** that runs like a desktop application. Both the frontend and AI backend execute entirely on the user's machine, with optional cloud sync for multi-device access.

### Core Principle: Local-First
- **Frontend (Vue)**: Runs at `localhost:5173` - talks to local backend
- **Backend (FastAPI)**: Runs at `localhost:5000` - processes everything locally
- **ChromaDB**: Vector database stored in `~/.clarity/chroma/`
- **No Internet Required**: Full functionality offline (embeddings, RAG, quiz generation)
- **Optional Cloud Sync**: Minimal Render service only for metadata backup (NOT documents)

---

## System Components

### 1. Frontend (Vue 3 + Tailwind) - RUNS LOCALLY

**Location:** `frontend/`

**Runs At:** `http://localhost:5173`

**Responsibilities:**
- User interface for notebooks, document upload, Q&A
- Talks to local backend on `localhost:5000` (NOT cloud)
- Optional Auth0 integration (only for sync feature)
- Optional sync trigger to cloud backend (metadata only)
- **Works 100% offline** - no cloud dependency for core features

**Key Technologies:**
- Vue 3 (Composition API)
- Vite (build tool)
- Tailwind CSS + DaisyUI (styling)
- Pinia (state management)
- Axios (HTTP client)
- Auth0 SPA SDK

**Routes:**
- `/` - Homepage (feature list)
- `/callback` - Auth0 callback handler
- `/notebooks` - Notebook list
- `/notebook/:id` - Single notebook view/editor

---

### 2. Local Backend (FastAPI RAG Runtime) - RUNS LOCALLY - THE CORE ENGINE

**Location:** `local_backend/`

**Runs At:** `http://localhost:5000`

**THIS IS WHERE ALL THE MAGIC HAPPENS (ON YOUR MACHINE):**
- Document ingestion (PDF, TXT, Markdown) - **local processing**
- Text chunking (500 tokens, 100 overlap) - **local CPU**
- Embedding generation (nomic-embed-text or MiniLM) - **local model inference**
- Vector storage (ChromaDB) - **local database at ~/.clarity/chroma/**
- RAG query pipeline - **local retrieval + generation**
- Local LLM inference (quiz/summary generation) - **local CPU/GPU**
- Sync coordination with cloud backend - **optional, only for metadata**

**KEY POINT:** This service runs on `localhost` - it's YOUR computer doing the work, not a cloud server.

**Key Technologies:**
- FastAPI + Uvicorn
- ChromaDB (vector database)
- sentence-transformers or nomic-embed-text
- PyPDF2 or pdfplumber (PDF parsing)
- tiktoken (tokenization)

**Storage:**
- Default base: `~/.clarity/`
  - `chroma/` - Vector database
  - `db/` - Optional local SQLite
  - `logs/` - Application logs

**Endpoints:**
- `GET /health` - Health check
- `POST /ingest` - Upload document, chunk, embed
- `POST /ask` - RAG query (question → retrieve → generate)
- `POST /embed` - Debugging endpoint for embeddings
- `POST /generate-quiz` - Generate quiz from topic
- `POST /sync/push` - Push local state to cloud
- `GET /sync/pull` - Pull cloud state to local

---

### 3. Cloud Sync Backend (Render + Postgres) - OPTIONAL - MINIMAL SERVICE

**Location:** `render_backend/`

**Runs At:** `https://your-app.onrender.com` (only when you enable sync)

**IMPORTANT - WHAT THIS SERVICE DOES NOT DO:**
- ❌ Does NOT process your documents
- ❌ Does NOT run AI models
- ❌ Does NOT store your PDFs or embeddings
- ❌ Does NOT perform RAG queries
- ❌ Is NOT required for Clarity to work

**What It Actually Does:**
- ✅ Stores notebook metadata (titles, timestamps, settings)
- ✅ Syncs notebook structure across devices
- ✅ Validates Auth0 JWTs (for security)
- ✅ Handles conflicts (last-write-wins)
- ✅ **Think of it as a simple bookmark sync service**

**Your documents, embeddings, and AI processing NEVER touch this service.**

**Key Technologies:**
- FastAPI
- SQLAlchemy + asyncpg
- PostgreSQL (Render managed)
- python-jose (JWT validation)

**Database Schema:**

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    auth0_sub VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE notebooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id),
    title VARCHAR(500),
    metadata JSONB,
    content_snapshot JSONB,
    last_sync TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE sync_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(50),
    timestamp TIMESTAMP DEFAULT NOW(),
    details JSONB
);
```

**Endpoints:**
- `POST /api/sync` - Store updated notebook state
- `GET /api/sync?user_id={id}` - Retrieve latest state

---

## Data Flow - ALL LOCAL!

### Document Ingestion Flow (100% on Your Machine)

```
User uploads PDF
    ↓
Frontend (localhost:5173) → POST localhost:5000/ingest
    ↓
Local Backend (localhost:5000):
    1. Parse PDF → extract text (LOCAL - on your CPU)
    2. Chunk text (500 tokens, 100 overlap) (LOCAL - on your CPU)
    3. Generate embeddings (batch of 32) (LOCAL - sentence-transformers model)
    4. Store in ChromaDB (LOCAL - ~/.clarity/chroma/)
    ↓
Response: {document_id, num_chunks, status: "success"}

🔒 YOUR PDF NEVER LEAVES YOUR COMPUTER
🔒 Embeddings computed locally
🔒 Vector DB stored locally
☁️ Cloud is NEVER involved in this process
```

### RAG Query Flow (100% on Your Machine)

```
User asks question
    ↓
Frontend (localhost:5173) → POST localhost:5000/ask {user_id, question, top_k=4}
    ↓
Local Backend (localhost:5000):
    1. Embed question (LOCAL - sentence-transformers)
    2. Query ChromaDB (LOCAL - cosine similarity search)
    3. Retrieve top-k chunks (LOCAL - from ~/.clarity/chroma/)
    4. Build prompt with context (LOCAL - string manipulation)
    5. Call local LLM (LOCAL - gpt-oss or mock on your CPU/GPU)
    6. Return answer + source chunks
    ↓
Response: {answer, source_chunks: [{id, score, text}], used_prompt}

🔒 Question embedding: LOCAL
🔒 Vector search: LOCAL
🔒 LLM inference: LOCAL
☁️ No cloud API calls for AI processing
```

### Sync Flow (OPTIONAL - Only Metadata)

```
User clicks "Sync" (OPTIONAL feature)
    ↓
Frontend → POST localhost:5000/sync/push (JWT in header)
    ↓
Local Backend:
    1. Gather notebook METADATA ONLY (titles, settings, timestamps)
    2. Call Render API: POST https://your-app.onrender.com/api/sync
    ↓
Render Backend (Cloud):
    1. Validate JWT (Auth0)
    2. Check last_sync timestamp
    3. Merge or conflict resolution
    4. Update Postgres (METADATA ONLY)
    ↓
Response: {status: "synced", conflicts: []}

📌 WHAT GETS SYNCED: Notebook titles, creation dates, settings
🔒 WHAT NEVER GETS SYNCED: PDFs, embeddings, ChromaDB, document content
☁️ Cloud only sees: "User has notebook named 'ML Notes' created on 2025-01-01"
🏠 Your documents stay: In ~/.clarity/ on your machine
```

---

## Authentication Flow (Auth0)

1. **User clicks "Login"** → Frontend redirects to Auth0
2. **Auth0 login page** → User authenticates
3. **Redirect to callback** → `http://localhost:5173/callback?code=...`
4. **Frontend exchanges code** → Gets access token + ID token
5. **Store tokens** → Pinia store + localStorage
6. **API calls** → Include `Authorization: Bearer <token>` header
7. **Backend validation** → Verify JWT signature, claims, expiry

---

## Embedding Strategy

### Primary: nomic-embed-text
- **Dimensions:** 768
- **Advantages:** High quality, trained for retrieval
- **Fallback:** If not available, use MiniLM

### Fallback: all-MiniLM-L6-v2
- **Dimensions:** 384
- **Advantages:** Fast, lightweight, good for general use

### Auto-detection Logic

```python
try:
    from nomic import embed
    EMBEDDER = "nomic-embed-text"
except ImportError:
    from sentence_transformers import SentenceTransformer
    EMBEDDER = "all-MiniLM-L6-v2"
```

---

## LLM Wrapper Design

**Interface:** `LLMInterface` (abstract base class)

**Implementations:**
- `MockLLM` - Returns hardcoded responses (for demo)
- `GPTOSSAdapter` - Integrates gpt-oss (local inference)
- `GeminiAdapter` - Google Gemini API (future)
- `OpenAIAdapter` - OpenAI API (future)

**Configuration via env:**
```bash
LLM_PROVIDER=mock  # or gpt-oss, gemini, openai
LLM_MODEL=gpt-oss
LLM_API_KEY=optional
```

---

## Chunking Policy

- **Strategy:** Fixed token count with overlap
- **Chunk size:** 500 tokens (~3500 characters)
- **Overlap:** 100 tokens
- **Sentence boundary preservation:** Use spaCy or regex to split at sentence end when possible

**Configurable via env:**
```bash
CLARITY_CHUNK_SIZE=500
CLARITY_CHUNK_OVERLAP=100
```

---

## Sync Conflict Resolution

**MVP Strategy: Last-Write-Wins**

1. Client sends `last_updated` timestamp per notebook
2. Server compares with stored `updated_at`
3. If client timestamp > server → accept update
4. If server timestamp > client → respond with conflict + server version
5. Client can choose to overwrite or merge manually

**Future:** Operational Transform or CRDT for fine-grained merging

---

## Security Considerations

1. **Local data encryption:** Future enhancement (encrypt chroma db with user password)
2. **JWT validation:** Both backends verify Auth0 tokens
3. **CORS:** Local backend allows `http://localhost:5173`; Render backend allows deployed frontend origin
4. **Rate limiting:** Add throttling to prevent abuse (future)
5. **Input sanitization:** Validate all user inputs, prevent injection attacks

---

## Performance Optimizations

1. **Batch embedding:** Process 32 texts at once
2. **Async ChromaDB queries:** Use async wrappers where available
3. **Lazy model loading:** Load embedder/LLM on first use, not at startup
4. **Caching:** Cache frequent queries (future)
5. **Progressive loading:** Load notebooks incrementally in frontend

---

## Monitoring & Observability

- **Structured JSON logs:** All services log to stdout + local files
- **Sentry integration:** Optional error tracking (SENTRY_DSN in .env)
- **Health checks:** `/health` endpoint for uptime monitoring
- **Metrics:** Future: Prometheus exporter for request counts, latency

---

## Development Workflow

### Local Development

1. Start local backend: `uvicorn app.main:app --reload --port 5000`
2. Start frontend: `npm run dev` (port 5173)
3. Access app: `http://localhost:5173`

### Testing

- **Backend:** `pytest tests/`
- **Frontend:** `npm run test` (vitest)
- **E2E:** Future: Playwright tests

### CI/CD

GitHub Actions pipeline:
1. Lint (ruff, eslint)
2. Unit tests (pytest, vitest)
3. Build Docker images
4. Deploy to Render (on merge to main)

---

## Deployment

### Local Backend
- Runs on user's machine (localhost:5000)
- No external deployment needed

### Frontend
- Build: `npm run build`
- Deploy to: Vercel, Netlify, Cloudflare Pages
- Or serve locally: `npm run preview`

### Render Backend
- Push to GitHub
- Render auto-deploys via `render.yaml`
- Provisions PostgreSQL automatically
- Set env vars in Render dashboard

---

## Future Enhancements

1. **Mobile app:** React Native or Flutter
2. **Real-time collaboration:** WebSocket sync
3. **Advanced LLM:** Support Llama 3, Mistral, etc.
4. **Scholar API integration:** Auto-fetch papers from arXiv, PubMed
5. **Spaced repetition:** Built-in flashcard scheduler
6. **Export formats:** Anki, Quizlet, PDF
7. **Voice input:** Whisper integration for audio notes
8. **Multi-modal:** Image/diagram understanding with vision models

---

## 2-Minute Demo Script (for Judges)

**Title:** "Clarity: Your Private AI Learning Assistant"

1. **[0:00-0:20] Intro**
   - "Clarity is a local-first learning assistant that respects your privacy."
   - "All AI inference happens on your machine. Your documents never leave your computer unless you sync."

2. **[0:20-0:45] Auth Flow**
   - Open homepage → Click "Get Started"
   - Auth0 login → Redirect back to app
   - "Secure authentication via Auth0, industry standard."

3. **[0:45-1:10] Document Ingestion**
   - Click "Upload Document"
   - Drag-drop a PDF (demo: machine learning paper)
   - Show progress: "Chunking → Embedding → Storing in ChromaDB"
   - "Behind the scenes: 500-token chunks, nomic embeddings, local vector DB."

4. **[1:10-1:35] RAG Query**
   - Ask question: "What is gradient descent?"
   - Show answer with source chunks highlighted
   - "RAG pipeline retrieves relevant context, local LLM generates answer."

5. **[1:35-1:50] Quiz Generation**
   - Click "Generate Quiz"
   - Show multiple-choice questions
   - "AI-generated quizzes help reinforce learning."

6. **[1:50-2:00] Sync**
   - Click "Sync to Cloud"
   - "Optional: sync notebooks across devices via Render + Postgres."
   - "But your documents stay local. Only metadata syncs."

**Closing:** "Clarity: Learn smarter, stay private. Thank you!"

---

## Technologies Summary

| Layer | Technology |
|-------|------------|
| Frontend | Vue 3, Vite, Tailwind, Pinia, Auth0 SDK |
| Local Backend | FastAPI, ChromaDB, nomic-embed-text, gpt-oss |
| Cloud Backend | FastAPI, PostgreSQL, SQLAlchemy, Auth0 JWT |
| Deployment | Render (cloud), Docker, GitHub Actions |
| Storage | ChromaDB (vectors), Postgres (metadata), local filesystem |

---

**Questions?** See README.md or open an issue on GitHub.
