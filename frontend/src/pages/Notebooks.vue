<template>
  <div class="notebooks-container">
    <QuickNav />
    <div class="header-section">
      <h1 class="page-title">
        <span class="title-icon">📚</span>
        <span class="title-text">My Notebooks</span>
      </h1>
      <button @click="syncAll" class="sync-button" :disabled="syncing">
        <span v-if="syncing" class="sync-spinner"></span>
        <span v-else class="sync-icon">🔄</span>
        <span>{{ syncing ? 'Syncing...' : 'Sync All' }}</span>
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p class="loading-text">Loading your notebooks...</p>
    </div>

    <!-- Notebooks List -->
    <NotebookList
      v-else
      :notebooks="notebooks"
      @create="createNotebook"
      @delete="deleteNotebook"
      @export="exportNotebook"
    />

    <!-- Create Notebook Modal -->
    <dialog ref="createModal" class="glass-modal" @click="handleModalClick">
      <div class="modal-content" @click.stop>
        <h3 class="modal-title">Create New Notebook</h3>
        <div class="form-group">
          <label class="form-label">Notebook Title</label>
          <input
            v-model="newNotebookTitle"
            type="text"
            placeholder="Enter notebook title"
            class="glass-input"
            @keydown.enter="confirmCreate"
          />
        </div>
        <div class="modal-actions">
          <button @click="confirmCreate" class="modal-button primary">
            <span>Create</span>
            <span class="button-icon">✨</span>
          </button>
          <button @click="closeCreateModal" class="modal-button secondary">Cancel</button>
        </div>
      </div>
    </dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth0 } from '@auth0/auth0-vue'
import { useUserStore } from '../stores/user'
import NotebookList from '../components/NotebookList.vue'
import QuickNav from '../components/QuickNav.vue'
import axios from 'axios'

const router = useRouter()
const auth0 = useAuth0()
const userStore = useUserStore()

const loading = ref(true)
const syncing = ref(false)
const notebooks = ref([])
const createModal = ref(null)
const newNotebookTitle = ref('')

onMounted(async () => {
  // Check if authenticated
  if (!auth0.isAuthenticated.value) {
    router.push('/')
    return
  }

  await loadNotebooks()
})

const loadNotebooks = async () => {
  loading.value = true
  try {
    const userId = auth0.user.value?.sub || 'anonymous'
    
    // Fetch notebooks from backend
    const response = await axios.get('/api/notebooks', {
      params: { user_id: userId }
    })
    
    notebooks.value = response.data
    userStore.setNotebooks(notebooks.value)
  } catch (error) {
    console.error('Failed to load notebooks:', error)
    // Fallback to stored notebooks if API fails
    notebooks.value = userStore.notebooks || []
  } finally {
    loading.value = false
  }
}

const createNotebook = () => {
  newNotebookTitle.value = ''
  createModal.value?.showModal()
}

const confirmCreate = async () => {
  if (!newNotebookTitle.value.trim()) return

  try {
    const userId = auth0.user.value?.sub || 'anonymous'
    
    // Create notebook via API
    const response = await axios.post('/api/notebooks', {
      user_id: userId,
      title: newNotebookTitle.value,
      description: null
    })
    
    const newNotebook = response.data
    notebooks.value.push(newNotebook)
    userStore.addNotebook(newNotebook)
    
    closeCreateModal()
    router.push(`/notebook/${newNotebook.id}`)
  } catch (error) {
    console.error('Failed to create notebook:', error)
    alert('Failed to create notebook: ' + (error.response?.data?.detail || error.message))
  }
}

const closeCreateModal = () => {
  createModal.value?.close()
  newNotebookTitle.value = ''
}

const handleModalClick = (e) => {
  // Close modal when clicking on backdrop (the dialog element itself)
  if (e.target === createModal.value) {
    closeCreateModal()
  }
}

const deleteNotebook = async (id) => {
  if (!confirm('Are you sure you want to delete this notebook?')) return

  try {
    const userId = auth0.user.value?.sub || 'anonymous'
    
    // Delete notebook via API
    await axios.delete(`/api/notebooks/${id}`, {
      params: { user_id: userId }
    })
    
    notebooks.value = notebooks.value.filter(n => n.id !== id)
    userStore.deleteNotebook(id)
  } catch (error) {
    console.error('Failed to delete notebook:', error)
    alert('Failed to delete notebook: ' + (error.response?.data?.detail || error.message))
  }
}

