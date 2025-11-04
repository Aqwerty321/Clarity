# Frontend Integration Guide - Dual API Architecture

This guide explains how the frontend should interact with both the **local AI backend** and the **optional cloud sync service**.

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│              Vue Frontend                        │
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │                                          │  │
│  │         AI Operations (Required)         │  │
│  │              ↓                           │  │
│  │      http://localhost:5000               │  │
│  │      (Local AI Backend)                  │  │
│  │                                          │  │
│  │  • POST /api/embed                       │  │
│  │  • POST /api/query                       │  │
│  │  • POST /api/quiz/generate               │  │
│  │  • POST /api/notebooks                   │  │
│  │                                          │  │
│  └──────────────────────────────────────────┘  │
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │                                          │  │
│  │       Sync Operations (Optional)         │  │
│  │              ↓                           │  │
│  │   https://clarity-sync.onrender.com      │  │
│  │       (Cloud Sync Service)               │  │
│  │                                          │  │
│  │  • POST /api/sync/notebooks              │  │
│  │  • GET  /api/sync/notebooks              │  │
│  │  • POST /api/sync/conversations          │  │
│  │  • PUT  /api/sync/settings               │  │
│  │                                          │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

## Environment Variables

### `.env.local` (Development)
```bash
# Local AI Backend (always required)
VITE_LOCAL_BACKEND_URL=http://localhost:5000

# Cloud Sync Service (optional, only if you want sync)
VITE_SYNC_SERVICE_URL=http://localhost:8000  # or leave empty to disable

# Auth0 (required if using sync)
VITE_AUTH0_DOMAIN=your-domain.auth0.com
VITE_AUTH0_CLIENT_ID=your-client-id
VITE_AUTH0_AUDIENCE=https://your-api
```

### `.env.production` (Production)
```bash
# Local AI Backend (still runs locally!)
VITE_LOCAL_BACKEND_URL=http://localhost:5000

# Cloud Sync Service (optional)
VITE_SYNC_SERVICE_URL=https://clarity-sync.onrender.com

# Auth0
VITE_AUTH0_DOMAIN=your-domain.auth0.com
VITE_AUTH0_CLIENT_ID=your-client-id
VITE_AUTH0_AUDIENCE=https://your-api
```

## API Client Configuration

### Create API Clients

```javascript
// src/api/clients.js

import axios from 'axios';

// Local AI Backend - Always required
export const localBackend = axios.create({
  baseURL: import.meta.env.VITE_LOCAL_BACKEND_URL || 'http://localhost:5000',
  timeout: 30000, // AI operations can take time
});

// Cloud Sync Service - Optional
const syncServiceUrl = import.meta.env.VITE_SYNC_SERVICE_URL;
export const syncService = syncServiceUrl
  ? axios.create({
      baseURL: syncServiceUrl,
      timeout: 10000,
    })
  : null;

// Check if sync is enabled
export const isSyncEnabled = !!syncService;

// Add Auth0 token to sync requests
export const configureSyncAuth = (getAccessToken) => {
  if (syncService) {
    syncService.interceptors.request.use(async (config) => {
      const token = await getAccessToken();
      config.headers.Authorization = `Bearer ${token}`;
      return config;
    });
  }
};
```

## Usage Examples

### 1. Ask a Question (AI Operation - Local)

```javascript
// src/pages/Notebooks.vue

import { localBackend } from '@/api/clients';

async function askQuestion(question) {
  try {
    // This ALWAYS goes to local backend
    const response = await localBackend.post('/api/query', {
      question,
      notebook_id: currentNotebook.id,
    });

    return response.data.answer;
  } catch (error) {
    console.error('AI query failed:', error);
    throw error;
  }
}
```

### 2. Save Notebook (Local + Optional Sync)

```javascript
// src/pages/Notebooks.vue

import { localBackend, syncService, isSyncEnabled } from '@/api/clients';

async function saveNotebook(notebook) {
  try {
    // 1. Save to local backend (always)
    await localBackend.post('/api/notebooks', notebook);
    console.log('Saved to local backend');

    // 2. Sync to cloud (optional, only if enabled and online)
    if (isSyncEnabled && navigator.onLine) {
      try {
        await syncService.post('/api/sync/notebooks', {
          id: notebook.id,
          title: notebook.title,
          content: notebook.content,
          device_id: getDeviceId(),
        });
        console.log('Synced to cloud');
      } catch (syncError) {
        // Sync failed, but local save succeeded - that's OK!
        console.warn('Cloud sync failed (local save OK):', syncError);
      }
    }

    return { success: true, synced: isSyncEnabled };
  } catch (error) {
    console.error('Local save failed:', error);
    throw error;
  }
}

// Get a unique device ID
function getDeviceId() {
  let deviceId = localStorage.getItem('clarity_device_id');
  if (!deviceId) {
    deviceId = crypto.randomUUID();
    localStorage.setItem('clarity_device_id', deviceId);
  }
  return deviceId;
}
```

