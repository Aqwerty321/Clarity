# 📁 Complete Project Structure

## Overview

This document shows the complete file structure of Clarity with the **local-first architecture**.

```
Clarity/
│
├── 📄 Documentation (New Architecture)
│   ├── ARCHITECTURE.md                    ⭐ Main architecture doc
│   ├── LOCAL_FIRST_ARCHITECTURE.md        ⭐ Implementation details
│   ├── LOCAL_FIRST_COMPLETE.md            ⭐ Summary & verification
│   ├── FRONTEND_INTEGRATION.md            ⭐ Frontend code guide
│   ├── DEPLOYMENT.md                      Updated for sync service
│   ├── DEPLOYMENT_READY.md                Updated for local-first
│   ├── DEPLOYMENT_CHECKLIST.md            Pre-deployment checks
│   ├── ENVIRONMENT_VARIABLES.md           All env vars explained
│   └── README.md                          Project overview
│
├── 🔧 Deployment Configuration
│   ├── render.yaml                        ⭐ Sync service config (not AI backend)
│   ├── Dockerfile                         ⭐ Sync service container
│   ├── .env.example                       Local development template
│   ├── .env.production.example            Production template
│   ├── .gitignore                         Git ignore rules
│   ├── start.sh                           Render startup script
│   ├── start-dev.sh                       Local dev quick start
│   └── stop-dev.sh                        Stop all services
│
├── 🎨 Frontend (Vue 3 PWA)
│   └── frontend/
│       ├── src/
│       │   ├── main.js                    App entry point
│       │   ├── App.vue                    Root component
│       │   ├── router.js                  Vue Router
│       │   │
│       │   ├── pages/
│       │   │   ├── Home.vue              Dashboard
│       │   │   ├── Notebooks.vue         Notebook management
│       │   │   ├── Quizzes.vue           Quiz interface
│       │   │   ├── Settings.vue          ⭐ AI model settings
│       │   │   ├── Marketplace.vue       Theme marketplace
│       │   │   └── Leaderboard.vue       Gamification
│       │   │
│       │   ├── components/
│       │   │   ├── QuickNav.vue          Navigation sidebar
│       │   │   ├── NotebookEditor.vue    Markdown editor
│       │   │   ├── ChatInterface.vue     Q&A interface
│       │   │   ├── QuizGenerator.vue     Quiz component
│       │   │   └── SyncStatus.vue        ⭐ Sync indicator (to be added)
│       │   │
│       │   ├── api/                      ⭐ NEW FOLDER
│       │   │   └── clients.js            ⭐ Dual API clients (to be added)
│       │   │
│       │   ├── stores/
│       │   │   ├── auth.js               Auth0 state
│       │   │   ├── notebooks.js          Notebook state
│       │   │   └── gamification.js       Points & streaks
│       │   │
│       │   └── assets/                   Static assets
│       │
│       ├── public/                       Public files
│       ├── package.json                  Dependencies
│       ├── vite.config.js                Vite configuration
│       └── tailwind.config.js            Tailwind CSS
│
├── 🤖 Local AI Backend (Runs on User's Machine)
│   └── local_backend/
│       ├── app/
│       │   ├── main.py                   FastAPI app (updated CORS)
│       │   ├── models.py                 Database models
│       │   │
│       │   ├── routers/
│       │   │   ├── embed.py              Embedding generation
│       │   │   ├── query.py              RAG queries
│       │   │   ├── quiz.py               Quiz generation
│       │   │   ├── notebooks.py          Notebook management
│       │   │   └── conversation.py       Conversation history
│       │   │
│       │   └── utils/
│       │       ├── rag.py                RAG implementation
│       │       ├── embeddings.py         Embedding utils
│       │       ├── ollama_client.py      Ollama integration
│       │       └── chroma_client.py      ChromaDB client
│       │
│       ├── requirements.txt              Python dependencies
│       └── tests/                        Unit tests
│
├── ☁️ Cloud Sync Service (Optional, Minimal)
│   └── sync_service/                     ⭐ NEW FOLDER
│       ├── main.py                       ⭐ Sync service (NO AI)
│       ├── requirements.txt              ⭐ Minimal dependencies
│       └── README.md                     ⭐ Sync service docs (to be added)
│
├── 🔄 CI/CD
│   └── .github/
│       └── workflows/
│           └── deploy.yml                GitHub Actions
│
├── 🗄️ Database (Local PostgreSQL)
│   └── migrations/                       Alembic migrations (future)
│
└── 📦 Local Data Storage
    └── .clarity/                         (gitignored)
        ├── chroma/                       Vector database
        └── uploads/                      User files

```

