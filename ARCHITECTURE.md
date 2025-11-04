# Clarity Architecture - Local-First Design

## Overview

Clarity is designed as a **local-first application** where all AI processing happens on the user's machine. The cloud infrastructure provides only **optional sync and backup** services.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    USER'S MACHINE (LOCAL)                    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │              Vue 3 Frontend (PWA)                  │    │
│  │  - Works offline (service worker)                  │    │
│  │  - Local state management                          │    │
│  │  - IndexedDB for offline data                      │    │
│  └────────────────┬───────────────────────────────────┘    │
│                   │                                          │
│                   ├──────────┬──────────┐                   │
│                   ▼          ▼          ▼                    │
│  ┌─────────────────┐ ┌──────────┐ ┌──────────────────┐    │
│  │  FastAPI        │ │ ChromaDB │ │  Local Files     │    │
│  │  AI Backend     │ │ Vectors  │ │  (Notebooks)     │    │
│  │  ───────────    │ │          │ │                  │    │
│  │  • Ollama       │ │          │ │                  │    │
│  │  • Embeddings   │ │          │ │                  │    │
│  │  • RAG          │ │          │ │                  │    │
│  │  • Quizzes      │ │          │ │                  │    │
│  └─────────────────┘ └──────────┘ └──────────────────┘    │
│         │                                                    │
│         │ (Optional HTTPS + Auth0 JWT)                     │
└─────────┼──────────────────────────────────────────────────┘
          │
          │ When online: sync metadata & backups
          ▼
┌─────────────────────────────────────────────────────────────┐
│                    CLOUD (OPTIONAL)                          │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │         Vercel/Netlify (Static Host)               │    │
│  │              - Serves Vue PWA                       │    │
│  │              - CDN distribution                     │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │         Render: Minimal Sync Service                │    │
│  │         (Python FastAPI - Sync Only)                │    │
│  │  ───────────────────────────────                    │    │
│  │  • User metadata sync                               │    │
│  │  • Notebook snapshots (text only)                   │    │
│  │  • Conversation history backup                      │    │
│  │  • Settings sync across devices                     │    │
│  │  • NO AI processing                                 │    │
│  │  • NO embedding generation                          │    │
│  │  • NO RAG queries                                   │    │
│  └─────────────────┬──────────────────────────────────┘    │
│                    │                                         │
│  ┌─────────────────▼──────────────────────────────────┐    │
│  │       Render PostgreSQL (User Data Only)           │    │
│  │  ────────────────────────────────────               │    │
│  │  • users (Auth0 ID, settings)                      │    │
│  │  • notebooks (metadata, text content)              │    │
│  │  • conversation_history (questions/answers)        │    │
│  │  • sync_metadata (last_sync timestamps)            │    │
│  │  • NO vector data                                  │    │
│  │  • NO model data                                   │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### Local Operation (Primary Mode)

```
1. User asks question
   ↓
2. Frontend → Local Backend (port 5000)
   ↓
3. Local Backend:
   - Generates embeddings (Ollama)
   - Queries ChromaDB (local vectors)
   - Uses RAG with local context
   - Generates response (Ollama)
   ↓
4. Response back to Frontend
   ↓
5. Display to user

NO NETWORK REQUIRED ✓
NO CLOUD API CALLS ✓
FULL PRIVACY ✓
```

### Sync Operation (When Online)

```
1. User saves notebook or changes settings
   ↓
2. Frontend → Cloud Sync Service (HTTPS + JWT)
   ↓
3. Sync Service:
   - Validates Auth0 token
   - Stores text content in PostgreSQL
   - Records sync timestamp
   - Returns confirmation
   ↓
4. Frontend updates local sync status

NO AI PROCESSING IN CLOUD ✓
ONLY METADATA SYNCED ✓
VECTORS STAY LOCAL ✓
```

## Component Responsibilities

