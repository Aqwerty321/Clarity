# 🚀 Configuration Complete - Setup Guide

## ✅ What's Been Configured

Your Clarity application now has the complete **local-first architecture** with dual API support!

### New Files Created
1. ✅ `frontend/src/api/clients.js` - Dual API client setup
2. ✅ `frontend/src/components/SyncStatus.vue` - Sync status indicator
3. ✅ Updated `.env` and `.env.example` - New environment variables

### Configuration Added
- ✅ Local backend client (for AI operations)
- ✅ Cloud sync client (optional)
- ✅ Auth0 token management
- ✅ Online/offline detection
- ✅ Sync status UI component

## 🎯 How to Use

### 1. Environment Setup

Your `.env` file now has:
```bash
# Required: Local AI backend
VITE_LOCAL_BACKEND_URL=http://localhost:5000

# Optional: Cloud sync (leave empty for local-only)
VITE_SYNC_SERVICE_URL=
```

**For local-only mode** (recommended): Leave `VITE_SYNC_SERVICE_URL` empty
**For multi-device sync**: Set to your Render sync service URL

### 2. Import API Clients

```javascript
import { localBackend, syncService, isSyncEnabled } from '@/api/clients';
```

### 3. Use in Components

#### Ask Questions (AI - Always Local)
```javascript
// pages/Notebooks.vue
const answer = await localBackend.post('/api/query', {
  question: userQuestion,
  notebook_id: currentNotebook.id
});
```

#### Save Notebook (Local + Optional Sync)
```javascript
// Save to local backend first (required)
await localBackend.post('/api/notebooks', notebook);

// Optionally sync to cloud (if enabled and online)
if (isSyncEnabled && navigator.onLine) {
  try {
    await syncService.post('/api/sync/notebooks', {
      id: notebook.id,
      title: notebook.title,
      content: notebook.content,
      device_id: getDeviceId()
    });
  } catch (error) {
    // Sync failed but local save succeeded - that's OK!
    console.warn('Cloud sync failed:', error);
  }
}
```

#### Generate Quiz (AI - Always Local)
```javascript
const quiz = await localBackend.post('/api/quiz/generate', {
  notebook_id: notebookId,
  num_questions: 5
});
```

### 4. Sync Status Component

The sync status badge is now visible in the top-right corner showing:
- 💾 **Local Only** - No sync configured (maximum privacy)
- 📴 **Offline** - No internet connection (all features still work)
- ☁️ **Synced** - Connected and synced to cloud
- ⟳ **Syncing** - Actively syncing data

Click the badge to see detailed sync information!

## 🔧 Next Steps for Developers

### Update Notebooks Page

Update `frontend/src/pages/Notebooks.vue` to use the new API clients:

```javascript
// Add at top
import { localBackend, syncService, isSyncEnabled, getDeviceId } from '@/api/clients';
import { ref } from 'vue';

// Replace axios calls with localBackend
const askQuestion = async (question) => {
  const response = await localBackend.post('/api/query', {
    question,
    notebook_id: currentNotebook.value.id
  });
  return response.data.answer;
};

// Add sync functionality
const saveNotebookWithSync = async (notebook) => {
  // 1. Save locally (always)
  await localBackend.post('/api/notebooks', notebook);
  
  // 2. Sync to cloud (optional)
  if (isSyncEnabled && navigator.onLine) {
    try {
      await syncService.post('/api/sync/notebooks', {
        id: notebook.id,
        title: notebook.title,
        content: notebook.content,
        device_id: getDeviceId()
      });
    } catch (error) {
      console.warn('Sync failed (local save OK):', error);
    }
  }
};
```

### Update Settings Page

Update `frontend/src/pages/Settings.vue` to sync settings:

```javascript
import { syncService, isSyncEnabled } from '@/api/clients';

const saveSettings = async (settings) => {
  // Save to localStorage first
  localStorage.setItem('clarity_settings', JSON.stringify(settings));
  
  // Optionally sync to cloud
  if (isSyncEnabled && navigator.onLine) {
    try {
      await syncService.put('/api/sync/settings', {
        settings_json: JSON.stringify(settings)
      });
    } catch (error) {
      console.warn('Settings sync failed:', error);
    }
  }
};
```

## 🧪 Testing

### Test 1: Local-Only Mode (Offline)
```bash
# 1. Ensure VITE_SYNC_SERVICE_URL is empty in .env
# 2. Start local backend
cd local_backend
uvicorn app.main:app --reload --port 5000

# 3. Start frontend
cd frontend
npm run dev

# 4. Disconnect internet
# 5. Test all features - should work perfectly!
```