## File Count Summary

| Category | Files | Purpose |
|----------|-------|---------|
| **Documentation** | 9 | Architecture, deployment, guides |
| **Configuration** | 9 | Docker, Render, scripts |
| **Frontend** | ~30 | Vue 3 PWA components |
| **Local Backend** | ~20 | FastAPI AI backend |
| **Sync Service** | 2 | ⭐ New minimal sync service |
| **CI/CD** | 1 | GitHub Actions |
| **Total** | ~70 | Complete application |

## Key Files by Purpose

### 🎯 Architecture Understanding
1. `ARCHITECTURE.md` - **Start here** for complete overview
2. `LOCAL_FIRST_ARCHITECTURE.md` - Deep dive into implementation
3. `LOCAL_FIRST_COMPLETE.md` - Verification & summary
4. `FRONTEND_INTEGRATION.md` - Frontend code examples

### 🚀 Deployment
1. `DEPLOYMENT_READY.md` - Quick start guide
2. `DEPLOYMENT.md` - Complete deployment steps
3. `DEPLOYMENT_CHECKLIST.md` - Pre-flight checklist
4. `render.yaml` - Render configuration
5. `Dockerfile` - Container configuration

### 💻 Development
1. `start-dev.sh` - Start all services locally
2. `stop-dev.sh` - Stop all services
3. `.env.example` - Environment template
4. `local_backend/app/main.py` - Backend entry point
5. `frontend/src/main.js` - Frontend entry point

### ⭐ New Architecture Files
1. `sync_service/main.py` - Cloud sync service (NEW)
2. `sync_service/requirements.txt` - Sync dependencies (NEW)
3. `frontend/src/api/clients.js` - Dual API setup (TO ADD)
4. `frontend/src/components/SyncStatus.vue` - Sync UI (TO ADD)

## Data Flow Diagram

```
┌─────────────────────────────────────────────────┐
│         USER'S BROWSER                           │
│                                                  │
│  Frontend (Vue 3)                                │
│  - localhost:5173                                │
│  - Service Worker (offline support)              │
│  - IndexedDB (offline cache)                     │
└────────────┬─────────────────┬───────────────────┘
             │                 │
             │ AI ops          │ Sync (optional)
             ▼                 ▼
┌─────────────────────┐  ┌──────────────────────┐
│  Local Backend      │  │  Cloud Sync Service  │
│  localhost:5000     │  │  Render (optional)   │
│  ─────────────      │  │  ──────────────      │
│  • Ollama           │  │  • Auth0 JWT         │
│  • ChromaDB         │  │  • Text backup       │
│  • PostgreSQL       │  │  • Settings sync     │
│  • RAG queries      │  │  • NO AI             │
│  • Quiz gen         │  │  • NO vectors        │
└─────────────────────┘  └──────────────────────┘
```

## Size Breakdown

### Frontend
```
Vue Components:     ~15 files (~3KB each)     ~45KB
Pages:              ~7 files  (~5KB each)     ~35KB
Stores:             ~3 files  (~2KB each)     ~6KB
Router & Main:      ~3 files  (~2KB each)     ~6KB
Total:              ~28 files                 ~92KB
```

### Local Backend
```
Main App:           ~3 files  (~5KB each)     ~15KB
Routers:            ~5 files  (~3KB each)     ~15KB
Utils:              ~5 files  (~4KB each)     ~20KB
Models:             ~2 files  (~3KB each)     ~6KB
Total:              ~15 files                 ~56KB
```

### Sync Service (New)
```
Main:               1 file    (~400 lines)    ~15KB
Requirements:       1 file                     ~1KB
Total:              2 files                    ~16KB
```

### Documentation (New)
```
Architecture:       4 files   (~3000 lines)   ~120KB
Deployment:         5 files   (~2500 lines)   ~100KB
Total:              9 files   (~5500 lines)   ~220KB
```

## Environment Files

### Development (`.env`)
```bash
# Local development configuration
DATABASE_URL=postgresql://postgres:password@localhost/clarity_db
OLLAMA_BASE_URL=http://localhost:11434
AUTH0_DOMAIN=dev-xxx.auth0.com
VITE_LOCAL_BACKEND_URL=http://localhost:5000
```

