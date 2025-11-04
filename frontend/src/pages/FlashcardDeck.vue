<template>
  <div class="deck-detail-container">
    <!-- Header -->
    <div class="header-section">
      <button @click="router.back()" class="back-button">
        <span>←</span>
        <span>Back</span>
      </button>
      <div class="header-content">
        <h1 class="deck-title">{{ deck?.title || 'Loading...' }}</h1>
        <p class="deck-description">{{ deck?.description || '' }}</p>
        <div class="deck-stats-row">
          <div class="stat-item">
            <span class="stat-icon">📄</span>
            <span>{{ cards.length }} cards</span>
          </div>
          <div class="stat-item">
            <span class="stat-icon">🆕</span>
            <span>{{ newCards }} new</span>
          </div>
          <div class="stat-item">
            <span class="stat-icon">🔄</span>
            <span>{{ reviewCards }} review</span>
          </div>
        </div>
      </div>
      <div class="header-actions">
        <button @click="startStudy" class="study-button" :disabled="cards.length === 0">
          <span class="button-icon">🎯</span>
          <span>Study Now</span>
        </button>
        <button @click="generateCards" class="generate-button" :disabled="!deck?.notebookId || generating">
          <span class="button-icon">{{ generating ? '⏳' : '✨' }}</span>
          <span>{{ generating ? 'Generating...' : 'Generate Cards' }}</span>
        </button>
        <button @click="addCard" class="add-button">
          <span class="button-icon">➕</span>
          <span>Add Card</span>
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p class="loading-text">Loading flashcards...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="cards.length === 0" class="empty-state">
      <div class="empty-icon">🎴</div>
      <h2 class="empty-title">No Cards Yet</h2>
      <p class="empty-description">Add your first flashcard to this deck</p>
      <button @click="addCard" class="cta-button">
        <span>Add Your First Card</span>
        <span class="button-icon">→</span>
      </button>
    </div>

    <!-- Cards List -->
    <div v-else class="cards-list">
      <div
        v-for="(card, index) in cards"
        :key="card.id"
        class="card-item"
        :style="{ animationDelay: `${index * 0.05}s` }"
      >
        <div class="card-number">{{ index + 1 }}</div>
        <div class="card-content">
          <div class="card-side">
            <span class="side-label">Front</span>
            <p class="card-text">{{ card.front }}</p>
          </div>
          <div class="card-divider">↔️</div>
          <div class="card-side">
            <span class="side-label">Back</span>
            <p class="card-text">{{ card.back }}</p>
          </div>
        </div>
        <div class="card-meta">
          <span v-if="card.isNew" class="meta-badge new">New</span>
          <span v-else-if="card.isDue" class="meta-badge due">Due</span>
          <span v-else-if="card.isMastered" class="meta-badge mastered">Mastered</span>
          <span v-else class="meta-badge learning">Learning</span>
          <span class="meta-info">{{ card.repetitions }} reviews</span>
        </div>
        <div class="card-actions">
          <button @click="editCard(card)" class="action-btn edit">
            <span>✏️</span>
          </button>
          <button @click="deleteCard(card.id)" class="action-btn delete">
            <span>🗑️</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Add/Edit Card Modal -->
    <dialog ref="cardModal" class="glass-modal">
      <div class="modal-content">
        <h3 class="modal-title">{{ editingCard ? 'Edit Card' : 'Add Card' }}</h3>
        <div class="form-group">
          <label class="form-label">Front (Question)</label>
          <textarea
            v-model="cardForm.front"
            placeholder="Enter the question or prompt..."
            class="glass-input"
            rows="4"
          ></textarea>
        </div>
        <div class="form-group">
          <label class="form-label">Back (Answer)</label>
          <textarea
            v-model="cardForm.back"
            placeholder="Enter the answer..."
            class="glass-input"
            rows="4"
          ></textarea>
        </div>
        <div class="modal-actions">
          <button @click="closeCardModal" class="modal-button cancel">Cancel</button>
          <button @click="saveCard" class="modal-button confirm">
            {{ editingCard ? 'Update' : 'Add' }} Card
          </button>
        </div>
      </div>
    </dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuth0 } from '@auth0/auth0-vue'
import axios from 'axios'

const router = useRouter()
const route = useRoute()
const auth0 = useAuth0()

const loading = ref(true)
const generating = ref(false)
const deck = ref(null)
const cards = ref([])
const cardModal = ref(null)
const editingCard = ref(null)
const cardForm = ref({
  front: '',
  back: ''
})

const newCards = computed(() => cards.value.filter(c => c.isNew).length)
const reviewCards = computed(() => cards.value.filter(c => c.isDue && !c.isNew).length)

onMounted(async () => {
  if (!auth0.isAuthenticated.value) {
    router.push('/')
    return
  }
  await loadDeck()
  await loadCards()
})

const loadDeck = async () => {
  try {
    const userId = auth0.user.value?.sub || 'anonymous'
    const response = await axios.get(`/api/flashcard-decks/${route.params.id}`, {
      params: { user_id: userId }
    })
    deck.value = response.data
  } catch (error) {
    console.error('Failed to load deck:', error)
    alert('Failed to load deck')
    router.back()
  }
}