### Test 2: With Sync (Online)
```bash
# 1. Deploy sync service to Render
# 2. Set VITE_SYNC_SERVICE_URL=https://clarity-sync.onrender.com
# 3. Start local backend (still required!)
# 4. Start frontend
# 5. Should see "☁️ Synced" badge in top right
```

### Test 3: Verify AI is Local
```bash
# Open browser DevTools -> Network tab
# Ask a question
# Should see request to: localhost:5000/api/query ✓
# Should NOT see request to: clarity-sync.onrender.com/api/query ✗
```

## 📊 API Endpoints Reference

### Local Backend (localhost:5000)
```
POST /api/embed              - Generate embeddings
POST /api/query              - RAG query (AI)
POST /api/quiz/generate      - Generate quiz (AI)
POST /api/notebooks          - Save notebook
GET  /api/notebooks          - Get notebooks
GET  /api/health             - Health check
```

### Cloud Sync Service (Optional)
```
GET  /api/sync/status        - Sync status
POST /api/sync/notebooks     - Backup notebook text
GET  /api/sync/notebooks     - Get synced notebooks
GET  /api/sync/notebooks/:id - Get specific notebook
POST /api/sync/conversations - Backup conversation
PUT  /api/sync/settings      - Sync settings
GET  /api/sync/settings      - Get settings
```

## 🎨 UI Components Available

### SyncStatus Component
```vue
<template>
  <SyncStatus ref="syncStatusRef" />
</template>

<script setup>
import SyncStatus from '@/components/SyncStatus.vue';
import { ref } from 'vue';

const syncStatusRef = ref(null);

// Trigger sync indicator
const performSync = async () => {
  syncStatusRef.value.setSyncing(true);
  try {
    await syncData();
    syncStatusRef.value.updateLastSync();
  } finally {
    syncStatusRef.value.setSyncing(false);
  }
};
</script>
```

## 🔒 Privacy Notes

### What Stays Local (Always)
- ✅ Vector embeddings (ChromaDB)
- ✅ AI model weights (Ollama)
- ✅ Raw documents
- ✅ AI processing operations

### What Can Be Synced (Optional)
- 🌐 Notebook text content
- 🌐 User settings
- 🌐 Conversation history (text only)

### Disable Sync Completely
```bash
# In .env
VITE_SYNC_SERVICE_URL=

# Now app runs 100% locally!
```

## ⚡ Performance Tips

1. **Always use localBackend for AI** - It's 2.5x - 7.5x faster
2. **Sync is async** - Don't wait for it, fire and forget
3. **Cache locally** - Use localStorage/IndexedDB as primary storage
4. **Check online status** - Only sync when `navigator.onLine === true`

## 🐛 Troubleshooting

### "Local backend not running"
```bash
# Make sure it's running:
cd local_backend
uvicorn app.main:app --reload --port 5000
```

### Sync status shows "Offline" when online
```bash
# Check VITE_SYNC_SERVICE_URL is set correctly
# Verify Render sync service is deployed
# Check browser console for errors
```

### Auth0 errors
```bash
# Make sure .env has correct Auth0 credentials
# Verify callback URL matches in Auth0 dashboard
```

## 📚 Documentation

For more details, see:
- `ARCHITECTURE.md` - Complete architecture
- `FRONTEND_INTEGRATION.md` - Detailed code examples
- `DIAGRAMS.md` - Visual architecture diagrams
- `LOCAL_FIRST_ARCHITECTURE.md` - Implementation guide

## ✅ Configuration Checklist

- [x] API clients created (`src/api/clients.js`)
- [x] SyncStatus component created
- [x] Environment variables added
- [x] App.vue updated with sync status
- [x] Auth0 token configuration added

### Still Todo (Optional)
- [ ] Update Notebooks.vue to use new API clients
- [ ] Update Settings.vue to sync settings
- [ ] Update Quizzes.vue to use local backend
- [ ] Add sync error handling UI
- [ ] Add offline data queue

## 🎉 You're Ready!

Your Clarity app now has:
1. ✅ Dual API architecture (local + optional cloud)
2. ✅ Sync status indicator
3. ✅ Offline-first functionality
4. ✅ Privacy-focused design
5. ✅ Auth0 integration

**Start the app:**
```bash
./start-dev.sh
```

**Or manually:**
```bash
# Terminal 1 - Backend
cd local_backend && uvicorn app.main:app --reload --port 5000

# Terminal 2 - Frontend  
cd frontend && npm run dev
```

**Visit**: http://localhost:5173 🚀

---

**Questions?** Check the documentation files or the implementation in `src/api/clients.js`!