### Frontend (Vue 3 PWA)
**Runs**: User's browser/Electron app
**Responsibilities**:
- ✅ User interface
- ✅ Offline functionality (service worker)
- ✅ Local state management (Pinia/Vuex)
- ✅ IndexedDB for offline storage
- ✅ Communicate with local backend
- ✅ Optional sync with cloud service
- ✅ Auth0 authentication

**Does NOT**:
- ❌ AI processing
- ❌ Embedding generation
- ❌ Vector storage

### Local Backend (FastAPI)
**Runs**: User's machine (localhost:5000)
**Responsibilities**:
- ✅ RAG operations (embed, query, retrieve)
- ✅ Ollama integration (local models)
- ✅ ChromaDB management (local vectors)
- ✅ Quiz generation (local AI)
- ✅ Notebook processing (local)
- ✅ ALL AI functionality

**Does NOT**:
- ❌ User authentication (handled by Auth0)
- ❌ Multi-device sync (handled by sync service)
- ❌ Cloud storage (optional sync service)

### Cloud Sync Service (Render)
**Runs**: Render web service (optional)
**Responsibilities**:
- ✅ User metadata sync
- ✅ Notebook text backup
- ✅ Conversation history backup
- ✅ Settings sync across devices
- ✅ Auth0 token validation
- ✅ Last sync timestamps

**Does NOT**:
- ❌ AI processing (use local backend)
- ❌ Embedding generation (use local backend)
- ❌ RAG queries (use local backend)
- ❌ Quiz generation (use local backend)
- ❌ Vector storage (use local ChromaDB)

### Cloud Database (Render PostgreSQL)
**Runs**: Render managed PostgreSQL (optional)
**Stores**:
- ✅ User profiles (Auth0 ID, email)
- ✅ Notebook metadata (title, created_at, updated_at)
- ✅ Notebook content (markdown text only)
- ✅ Conversation history (questions/answers text)
- ✅ User settings (preferences, model choices)
- ✅ Sync metadata (timestamps, device info)

**Does NOT Store**:
- ❌ Vector embeddings (local ChromaDB only)
- ❌ AI model weights (local Ollama only)
- ❌ Private documents (stay local)

## Offline-First Capabilities

### Works WITHOUT Internet
- ✅ Ask questions (local AI)
- ✅ Generate quizzes (local AI)
- ✅ Create/edit notebooks (local storage)
- ✅ Search notes (local ChromaDB)
- ✅ View conversation history (local)
- ✅ All core features

### Requires Internet (Optional)
- 🌐 Initial app download
- 🌐 Auth0 login (first time)
- 🌐 Sync notebooks to cloud
- 🌐 Access from other devices
- 🌐 Backup conversation history

## Privacy & Security

### Data Privacy
- ✅ **Documents**: Never leave user's machine
- ✅ **Vectors**: Stored locally in ChromaDB
- ✅ **AI Processing**: 100% local (Ollama)
- ✅ **Questions/Answers**: Local-first, optional cloud backup
- ✅ **API Keys**: Never required for local operation

### Cloud Privacy (When Using Sync)
- 🔒 Only text content synced (no vectors)
- 🔒 Auth0 JWT for authentication
- 🔒 HTTPS for all sync operations
- 🔒 User can disable sync entirely
- 🔒 User can delete cloud data anytime

## Deployment Models

### 1. Desktop App (Recommended)
**How**: Electron app with embedded backend
**Pros**:
- ✅ No server needed
- ✅ Completely offline
- ✅ One-click install
- ✅ No cloud costs
**Cons**:
- ⚠️ Must install on each device
- ⚠️ Manual updates

### 2. PWA (Progressive Web App)
**How**: Hosted frontend + local backend
**Pros**:
- ✅ Install from browser
- ✅ Cross-platform
- ✅ Auto-updates
- ✅ Optional cloud sync
**Cons**:
- ⚠️ Must run local backend separately
- ⚠️ Requires technical setup