const loadCards = async () => {
  loading.value = true
  try {
    const userId = auth0.user.value?.sub || 'anonymous'
    const response = await axios.get(`/api/flashcard-decks/${route.params.id}/cards`, {
      params: { user_id: userId }
    })
    cards.value = response.data
  } catch (error) {
    console.error('Failed to load cards:', error)
    cards.value = []
  } finally {
    loading.value = false
  }
}

const startStudy = () => {
  router.push(`/flashcard-deck/${route.params.id}/study`)
}

const generateCards = async () => {
  if (!deck.value?.notebookId) {
    alert('This deck is not linked to a notebook. Please create cards manually or create a new deck from a notebook.')
    return
  }

  if (cards.value.length > 0 && !confirm('This will generate additional cards from the notebook. Continue?')) {
    return
  }

  generating.value = true
  try {
    const userId = auth0.user.value?.sub || 'anonymous'
    console.log('Generating cards from notebook:', deck.value.notebookId)
    
    // Call the generate endpoint
    const response = await axios.post(
      `/api/flashcard-decks/${route.params.id}/generate?user_id=${userId}`
    )
    
    console.log('Generated cards:', response.data)
    
    // Reload cards
    await loadCards()
    
    alert(`Successfully generated ${response.data.count || 10} new flashcards!`)
  } catch (error) {
    console.error('Failed to generate cards:', error)
    alert('Failed to generate cards: ' + (error.response?.data?.detail || error.message))
  } finally {
    generating.value = false
  }
}

const addCard = () => {
  editingCard.value = null
  cardForm.value = { front: '', back: '' }
  cardModal.value?.showModal()
}

const editCard = (card) => {
  editingCard.value = card
  cardForm.value = { front: card.front, back: card.back }
  cardModal.value?.showModal()
}

const saveCard = async () => {
  if (!cardForm.value.front.trim() || !cardForm.value.back.trim()) {
    alert('Please fill in both front and back')
    return
  }

  try {
    const userId = auth0.user.value?.sub || 'anonymous'
    
    if (editingCard.value) {
      // Update existing card
      const response = await axios.put(`/api/flashcard-cards/${editingCard.value.id}`, cardForm.value, {
        params: { user_id: userId }
      })
      const index = cards.value.findIndex(c => c.id === editingCard.value.id)
      if (index !== -1) {
        cards.value[index] = response.data
      }
    } else {
      // Create new card
      const response = await axios.post(`/api/flashcard-decks/${route.params.id}/cards`, cardForm.value, {
        params: { user_id: userId }
      })
      cards.value.push(response.data)
    }
    
    closeCardModal()
  } catch (error) {
    console.error('Failed to save card:', error)
    alert('Failed to save card: ' + (error.response?.data?.detail || error.message))
  }
}

const deleteCard = async (id) => {
  if (!confirm('Are you sure you want to delete this card?')) return

  try {
    const userId = auth0.user.value?.sub || 'anonymous'
    await axios.delete(`/api/flashcard-cards/${id}`, {
      params: { user_id: userId }
    })
    cards.value = cards.value.filter(c => c.id !== id)
  } catch (error) {
    console.error('Failed to delete card:', error)
    alert('Failed to delete card')
  }
}

const closeCardModal = () => {
  cardModal.value?.close()
}
</script>

<style scoped>
.deck-detail-container {
  min-height: 100vh;
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.header-section {
  margin-bottom: 3rem;
  animation: slideDown 0.6s ease-out;
}

.back-button {
  background: rgba(15, 12, 41, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(139, 182, 255, 0.2);
  color: #8bb6ff;
  padding: 0.75rem 1.5rem;
  border-radius: 12px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.back-button:hover {
  background: rgba(15, 12, 41, 0.2);
  border-color: rgba(139, 182, 255, 0.4);
  transform: translateX(-5px);
}

.header-content {
  margin-bottom: 1.5rem;
}

.deck-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  background: linear-gradient(135deg, #8bb6ff 0%, #c4e0ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.deck-description {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 1rem;
}

.deck-stats-row {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.8);
}

.stat-icon {
  font-size: 1.2rem;
}

.header-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.study-button, .generate-button, .add-button {
  background: rgba(15, 12, 41, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(139, 182, 255, 0.3);
  color: #8bb6ff;
  padding: 1rem 2rem;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.generate-button {
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.15), rgba(196, 224, 255, 0.1));
  border-color: rgba(139, 182, 255, 0.4);
}

.study-button:hover:not(:disabled), .generate-button:hover:not(:disabled), .add-button:hover {
  background: rgba(139, 182, 255, 0.1);
  border-color: rgba(139, 182, 255, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(139, 182, 255, 0.2);
}

.generate-button:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.25), rgba(196, 224, 255, 0.15));
  box-shadow: 0 8px 32px rgba(139, 182, 255, 0.3);
}

