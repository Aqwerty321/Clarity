# Deployment Guide for Clarity

This guide covers deploying Clarity's **optional cloud sync service**. 

## ⚠️ Important: Local-First Architecture

Clarity is designed to run **entirely on your local machine**:
- ✅ **AI Backend**: Runs locally (FastAPI + Ollama)
- ✅ **Vector Database**: Local ChromaDB
- ✅ **AI Processing**: 100% local (private & offline)
- ✅ **Core Features**: Work without internet

This deployment guide is for the **optional sync service** that enables:
- 🌐 Multi-device notebook sync
- 🌐 Conversation history backup
- 🌐 Settings sync across devices

**The sync service does NOT process AI requests** - it only stores metadata and text backups.

See `ARCHITECTURE.md` for complete architecture details.

## Architecture Overview

- **Frontend**: Vercel/Netlify (PWA for multi-device access)
- **Sync Service**: Render (minimal metadata sync - NO AI)
- **Database**: Render PostgreSQL (user data only - NO vectors)
- **AI Backend**: Runs locally on user's machine (NOT deployed)

## Prerequisites

1. GitHub account
2. Render account (https://render.com)
3. Vercel or Netlify account
4. Auth0 account
5. (Optional) OpenAI API key if not using local Ollama

---

## Part 1: Database Setup (Render PostgreSQL)

### Step 1: Create PostgreSQL Database

1. Log in to Render Dashboard
2. Click **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name**: `clarity-db`
   - **Database**: `clarity_db`
   - **User**: `clarity_user`
   - **Region**: Choose closest to you
   - **Plan**: Free (or paid for production)
4. Click **"Create Database"**
5. **Save the connection details**:
   - Internal Database URL (use this in backend)
   - External Database URL (for local testing)

### Step 2: Test Database Connection

```bash
# Install PostgreSQL client if needed
# Windows: https://www.postgresql.org/download/windows/
# Mac: brew install postgresql
# Linux: sudo apt-get install postgresql-client

# Test connection using External URL
psql <EXTERNAL_DATABASE_URL>

# If successful, you'll see:
# clarity_db=>
```

---

## Part 2: Backend Deployment (Render)

### Step 1: Prepare Backend for Deployment

Create `local_backend/.env.production`:
```env
DATABASE_URL=<your-render-internal-database-url>
AUTH0_DOMAIN=<your-auth0-domain>
AUTH0_API_AUDIENCE=<your-auth0-audience>
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=llama3.1
EMBEDDER_MODEL=nomic-embed-text
PORT=10000
```

### Step 2: Update requirements.txt

Ensure all dependencies are listed in `local_backend/requirements.txt`:
```bash
cd local_backend
pip freeze > requirements.txt
```

### Step 3: Create Render Web Service

1. Go to Render Dashboard → **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `clarity-backend`
   - **Region**: Same as database
   - **Branch**: `main`
   - **Root Directory**: (leave empty)
   - **Runtime**: Python 3
   - **Build Command**: 
     ```bash
     cd local_backend && pip install -r requirements.txt
     ```
   - **Start Command**: 
     ```bash
     cd local_backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```

### Step 4: Set Environment Variables

In Render dashboard, go to **Environment** tab and add:

```
DATABASE_URL=<from-your-postgres-instance>
AUTH0_DOMAIN=your-domain.auth0.com
AUTH0_API_AUDIENCE=your-api-audience
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=llama3.1
EMBEDDER_MODEL=nomic-embed-text
CORS_ORIGINS=*
PORT=10000
```

### Step 5: Deploy

1. Click **"Create Web Service"**
2. Wait for deployment (5-10 minutes first time)
3. Note your backend URL: `https://clarity-backend-xxxx.onrender.com`

### Step 6: Test Backend

```bash
# Test health endpoint
curl https://clarity-backend-xxxx.onrender.com/api/health

# Should return:
# {"status":"healthy","version":"1.0.0",...}
```

---

## Part 3: Frontend Deployment (Vercel)

### Step 1: Prepare Frontend

Create `frontend/.env.production`:
```env
VITE_API_BASE_URL=https://clarity-backend-xxxx.onrender.com
VITE_AUTH0_DOMAIN=your-domain.auth0.com
VITE_AUTH0_CLIENT_ID=your-client-id
VITE_AUTH0_AUDIENCE=your-api-audience
VITE_AUTH0_REDIRECT_URI=https://your-app.vercel.app/callback
```

### Step 2: Install Vercel CLI

```bash
npm install -g vercel
```

### Step 3: Deploy to Vercel

```bash
cd frontend

# Login to Vercel
vercel login

# Deploy
vercel --prod
```

### Step 4: Configure Environment Variables in Vercel

1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Add all variables from `.env.production`
3. Redeploy if needed

### Alternative: Deploy to Netlify

```bash
cd frontend

# Build
npm run build

# Install Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Deploy
netlify deploy --prod --dir=dist
```

---

## Part 4: Auth0 Configuration

### Step 1: Configure Auth0 Application

1. Go to Auth0 Dashboard → Applications → Your Application
2. **Settings** tab:

   **Application URIs**:
   - Allowed Callback URLs:
     ```
     http://localhost:5173/callback,
     https://your-app.vercel.app/callback
     ```
   - Allowed Logout URLs:
     ```
     http://localhost:5173,
     https://your-app.vercel.app
     ```
   - Allowed Web Origins:
     ```
     http://localhost:5173,
     https://your-app.vercel.app
     ```
   - Allowed Origins (CORS):
     ```
     http://localhost:5173,
     https://your-app.vercel.app
     ```

3. **Save Changes**

### Step 2: Configure Auth0 API

1. Go to Auth0 Dashboard → APIs → Your API
2. Note the **API Identifier** (use as `AUTH0_API_AUDIENCE`)
3. Enable **RS256** signing algorithm

---

## Part 5: AI Models Configuration

### Option A: Use Local Ollama (Recommended for Local-First)

**Note**: Render free tier doesn't support running Ollama. For production with Ollama, you'll need:
- Self-hosted server with Ollama
- Render paid plan with custom runtime

For now, use OpenAI for cloud deployment.

### Option B: Use OpenAI (Cloud)

1. Get OpenAI API key from https://platform.openai.com
2. Update backend environment variables:
   ```env
   OPENAI_API_KEY=sk-...
   LLM_MODEL=gpt-4
   EMBEDDER_MODEL=text-embedding-ada-002
   ```
3. Update backend code to use OpenAI (already configured in settings)

---

## Part 6: Verification Checklist

### Backend Health Check
```bash
curl https://clarity-backend-xxxx.onrender.com/api/health
```

### Frontend Access
Visit: `https://your-app.vercel.app`

### Test Flow
1. ✅ Login with Auth0
2. ✅ Create a notebook
3. ✅ Upload a document
4. ✅ Ask a question
5. ✅ Generate flashcards
6. ✅ Take a quiz
7. ✅ Check analytics

---

## Part 7: Monitoring & Maintenance

### Render Monitoring
- View logs: Render Dashboard → Service → Logs
- Monitor health: /api/health endpoint
- Database metrics: PostgreSQL instance dashboard

### Error Tracking
Add Sentry (optional):
```bash
pip install sentry-sdk[fastapi]
```

### Scaling
- Database: Upgrade to paid plan for more connections
- Backend: Enable autoscaling in Render
- Frontend: Vercel automatically scales

---

## Troubleshooting

### Backend Won't Start
```bash
# Check Render logs
# Common issues:
# 1. DATABASE_URL incorrect
# 2. Missing environment variables
# 3. Python dependencies not installed
```

### CORS Errors
```bash
# Update CORS_ORIGINS in backend
CORS_ORIGINS=https://your-app.vercel.app,http://localhost:5173
```

### Database Connection Timeouts
```bash
# Use Internal Database URL (faster)
# Check connection pool settings in SQLAlchemy
```

### Auth0 Login Fails
```bash
# Verify callback URL matches exactly
# Check Auth0 application settings
# Verify JWT token validation
```

---

## Cost Estimation

### Free Tier (Hobby Projects)
- Render PostgreSQL: Free (no backups, limited resources)
- Render Web Service: Free (sleep after inactivity)
- Vercel: Free (generous limits)
- Total: **$0/month**

### Production (Paid)
- Render PostgreSQL: $7/month (with backups)
- Render Web Service: $7/month (always on)
- Vercel Pro: $20/month (team features)
- OpenAI API: Pay-as-you-go
- Total: **~$34/month + API costs**

---

## Local Development After Deployment

Your local setup still works! Just use different `.env` files:
- `.env` - Local development
- `.env.production` - Cloud deployment

```bash
# Run locally
cd local_backend
uvicorn app.main:app --reload --port 5000

cd frontend  
npm run dev
```

---

## Next Steps

1. ✅ Set up CI/CD (GitHub Actions)
2. ✅ Add database migrations (Alembic)
3. ✅ Implement caching (Redis)
4. ✅ Add rate limiting
5. ✅ Set up monitoring (Sentry, DataDog)
6. ✅ Configure backups
7. ✅ Add health checks
8. ✅ Implement logging

---

## Support

- Issues: https://github.com/yourusername/clarity/issues
- Render Docs: https://render.com/docs
- Vercel Docs: https://vercel.com/docs
- Auth0 Docs: https://auth0.com/docs