### 3. Generate Quiz (AI Operation - Local)

```javascript
// src/pages/Notebooks.vue

import { localBackend } from '@/api/clients';

async function generateQuiz(notebookId) {
  try {
    // This ALWAYS goes to local backend
    const response = await localBackend.post('/api/quiz/generate', {
      notebook_id: notebookId,
      num_questions: 5,
    });

    return response.data.questions;
  } catch (error) {
    console.error('Quiz generation failed:', error);
    throw error;
  }
}
```

### 4. Sync Conversation History (Optional Sync)

```javascript
// src/pages/Notebooks.vue

import { syncService, isSyncEnabled } from '@/api/clients';

async function syncConversation(conversation) {
  // Only sync if enabled
  if (!isSyncEnabled || !navigator.onLine) {
    return;
  }

  try {
    await syncService.post('/api/sync/conversations', {
      id: conversation.id,
      notebook_id: conversation.notebook_id,
      question: conversation.question,
      answer: conversation.answer,
    });
    console.log('Conversation synced to cloud');
  } catch (error) {
    // Sync is optional - don't break the app if it fails
    console.warn('Conversation sync failed:', error);
  }
}
```

### 5. Load Synced Notebooks (Optional Sync)

```javascript
// src/pages/Notebooks.vue

import { localBackend, syncService, isSyncEnabled } from '@/api/clients';

async function loadNotebooks() {
  // 1. Always load from local backend first
  const localNotebooks = await localBackend.get('/api/notebooks');
  
  // 2. If sync enabled and online, merge with cloud notebooks
  if (isSyncEnabled && navigator.onLine) {
    try {
      const cloudNotebooks = await syncService.get('/api/sync/notebooks');
      
      // Merge logic: prefer most recent version
      return mergeNotebooks(localNotebooks.data, cloudNotebooks.data.notebooks);
    } catch (error) {
      console.warn('Could not load cloud notebooks:', error);
      // Fall back to local only
      return localNotebooks.data;
    }
  }
  
  return localNotebooks.data;
}

function mergeNotebooks(local, cloud) {
  const merged = new Map();
  
  // Add all local notebooks
  local.forEach(nb => merged.set(nb.id, nb));
  
  // Merge cloud notebooks (prefer newer)
  cloud.forEach(cloudNb => {
    const localNb = merged.get(cloudNb.id);
    if (!localNb || new Date(cloudNb.updated_at) > new Date(localNb.updated_at)) {
      merged.set(cloudNb.id, cloudNb);
    }
  });
  
  return Array.from(merged.values());
}
```

### 6. Sync User Settings (Optional Sync)

```javascript
// src/pages/Settings.vue

import { syncService, isSyncEnabled } from '@/api/clients';

async function saveSettings(settings) {
  // 1. Always save to localStorage
  localStorage.setItem('clarity_settings', JSON.stringify(settings));
  
  // 2. Optionally sync to cloud
  if (isSyncEnabled && navigator.onLine) {
    try {
      await syncService.put('/api/sync/settings', {
        settings_json: JSON.stringify(settings),
      });
      console.log('Settings synced to cloud');
    } catch (error) {
      console.warn('Settings sync failed:', error);
    }
  }
}

async function loadSettings() {
  // 1. Try to load from cloud first (if sync enabled)
  if (isSyncEnabled && navigator.onLine) {
    try {
      const response = await syncService.get('/api/sync/settings');
      const cloudSettings = JSON.parse(response.data.settings_json);
      
      // Save to localStorage for offline use
      localStorage.setItem('clarity_settings', JSON.stringify(cloudSettings));
      
      return cloudSettings;
    } catch (error) {
      console.warn('Could not load cloud settings:', error);
    }
  }
  
  // 2. Fall back to localStorage
  const localSettings = localStorage.getItem('clarity_settings');
  return localSettings ? JSON.parse(localSettings) : getDefaultSettings();
}
```

## Error Handling

### Local Backend Errors

