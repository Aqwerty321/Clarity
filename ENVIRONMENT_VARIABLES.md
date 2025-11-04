# Environment Variables Configuration Guide

This document explains all environment variables used in Clarity.

## Backend Environment Variables (local_backend/.env)

### Database Configuration

```env
# PostgreSQL Database URL
# Local: postgresql://postgres:postgres@localhost:5432/clarity_db
# Render: postgresql://user:pass@host.render.com/clarity_db
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/clarity_db
```

### Auth0 Configuration

```env
# Auth0 Domain (from Auth0 Dashboard)
# Example: your-tenant.auth0.com or your-tenant.us.auth0.com
AUTH0_DOMAIN=your-domain.auth0.com

# Auth0 API Audience (API Identifier from Auth0 Dashboard)
# Example: https://your-api-identifier or https://api.clarity.app
AUTH0_API_AUDIENCE=your-api-audience
```

### AI Models Configuration

```env
# Ollama Base URL (for local AI models)
# Local: http://localhost:11434
# Remote: http://your-ollama-server:11434
OLLAMA_BASE_URL=http://localhost:11434

# LLM Model Name
# Options: llama3.1, llama2, mistral, codellama, gpt-4 (if using OpenAI)
LLM_MODEL=llama3.1

# Embedding Model Name
# Options: nomic-embed-text, all-MiniLM-L6-v2, text-embedding-ada-002 (if using OpenAI)
EMBEDDER_MODEL=nomic-embed-text

# Optional: OpenAI API Key (if using OpenAI instead of Ollama)
# OPENAI_API_KEY=sk-...

# Optional: Anthropic API Key (if using Claude)
# ANTHROPIC_API_KEY=sk-ant-...
```

### ChromaDB Configuration

```env
# ChromaDB Persistence Directory
# Local: ~/.clarity/chroma or ./chroma_data
# Render: /opt/render/.clarity/chroma
CHROMA_PERSIST_DIRECTORY=~/.clarity/chroma
```

### CORS Configuration

```env
# Allowed CORS Origins (comma-separated)
# Local: http://localhost:5173
# Production: https://your-app.vercel.app,http://localhost:5173
CORS_ORIGINS=http://localhost:5173,http://localhost:5174
```

### Server Configuration

```env
# Server Host (usually 0.0.0.0 for production, 127.0.0.1 for local)
HOST=127.0.0.1

# Server Port (Render sets this automatically with $PORT)
PORT=5000
```

---

## Frontend Environment Variables (frontend/.env)

### API Configuration

```env
# Backend API Base URL
# Local: http://localhost:5000
# Production: https://your-backend.onrender.com
VITE_API_BASE_URL=http://localhost:5000
```

### Auth0 Configuration

```env
# Auth0 Domain (same as backend)
VITE_AUTH0_DOMAIN=your-domain.auth0.com

# Auth0 Client ID (from Auth0 Application)
VITE_AUTH0_CLIENT_ID=your-client-id

# Auth0 API Audience (same as backend)
VITE_AUTH0_AUDIENCE=your-api-audience

# Auth0 Redirect URI (where Auth0 redirects after login)
# Local: http://localhost:5173/callback
# Production: https://your-app.vercel.app/callback
VITE_AUTH0_REDIRECT_URI=http://localhost:5173/callback
```

---

## Environment Files Structure

### Local Development

```
clarity/
├── .env                          # Root-level shared config (optional)
├── local_backend/
│   └── .env                      # Backend config (local)
└── frontend/
    └── .env                      # Frontend config (local)
```

### Production Deployment

```
clarity/
├── .env.production.example       # Template for production
├── local_backend/
│   └── .env.production          # Backend config (production) - NOT in git
└── frontend/
    └── .env.production          # Frontend config (production) - NOT in git
```

---

## Platform-Specific Configuration

### Render (Backend)

Set these in Render Dashboard → Service → Environment:

```
DATABASE_URL=<from-postgres-instance>
AUTH0_DOMAIN=your-domain.auth0.com
AUTH0_API_AUDIENCE=your-api-audience
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=llama3.1
EMBEDDER_MODEL=nomic-embed-text
CORS_ORIGINS=https://your-app.vercel.app,http://localhost:5173
PORT=10000
```

### Vercel (Frontend)

Set these in Vercel Dashboard → Project → Settings → Environment Variables:

