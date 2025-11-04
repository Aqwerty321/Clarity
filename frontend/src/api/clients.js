/**
 * API Clients for Clarity Local-First Architecture
 * 
 * Two API clients:
 * 1. localBackend - For all AI operations (REQUIRED, localhost:5000)
 * 2. syncService - For optional cloud sync (OPTIONAL, Render)
 */

import axios from 'axios';

// ============================================================================
// LOCAL BACKEND - Required for all AI operations
// ============================================================================

/**
 * Local AI Backend Client
 * Runs on user's machine at localhost:5000
 * Handles: Embeddings, RAG queries, quiz generation, all AI operations
 */
export const localBackend = axios.create({
  baseURL: import.meta.env.VITE_LOCAL_BACKEND_URL || 'http://localhost:5000',
  timeout: 30000, // AI operations can take time
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for logging (development)
localBackend.interceptors.request.use(
  (config) => {
    if (import.meta.env.DEV) {
      console.log('🤖 [Local AI]', config.method?.toUpperCase(), config.url);
    }
    return config;
  },
  (error) => {
    console.error('❌ [Local AI] Request error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
localBackend.interceptors.response.use(
  (response) => {
    if (import.meta.env.DEV) {
      console.log('✅ [Local AI] Response:', response.status, response.config.url);
    }
    return response;
  },
  (error) => {
    if (error.code === 'ECONNREFUSED' || error.code === 'ERR_NETWORK') {
      console.error('❌ [Local AI] Backend not reachable. Is it running on port 5000?');
      throw new Error('Local AI backend not running. Please start it with: uvicorn app.main:app --reload --port 5000');
    }
    throw error;
  }
);

// ============================================================================
// CLOUD SYNC SERVICE - Optional for multi-device sync
// ============================================================================

/**
 * Cloud Sync Service Client (Optional)
 * Only for metadata and text backup - NO AI processing
 * Handles: Notebook sync, settings sync, conversation backup
 */
const syncServiceUrl = import.meta.env.VITE_SYNC_SERVICE_URL;

export const syncService = syncServiceUrl
  ? axios.create({
      baseURL: syncServiceUrl,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    })
  : null;

// Check if sync is enabled
export const isSyncEnabled = !!syncService;

// Add request interceptor for sync service
if (syncService) {
  syncService.interceptors.request.use(
    (config) => {
      if (import.meta.env.DEV) {
        console.log('☁️ [Cloud Sync]', config.method?.toUpperCase(), config.url);
      }
      return config;
    },
    (error) => {
      console.error('❌ [Cloud Sync] Request error:', error);
      return Promise.reject(error);
    }
  );

  syncService.interceptors.response.use(
    (response) => {
      if (import.meta.env.DEV) {
        console.log('✅ [Cloud Sync] Response:', response.status, response.config.url);
      }
      return response;
    },
    (error) => {
      // Sync failures are non-critical
      console.warn('⚠️ [Cloud Sync] Failed (local still works):', error.message);
      throw error;
    }
  );
}

// ============================================================================
// AUTH CONFIGURATION
// ============================================================================

/**
 * Configure Auth0 token for sync service
 * Call this after Auth0 login
 */
export const configureSyncAuth = (getAccessTokenFn) => {
  if (syncService) {
    syncService.interceptors.request.use(async (config) => {
      try {
        const token = await getAccessTokenFn();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
      } catch (error) {
        console.warn('⚠️ [Cloud Sync] Could not get auth token:', error);
      }
      return config;
    });
  }
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Get a unique device ID for sync tracking
 */
export const getDeviceId = () => {
  let deviceId = localStorage.getItem('clarity_device_id');
  if (!deviceId) {
    deviceId = crypto.randomUUID();
    localStorage.setItem('clarity_device_id', deviceId);
  }
  return deviceId;
};

/**
 * Check if the app is online
 */
export const isOnline = () => navigator.onLine;

/**
 * Sync status helper
 */
export const getSyncStatus = () => {
  if (!isSyncEnabled) {
    return { enabled: false, status: 'Local Only', icon: '💾' };
  }
  if (!isOnline()) {
    return { enabled: true, status: 'Offline', icon: '📴' };
  }
  return { enabled: true, status: 'Online', icon: '☁️' };
};

// ============================================================================
// EXPORTS
// ============================================================================

export default {
  localBackend,
  syncService,
  isSyncEnabled,
  configureSyncAuth,
  getDeviceId,
  isOnline,
  getSyncStatus,
};
