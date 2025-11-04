<template>
  <div class="mind-maps-page">
    <QuickNav />
    <!-- Header -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <span class="title-icon">🧠</span>
          Mind Maps
        </h1>
        <p class="page-subtitle">Visualize your knowledge with AI-powered mind maps</p>
      </div>
      <button @click="createModal?.showModal()" class="create-button">
        <span class="button-icon">✨</span>
        Generate Mind Map
      </button>
    </div>

    <!-- Mind Maps Grid -->
    <div v-if="mindMaps.length > 0" class="mind-maps-grid">
      <div 
        v-for="map in mindMaps" 
        :key="map.id" 
        class="mind-map-card glass-card"
        @click="navigateToMap(map.id)"
      >
        <div class="card-header">
          <h3 class="map-title">{{ map.title }}</h3>
          <button @click.stop="deleteMap(map.id)" class="delete-button">🗑️</button>
        </div>
        
        <p v-if="map.description" class="map-description">{{ map.description }}</p>
        
        <div class="map-info">
          <div class="info-item">
            <span class="info-icon">🔗</span>
            <span class="info-text">{{ map.nodeCount || 0 }} nodes</span>
          </div>
          <div class="info-item">
            <span class="info-icon">📊</span>
            <span class="info-text">{{ map.depth || 0 }} levels</span>
          </div>
          <div v-if="map.notebookTitle" class="info-item linked">
            <span class="info-icon">📓</span>
            <span class="info-text">{{ map.notebookTitle }}</span>
          </div>
        </div>

        <div class="map-preview">
          <div class="preview-node" v-for="i in Math.min(map.nodeCount || 3, 5)" :key="i" 
               :style="{ 
                 left: `${20 + i * 15}%`, 
                 top: `${30 + Math.sin(i) * 20}%`,
                 animationDelay: `${i * 0.1}s`
               }">
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <div class="empty-icon">🧠</div>
      <h2 class="empty-title">No Mind Maps Yet</h2>
      <p class="empty-subtitle">Generate your first AI-powered mind map from a notebook</p>
      <button @click="createModal?.showModal()" class="create-button-large">
        <span class="button-icon">✨</span>
        Generate Mind Map
      </button>
    </div>

    <!-- Create Mind Map Modal -->
    <dialog ref="createModal" class="glass-modal" @click="handleModalClick">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2 class="modal-title">
            <span class="title-icon">✨</span>
            Generate Mind Map
          </h2>
          <button @click="createModal?.close()" class="close-button">✕</button>
        </div>

        <form @submit.prevent="confirmCreate" class="modal-form">
          <div class="form-group">
            <label class="form-label">Title</label>
            <input 
              v-model="form.title" 
              type="text" 
              class="glass-input" 
              placeholder="My Knowledge Graph"
              required
            />
          </div>

          <div class="form-group">
            <label class="form-label">Description (Optional)</label>
            <textarea 
              v-model="form.description" 
              class="glass-input" 
              placeholder="A visual representation of..."
              rows="3"
            ></textarea>
          </div>

          <div class="form-group">
            <label class="form-label">Source Notebook</label>
            <select v-model="form.notebookId" class="glass-input" required>
              <option value="">Select a notebook...</option>
              <option v-for="notebook in notebooks" :key="notebook.id" :value="notebook.id">
                {{ notebook.title }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">Max Depth</label>
            <input 
              v-model.number="form.maxDepth" 
              type="number" 
              class="glass-input" 
              min="1"
              max="5"
              placeholder="3"
            />
            <span class="form-hint">How many levels deep (1-5)</span>
          </div>

          <div class="modal-actions">
            <button type="button" @click="createModal?.close()" class="cancel-button">
              Cancel
            </button>
            <button type="submit" class="submit-button" :disabled="creating">
              <span v-if="!creating">✨ Generate</span>
              <span v-else>⏳ Generating...</span>
            </button>
          </div>
        </form>
      </div>
    </dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth0 } from '@auth0/auth0-vue'
