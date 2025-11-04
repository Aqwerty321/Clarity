<template>
  <div class="flashcards-container">
    <QuickNav />
    <div class="header-section">
      <h1 class="page-title">
        <span class="title-icon">🎴</span>
        <span class="title-text">My Flashcard Decks</span>
      </h1>
      <button @click="createDeck" class="create-button">
        <span class="button-icon">✨</span>
        <span>Create Deck</span>
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p class="loading-text">Loading your flashcard decks...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="decks.length === 0" class="empty-state">
      <div class="empty-icon">🎴</div>
      <h2 class="empty-title">No Flashcard Decks Yet</h2>
      <p class="empty-description">Create your first flashcard deck from your study materials</p>
      <button @click="createDeck" class="cta-button">
        <span>Create Your First Deck</span>
        <span class="button-icon">→</span>
      </button>
    </div>

    <!-- Decks Grid -->
    <div v-else class="decks-grid">
      <div
        v-for="(deck, index) in decks"
        :key="deck.id"
        class="deck-card"
        :style="{ animationDelay: `${index * 0.1}s` }"
        @click="openDeck(deck.id)"
      >
        <div class="card-glow"></div>
        <div class="deck-header">
          <div class="deck-icon">🎴</div>
          <div class="deck-stats">
            <span class="stat-badge new">{{ deck.newCards || 0 }} new</span>
            <span class="stat-badge review">{{ deck.reviewCards || 0 }} review</span>
          </div>
        </div>
        <h2 class="deck-title">{{ deck.title }}</h2>
        <p class="deck-description">{{ deck.description || 'No description' }}</p>
        <div class="deck-info">
          <div class="info-item">
            <span class="info-icon">📄</span>
            <span>{{ deck.cardCount || 0 }} cards</span>
          </div>
          <div class="info-item">
            <span class="info-icon">🎯</span>
            <span>{{ deck.masteredCards || 0 }} mastered</span>
          </div>
          <div v-if="deck.notebookId" class="info-item linked-notebook">
            <span class="info-icon">✨</span>
            <span>AI-enabled</span>
          </div>
        </div>
        <div class="deck-actions">
          <button @click.stop="studyDeck(deck.id)" class="action-button study">
            <span>Study Now</span>
          </button>
          <button @click.stop="editDeck(deck.id)" class="action-button edit">
            <span>✏️</span>
          </button>
          <button @click.stop="deleteDeck(deck.id)" class="action-button delete">
            <span>🗑️</span>
          </button>
        </div>
        <div class="card-shine"></div>
      </div>
    </div>

    <!-- Create Deck Modal -->
    <dialog ref="createModal" class="glass-modal" @click="handleModalClick">
      <div class="modal-content" @click.stop>
        <h3 class="modal-title">Create Flashcard Deck</h3>
        <div class="form-group">
          <label class="form-label">Deck Title</label>
          <input
            v-model="newDeck.title"
            type="text"
            placeholder="e.g., Spanish Vocabulary"
            class="glass-input"
            @keydown.enter="handleCreateMethod"
          />
        </div>
        <div class="form-group">
          <label class="form-label">Description (optional)</label>
          <textarea
            v-model="newDeck.description"
            placeholder="Brief description of this deck"
            class="glass-input"
            rows="3"
          ></textarea>
        </div>
        <div class="form-group">
          <label class="form-label">Create from</label>
          <div class="create-options">
            <button
              @click="createMethod = 'notebook'"
              :class="['option-button', { active: createMethod === 'notebook' }]"
            >
              <span class="option-icon">📚</span>
              <span>From Notebook</span>
            </button>
            <button
              @click="createMethod = 'manual'"
              :class="['option-button', { active: createMethod === 'manual' }]"
            >
              <span class="option-icon">✍️</span>
              <span>Manual Entry</span>
            </button>
          </div>
        </div>
        <div v-if="createMethod === 'notebook'" class="form-group">
          <label class="form-label">Select Notebook</label>
          <select v-model="newDeck.notebookId" class="glass-input">
            <option value="">Choose a notebook...</option>
            <option v-for="notebook in notebooks" :key="notebook.id" :value="notebook.id">
              {{ notebook.title }}
            </option>
          </select>
        </div>
        <div class="modal-actions">
          <button @click.stop="confirmCreate" class="modal-button primary">
            <span>Create Deck</span>
            <span class="button-icon">✨</span>
          </button>
          <button @click.stop="closeCreateModal" class="modal-button secondary">Cancel</button>
        </div>
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

const loading = ref(true)
const decks = ref([])
const notebooks = ref([])
const createModal = ref(null)
const createMethod = ref('notebook')
const newDeck = ref({
  title: '',
  description: '',
  notebookId: ''
})

onMounted(async () => {
  if (!auth0.isAuthenticated.value) {
    router.push('/')
    return
  }
  await loadDecks()
  await loadNotebooks()
})