.study-button:disabled, .generate-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.button-icon {
  font-size: 1.3rem;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  animation: fadeIn 0.3s ease-out;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 3px solid rgba(139, 182, 255, 0.2);
  border-top: 3px solid #8bb6ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-text {
  margin-top: 1.5rem;
  color: rgba(255, 255, 255, 0.6);
  font-size: 1.1rem;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  animation: fadeIn 0.5s ease-out;
}

.empty-icon {
  font-size: 5rem;
  margin-bottom: 1rem;
  animation: bounce 2s ease-in-out infinite;
}

.empty-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  color: #8bb6ff;
}

.empty-description {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 2rem;
}

.cta-button {
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.2), rgba(196, 224, 255, 0.1));
  backdrop-filter: blur(20px);
  border: 1px solid rgba(139, 182, 255, 0.3);
  color: #8bb6ff;
  padding: 1rem 2rem;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
}

.cta-button:hover {
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.3), rgba(196, 224, 255, 0.2));
  border-color: rgba(139, 182, 255, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(139, 182, 255, 0.3);
}

.cards-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.card-item {
  background: rgba(15, 12, 41, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(139, 182, 255, 0.2);
  border-radius: 16px;
  padding: 1.5rem;
  display: grid;
  grid-template-columns: auto 1fr auto auto;
  gap: 1.5rem;
  align-items: center;
  transition: all 0.3s ease;
  animation: cardSlideUp 0.5s ease-out backwards;
}

.card-item:hover {
  background: rgba(15, 12, 41, 0.15);
  border-color: rgba(139, 182, 255, 0.4);
  transform: translateX(5px);
}

.card-number {
  font-size: 1.5rem;
  font-weight: 700;
  color: rgba(139, 182, 255, 0.5);
  min-width: 40px;
  text-align: center;
}

.card-content {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 1.5rem;
  align-items: center;
  flex: 1;
}

.card-side {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.side-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: rgba(139, 182, 255, 0.7);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.card-text {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.5;
}

.card-divider {
  font-size: 1.5rem;
  color: rgba(139, 182, 255, 0.3);
}

.card-meta {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  align-items: flex-end;
}

.meta-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.meta-badge.new {
  background: rgba(139, 182, 255, 0.2);
  color: #8bb6ff;
}

.meta-badge.due {
  background: rgba(255, 200, 87, 0.2);
  color: #ffc857;
}

.meta-badge.learning {
  background: rgba(139, 182, 255, 0.2);
  color: #8bb6ff;
}

.meta-badge.mastered {
  background: rgba(119, 221, 119, 0.2);
  color: #77dd77;
}

.meta-info {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.5);
}

.card-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  background: rgba(15, 12, 41, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(139, 182, 255, 0.2);
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-btn.edit:hover {
  background: rgba(139, 182, 255, 0.2);
  border-color: rgba(139, 182, 255, 0.4);
}

.action-btn.delete:hover {
  background: rgba(255, 99, 99, 0.2);
  border-color: rgba(255, 99, 99, 0.4);
}

.glass-modal {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(15, 12, 41, 0.95);
  backdrop-filter: blur(30px);
  border: 1px solid rgba(139, 182, 255, 0.3);
  border-radius: 24px;
  padding: 0;
  max-width: 600px;
  width: 90%;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.glass-modal::backdrop {
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(10px);
}

.modal-content {
  padding: 2rem;
}

.modal-title {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  color: #8bb6ff;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.95rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
}

.glass-input {
  width: 100%;
  background: rgba(15, 12, 41, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(139, 182, 255, 0.2);
  border-radius: 12px;
  padding: 0.75rem 1rem;
  color: white;
  font-size: 1rem;
  font-family: inherit;
  transition: all 0.3s ease;
  resize: vertical;
}

.glass-input:focus {
  outline: none;
  border-color: rgba(139, 182, 255, 0.5);
  background: rgba(15, 12, 41, 0.15);
  box-shadow: 0 0 20px rgba(139, 182, 255, 0.1);
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
}

.modal-button {
  padding: 0.75rem 2rem;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.modal-button.cancel {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.7);
}

.modal-button.cancel:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.3);
}

.modal-button.confirm {
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.3), rgba(196, 224, 255, 0.2));
  border: 1px solid rgba(139, 182, 255, 0.4);
  color: #8bb6ff;
}

.modal-button.confirm:hover {
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.4), rgba(196, 224, 255, 0.3));
  box-shadow: 0 8px 32px rgba(139, 182, 255, 0.2);
  transform: translateY(-2px);
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
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

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

@media (max-width: 1024px) {
  .card-item {
    grid-template-columns: auto 1fr;
    gap: 1rem;
  }
  
  .card-content {
    grid-column: 1 / -1;
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .card-divider {
    display: none;
  }
  
  .card-meta {
    grid-column: 1 / -1;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }
  
  .card-actions {
    grid-column: 1 / -1;
    justify-content: flex-end;
  }
}

@media (max-width: 768px) {
  .deck-detail-container {
    padding: 1rem;
  }
  
  .deck-title {
    font-size: 2rem;
  }
  
  .header-actions {
    width: 100%;
  }
  
  .study-button, .add-button {
    flex: 1;
    justify-content: center;
  }
}
</style>
