# Auth0 Integration Guide for Clarity

## 🎯 Quick Setup (5 minutes)

### Step 1: Get Your Auth0 Credentials

You've already created an Auth0 account. Now get your credentials:

1. **Go to Auth0 Dashboard**: https://manage.auth0.com/
2. **Navigate to**: Applications → Applications
3. **Find your application** (or create a new "Single Page Application")
4. **Copy these values**:
   - Domain (looks like: `dev-abc123.us.auth0.com`)
   - Client ID (looks like: `aBcDeFgHiJkLmNoPqRsTuVwXyZ123456`)
   - Client Secret (looks like: `xYz789...` - **keep this secret!**)

---

### Step 2: Configure Auth0 Application Settings

In your Auth0 Application settings, add these URLs:

#### ✅ Allowed Callback URLs
```
http://localhost:5173/callback
```

#### ✅ Allowed Logout URLs
```
http://localhost:5173
```

#### ✅ Allowed Web Origins
```
http://localhost:5173
```

#### ✅ Allowed Origins (CORS)
```
http://localhost:5173
```

**Click "Save Changes"** at the bottom!

---

### Step 3: Create Your `.env` File

Copy `.env.example` to `.env` and fill in your Auth0 credentials:

**Windows PowerShell:**
```powershell
Copy-Item .env.example .env
```

**Now edit `c:\Clarity\.env`** with your actual values:

```bash
# ======================
# Auth0 Configuration
# ======================
AUTH0_DOMAIN=dev-abc123.us.auth0.com          # 👈 YOUR DOMAIN HERE
AUTH0_CLIENT_ID=aBcDeFgHiJkLmNoPqRsTuVwXyZ    # 👈 YOUR CLIENT ID HERE
AUTH0_CLIENT_SECRET=xYz789...                 # 👈 YOUR CLIENT SECRET HERE
AUTH0_AUDIENCE=https://clarity-api

# Frontend Auth0 (copy same values as above)
VITE_AUTH0_DOMAIN=dev-abc123.us.auth0.com     # 👈 SAME AS AUTH0_DOMAIN
VITE_AUTH0_CLIENT_ID=aBcDeFgHiJkLmNoPqRsTuVwXyZ  # 👈 SAME AS AUTH0_CLIENT_ID
VITE_AUTH0_AUDIENCE=https://clarity-api
VITE_AUTH0_CALLBACK_URL=http://localhost:5173/callback

# Leave everything else as default for now
LOCAL_BACKEND_HOST=0.0.0.0
LOCAL_BACKEND_PORT=5000
CLARITY_BASE_DIR=~/.clarity
EMBEDDING_MODEL=all-MiniLM-L6-v2
LLM_PROVIDER=mock
DEBUG=true
```

**⚠️ IMPORTANT**: 
- Replace `dev-abc123.us.auth0.com` with YOUR actual Auth0 domain
- Replace `aBcDeFgHiJkLmNoPqRsTuVwXyZ` with YOUR actual Client ID
- Replace `xYz789...` with YOUR actual Client Secret

---

### Step 4: Install Dependencies

#### Backend Dependencies:
```powershell
cd local_backend
python -m pip install -r requirements.txt
cd ..
```

#### Frontend Dependencies:
```powershell
cd frontend
npm install
cd ..
```

---

### Step 5: Start Clarity! 🚀

Run the startup script:
```powershell
.\infra\scripts\start_local.ps1
```

Or manually start both services:

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

## 🧪 Test Auth0 Integration

1. **Open browser**: http://localhost:5173
2. **Click "Log In"** button (top right)
3. **Auth0 login page should appear**
4. **Sign up or log in**
5. **You'll be redirected back** to http://localhost:5173/callback
6. **Then redirected to** http://localhost:5173/notebooks
7. **You should see** "Welcome, [your name]!" and the logout button

---

## 🔧 Troubleshooting

### "Callback URL mismatch" Error
**Fix**: In Auth0 Dashboard → Your App → Settings → Add `http://localhost:5173/callback` to "Allowed Callback URLs"