const exportNotebook = async (id) => {
  try {
    // Mock export - replace with actual API call
    const notebook = notebooks.value.find(n => n.id === id)
    if (!notebook) return

    const blob = new Blob([JSON.stringify(notebook, null, 2)], {
      type: 'application/json',
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${notebook.title}.json`
    a.click()
    URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Failed to export notebook:', error)
  }
}

const syncAll = async () => {
  syncing.value = true
  try {
    // Mock sync - replace with actual API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    console.log('Synced all notebooks')
  } catch (error) {
    console.error('Failed to sync notebooks:', error)
  } finally {
    syncing.value = false
  }
}
</script>

<style scoped>
.notebooks-container {
  animation: fadeIn 0.6s ease-in-out;
  padding-left: 10rem;
}

@media (max-width: 1024px) {
  .notebooks-container {
    padding-left: 1rem;
    padding-top: 6rem;
  }
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: rgba(15, 12, 41, 0.1);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(139, 182, 255, 0.15);
  border-radius: 16px;
  transition: all 0.4s ease-in-out;
  animation: slideDown 0.6s ease-in-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.header-section:hover {
  background: rgba(15, 12, 41, 0.15);
  border-color: rgba(139, 182, 255, 0.25);
  box-shadow: 0 10px 40px rgba(139, 182, 255, 0.1);
}

.page-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 2rem;
  font-weight: 700;
  margin: 0;
}

.title-icon {
  font-size: 2.5rem;
  animation: bounce 2s infinite ease-in-out;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}

.title-text {
  background: linear-gradient(135deg, #8bb6ff, #c4e0ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.sync-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: rgba(139, 182, 255, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(139, 182, 255, 0.2);
  border-radius: 10px;
  color: rgba(200, 220, 255, 0.95);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease-in-out;
}

.sync-button:hover:not(:disabled) {
  background: rgba(139, 182, 255, 0.2);
  border-color: rgba(139, 182, 255, 0.4);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(139, 182, 255, 0.2);
}

.sync-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.sync-icon {
  font-size: 1.25rem;
  transition: transform 0.3s ease-in-out;
}

.sync-button:hover:not(:disabled) .sync-icon {
  transform: rotate(180deg);
}

.sync-spinner {
  width: 1.25rem;
  height: 1.25rem;
  border: 2px solid rgba(139, 182, 255, 0.3);
  border-top-color: rgba(139, 182, 255, 0.9);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Loading State */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  background: rgba(15, 12, 41, 0.1);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(139, 182, 255, 0.15);
  border-radius: 16px;
  animation: pulse 2s infinite ease-in-out;
}

.loading-spinner {
  width: 3rem;
  height: 3rem;
  border: 3px solid rgba(139, 182, 255, 0.2);
  border-top-color: rgba(139, 182, 255, 0.8);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

.loading-text {
  color: rgba(200, 220, 255, 0.8);
  font-size: 1.125rem;
}

/* Modal Styles */
.glass-modal {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: transparent;
  border: none;
  padding: 0;
  max-width: 500px;
  width: 90%;
}

.glass-modal::backdrop {
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.modal-content {
  background: rgba(15, 12, 41, 0.95);
  backdrop-filter: blur(30px);
  -webkit-backdrop-filter: blur(30px);
  border: 1px solid rgba(139, 182, 255, 0.3);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  animation: modalSlide 0.4s ease-in-out;
}

@keyframes modalSlide {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.modal-title {
  font-size: 1.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, #8bb6ff, #c4e0ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-label {
  display: block;
  color: rgba(200, 220, 255, 0.9);
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.glass-input {
  width: 100%;
  padding: 0.75rem 1rem;
  background: rgba(139, 182, 255, 0.05);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(139, 182, 255, 0.2);
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.95);
  font-size: 1rem;
  transition: all 0.3s ease-in-out;
}

.glass-input:focus {
  outline: none;
  background: rgba(139, 182, 255, 0.1);
  border-color: rgba(139, 182, 255, 0.4);
  box-shadow: 0 0 20px rgba(139, 182, 255, 0.2);
}

.glass-input::placeholder {
  color: rgba(200, 220, 255, 0.5);
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.modal-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease-in-out;
  border: none;
}

.modal-button.primary {
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.3), rgba(168, 216, 255, 0.3));
  border: 1px solid rgba(139, 182, 255, 0.4);
  color: rgba(255, 255, 255, 0.95);
}

.modal-button.primary:hover {
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.4), rgba(168, 216, 255, 0.4));
  border-color: rgba(139, 182, 255, 0.6);
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(139, 182, 255, 0.3);
}

.modal-button.secondary {
  background: rgba(139, 182, 255, 0.05);
  border: 1px solid rgba(139, 182, 255, 0.2);
  color: rgba(200, 220, 255, 0.9);
}

.modal-button.secondary:hover {
  background: rgba(139, 182, 255, 0.1);
  border-color: rgba(139, 182, 255, 0.3);
}

.button-icon {
  font-size: 1.125rem;
  transition: transform 0.3s ease-in-out;
}

.modal-button:hover .button-icon {
  transform: scale(1.2);
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.8;
  }
}
</style>