### Production Frontend (`.env.production`)
```bash
# Frontend still talks to local backend!
VITE_LOCAL_BACKEND_URL=http://localhost:5000
VITE_SYNC_SERVICE_URL=https://clarity-sync.onrender.com
VITE_AUTH0_DOMAIN=your-domain.auth0.com
```

### Production Sync Service (Render)
```bash
# Sync service environment
DATABASE_URL=<RENDER_POSTGRESQL_URL>
AUTH0_DOMAIN=your-domain.auth0.com
AUTH0_API_AUDIENCE=https://your-api
CORS_ORIGINS=https://your-app.vercel.app
```

## Dependencies

### Frontend
```json
{
  "vue": "^3.3.11",
  "vue-router": "^4.2.5",
  "pinia": "^2.1.7",
  "@auth0/auth0-vue": "^2.3.2",
  "axios": "^1.6.2",
  "marked": "^11.0.0"
}
```

### Local Backend
```txt
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
chromadb==0.4.18
ollama==0.1.0
langchain==0.1.0
```

### Sync Service (New - Minimal)
```txt
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
PyJWT==2.8.0
```

**Note**: No ChromaDB, no Ollama, no LangChain in sync service!

## Ports Used

| Service | Port | Required | Purpose |
|---------|------|----------|---------|
| Frontend | 5173 | ✅ Yes | User interface |
| Local Backend | 5000 | ✅ Yes | AI operations |
| Ollama | 11434 | ✅ Yes | Local AI models |
| PostgreSQL | 5432 | ✅ Yes | Local database |
| Sync Service | 8000 | ⚠️ Optional | Cloud sync |

## Storage Locations

### Local Storage
```
~/.clarity/
├── chroma/                    Vector database
│   ├── index/                 Vector indexes
│   └── data/                  Embeddings
│
├── uploads/                   User files
│   ├── pdfs/                  PDF documents
│   └── images/                Images
│
└── models/                    Ollama models
    ├── llama3.1/              LLM model
    └── nomic-embed-text/      Embedding model
```

### Cloud Storage (Optional)
```
Render PostgreSQL:
├── users                      User accounts
├── notebook_sync              Notebook backups (text only)
├── conversation_sync          Conversation history
└── user_settings              Settings sync
```

**Note**: No vectors, no models, no documents in cloud!

## Git Status

### Tracked Files
```bash
# Configuration
render.yaml, Dockerfile, .github/workflows/

# Documentation
*.md files (9 files)

# Source code
frontend/src/**, local_backend/**, sync_service/**

# Scripts
start-dev.sh, stop-dev.sh, start.sh
```

### Ignored Files (.gitignore)
```bash
# Sensitive
.env, .env.local

# Generated
node_modules/, venv/, __pycache__/

# Data
.clarity/, chroma/, *.db

# Build
dist/, build/
```

## Next Steps for Frontend Integration

### 1. Create API Clients
```bash
# Create new file
touch frontend/src/api/clients.js

# Follow FRONTEND_INTEGRATION.md for code
```

### 2. Add Sync Status Component
```bash
# Create new file
touch frontend/src/components/SyncStatus.vue

# Add sync status indicator
```

### 3. Update Pages
```bash
# Update these files:
- frontend/src/pages/Notebooks.vue    (dual API calls)
- frontend/src/pages/Settings.vue     (sync toggle)
- frontend/src/App.vue                (sync status)
```

### 4. Add Environment Variables
```bash
# Update .env
VITE_LOCAL_BACKEND_URL=http://localhost:5000
VITE_SYNC_SERVICE_URL=  # Leave empty for local-only
```

## Summary

The project now has a **complete local-first architecture**:

1. ✅ **Local Backend** (`local_backend/`) - All AI operations
2. ✅ **Sync Service** (`sync_service/`) - Optional metadata backup
3. ✅ **Frontend** (`frontend/`) - Talks to both (AI local, sync optional)
4. ✅ **Documentation** (9 files) - Complete guides
5. ✅ **Deployment** - Correct configuration for sync-only cloud

**Total Lines of Code (New)**:
- Sync Service: ~400 lines
- Documentation: ~5,500 lines
- Configuration Updates: ~100 lines
- **Total: ~6,000 lines** ✨

---

**Next**: Review `ARCHITECTURE.md` and start integrating the dual API setup in the frontend!
