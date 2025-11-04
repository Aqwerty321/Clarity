# Clarity

**Local-first, privacy-focused personal learning assistant**

Clarity is a **desktop-app-like web application** that runs entirely on your machine. Both the Vue frontend and FastAPI AI backend operate locally - no internet required for core functionality. Built with Vue 3, FastAPI, and ChromaDB.

---

## 🎯 Features

- **100% Local-First**: Both frontend and AI backend run on your computer. Works completely offline.
- **Desktop App Experience**: Full functionality without internet - embeddings, RAG queries, quiz generation all happen locally.
- **Privacy-First**: Your documents and AI models never leave your machine. Zero data sent to cloud for processing.
- **Optional Cloud Sync**: When online, optionally backup notebook metadata (not documents) to Render for multi-device access.
- **Smart Learning**: Upload PDFs/documents, ask questions, generate quizzes, create flashcards - all processed locally.

---

## 🛠 Tech Stack

### Frontend (Runs Locally)
- **Vue 3** + **Vite** + **Tailwind CSS**
- **Pinia** for state management
- Talks to local backend on `localhost:5000`
- Works offline (PWA/Electron-ready)

### Local Backend (Runs Locally - The Core AI Engine)
- **FastAPI** + **Uvicorn** on `localhost:5000`
- **ChromaDB** for vector storage (persisted locally)
- **nomic-embed-text** or **all-MiniLM-L6-v2** embeddings (local models)
- **gpt-oss** or mock LLM for generation (local inference)
- **All AI processing happens on your machine**

### Cloud Sync Backend (Optional - Minimal Service)
- **FastAPI** deployed to **Render** (only for sync when online)
- **PostgreSQL** for notebook metadata only (not documents!)
- **Auth0 JWT** verification
- **Used only for multi-device sync - NOT required for core functionality**

---

## 🚀 Quick Start (100% Local - No Cloud Required!)

### Prerequisites
- Python 3.9+
- Node.js 18+
- **That's it!** No cloud services needed for core functionality
- Docker (optional, for containerized deployment)

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd clarity
cp .env.example .env
```

**Edit `.env`** and add your Auth0 credentials:
- `AUTH0_DOMAIN`
- `AUTH0_CLIENT_ID`
- `AUTH0_CLIENT_SECRET`
- `VITE_AUTH0_DOMAIN`
- `VITE_AUTH0_CLIENT_ID`

### 2. Install Dependencies

#### Frontend
```bash
cd frontend
npm install
```

#### Local Backend
```bash
cd ../local_backend
pip install -r requirements.txt
```

### 3. Run Demo

From the project root:

```bash
# Linux/macOS
bash infra/scripts/start_local.sh

# Windows (PowerShell)
.\infra\scripts\start_local.ps1
```

This will:
1. Start the local FastAPI backend on `http://localhost:5000`
2. Start the Vue frontend on `http://localhost:5173`
3. Seed demo data into ChromaDB
4. Open your browser automatically

---

## 📖 Development Guide

### Running Services Individually

#### Frontend (Vue)
```bash
cd frontend
npm run dev
```
Runs on `http://localhost:5173`

#### Local Backend (FastAPI)
```bash
cd local_backend
uvicorn app.main:app --reload --port 5000
```
Runs on `http://localhost:5000`

#### Render Backend (Cloud Sync)
```bash
cd render_backend
uvicorn app:app --reload --port 8000
```
Runs on `http://localhost:8000`

### Using Docker Compose

```bash
docker-compose up
```

This starts:
- Frontend at `http://localhost:5173`
- Local backend at `http://localhost:5000`
- PostgreSQL at `localhost:5432` (for local testing)

---

## 🧪 Testing

### Backend Tests
```bash
cd local_backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm run test
```

---

## 🌐 Deployment

### Render Backend (Cloud Sync)

1. Push to GitHub
2. Connect your repo to Render
3. Render will detect `render.yaml` and provision:
   - Web service for the sync API
   - PostgreSQL database

Set environment variables in Render dashboard:
- `AUTH0_DOMAIN`
- `AUTH0_AUDIENCE`
- `DATABASE_URL` (auto-provisioned)

### Frontend (Static Hosting)

```bash
cd frontend
npm run build
```

Deploy the `dist/` folder to:
- Vercel
- Netlify
- Cloudflare Pages
- Or serve locally via `npm run preview`

---

## 🏗 Architecture

See [`doc/architecture.md`](./doc/architecture.md) for detailed system design.

**High-level flow:**

1. **User uploads document** → Frontend sends to local backend
2. **Local backend chunks & embeds** → Stores in ChromaDB
3. **User asks question** → RAG pipeline retrieves relevant chunks → Local LLM generates answer
4. **Quiz generation** → LLM creates questions from context
5. **Sync** → Notebooks/metadata pushed to Render backend (PostgreSQL)

---

## 📂 Project Structure

```
clarity/
├── frontend/              # Vue 3 + Tailwind
├── local_backend/         # FastAPI RAG runtime
├── render_backend/        # Cloud sync API
├── infra/                 # Docker, scripts
├── demo_data/             # Sample PDFs for testing
└── doc/                   # Architecture docs
```

---

## 🔐 Security & Privacy Notes

- **🏠 Local-first Design**: Frontend and AI backend run on `localhost` - your computer, your data.
- **📄 Documents Stay Local**: PDFs, embeddings, and ChromaDB vector store never leave your machine.
- **🔒 Zero Cloud Processing**: All AI inference (embeddings, RAG, LLM) happens on your CPU/GPU.
- **☁️ Optional Metadata Sync**: Cloud sync only stores notebook titles and metadata - NOT your documents.
- **🔑 Auth0**: Industry-standard OAuth/OIDC (only used if you enable cloud sync).
- **📡 Offline First**: Works without internet - sync is a bonus feature, not a requirement.
- **🚫 No Telemetry**: Zero tracking, analytics, or data collection.

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repo
2. Create a feature branch
3. Submit a pull request

Run linters before committing:
```bash
# Backend
ruff local_backend/
pytest

# Frontend
npm run lint
npm run test
```

---

## 📄 License

MIT License - see LICENSE file

---

## 🙏 Acknowledgments

- **nomic-embed-text** for high-quality embeddings
- **ChromaDB** for vector storage
- **Auth0** for authentication
- **Render** for easy cloud deployment

---

## 📞 Support

- Issues: [GitHub Issues](your-repo/issues)
- Docs: [`doc/architecture.md`](./doc/architecture.md)

**Built with ❤️ for learners who value privacy.**
