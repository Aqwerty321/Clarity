<template>
  <div class="notebooks-grid">
    <div
      v-for="(notebook, index) in notebooks"
      :key="notebook.id"
      class="notebook-card"
      :style="{ animationDelay: `${index * 0.1}s` }"
      @click="openNotebook(notebook.id)"
    >
      <div class="card-glow"></div>
      <div class="card-content">
        <div class="card-icon">📓</div>
        <h2 class="card-title">{{ notebook.title }}</h2>
        <div class="card-stats">
          <div class="stat">
            <span class="stat-icon">📄</span>
            <span class="stat-value">{{ notebook.documentCount || 0 }} documents</span>
          </div>
          <div class="stat">
            <span class="stat-icon">🕐</span>
            <span class="stat-value">{{ formatDate(notebook.updatedAt) }}</span>
          </div>
        </div>
        <div class="card-actions">
          <button
            @click.stop="$emit('delete', notebook.id)"
            class="action-button delete"
          >
            <span>🗑️</span>
          </button>
          <button
            @click.stop="$emit('export', notebook.id)"
            class="action-button export"
          >
            <span>📤</span>
          </button>
        </div>
      </div>
      <div class="card-shine"></div>
    </div>
    
    <div
      class="notebook-card create-card"
      @click="$emit('create')"
    >
      <div class="create-content">
        <div class="create-icon">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="icon"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 4v16m8-8H4"
            />
          </svg>
        </div>
        <p class="create-text">Create New Notebook</p>
      </div>
      <div class="create-pulse"></div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

defineProps({
  notebooks: {
    type: Array,
    default: () => [],
  },
})

defineEmits(['create', 'delete', 'export'])

const router = useRouter()

const openNotebook = (id) => {
  router.push(`/notebook/${id}`)
}

const formatDate = (dateString) => {
  if (!dateString) return 'Never'
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  
  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  
  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `${diffHours}h ago`
  
  const diffDays = Math.floor(diffHours / 24)
  if (diffDays < 7) return `${diffDays}d ago`
  
  return date.toLocaleDateString()
}
</script>

<style scoped>
.notebooks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
}

.notebook-card {
  background: rgba(15, 12, 41, 0.1);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(139, 182, 255, 0.15);
  border-radius: 16px;
  padding: 1.5rem;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.4s ease-in-out;
  animation: cardSlideUp 0.6s ease-in-out both;
}

@keyframes cardSlideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.notebook-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, 
    transparent, 
    rgba(139, 182, 255, 0.6), 
    transparent
  );
  transform: translateX(-100%);
  transition: transform 0.6s ease-in-out;
}

.notebook-card:hover::before {
  transform: translateX(100%);
}

.notebook-card:hover {
  background: rgba(15, 12, 41, 0.15);
  border-color: rgba(139, 182, 255, 0.3);
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 20px 60px rgba(139, 182, 255, 0.2);
}

.card-glow {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(139, 182, 255, 0.1) 0%, transparent 70%);
  opacity: 0;
  transition: opacity 0.4s ease-in-out;
  pointer-events: none;
}

.notebook-card:hover .card-glow {
  opacity: 1;
}

.card-content {
  position: relative;
  z-index: 1;
}

.card-icon {
  font-size: 2.5rem;
  margin-bottom: 0.75rem;
  animation: float 3s infinite ease-in-out;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-5px);
  }
}

.card-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: rgba(200, 220, 255, 0.95);
  margin-bottom: 1rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-stats {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.stat {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: rgba(200, 220, 255, 0.7);
}

.stat-icon {
  font-size: 1rem;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.action-button {
  width: 2.5rem;
  height: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(139, 182, 255, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(139, 182, 255, 0.2);
  border-radius: 8px;
  font-size: 1.125rem;
  cursor: pointer;
  transition: all 0.3s ease-in-out;
}

.action-button:hover {
  background: rgba(139, 182, 255, 0.2);
  border-color: rgba(139, 182, 255, 0.4);
  transform: scale(1.1);
}

.action-button.delete:hover {
  background: rgba(255, 107, 107, 0.2);
  border-color: rgba(255, 107, 107, 0.4);
}

.action-button.export:hover {
  background: rgba(107, 255, 178, 0.2);
  border-color: rgba(107, 255, 178, 0.4);
}

.card-shine {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(45deg, 
    transparent, 
    rgba(255, 255, 255, 0.03), 
    transparent
  );
  transform: rotate(45deg);
  transition: all 0.6s ease-in-out;
  pointer-events: none;
}

.notebook-card:hover .card-shine {
  left: 100%;
}

/* Create Card */
.create-card {
  border: 2px dashed rgba(139, 182, 255, 0.3);
  background: rgba(15, 12, 41, 0.05);
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
}

.create-card:hover {
  border-color: rgba(139, 182, 255, 0.5);
  background: rgba(15, 12, 41, 0.1);
}

.create-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  position: relative;
  z-index: 1;
}

.create-icon {
  width: 4rem;
  height: 4rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(139, 182, 255, 0.1);
  border: 2px solid rgba(139, 182, 255, 0.2);
  border-radius: 50%;
  transition: all 0.4s ease-in-out;
}

.create-card:hover .create-icon {
  background: rgba(139, 182, 255, 0.2);
  border-color: rgba(139, 182, 255, 0.4);
  transform: rotate(90deg) scale(1.1);
}

.icon {
  width: 2rem;
  height: 2rem;
  stroke: rgba(139, 182, 255, 0.8);
}

.create-text {
  color: rgba(200, 220, 255, 0.7);
  font-weight: 600;
  font-size: 1rem;
  transition: color 0.3s ease-in-out;
}

.create-card:hover .create-text {
  color: rgba(200, 220, 255, 0.95);
}

.create-pulse {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 100px;
  height: 100px;
  transform: translate(-50%, -50%);
  background: radial-gradient(circle, rgba(139, 182, 255, 0.2) 0%, transparent 70%);
  border-radius: 50%;
  opacity: 0;
  transition: opacity 0.4s ease-in-out;
  animation: pulse 2s infinite ease-in-out;
  pointer-events: none;
}

.create-card:hover .create-pulse {
  opacity: 1;
}

@keyframes pulse {
  0%, 100% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0.5;
  }
  50% {
    transform: translate(-50%, -50%) scale(1.5);
    opacity: 0;
  }
}
</style>
