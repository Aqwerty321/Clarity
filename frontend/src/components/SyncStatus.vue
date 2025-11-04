<template>
  <div class="sync-status-container">
    <div 
      class="sync-status-badge"
      :class="statusClass"
      @click="showDetails = !showDetails"
      :title="statusTooltip"
    >
      <span class="status-icon">{{ statusIcon }}</span>
      <span class="status-text">{{ statusText }}</span>
      <span v-if="syncing" class="sync-spinner">⟳</span>
    </div>

    <!-- Detailed sync info (expandable) -->
    <Transition name="slide-fade">
      <div v-if="showDetails" class="sync-details glass-card">
        <div class="detail-row">
          <span class="detail-label">Mode:</span>
          <span class="detail-value">{{ syncMode }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Connection:</span>
          <span class="detail-value">{{ connectionStatus }}</span>
        </div>
        <div v-if="lastSync" class="detail-row">
          <span class="detail-label">Last Sync:</span>
          <span class="detail-value">{{ lastSyncFormatted }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Local AI:</span>
          <span class="detail-value" :class="{ 'text-green-400': localBackendStatus, 'text-red-400': !localBackendStatus }">
            {{ localBackendStatus ? '✓ Running' : '✗ Not running' }}
          </span>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { isSyncEnabled, isOnline, localBackend, syncService } from '@/api/clients';

// State
const showDetails = ref(false);
const syncing = ref(false);
const lastSync = ref(null);
const localBackendStatus = ref(false);
const online = ref(navigator.onLine);

// Computed
const statusIcon = computed(() => {
  if (syncing.value) return '⟳';
  if (!isSyncEnabled) return '💾';
  if (!online.value) return '📴';
  return '☁️';
});

const statusText = computed(() => {
  if (syncing.value) return 'Syncing...';
  if (!isSyncEnabled) return 'Local Only';
  if (!online.value) return 'Offline';
  return 'Synced';
});

const statusClass = computed(() => {
  if (syncing.value) return 'syncing';
  if (!isSyncEnabled) return 'local-only';
  if (!online.value) return 'offline';
  return 'synced';
});

const statusTooltip = computed(() => {
  if (!isSyncEnabled) return 'Running in local-only mode. All features available.';
  if (!online.value) return 'Offline mode. Changes will sync when online.';
  if (syncing.value) return 'Syncing your data to cloud...';
  return 'Connected and synced to cloud backup.';
});

const syncMode = computed(() => {
  return isSyncEnabled ? 'Local + Cloud Sync' : 'Local Only';
});

const connectionStatus = computed(() => {
  if (!isSyncEnabled) return 'Not configured';
  if (!online.value) return 'Offline';
  return 'Online';
});

const lastSyncFormatted = computed(() => {
  if (!lastSync.value) return 'Never';
  const date = new Date(lastSync.value);
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  
  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays}d ago`;
});

// Methods
const checkLocalBackend = async () => {
  try {
    await localBackend.get('/api/health');
    localBackendStatus.value = true;
  } catch (error) {
    localBackendStatus.value = false;
  }
};

const updateOnlineStatus = () => {
  online.value = navigator.onLine;
};

const loadLastSync = () => {
  const saved = localStorage.getItem('clarity_last_sync');
  if (saved) {
    lastSync.value = saved;
  }
};

const saveLastSync = () => {
  const now = new Date().toISOString();
  lastSync.value = now;
  localStorage.setItem('clarity_last_sync', now);
};

// Expose methods for parent components to call
defineExpose({
  setSyncing: (value) => { syncing.value = value; },
  updateLastSync: saveLastSync,
});

// Lifecycle
onMounted(() => {
  // Check local backend status
  checkLocalBackend();
  const backendCheckInterval = setInterval(checkLocalBackend, 30000); // Check every 30s

  // Load last sync time
  loadLastSync();

  // Listen for online/offline events
  window.addEventListener('online', updateOnlineStatus);
  window.addEventListener('offline', updateOnlineStatus);

  // Cleanup
  onUnmounted(() => {
    clearInterval(backendCheckInterval);
    window.removeEventListener('online', updateOnlineStatus);
    window.removeEventListener('offline', updateOnlineStatus);
  });
});
</script>

<style scoped>
.sync-status-container {
  position: relative;
}

.sync-status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.sync-status-badge:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.sync-status-badge.local-only {
  background: rgba(99, 102, 241, 0.2);
  border: 1px solid rgba(99, 102, 241, 0.5);
  color: #a5b4fc;
}

.sync-status-badge.offline {
  background: rgba(251, 191, 36, 0.2);
  border: 1px solid rgba(251, 191, 36, 0.5);
  color: #fcd34d;
}

.sync-status-badge.synced {
  background: rgba(34, 197, 94, 0.2);
  border: 1px solid rgba(34, 197, 94, 0.5);
  color: #86efac;
}

.sync-status-badge.syncing {
  background: rgba(59, 130, 246, 0.2);
  border: 1px solid rgba(59, 130, 246, 0.5);
  color: #93c5fd;
}

.status-icon {
  font-size: 1.25rem;
}

.status-text {
  font-weight: 600;
}

.sync-spinner {
  display: inline-block;
  animation: spin 1s linear infinite;
  font-size: 1.25rem;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* Details card */
.sync-details {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  min-width: 250px;
  padding: 1rem;
  border-radius: 0.75rem;
  background: rgba(15, 23, 42, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
  z-index: 100;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-label {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.875rem;
}

.detail-value {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
  font-size: 0.875rem;
}

/* Transition */
.slide-fade-enter-active {
  transition: all 0.3s ease;
}

.slide-fade-leave-active {
  transition: all 0.2s ease;
}

.slide-fade-enter-from {
  transform: translateY(-10px);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateY(-10px);
  opacity: 0;
}
</style>