### "Login required" Error
**Fix**: Check that `VITE_AUTH0_DOMAIN` and `VITE_AUTH0_CLIENT_ID` are correctly set in `.env`

### Auth0 login page doesn't appear
**Fix**: 
1. Check browser console for errors
2. Verify `.env` file exists and has correct values
3. Restart the frontend: `Ctrl+C` then `npm run dev`

### "Invalid state" Error
**Fix**: 
1. Clear browser localStorage: `localStorage.clear()` in browser console
2. Hard refresh: `Ctrl+Shift+R`
3. Try logging in again

---

## 📋 Auth0 Application Configuration Checklist

In Auth0 Dashboard → Applications → [Your App] → Settings:

- ✅ Application Type: **Single Page Application**
- ✅ Allowed Callback URLs: `http://localhost:5173/callback`
- ✅ Allowed Logout URLs: `http://localhost:5173`
- ✅ Allowed Web Origins: `http://localhost:5173`
- ✅ Allowed Origins (CORS): `http://localhost:5173`
- ✅ Rotate Refresh Tokens: **Enabled**
- ✅ Absolute Expiration: `2592000` (30 days)
- ✅ Inactivity Expiration: `1296000` (15 days)

**Scroll down and click "Save Changes"!**

---

## 🎓 How Auth0 Works in Clarity

### Local-First Architecture

**IMPORTANT**: Auth0 is ONLY used for cloud sync (optional feature). You can use Clarity 100% offline without Auth0!

#### Without Auth0 (Default):
- ✅ Upload documents locally
- ✅ Generate embeddings locally
- ✅ Ask questions (RAG) locally
- ✅ Generate quizzes locally
- ❌ Cannot sync across devices

#### With Auth0 (Optional):
- ✅ Everything above PLUS
- ✅ Sync notebook metadata to cloud
- ✅ Access notebooks from multiple devices
- ✅ **Documents still stay local** (only metadata syncs)

### Authentication Flow

```
1. User clicks "Log In"
   ↓
2. Redirect to Auth0 login page (auth0.com)
   ↓
3. User enters credentials
   ↓
4. Auth0 validates and issues JWT token
   ↓
5. Redirect to http://localhost:5173/callback
   ↓
6. Frontend stores JWT in browser
   ↓
7. User clicks "Sync" button
   ↓
8. Frontend → Local Backend (with JWT)
   ↓
9. Local Backend → Render Sync API (with JWT)
   ↓
10. Render validates JWT and syncs metadata
```

**Key Point**: Auth0 only authenticates for cloud sync. All AI processing happens locally without any authentication!

---

## 🔒 Security Notes

- **Client Secret**: Never commit `.env` to Git (already in `.gitignore`)
- **JWT Token**: Stored in browser, expires after 30 days
- **Local-First**: Documents NEVER sent to Auth0 or cloud
- **Cloud Sync**: Only notebook metadata (titles, timestamps) synced
- **Offline**: Can use Clarity without internet after login (JWT cached)

---

## 🚀 Next Steps

After successful Auth0 integration:

1. **Upload a document**: Try the demo PDFs in `demo_data/`
2. **Ask questions**: Test the RAG pipeline
3. **Generate quiz**: Create flashcards from your notes
4. **Sync (optional)**: If you set up Render backend, test cloud sync

---

## 📚 Additional Resources

- **Auth0 Vue.js SDK**: https://auth0.com/docs/quickstart/spa/vuejs
- **Auth0 Dashboard**: https://manage.auth0.com/
- **Clarity Architecture**: See `doc/architecture.md`
- **Full Setup Guide**: See `SETUP.md`

---

## 🆘 Need Help?

Common issues:

1. **"npm: command not found"** → Install Node.js 18+ from https://nodejs.org/
2. **"python: command not found"** → Install Python 3.9+ from https://python.org/
3. **Auth0 errors** → Double-check domain and client ID in `.env`
4. **Port already in use** → Kill process: `netstat -ano | findstr :5000` then `taskkill /PID [pid] /F`

Still stuck? Check `SETUP.md` for detailed troubleshooting.
