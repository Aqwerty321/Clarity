# Clarity - Quick Reference

## 🚀 Commands Cheat Sheet

### Development

```powershell
# Start everything (Windows)
.\infra\scripts\start_local.ps1

# Start backend only
cd local_backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 5000

# Start frontend only
cd frontend
npm run dev

# Docker Compose
docker-compose up -d
docker-compose down
```

### Testing

```powershell
# Backend tests
cd local_backend
pytest tests/ -v

# Frontend tests
cd frontend
npm run test

# With coverage
pytest tests/ --cov=app --cov-report=html
```

### Building

```powershell
# Frontend production build
cd frontend
npm run build

# Docker images
docker build -t clarity-backend local_backend/
docker build -t clarity-frontend frontend/
```

---

## 🔧 Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `AUTH0_DOMAIN` | Auth0 tenant domain | `your-tenant.auth0.com` |
| `AUTH0_CLIENT_ID` | Auth0 application client ID | `abc123...` |
| `AUTH0_CLIENT_SECRET` | Auth0 application secret | `xyz789...` |
| `VITE_AUTH0_DOMAIN` | Frontend Auth0 domain | Same as AUTH0_DOMAIN |
| `VITE_AUTH0_CLIENT_ID` | Frontend Auth0 client ID | Same as AUTH0_CLIENT_ID |
| `CLARITY_CHUNK_SIZE` | Token count per chunk | `500` |
| `CLARITY_CHUNK_OVERLAP` | Overlap between chunks | `100` |
| `EMBEDDING_MODEL` | Embedding model name | `all-MiniLM-L6-v2` |
| `LLM_PROVIDER` | LLM provider | `mock`, `gpt-oss`, `openai` |
| `RENDER_BACKEND_URL` | Cloud sync URL | `https://app.onrender.com` |

---

## 📡 API Endpoints

### Local Backend (http://localhost:5000)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/api/ingest` | Upload & process document |
| `POST` | `/api/embed` | Generate embeddings |
| `POST` | `/api/ask` | RAG question answering |
| `POST` | `/api/generate-quiz` | Generate quiz |
| `POST` | `/api/sync/push` | Push to cloud |
| `GET` | `/api/sync/pull` | Pull from cloud |
| `GET` | `/docs` | Swagger API docs |

### Cloud Sync Backend (Render)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/api/sync` | Push notebooks |
| `GET` | `/api/sync` | Pull notebooks |

---

## 🗂️ File Locations

| Item | Path |
|------|------|
| ChromaDB data | `~/.clarity/chroma/` |
| Logs | `~/.clarity/logs/` |
| Frontend build | `frontend/dist/` |
| Environment config | `.env` |
| Demo data | `demo_data/` |

---

## 🐛 Common Issues & Fixes

### "Module not found"
```powershell
# Backend
pip install -r local_backend/requirements.txt

# Frontend
npm install --prefix frontend
```

### "Auth0 error"
- Check `.env` credentials
- Verify callback URL: `http://localhost:5173/callback`
- Ensure Auth0 app type is "Single Page Application"

### "ChromaDB permission error"
```powershell
# Delete and recreate
Remove-Item -Recurse -Force ~/.clarity/chroma
```

### "Port already in use"
```powershell
# Find and kill process (Windows)
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Change port in config files
# Backend: local_backend/app/main.py
# Frontend: frontend/vite.config.js
```

---

## 📝 Code Snippets

### Add a new API endpoint

```python
# local_backend/app/api/endpoints.py
@router.post("/my-endpoint")
async def my_endpoint(request: MyRequest):
    # Your logic here
    return {"status": "success"}
```

### Add a new Vue component

```vue
<!-- frontend/src/components/MyComponent.vue -->
<template>
  <div>
    <h1>{{ title }}</h1>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const title = ref('My Component')
</script>
```

### Query ChromaDB

```python
from app.services.chroma_service import chroma_service
from app.services.embedder import embedder

# Embed query
query_emb = embedder.embed_query("your question")

# Search
results = chroma_service.query(
    user_id="user123",
    query_embedding=query_emb,
    top_k=5
)
```

---

## 🎨 Styling Guide

### Tailwind CSS Classes

```html
<!-- Button -->
<button class="btn btn-primary">Click me</button>

<!-- Card -->
<div class="card bg-base-100 shadow-xl">
  <div class="card-body">
    <h2 class="card-title">Card Title</h2>
  </div>
</div>

<!-- Input -->
<input type="text" class="input input-bordered w-full" />

<!-- Modal -->
<dialog class="modal">
  <div class="modal-box">
    <h3 class="font-bold text-lg">Modal Title</h3>
  </div>
</dialog>
```

---

## 🧪 Testing Examples

### Backend test

```python
def test_my_endpoint():
    response = client.post("/api/my-endpoint", json={"data": "test"})
    assert response.status_code == 200
```

### Frontend test

```javascript
import { describe, it, expect } from 'vitest'

describe('MyComponent', () => {
  it('renders correctly', () => {
    expect(true).toBe(true)
  })
})
```

---

## 📦 Deployment Checklist

### Render Backend

- [ ] Push code to GitHub
- [ ] Connect repo to Render
- [ ] Verify `render.yaml` is correct
- [ ] Set environment variables in dashboard
- [ ] Test endpoints

### Frontend (Vercel/Netlify)

- [ ] Build: `npm run build`
- [ ] Deploy `dist/` folder
- [ ] Set environment variables
- [ ] Update Auth0 callback URLs
- [ ] Test login flow

---

## 💡 Pro Tips

1. **Use the startup script** - Simplest way to run locally
2. **Check logs** - `~/.clarity/logs/` for debugging
3. **API docs** - Use http://localhost:5000/docs for testing
4. **Demo data** - Run `seed_demo.py` for instant content
5. **Docker** - Use docker-compose for isolated environment

---

## 📚 Learn More

- Architecture: `doc/architecture.md`
- Setup Guide: `SETUP.md`
- Contributing: `CONTRIBUTING.md`
- API Docs: http://localhost:5000/docs

---

**Quick Start**: `.\infra\scripts\start_local.ps1` → Open http://localhost:5173 🚀
