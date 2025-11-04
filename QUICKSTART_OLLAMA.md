# 🚀 Quick Start Guide - Clarity with Ollama

## Prerequisites Checklist

- ✅ **Auth0 configured** in `.env`
- ✅ **Ollama installed** and running
- ✅ **nomic-embed-text** installed in Ollama (768-dim embeddings)
- ✅ **gpt-oss** installed in Ollama (LLM generation)

---

## Step 1: Verify Ollama Models

Check that you have the required models:

```powershell
ollama list
```

You should see:
- `nomic-embed-text`
- `gpt-oss`

If missing, install them:
```powershell
ollama pull nomic-embed-text
ollama pull gpt-oss
```

---

## Step 2: Run Health Check

Verify everything is configured:

```powershell
cd c:\Clarity
python health_check.py
```

This will check:
- ✅ Ollama is running and has required models
- ✅ Auth0 credentials are configured
- ✅ Python packages are installed

---

## Step 3: Install Dependencies (First Time Only)

### Backend:
```powershell
cd local_backend
python -m pip install -r requirements.txt
cd ..
```

### Frontend:
```powershell
cd frontend
npm install
cd ..
```

---

## Step 4: Start Clarity!

### Option A: Use Startup Script (Recommended)
```powershell
.\infra\scripts\start_local.ps1
```

### Option B: Manual Start (2 terminals)

**Terminal 1 - Backend:**
```powershell
cd local_backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm run dev
```

---

## Step 5: Open Clarity

Open your browser to: **http://localhost:5173**

You should see:
1. **Home page** with "Welcome to Clarity"
2. **Log In** button (top right)
3. Click **Log In** → Auth0 login page
4. After login → Redirected to **Notebooks** page

---

## Step 6: Test the RAG Pipeline

### 6.1 Upload a Document

1. Click **"+ New Notebook"**
2. Name it (e.g., "Machine Learning")
3. Click **"Upload Document"**
4. Select a PDF, TXT, or Markdown file (try `demo_data/machine_learning_basics.md`)

**What happens:**
- 📄 Document uploaded to `localhost:5000/api/ingest`
- 🔪 Text chunked into 500-token pieces
- 🧮 **Ollama generates embeddings** using nomic-embed-text (768-dim)
- 💾 Vectors stored in ChromaDB at `~/.clarity/chroma/`

### 6.2 Ask a Question

1. Type a question in the input box (e.g., "What is a neural network?")
2. Click **"Ask"**

**What happens:**
- 🧮 **Ollama embeds your question** using nomic-embed-text
- 🔍 ChromaDB searches for similar chunks (cosine similarity)
- 📋 Top 4 chunks retrieved as context
- 🤖 **Ollama generates answer** using gpt-oss with RAG prompt
- ✨ Answer displayed with source chunks!

### 6.3 Generate Quiz

1. Click **"Generate Quiz"** button
2. Select difficulty and number of questions
3. Click **"Generate"**

**What happens:**
- 📚 Top context chunks sent to **Ollama gpt-oss**
- ❓ Multiple-choice questions generated
- 📥 Export as flashcards or PDF

---

## Architecture Overview

```
Your Browser (localhost:5173)
    ↓
Vue Frontend (localhost:5173)
    ↓ HTTP requests
Local FastAPI Backend (localhost:5000)
    ↓ Embeddings & LLM
Ollama (localhost:11434)
    ├── nomic-embed-text (768-dim vectors)
    └── gpt-oss (text generation)
    ↓
ChromaDB (~/.clarity/chroma/)
    └── User collections with embedded documents
```

**100% LOCAL - NO CLOUD AI PROCESSING! 🏠🔒**

---

## What's Wired Up