import QuickNav from '../components/QuickNav.vue'
import axios from 'axios'

const router = useRouter()
const auth0 = useAuth0()

const mindMaps = ref([])
const notebooks = ref([])
const createModal = ref(null)
const creating = ref(false)

const form = ref({
  title: '',
  description: '',
  notebookId: '',
  maxDepth: 3
})

const loadMindMaps = async () => {
  try {
    const userId = auth0.user.value?.sub || 'anonymous'
    const response = await axios.get(`/api/mind-maps?user_id=${userId}`)
    mindMaps.value = response.data
    console.log('Loaded mind maps:', mindMaps.value)
  } catch (error) {
    console.error('Failed to load mind maps:', error)
  }
}

const loadNotebooks = async () => {
  try {
    const userId = auth0.user.value?.sub || 'anonymous'
    const response = await axios.get(`/api/notebooks?user_id=${userId}`)
    notebooks.value = response.data
  } catch (error) {
    console.error('Failed to load notebooks:', error)
  }
}

const confirmCreate = async () => {
  if (!form.value.notebookId) {
    alert('Please select a notebook')
    return
  }

  creating.value = true
  try {
    const userId = auth0.user.value?.sub || 'anonymous'
    const response = await axios.post('/api/mind-maps', {
      user_id: userId,
      title: form.value.title,
      description: form.value.description || null,
      notebook_id: form.value.notebookId,
      max_depth: form.value.maxDepth || 3
    })

    console.log('Created mind map:', response.data)
    
    createModal.value?.close()
    form.value = { title: '', description: '', notebookId: '', maxDepth: 3 }
    
    // Navigate to the new mind map
    router.push(`/mind-maps/${response.data.id}`)
  } catch (error) {
    console.error('Failed to create mind map:', error)
    alert('Failed to generate mind map: ' + (error.response?.data?.detail || error.message))
  } finally {
    creating.value = false
  }
}

const navigateToMap = (mapId) => {
  router.push(`/mind-maps/${mapId}`)
}

const deleteMap = async (mapId) => {
  if (!confirm('Are you sure you want to delete this mind map?')) return

  try {
    const userId = auth0.user.value?.sub || 'anonymous'
    await axios.delete(`/api/mind-maps/${mapId}?user_id=${userId}`)
    await loadMindMaps()
  } catch (error) {
    console.error('Failed to delete mind map:', error)
    alert('Failed to delete mind map')
  }
}

const handleModalClick = (e) => {
  if (e.target === createModal.value) {
    createModal.value?.close()
  }
}

onMounted(() => {
  loadMindMaps()
  loadNotebooks()
})
</script>

<style scoped>
.mind-maps-page {
  min-height: 100vh;
  padding: 2rem 2rem 2rem 10rem;
  background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
  position: relative;
  overflow: hidden;
}

@media (max-width: 1024px) {
  .mind-maps-page {
    padding: 1rem;
    padding-top: 6rem;
  }
}

/* Animated background particles */
.mind-maps-page::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 20% 50%, rgba(139, 182, 255, 0.1) 0%, transparent 50%),
              radial-gradient(circle at 80% 80%, rgba(196, 224, 255, 0.1) 0%, transparent 50%),
              radial-gradient(circle at 40% 20%, rgba(168, 216, 255, 0.05) 0%, transparent 50%);
  animation: floatParticles 20s ease-in-out infinite;
  pointer-events: none;
}

@keyframes floatParticles {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(20px, -20px) scale(1.1); }
}

/* Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 3rem;
  position: relative;
  z-index: 1;
}

.header-content {
  flex: 1;
}

.page-title {
  font-size: 3rem;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.95);
  margin: 0 0 0.5rem 0;
  display: flex;
  align-items: center;
  gap: 1rem;
  text-shadow: 0 0 30px rgba(139, 182, 255, 0.5);
}

.title-icon {
  font-size: 3rem;
  filter: drop-shadow(0 0 10px rgba(139, 182, 255, 0.6));
  animation: pulse 3s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); filter: drop-shadow(0 0 10px rgba(139, 182, 255, 0.6)); }
  50% { transform: scale(1.1); filter: drop-shadow(0 0 20px rgba(139, 182, 255, 0.9)); }
}

.page-subtitle {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
}

.create-button {
  padding: 1rem 2rem;
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.2), rgba(196, 224, 255, 0.15));
  border: 1px solid rgba(139, 182, 255, 0.3);
  border-radius: 16px;
  color: rgba(255, 255, 255, 0.95);
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  backdrop-filter: blur(20px);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
  box-shadow: 0 8px 32px rgba(139, 182, 255, 0.2);
}

.create-button:hover {
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.3), rgba(196, 224, 255, 0.2));
  border-color: rgba(139, 182, 255, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(139, 182, 255, 0.4);
}

.button-icon {
  font-size: 1.2rem;
  animation: sparkle 2s ease-in-out infinite;
}

@keyframes sparkle {
  0%, 100% { transform: rotate(0deg) scale(1); opacity: 1; }
  50% { transform: rotate(180deg) scale(1.2); opacity: 0.8; }
}

/* Mind Maps Grid */
.mind-maps-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 2rem;
  position: relative;
  z-index: 1;
}

.mind-map-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  padding: 2rem;
  backdrop-filter: blur(20px);
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.mind-map-card::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(139, 182, 255, 0.1) 0%, transparent 70%);
  opacity: 0;
  transition: opacity 0.4s ease;
}

.mind-map-card:hover::before {
  opacity: 1;
  animation: rotate 8s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.mind-map-card:hover {
  transform: translateY(-8px) scale(1.02);
  border-color: rgba(139, 182, 255, 0.4);
  box-shadow: 0 20px 60px rgba(139, 182, 255, 0.3),
              0 0 80px rgba(139, 182, 255, 0.2) inset;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
  position: relative;
  z-index: 2;
}

.map-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.95);
  margin: 0;
  flex: 1;
}

.delete-button {
  background: rgba(255, 107, 107, 0.1);
  border: 1px solid rgba(255, 107, 107, 0.3);
  border-radius: 12px;
  padding: 0.5rem;
  font-size: 1.2rem;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.delete-button:hover {
  background: rgba(255, 107, 107, 0.2);
  border-color: rgba(255, 107, 107, 0.5);
  transform: scale(1.1);
}

.map-description {
  color: rgba(255, 255, 255, 0.7);
  margin: 0 0 1.5rem 0;
  line-height: 1.6;
  position: relative;
  z-index: 2;
}

.map-info {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem;
  position: relative;
  z-index: 2;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
}

.info-item.linked {
  background: rgba(139, 182, 255, 0.1);
  border-color: rgba(139, 182, 255, 0.3);
  color: rgba(196, 224, 255, 0.95);
  font-weight: 600;
}

.info-icon {
  font-size: 1rem;
}

/* Preview Animation */
.map-preview {
  position: relative;
  height: 120px;
  margin-top: 1.5rem;
  border-radius: 16px;
  background: rgba(0, 0, 0, 0.2);
  overflow: hidden;
  z-index: 1;
}

.preview-node {
  position: absolute;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(139, 182, 255, 0.6), rgba(196, 224, 255, 0.3));
  border: 2px solid rgba(139, 182, 255, 0.8);
  animation: float 3s ease-in-out infinite;
  box-shadow: 0 0 20px rgba(139, 182, 255, 0.6);
}

@keyframes float {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-10px) scale(1.1); }
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  position: relative;
  z-index: 1;
}

.empty-icon {
  font-size: 6rem;
  margin-bottom: 1.5rem;
  filter: drop-shadow(0 0 30px rgba(139, 182, 255, 0.5));
  animation: bounce 2s ease-in-out infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

.empty-title {
  font-size: 2rem;
  color: rgba(255, 255, 255, 0.9);
  margin: 0 0 1rem 0;
}

.empty-subtitle {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.6);
  margin: 0 0 2rem 0;
}

