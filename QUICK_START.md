# 🚀 Clarity Quick Start Guide

## Status: ✅ ALL SYSTEMS OPERATIONAL

---

## One-Command Start

### Terminal 1 - Backend:
```powershell
cd C:\Clarity\local_backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
```

### Terminal 2 - Frontend:
```powershell
cd C:\Clarity\frontend
npm run dev
```

### Browser:
Open: http://localhost:5173

---

## What's Working ✅

| Component | Status | Details |
|-----------|--------|---------|
| 🔐 Auth0 | ✅ | dev-dkxvd0av88nbdm35.eu.auth0.com |
| 🧠 Embeddings | ✅ | nomic-embed-text (768-dim) |
| 🤖 LLM | ✅ | gpt-oss:20b (13GB) |
| 💾 ChromaDB | ✅ | ~/.clarity/chroma |
| 🔙 Backend | ✅ | FastAPI on :5000 |
| 🎨 Frontend | ✅ | Vue 3 on :5173 |
| 📄 PDF Parser | ✅ | pdfplumber |

---

## Quick Verification

Run this to check everything:
```powershell
cd C:\Clarity
python verify_system.py
```

---

## URLs

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5000
- **API Docs**: http://localhost:5000/docs
- **Ollama**: http://localhost:11434

---

## Current Configuration

```env
EMBEDDING_MODEL=nomic-embed-text      # 768-dimensional
LLM_PROVIDER=gpt-oss                   # Using Ollama
LLM_MODEL=gpt-oss:20b                  # 13GB model
OLLAMA_BASE_URL=http://localhost:11434
```

---

## What It Does

1. **Upload PDF** → Extract text with pdfplumber
2. **Embed** → Generate 768-dim vectors with nomic-embed-text
3. **Store** → Save to ChromaDB vector database
4. **Query** → Ask questions about your documents
5. **Retrieve** → Find relevant context from ChromaDB
6. **Generate** → Answer with gpt-oss:20b

---

## Models Available

- ✅ `nomic-embed-text:latest` - 274 MB (embeddings)
- ✅ `gpt-oss:20b` - 13 GB (primary LLM)
- ✅ `llama3.2-vision:11b` - Vision model
- ✅ `gemma3:27b` - Alternative LLM

---

## Logs to Watch

Backend startup shows:
```
✅ Using Ollama for embeddings: nomic-embed-text (768-dim)
✅ Using Ollama for LLM: gpt-oss:20b
Initialized LLM: gpt-oss:20b
🚀 Starting Clarity Local Backend
✅ Server is ready!
```

If you see this, everything is working! 🎉

---

## Troubleshooting

**Backend won't start?**
- Make sure you're in `C:\Clarity\local_backend`
- Check if port 5000 is available

**Frontend won't start?**
- Run `npm install` in the frontend folder
- Check if port 5173 is available

**Ollama not responding?**
- Check if Ollama service is running
- Verify: `ollama list` shows your models

**Environment variables not loading?**
- `.env` file is in `C:\Clarity\` (project root)
- Backend loads it from parent directory automatically

---

## 📖 Full Documentation

See `VERIFICATION_REPORT.md` for complete system details and test results.

---

**Ready to use! 🚀**