### ✅ Embeddings (nomic-embed-text via Ollama)
- **File:** `local_backend/app/services/embedder.py`
- **Config:** `EMBEDDING_MODEL=nomic-embed-text` in `.env`
- **Dimension:** 768 (higher quality than MiniLM's 384)
- **Endpoint:** `http://localhost:11434/api/embeddings`
- **Fallback:** sentence-transformers if Ollama unavailable

### ✅ LLM Generation (gpt-oss via Ollama)
- **File:** `local_backend/app/services/llm_wrapper.py`
- **Config:** `LLM_PROVIDER=gpt-oss` in `.env`
- **Endpoint:** `http://localhost:11434/api/generate`
- **Fallback:** MockLLM if Ollama unavailable

### ✅ Auth0 Integration
- **Frontend:** `VITE_AUTH0_DOMAIN` and `VITE_AUTH0_CLIENT_ID` configured
- **File:** `frontend/src/main.js` - Auth0 SDK initialized
- **Usage:** Optional cloud sync only (NOT required for local RAG)

### ✅ ChromaDB Vector Storage
- **Location:** `~/.clarity/chroma/`
- **Collections:** Per-user (e.g., `clarity_user__auth0_123456`)
- **Dimension:** Auto-detected (768 for nomic, 384 for MiniLM)

### ✅ API Endpoints
- `POST /api/ingest` - Upload & embed documents
- `POST /api/ask` - RAG question answering
- `POST /api/generate-quiz` - Quiz generation
- `GET /api/health` - Health check

---

## Troubleshooting

### "Cannot connect to Ollama"
```powershell
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start Ollama
ollama serve
```

### "Model not found"
```powershell
ollama pull nomic-embed-text
ollama pull gpt-oss
```

### "Auth0 callback error"
- Check Auth0 Dashboard → Your App → Settings
- Verify "Allowed Callback URLs" includes `http://localhost:5173/callback`
- Check `.env` has correct `VITE_AUTH0_DOMAIN` and `VITE_AUTH0_CLIENT_ID`

### "Module not found" errors
```powershell
cd local_backend
pip install -r requirements.txt
```

### Port already in use
```powershell
# Find process using port 5000
netstat -ano | findstr :5000

# Kill it (replace PID with actual process ID)
taskkill /PID <PID> /F
```

---

## Environment Variables Summary

Your `.env` is configured with:

```bash
# Auth0 (Frontend & Backend)
AUTH0_DOMAIN=dev-dkxvd0av88nbdm35.eu.auth0.com
AUTH0_CLIENT_ID=b71r2ACgJh5u9RAAYPpBRvAmwEMYAQ7P
VITE_AUTH0_DOMAIN=dev-dkxvd0av88nbdm35.eu.auth0.com
VITE_AUTH0_CLIENT_ID=b71r2ACgJh5u9RAAYPpBRvAmwEMYAQ7P

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
EMBEDDING_MODEL=nomic-embed-text
LLM_PROVIDER=gpt-oss
OLLAMA_LLM_MODEL=gpt-oss

# Local Storage
CLARITY_BASE_DIR=~/.clarity
```

---

## Next Steps

1. ✅ **Run health check**: `python health_check.py`
2. ✅ **Start app**: `.\infra\scripts\start_local.ps1`
3. ✅ **Open browser**: http://localhost:5173
4. ✅ **Log in** with Auth0
5. ✅ **Upload** a document from `demo_data/`
6. ✅ **Ask** questions about your documents
7. ✅ **Generate** quizzes and flashcards

---

## Performance Tips

### Faster Embeddings
- nomic-embed-text is already fast (768-dim)
- Batch processing: 32 texts at a time (configured)

### Faster LLM Generation
- gpt-oss runs on CPU by default
- For faster inference: Use GPU-enabled Ollama
- Adjust `num_predict` in `.env` for shorter responses

### Monitor Resource Usage
```powershell
# Check Ollama logs
ollama logs

# Check disk usage
dir ~/.clarity/chroma/
```

---

## Demo Workflow

1. **Upload** `demo_data/machine_learning_basics.md`
2. **Ask**: "What is supervised learning?"
3. **See**: Answer with source chunks from your document
4. **Generate Quiz**: 5 questions about ML basics
5. **Export**: Flashcards or PDF

**All processing happens on your machine! 🏠**

---

## What's Local vs. Cloud

| Feature | Where It Runs | Data Sent to Cloud? |
|---------|---------------|---------------------|
| Document upload | Local (localhost:5000) | ❌ No |
| Text extraction | Local CPU | ❌ No |
| Chunking | Local CPU | ❌ No |
| Embeddings | Local Ollama (nomic) | ❌ No |
| Vector storage | Local ChromaDB | ❌ No |
| RAG queries | Local Ollama (gpt-oss) | ❌ No |
| Quiz generation | Local Ollama (gpt-oss) | ❌ No |
| Auth0 login | Auth0.com | ✅ Yes (only credentials) |
| Cloud sync | Render.com (optional) | ✅ Yes (only metadata, not docs) |

**Your documents and AI processing stay 100% local! 🔒**

---

## Support

- **Architecture:** See `doc/architecture.md`
- **Setup:** See `SETUP.md`
- **Auth0:** See `AUTH0_SETUP.md`
- **API Docs:** http://localhost:5000/docs (when backend running)

Enjoy your local-first, privacy-focused learning assistant! 🎓✨