const loadDecks = async () => {
  loading.value = true
  try {
    const userId = auth0.user.value?.sub || 'anonymous'
    const response = await axios.get('/api/flashcard-decks', {
      params: { user_id: userId }
    })
    
    // Log to check for duplicates
    console.log('Loaded decks:', response.data)
    console.log('Deck IDs:', response.data.map(d => d.id))
    
    // Remove any duplicate decks (by ID)
    const uniqueDecks = response.data.reduce((acc, deck) => {
      if (!acc.find(d => d.id === deck.id)) {
        acc.push(deck)
      }
      return acc
    }, [])
    
    if (uniqueDecks.length !== response.data.length) {
      console.warn(`Removed ${response.data.length - uniqueDecks.length} duplicate decks from display`)
    }
    
    decks.value = uniqueDecks
  } catch (error) {
    console.error('Failed to load flashcard decks:', error)
    decks.value = []
  } finally {
    loading.value = false
  }
}

const loadNotebooks = async () => {
  try {
    const userId = auth0.user.value?.sub || 'anonymous'
    const response = await axios.get('/api/notebooks', {
      params: { user_id: userId }
    })
    notebooks.value = response.data
  } catch (error) {
    console.error('Failed to load notebooks:', error)
  }
}

const createDeck = () => {
  newDeck.value = { title: '', description: '', notebookId: '' }
  createMethod.value = 'notebook'
  createModal.value?.showModal()
}

const handleCreateMethod = () => {
  if (createMethod.value === 'manual') {
    confirmCreate()
  }
}

const confirmCreate = async () => {
  console.log('Creating deck...', { 
    title: newDeck.value.title,
    method: createMethod.value,
    notebookId: newDeck.value.notebookId 
  })

  if (!newDeck.value.title.trim()) {
    alert('Please enter a deck title')
    return
  }

  if (createMethod.value === 'notebook' && !newDeck.value.notebookId) {
    alert('Please select a notebook')
    return
  }

  // Close modal immediately to prevent multiple clicks
  const isManual = createMethod.value === 'manual'
  closeCreateModal()

  try {
    const userId = auth0.user.value?.sub || 'anonymous'
    console.log('Sending request to create deck...', { userId })
    
    const response = await axios.post('/api/flashcard-decks', {
      user_id: userId,
      title: newDeck.value.title,
      description: newDeck.value.description,
      notebook_id: isManual ? null : newDeck.value.notebookId,
      generate_from_notebook: !isManual
    })
    
    console.log('Deck created successfully:', response.data)
    
    // Reload decks to ensure we have the latest data
    await loadDecks()
    
    if (isManual) {
      router.push(`/flashcard-deck/${response.data.id}`)
    } else {
      // Show success message for AI generation
      alert('Deck created! Generating flashcards from notebook...')
    }
  } catch (error) {
    console.error('Failed to create deck:', error)
    alert('Failed to create deck: ' + (error.response?.data?.detail || error.message))
  }
}

const closeCreateModal = () => {
  createModal.value?.close()
}

const handleModalClick = (e) => {
  // Close modal when clicking on backdrop
  if (e.target === createModal.value) {
    closeCreateModal()
  }
}

const openDeck = (id) => {
  router.push(`/flashcard-deck/${id}`)
}

const studyDeck = (id) => {
  router.push(`/flashcard-deck/${id}/study`)
}

const editDeck = (id) => {
  router.push(`/flashcard-deck/${id}`)
}

const deleteDeck = async (id) => {
  if (!confirm('Are you sure you want to delete this deck?')) return

  try {
    const userId = auth0.user.value?.sub || 'anonymous'
    console.log('Deleting deck:', id)
    
    await axios.delete(`/api/flashcard-decks/${id}`, {
      params: { user_id: userId }
    })
    
    // Remove from local state
    decks.value = decks.value.filter(d => d.id !== id)
    console.log('Deck deleted successfully')
  } catch (error) {
    console.error('Failed to delete deck:', error)
    alert('Failed to delete deck: ' + (error.response?.data?.detail || error.message))
  }
}
</script>

<style scoped>
.flashcards-container {
  animation: fadeIn 0.6s ease-in-out;
  padding-left: 10rem;
}

@media (max-width: 1024px) {
  .flashcards-container {
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
  animation: flip 3s infinite ease-in-out;
}

@keyframes flip {
  0%, 100% { transform: rotateY(0deg); }
  50% { transform: rotateY(180deg); }
}

.title-text {
  background: linear-gradient(135deg, #8bb6ff, #c4e0ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.create-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.2), rgba(168, 216, 255, 0.2));
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(139, 182, 255, 0.3);
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.95);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease-in-out;
}

.create-button:hover {
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.3), rgba(168, 216, 255, 0.3));
  border-color: rgba(139, 182, 255, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(139, 182, 255, 0.3);
}

.button-icon {
  font-size: 1.125rem;
  transition: transform 0.3s ease-in-out;
}

.create-button:hover .button-icon {
  transform: scale(1.2);
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

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  color: rgba(200, 220, 255, 0.8);
  font-size: 1.125rem;
}

/* Empty State */
.empty-state {
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
  text-align: center;
  animation: fadeIn 0.6s ease-in-out;
}