.create-button-large {
  padding: 1.25rem 3rem;
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.25), rgba(196, 224, 255, 0.15));
  border: 2px solid rgba(139, 182, 255, 0.4);
  border-radius: 20px;
  color: rgba(255, 255, 255, 0.95);
  font-size: 1.2rem;
  font-weight: 600;
  cursor: pointer;
  backdrop-filter: blur(20px);
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  transition: all 0.4s ease;
  box-shadow: 0 12px 40px rgba(139, 182, 255, 0.3);
}

.create-button-large:hover {
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.35), rgba(196, 224, 255, 0.25));
  transform: translateY(-4px) scale(1.05);
  box-shadow: 0 20px 60px rgba(139, 182, 255, 0.5);
}

/* Modal Styles */
.glass-modal {
  border: none;
  background: transparent;
  padding: 0;
  max-width: 600px;
  width: 90%;
  border-radius: 32px;
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  box-shadow: 0 25px 100px rgba(0, 0, 0, 0.5);
  z-index: 200;
}

.glass-modal::backdrop {
  background: rgba(15, 12, 41, 0.85);
  backdrop-filter: blur(10px);
  z-index: 199;
}

.modal-content {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 32px;
  padding: 2.5rem;
  backdrop-filter: blur(30px);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.modal-title {
  font-size: 2rem;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.95);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.close-button {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  width: 40px;
  height: 40px;
  font-size: 1.5rem;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-button:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: rotate(90deg);
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-size: 0.95rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.glass-input {
  padding: 0.875rem 1.25rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  color: rgba(255, 255, 255, 0.95);
  font-size: 1rem;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.glass-input:focus {
  outline: none;
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(139, 182, 255, 0.5);
  box-shadow: 0 0 20px rgba(139, 182, 255, 0.3);
}

.glass-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

select.glass-input {
  cursor: pointer;
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  background: rgba(139, 182, 255, 0.05) url("data:image/svg+xml,%3Csvg width='12' height='8' viewBox='0 0 12 8' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1.5L6 6.5L11 1.5' stroke='rgba(139,182,255,0.8)' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") no-repeat;
  background-position: right 1rem center;
  background-size: auto, 12px;
  padding-right: 3rem;
  transition: all 0.3s ease;
}

select.glass-input:hover {
  border-color: rgba(139, 182, 255, 0.4);
  background: rgba(139, 182, 255, 0.08) url("data:image/svg+xml,%3Csvg width='12' height='8' viewBox='0 0 12 8' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1.5L6 6.5L11 1.5' stroke='rgba(139,182,255,0.9)' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") no-repeat right 1rem center;
  background-size: 12px;
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(139, 182, 255, 0.15);
}

select.glass-input:focus {
  background: rgba(139, 182, 255, 0.1) url("data:image/svg+xml,%3Csvg width='12' height='8' viewBox='0 0 12 8' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1.5L6 6.5L11 1.5' stroke='rgba(139,182,255,1)' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") no-repeat right 1rem center;
  background-size: 12px;
}

select.glass-input option {
  background: rgba(15, 12, 41, 0.98);
  color: rgba(255, 255, 255, 0.95);
  padding: 0.75rem;
  border-radius: 8px;
}

/* Number input styling */
input[type="number"].glass-input {
  appearance: textfield;
  -moz-appearance: textfield;
}

input[type="number"].glass-input::-webkit-outer-spin-button,
input[type="number"].glass-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

textarea.glass-input {
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
}

.form-hint {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.5);
  font-style: italic;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.cancel-button {
  flex: 1;
  padding: 0.875rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cancel-button:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.25);
}

.submit-button {
  flex: 1;
  padding: 0.875rem;
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.3), rgba(196, 224, 255, 0.2));
  border: 1px solid rgba(139, 182, 255, 0.4);
  border-radius: 16px;
  color: rgba(255, 255, 255, 0.95);
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 24px rgba(139, 182, 255, 0.3);
}

.submit-button:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.4), rgba(196, 224, 255, 0.3));
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(139, 182, 255, 0.4);
}

.submit-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
