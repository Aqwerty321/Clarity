# Clarity - Setup Complete! 🎉

Your **Clarity** web application has been successfully scaffolded!

## 📁 Project Structure

```
clarity/
├── frontend/              # Vue 3 + Tailwind + Auth0
├── local_backend/         # FastAPI + ChromaDB + RAG
├── render_backend/        # Cloud sync service
├── infra/                # Docker & deployment configs
├── demo_data/            # Sample documents
├── .github/workflows/    # CI/CD pipeline
└── doc/                  # Architecture documentation
```

## 🚀 Next Steps

### 1. Configure Auth0

1. Create an Auth0 account at https://auth0.com
2. Create a new Application (Single Page Application)
3. Note your:
   - Domain (e.g., `your-tenant.auth0.com`)
   - Client ID
   - Client Secret
4. Add callback URL: `http://localhost:5173/callback`
5. Update `.env` file with your credentials

### 2. Install Dependencies

**Backend:**
```powershell
cd local_backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Frontend:**
```powershell
cd frontend
npm install
```

### 3. Run the Application

**Option A: Use the startup script (recommended)**
```powershell
.\infra\scripts\start_local.ps1
```

**Option B: Run services manually**

Terminal 1 (Backend):
```powershell
cd local_backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 5000
```

Terminal 2 (Frontend):
```powershell
cd frontend
npm run dev
```

### 4. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5000
- **API Docs**: http://localhost:5000/docs

## 🧪 Testing

**Backend tests:**
```powershell
cd local_backend
pytest tests/ -v
```

**Frontend tests:**
```powershell
cd frontend
npm run test
```

## 📚 Key Features Implemented

✅ **Frontend**
- Vue 3 + Vite + Tailwind CSS
- Auth0 authentication flow
- Notebook CRUD interface
- Document upload UI
- Question answering interface
- Quiz generation modal

✅ **Local Backend**
- FastAPI with CORS support
- Document ingestion (PDF, TXT, Markdown)
- Text chunking (configurable size/overlap)
- Embedding generation (sentence-transformers)
- ChromaDB vector storage
- RAG query pipeline
- LLM wrapper (mock + extensible)
- Sync client for cloud backend

✅ **Cloud Sync Backend**
- FastAPI service for Render
- PostgreSQL integration
- Auth0 JWT verification
- Notebook sync endpoints
- render.yaml deployment config

✅ **DevOps**
- Docker & docker-compose setup
- GitHub Actions CI pipeline
- Startup scripts for Windows/Linux
- Comprehensive documentation

## 🔧 Configuration

Key environment variables in `.env`:

```env
# Auth0
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_CLIENT_ID=your_client_id
VITE_AUTH0_DOMAIN=your-tenant.auth0.com
VITE_AUTH0_CLIENT_ID=your_client_id

# Local Backend
CLARITY_CHUNK_SIZE=500
CLARITY_CHUNK_OVERLAP=100
EMBEDDING_MODEL=all-MiniLM-L6-v2
LLM_PROVIDER=mock

# Cloud Sync
RENDER_BACKEND_URL=https://your-app.onrender.com
```

## 📖 Documentation

- **Architecture**: `doc/architecture.md`
- **Contributing**: `CONTRIBUTING.md`
- **API Docs**: http://localhost:5000/docs (when running)

## 🎯 Demo Data

Load sample documents:
```powershell
cd demo_data
python seed_demo.py
```

Or upload files through the UI after logging in.

## 🐛 Troubleshooting

**Import errors:**
- Make sure dependencies are installed: `pip install -r requirements.txt`

**Auth0 errors:**
- Verify `.env` credentials
- Check callback URLs in Auth0 dashboard

**ChromaDB issues:**
- Delete `~/.clarity/chroma/` and restart

**Port conflicts:**
- Backend uses port 5000
- Frontend uses port 5173
- Change in config files if needed

## 🚢 Deployment

**Frontend (Vercel/Netlify):**
```powershell
cd frontend
npm run build
# Deploy dist/ folder
```

**Render Backend:**
1. Push to GitHub
2. Connect repo to Render
3. Render will detect `render.yaml`
4. Set environment variables in dashboard

## 📞 Support

- Issues: Open a GitHub issue
- Docs: Check `doc/architecture.md`
- Logs: Check `~/.clarity/logs/`

---

**Built with ❤️ for learners who value privacy.**

MVP is ready for demo! 🚀