.empty-icon {
  font-size: 5rem;
  margin-bottom: 1rem;
  animation: bounce 2s infinite ease-in-out;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.empty-title {
  font-size: 1.75rem;
  font-weight: 700;
  background: linear-gradient(135deg, #8bb6ff, #c4e0ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.5rem;
}

.empty-description {
  color: rgba(200, 220, 255, 0.7);
  font-size: 1.125rem;
  margin-bottom: 2rem;
}

.cta-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 2rem;
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.2), rgba(168, 216, 255, 0.2));
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(139, 182, 255, 0.3);
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.95);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.4s ease-in-out;
}

.cta-button:hover {
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.3), rgba(168, 216, 255, 0.3));
  border-color: rgba(139, 182, 255, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 15px 40px rgba(139, 182, 255, 0.3);
}

/* Decks Grid */
.decks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.deck-card {
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

.deck-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, transparent, rgba(139, 182, 255, 0.6), transparent);
  transform: translateX(-100%);
  transition: transform 0.6s ease-in-out;
}

.deck-card:hover::before {
  transform: translateX(100%);
}

.deck-card:hover {
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

.deck-card:hover .card-glow {
  opacity: 1;
}

.deck-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.deck-icon {
  font-size: 2.5rem;
  animation: float 3s infinite ease-in-out;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}

.deck-stats {
  display: flex;
  gap: 0.5rem;
}

.stat-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.stat-badge.new {
  background: rgba(107, 255, 178, 0.2);
  border: 1px solid rgba(107, 255, 178, 0.3);
  color: rgba(150, 255, 200, 0.95);
}

.stat-badge.review {
  background: rgba(255, 178, 107, 0.2);
  border: 1px solid rgba(255, 178, 107, 0.3);
  color: rgba(255, 200, 150, 0.95);
}

.deck-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: rgba(200, 220, 255, 0.95);
  margin-bottom: 0.5rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.deck-description {
  color: rgba(200, 220, 255, 0.6);
  font-size: 0.875rem;
  margin-bottom: 1rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.deck-info {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.875rem;
  color: rgba(200, 220, 255, 0.7);
}

.info-item.linked-notebook {
  color: rgba(196, 224, 255, 0.9);
  font-weight: 600;
}

.info-icon {
  font-size: 1rem;
}

.deck-actions {
  display: flex;
  gap: 0.5rem;
}

.action-button {
  flex: 1;
  padding: 0.625rem 1rem;
  background: rgba(139, 182, 255, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(139, 182, 255, 0.2);
  border-radius: 8px;
  color: rgba(200, 220, 255, 0.9);
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.3s ease-in-out;
}

.action-button:hover {
  background: rgba(139, 182, 255, 0.2);
  border-color: rgba(139, 182, 255, 0.4);
  transform: translateY(-2px);
}

.action-button.study {
  background: linear-gradient(135deg, rgba(107, 255, 178, 0.2), rgba(107, 255, 178, 0.15));
  border-color: rgba(107, 255, 178, 0.3);
  color: rgba(150, 255, 200, 0.95);
}

.action-button.study:hover {
  background: linear-gradient(135deg, rgba(107, 255, 178, 0.3), rgba(107, 255, 178, 0.2));
  border-color: rgba(107, 255, 178, 0.5);
  box-shadow: 0 5px 20px rgba(107, 255, 178, 0.2);
}

.action-button.edit,
.action-button.delete {
  flex: 0 0 auto;
  width: 2.5rem;
  padding: 0.625rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-button.edit:hover {
  background: rgba(139, 182, 255, 0.2);
  border-color: rgba(139, 182, 255, 0.4);
}

.action-button.delete:hover {
  background: rgba(255, 107, 107, 0.2);
  border-color: rgba(255, 107, 107, 0.4);
}

.card-shine {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.03), transparent);
  transform: rotate(45deg);
  transition: all 0.6s ease-in-out;
  pointer-events: none;
}

.deck-card:hover .card-shine {
  left: 100%;
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
  max-width: 600px;
  width: 90%;
  z-index: 200;
}

.glass-modal::backdrop {
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  z-index: 199;
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
  font-family: inherit;
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

textarea.glass-input {
  resize: vertical;
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
  transition: all 0.3s ease-in-out;
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

.create-options {
  display: flex;
  gap: 0.75rem;
}

.option-button {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  background: rgba(139, 182, 255, 0.05);
  border: 1px solid rgba(139, 182, 255, 0.2);
  border-radius: 10px;
  color: rgba(200, 220, 255, 0.7);
  cursor: pointer;
  transition: all 0.3s ease-in-out;
}

.option-button:hover {
  background: rgba(139, 182, 255, 0.1);
  border-color: rgba(139, 182, 255, 0.3);
}

.option-button.active {
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.2), rgba(168, 216, 255, 0.2));
  border-color: rgba(139, 182, 255, 0.4);
  color: rgba(200, 220, 255, 0.95);
}

.option-icon {
  font-size: 2rem;
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

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.8; }
}
</style>
