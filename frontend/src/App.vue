<template>
  <div id="app" class="min-h-screen midnight-gradient">
    <!-- Animated background particles -->
    <div class="particles">
      <div v-for="i in 20" :key="i" class="particle" :style="{ left: `${Math.random() * 100}%`, animationDelay: `${Math.random() * 5}s` }"></div>
    </div>

    <!-- Sync Status Indicator (top right) -->
    <div class="sync-status-wrapper">
      <SyncStatus ref="syncStatusRef" />
    </div>
    
    <main class="main-content">
      <router-view />
    </main>
    
    <footer class="glass-footer">
      <div class="container mx-auto px-4 py-6 text-center">
        <p class="footer-text">© 2025 Clarity - Local-first learning assistant. Built with ❤️ for privacy.</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuth0 } from '@auth0/auth0-vue'
import SyncStatus from './components/SyncStatus.vue'
import { configureSyncAuth } from './api/clients'

const $auth0 = useAuth0()
const syncStatusRef = ref(null)

// Configure sync service with Auth0 token
onMounted(() => {
  if ($auth0.isAuthenticated.value) {
    configureSyncAuth(async () => {
      const token = await $auth0.getAccessTokenSilently()
      return token
    })
  }
})
</script>

<style scoped>
/* Midnight Blue Gradient Background */
.midnight-gradient {
  background: linear-gradient(135deg, 
    #0f0c29 0%, 
    #302b63 50%, 
    #24243e 100%
  );
  position: relative;
  overflow-x: hidden;
}

/* Sync Status Wrapper */
.sync-status-wrapper {
  position: fixed;
  bottom: 1.5rem;
  right: 1.5rem;
  z-index: 100;
}

/* Animated Particles */
.particles {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.particle {
  position: absolute;
  width: 4px;
  height: 4px;
  background: rgba(139, 182, 255, 0.4);
  border-radius: 50%;
  animation: float 15s infinite ease-in-out;
  box-shadow: 0 0 10px rgba(139, 182, 255, 0.6);
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) translateX(0) scale(1);
    opacity: 0;
  }
  10% {
    opacity: 0.8;
  }
  50% {
    transform: translateY(-100vh) translateX(50px) scale(1.5);
    opacity: 0.6;
  }
  90% {
    opacity: 0.8;
  }
}

/* Glassmorphism Navigation */
.glass-nav {
  background: rgba(15, 12, 41, 0.1);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(139, 182, 255, 0.1);
  position: sticky;
  top: 0;
  z-index: 50;
  transition: all 0.4s ease-in-out;
}

.glass-nav:hover {
  background: rgba(15, 12, 41, 0.15);
  border-bottom: 1px solid rgba(139, 182, 255, 0.2);
}

.logo-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 12px;
  background: rgba(139, 182, 255, 0.05);
  border: 1px solid rgba(139, 182, 255, 0.1);
  transition: all 0.4s ease-in-out;
}

.logo-link:hover {
  background: rgba(139, 182, 255, 0.15);
  border: 1px solid rgba(139, 182, 255, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(139, 182, 255, 0.2);
}

.logo-icon {
  font-size: 1.75rem;
  animation: pulse 2s infinite ease-in-out;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

.logo-text {
  font-size: 1.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, #8bb6ff, #a8d8ff, #c4e0ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 10px;
  background: rgba(139, 182, 255, 0.05);
  border: 1px solid rgba(139, 182, 255, 0.1);
  color: rgba(200, 220, 255, 0.8);
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease-in-out;
}

.nav-link:hover {
  background: rgba(139, 182, 255, 0.15);
  border-color: rgba(139, 182, 255, 0.3);
  color: rgba(200, 220, 255, 1);
  transform: translateY(-2px);
}

.nav-link.router-link-active {
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.2), rgba(168, 216, 255, 0.2));
  border-color: rgba(139, 182, 255, 0.3);
  color: rgba(255, 255, 255, 0.95);
}

.nav-icon {
  font-size: 1.125rem;
}

/* Main Content */
.main-content {
  position: relative;
  z-index: 1;
  min-height: calc(100vh - 200px);
  animation: fadeIn 0.6s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Glassmorphism Footer */
.glass-footer {
  background: rgba(15, 12, 41, 0.1);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-top: 1px solid rgba(139, 182, 255, 0.1);
  margin-top: 4rem;
  position: relative;
  z-index: 0;
}

.footer-text {
  color: rgba(200, 220, 255, 0.7);
  font-size: 0.9rem;
  transition: color 0.3s ease-in-out;
}

.footer-text:hover {
  color: rgba(200, 220, 255, 1);
}

/* Global Glass Card Styles */
:deep(.glass-card) {
  background: rgba(15, 12, 41, 0.1);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(139, 182, 255, 0.15);
  border-radius: 16px;
  transition: all 0.4s ease-in-out;
}

:deep(.glass-card:hover) {
  background: rgba(15, 12, 41, 0.15);
  border: 1px solid rgba(139, 182, 255, 0.3);
  transform: translateY(-4px);
  box-shadow: 0 20px 60px rgba(139, 182, 255, 0.15);
}
</style>