```
VITE_API_BASE_URL=https://your-backend.onrender.com
VITE_AUTH0_DOMAIN=your-domain.auth0.com
VITE_AUTH0_CLIENT_ID=your-client-id
VITE_AUTH0_AUDIENCE=your-api-audience
VITE_AUTH0_REDIRECT_URI=https://your-app.vercel.app/callback
```

### Netlify (Frontend)

Set these in Netlify Dashboard → Site → Site settings → Environment variables:

```
VITE_API_BASE_URL=https://your-backend.onrender.com
VITE_AUTH0_DOMAIN=your-domain.auth0.com
VITE_AUTH0_CLIENT_ID=your-client-id
VITE_AUTH0_AUDIENCE=your-api-audience
VITE_AUTH0_REDIRECT_URI=https://your-app.netlify.app/callback
```

---

## Variable Descriptions

### Critical Variables (Required)

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `AUTH0_DOMAIN` | Auth0 tenant domain | `your-tenant.auth0.com` |
| `AUTH0_API_AUDIENCE` | Auth0 API identifier | `https://api.clarity.app` |
| `VITE_AUTH0_CLIENT_ID` | Auth0 client ID | `abc123xyz...` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OLLAMA_BASE_URL` | Ollama server URL | `http://localhost:11434` |
| `LLM_MODEL` | Language model name | `llama3.1` |
| `EMBEDDER_MODEL` | Embedding model name | `nomic-embed-text` |
| `CORS_ORIGINS` | Allowed origins | `*` (development) |
| `PORT` | Server port | `5000` |

### API Keys (When Not Using Ollama)

| Variable | Description | Format |
|----------|-------------|--------|
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `ANTHROPIC_API_KEY` | Anthropic API key | `sk-ant-...` |

---

## Security Best Practices

### ✅ DO:
- Use environment variables for all secrets
- Add `.env` to `.gitignore`
- Use different values for development and production
- Rotate API keys regularly
- Use HTTPS in production
- Limit CORS origins in production

### ❌ DON'T:
- Commit `.env` files to Git
- Share API keys publicly
- Use production keys in development
- Use `*` for CORS in production
- Store secrets in code

---

## Troubleshooting

### Backend won't connect to database
```bash
# Check DATABASE_URL format
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL

# Common issues:
# - Wrong host/port
# - Wrong username/password
# - Database doesn't exist
# - SSL mode incorrect
```

### Frontend can't reach backend
```bash
# Check VITE_API_BASE_URL
echo $VITE_API_BASE_URL

# Test backend health
curl $VITE_API_BASE_URL/api/health

# Common issues:
# - Wrong URL
# - CORS not configured
# - Backend not running
```

### Auth0 login fails
```bash
# Check Auth0 variables
echo $AUTH0_DOMAIN
echo $AUTH0_CLIENT_ID
echo $AUTH0_API_AUDIENCE

# Common issues:
# - Wrong domain
# - Wrong client ID
# - Callback URL not configured
# - Wrong audience
```

### Ollama not working
```bash
# Check Ollama URL
curl $OLLAMA_BASE_URL/api/tags

# Pull models if needed
ollama pull llama3.1
ollama pull nomic-embed-text

# Common issues:
# - Ollama not running
# - Models not pulled
# - Wrong URL
```

---

## Quick Setup Scripts

### Copy and Configure (Linux/Mac)
```bash
# Backend
cp local_backend/.env.example local_backend/.env
nano local_backend/.env

# Frontend
cp frontend/.env.example frontend/.env
nano frontend/.env
```

### Copy and Configure (Windows)
```powershell
# Backend
copy local_backend\.env.example local_backend\.env
notepad local_backend\.env

# Frontend
copy frontend\.env.example frontend\.env
notepad frontend\.env
```

---

## Validation

### Validate Backend Config
```bash
cd local_backend
python -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('✅ DATABASE_URL:', os.getenv('DATABASE_URL')[:30] + '...')
print('✅ AUTH0_DOMAIN:', os.getenv('AUTH0_DOMAIN'))
print('✅ AUTH0_API_AUDIENCE:', os.getenv('AUTH0_API_AUDIENCE'))
print('✅ LLM_MODEL:', os.getenv('LLM_MODEL'))
"
```

### Validate Frontend Config
```bash
cd frontend
cat .env
```
