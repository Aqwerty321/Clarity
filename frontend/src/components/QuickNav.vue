<template>
  <div class="quick-nav">
    <router-link to="/notebooks" class="nav-item" :class="{ active: currentRoute === 'notebooks' }">
      <span class="nav-icon">📚</span>
      <span class="nav-label">Notebooks</span>
    </router-link>
    <router-link to="/quiz" class="nav-item" :class="{ active: currentRoute === 'quiz' }">
      <span class="nav-icon">🎯</span>
      <span class="nav-label">Quiz</span>
    </router-link>
    <router-link to="/flashcards" class="nav-item" :class="{ active: currentRoute === 'flashcards' }">
      <span class="nav-icon">🎴</span>
      <span class="nav-label">Flashcards</span>
    </router-link>
    <router-link to="/mind-maps" class="nav-item" :class="{ active: currentRoute === 'mind-maps' }">
      <span class="nav-icon">🧠</span>
      <span class="nav-label">Mind Maps</span>
    </router-link>
    <router-link to="/analytics" class="nav-item" :class="{ active: currentRoute === 'analytics' }">
      <span class="nav-icon">📊</span>
      <span class="nav-label">Analytics</span>
    </router-link>
    <router-link to="/marketplace" class="nav-item" :class="{ active: currentRoute === 'marketplace' }">
      <span class="nav-icon">🏪</span>
      <span class="nav-label">Marketplace</span>
    </router-link>
    <router-link to="/settings" class="nav-item" :class="{ active: currentRoute === 'settings' }">
      <span class="nav-icon">⚙️</span>
      <span class="nav-label">Settings</span>
    </router-link>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const currentRoute = computed(() => route.path.split('/')[1])
</script>

<style scoped>
.quick-nav {
  position: fixed;
  top: 50%;
  left: 2rem;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  gap: 1rem;
  z-index: 100;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  text-decoration: none;
  color: rgba(255, 255, 255, 0.7);
  transition: all 0.3s ease;
  backdrop-filter: blur(20px);
  cursor: pointer;
  min-width: 80px;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(139, 182, 255, 0.4);
  color: rgba(255, 255, 255, 0.95);
  transform: translateX(8px);
  box-shadow: 0 8px 32px rgba(139, 182, 255, 0.3);
}

.nav-item.active {
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.25), rgba(196, 224, 255, 0.15));
  border-color: rgba(139, 182, 255, 0.5);
  color: rgba(255, 255, 255, 0.95);
  box-shadow: 0 8px 32px rgba(139, 182, 255, 0.4);
}

.nav-icon {
  font-size: 2rem;
  filter: drop-shadow(0 0 8px rgba(139, 182, 255, 0.5));
}

.nav-label {
  font-size: 0.75rem;
  font-weight: 600;
  text-align: center;
  white-space: nowrap;
}

/* Responsive */
@media (max-width: 1024px) {
  .quick-nav {
    position: static;
    transform: none;
    flex-direction: row;
    justify-content: center;
    padding: 1rem;
    margin-bottom: 2rem;
  }
  
  .nav-item:hover {
    transform: translateY(-4px);
  }
}
</style>