### 3. Hybrid (Recommended for Multi-Device)
**How**: PWA + local backend + cloud sync
**Pros**:
- ✅ Best of both worlds
- ✅ Works offline
- ✅ Syncs across devices
- ✅ Privacy-focused
**Cons**:
- ⚠️ Small cloud hosting cost (~$7/month)
- ⚠️ Requires Render setup

## Cost Analysis

### Pure Local (Desktop App)
| Component | Cost |
|-----------|------|
| Ollama | Free |
| ChromaDB | Free |
| Local Backend | Free |
| Frontend | Free |
| **Total** | **$0/month** |

### Hybrid (Multi-Device Sync)
| Component | Cost |
|-----------|------|
| Ollama | Free |
| ChromaDB | Free |
| Local Backend | Free |
| Frontend | Free (Vercel/Netlify) |
| Sync Service | $7/month (Render) |
| PostgreSQL | $7/month (Render) |
| **Total** | **$14/month** |

### Optional: Cloud AI Fallback
| Component | Cost |
|-----------|------|
| OpenAI API | ~$0.002/1K tokens |
| (For when Ollama unavailable) | ~$5-20/month typical |

## Technology Stack

### Local Components
- **Frontend**: Vue 3, Vite, Pinia, Auth0
- **Backend**: FastAPI, Python 3.11
- **AI**: Ollama (llama3.1, nomic-embed-text)
- **Vectors**: ChromaDB (local persistence)
- **Storage**: File system + IndexedDB

### Cloud Components (Optional)
- **Hosting**: Vercel/Netlify (frontend static)
- **Sync Service**: Render (Python FastAPI)
- **Database**: Render PostgreSQL
- **Auth**: Auth0 (free tier)
- **CDN**: Automatic with Vercel/Netlify

## Development Setup

### Local Development (Recommended)
```bash
# Start local backend
cd local_backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 5000

# Start frontend
cd frontend
npm install
npm run dev

# Start Ollama (separate terminal)
ollama serve
ollama pull llama3.1
ollama pull nomic-embed-text
```

### Cloud Sync Setup (Optional)
```bash
# Deploy sync service to Render
# See DEPLOYMENT.md for details

# Configure environment
SYNC_SERVICE_URL=https://clarity-sync.onrender.com
ENABLE_SYNC=true
```

## API Boundaries

### Local Backend API (localhost:5000)
```
POST /api/embed          - Generate embeddings
POST /api/query          - RAG query
POST /api/quiz/generate  - Generate quiz
POST /api/notebooks      - Manage notebooks locally
GET  /api/health         - Health check
```

### Cloud Sync API (Optional)
```
GET  /api/sync/status              - Check sync status
POST /api/sync/notebooks           - Sync notebook metadata
POST /api/sync/conversation        - Sync conversation history
GET  /api/sync/notebooks/:id       - Get notebook from cloud
PUT  /api/sync/settings            - Sync user settings
```

**Note**: Cloud API does NOT expose AI endpoints!

## Migration Path

### Phase 1: Local Only (Current)
- ✅ Desktop app experience
- ✅ Single device
- ✅ No cloud dependency

### Phase 2: Add Sync (Optional)
- ✅ Deploy sync service
- ✅ Enable cross-device sync
- ✅ Keep AI local

### Phase 3: Progressive Enhancement (Future)
- 🔄 Electron packaging
- 🔄 Mobile apps (React Native)
- 🔄 Browser extensions

## Summary

**Clarity is a LOCAL-FIRST application:**

1. **AI runs on your machine** (Ollama, ChromaDB)
2. **No cloud required** for core functionality
3. **Optional sync** for convenience
4. **Privacy-focused** by design
5. **Cost-effective** (free for local, ~$14/month for sync)

The cloud infrastructure is **minimal and optional** - just metadata sync and backup. All the intelligence stays on your machine.