```javascript
try {
  const answer = await localBackend.post('/api/query', { question });
} catch (error) {
  if (error.code === 'ECONNREFUSED') {
    // Local backend not running
    showError('Please start the local AI backend on port 5000');
  } else if (error.response?.status === 500) {
    // Backend error
    showError('AI processing failed. Please try again.');
  } else {
    showError('Unexpected error. Please check console.');
  }
}
```

### Sync Service Errors

```javascript
try {
  await syncService.post('/api/sync/notebooks', notebook);
} catch (error) {
  if (error.code === 'ECONNREFUSED' || !navigator.onLine) {
    // Offline or service unavailable - that's OK!
    showInfo('Working offline. Changes will sync when online.');
  } else if (error.response?.status === 401) {
    // Auth token expired
    showWarning('Please log in again to enable sync.');
  } else {
    // Other sync errors - not critical
    console.warn('Sync failed:', error);
    showInfo('Saved locally. Sync will retry later.');
  }
}
```

## Sync Status Component

```vue
<!-- src/components/SyncStatus.vue -->
<template>
  <div class="sync-status">
    <span v-if="!isSyncEnabled" class="status-badge local">
      <Icon name="check-circle" />
      Local Only
    </span>
    <span v-else-if="!isOnline" class="status-badge offline">
      <Icon name="wifi-off" />
      Offline
    </span>
    <span v-else-if="syncing" class="status-badge syncing">
      <Icon name="refresh" class="spin" />
      Syncing...
    </span>
    <span v-else class="status-badge synced">
      <Icon name="cloud-check" />
      Synced
    </span>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { isSyncEnabled } from '@/api/clients';

const isOnline = ref(navigator.onLine);
const syncing = ref(false);

onMounted(() => {
  window.addEventListener('online', () => isOnline.value = true);
  window.addEventListener('offline', () => isOnline.value = false);
});
</script>
```

## Best Practices

### 1. Always Prioritize Local Operations
```javascript
// ✅ Good: Local first, sync second
await localBackend.post('/api/notebooks', notebook);
if (isSyncEnabled) {
  syncService.post('/api/sync/notebooks', notebook).catch(console.warn);
}

// ❌ Bad: Depends on cloud
await syncService.post('/api/sync/notebooks', notebook);
```

### 2. Graceful Degradation
```javascript
// ✅ Good: App works without sync
if (isSyncEnabled && navigator.onLine) {
  try {
    await syncToCloud();
  } catch {
    // Silent failure - local works fine
  }
}

// ❌ Bad: Breaks app if sync fails
await syncToCloud(); // Will throw if offline
```

### 3. Show Sync Status
```javascript
// ✅ Good: User knows what's happening
if (isSyncEnabled) {
  showStatus('Synced to cloud');
} else {
  showStatus('Saved locally');
}

// ❌ Bad: User doesn't know if sync is working
showStatus('Saved');
```

### 4. Handle Offline Mode
```javascript
// ✅ Good: Check online status
if (navigator.onLine && isSyncEnabled) {
  await syncToCloud();
}

// ❌ Bad: Tries to sync offline
await syncToCloud(); // Will fail offline
```

## Testing

### Test Local-Only Mode
```bash
# Disable sync in .env
VITE_SYNC_SERVICE_URL=

# Start app
npm run dev

# All features should work ✓
```

### Test Sync Mode
```bash
# Enable sync in .env
VITE_SYNC_SERVICE_URL=https://clarity-sync.onrender.com

# Start app
npm run dev

# Should see sync status indicators ✓
```

### Test Offline Mode
```bash
# Enable sync
VITE_SYNC_SERVICE_URL=https://clarity-sync.onrender.com

# Start app
npm run dev

# Disconnect from internet in browser DevTools
# All features should still work ✓
```

## Summary

### Local Backend (Always Required)
- **Purpose**: All AI operations
- **URL**: `http://localhost:5000`
- **Endpoints**: `/api/query`, `/api/quiz/generate`, `/api/embed`
- **Required**: Yes
- **Works Offline**: Yes

### Sync Service (Optional)
- **Purpose**: Multi-device sync
- **URL**: `https://clarity-sync.onrender.com`
- **Endpoints**: `/api/sync/notebooks`, `/api/sync/settings`
- **Required**: No
- **Works Offline**: No (gracefully degrades)

### Key Principles
1. ✅ Local backend is primary
2. ✅ Sync is optional enhancement
3. ✅ App works 100% offline
4. ✅ Graceful degradation if sync fails
5. ✅ User always knows sync status
