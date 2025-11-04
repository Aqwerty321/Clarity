<template>
  <div class="study-container">
    <!-- Header -->
    <div class="study-header">
      <button @click="exitStudy" class="exit-button">
        <span>✕</span>
      </button>
      <div class="progress-info">
        <div class="session-stats">
          <span class="stat-item">
            <span class="stat-icon">📊</span>
            <span>{{ currentCardIndex + 1 }} / {{ studyCards.length }}</span>
          </span>
          <span class="stat-item">
            <span class="stat-icon">✅</span>
            <span>{{ stats.correct }}</span>
          </span>
          <span class="stat-item">
            <span class="stat-icon">❌</span>
            <span>{{ stats.incorrect }}</span>
          </span>
        </div>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: `${progress}%` }"></div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p class="loading-text">Preparing your study session...</p>
    </div>

    <!-- No Cards State -->
    <div v-else-if="studyCards.length === 0" class="empty-state">
      <div class="empty-icon">🎉</div>
      <h2 class="empty-title">All Caught Up!</h2>
      <p class="empty-description">You've reviewed all due cards. Great job!</p>
      <p class="empty-hint">Cards will be ready for review based on the spaced repetition schedule.</p>
      <div class="empty-actions">
        <button @click="startPracticeMode" class="cta-button practice">
          <span>🎯 Practice All Cards</span>
        </button>
        <button @click="exitStudy" class="cta-button secondary">
          <span>Back to Deck</span>
        </button>
      </div>
    </div>

    <!-- Study Card -->
    <div v-else-if="currentCard" class="study-content">
      <FlashcardCard
        ref="flashcardRef"
        :card="currentCard"
        :show-controls="true"
        @rate="handleRating"
      />
    </div>

    <!-- Session Complete Modal -->
    <dialog ref="completeModal" class="glass-modal">
      <div class="modal-content">
        <h2 class="modal-title">🎉 Session Complete!</h2>
        <div class="session-summary">
          <div class="summary-stat">
            <span class="summary-label">Cards Reviewed</span>
            <span class="summary-value">{{ stats.total }}</span>
          </div>
          <div class="summary-stat">
            <span class="summary-label">Correct</span>
            <span class="summary-value correct">{{ stats.correct }}</span>
          </div>
          <div class="summary-stat">
            <span class="summary-label">Needs Practice</span>
            <span class="summary-value incorrect">{{ stats.incorrect }}</span>
          </div>
          <div class="summary-stat">
            <span class="summary-label">Accuracy</span>
            <span class="summary-value">{{ accuracy }}%</span>
          </div>
        </div>
        <div class="modal-actions">
          <button @click="exitStudy" class="modal-button">
            Back to Deck
          </button>
        </div>
      </div>
    </dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuth0 } from '@auth0/auth0-vue'
import axios from 'axios'
import FlashcardCard from '../components/FlashcardCard.vue'

const router = useRouter()
const route = useRoute()
const auth0 = useAuth0()

const loading = ref(true)
const deck = ref(null)
const studyCards = ref([])
const currentCardIndex = ref(0)
const flashcardRef = ref(null)
const completeModal = ref(null)
const practiceMode = ref(false)
const stats = ref({
  total: 0,
  correct: 0,
  incorrect: 0
})

const currentCard = computed(() => studyCards.value[currentCardIndex.value])
const progress = computed(() => {
  if (studyCards.value.length === 0) return 0
  return ((currentCardIndex.value + 1) / studyCards.value.length) * 100
})
const accuracy = computed(() => {
  if (stats.value.total === 0) return 0
  return Math.round((stats.value.correct / stats.value.total) * 100)
})

onMounted(async () => {
  if (!auth0.isAuthenticated.value) {
    router.push('/')
    return
  }
  await loadStudyCards()
  
  // Keyboard shortcuts
  window.addEventListener('keydown', handleKeyPress)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyPress)
})

const loadStudyCards = async () => {
  loading.value = true
  try {
    const userId = auth0.user.value?.sub || 'anonymous'
    
    // Load deck details for analytics
    const deckResponse = await axios.get(`/api/flashcard-decks/${route.params.id}`, {
      params: { user_id: userId }
    })
    deck.value = deckResponse.data
    
    // Load study cards
    const response = await axios.get(`/api/flashcard-decks/${route.params.id}/study`, {
      params: { 
        user_id: userId, 
        limit: 20,
        practice_mode: practiceMode.value 
      }
    })
    studyCards.value = response.data
  } catch (error) {
    console.error('Failed to load study cards:', error)
    studyCards.value = []
  } finally {
    loading.value = false
  }
}

const startPracticeMode = async () => {
  practiceMode.value = true
  currentCardIndex.value = 0
  stats.value = { total: 0, correct: 0, incorrect: 0 }
  await loadStudyCards()
}

const handleRating = async (rating) => {
  if (!currentCard.value) return

  try {
    const userId = auth0.user.value?.sub || 'anonymous'
    
    // Rate the card (updates spaced repetition)
    await axios.post(`/api/flashcard-cards/${currentCard.value.id}/rate`, 
      { rating },
      { params: { user_id: userId } }
    )

    // Record attempt for analytics
    const wasCorrect = rating !== 'again'
    const qualityMap = { again: 0, hard: 2, good: 3, easy: 5 }
    
    try {
      const formData = new FormData()
      formData.append('user_id', userId)
      formData.append('deck_id', route.params.id)
      formData.append('card_id', currentCard.value.id)
      formData.append('notebook_id', deck.value?.notebook_id || '')
      formData.append('topic', deck.value?.title || 'General')
      formData.append('quality', qualityMap[rating].toString())
      formData.append('was_correct', wasCorrect.toString())
      
      console.log('📊 Recording flashcard attempt:', {
        deck: deck.value?.title,
        rating,
        quality: qualityMap[rating],
        wasCorrect
      })
      
      const response = await axios.post('/api/flashcard-attempts', formData)
      console.log('✅ Flashcard attempt recorded for analytics:', response.data)
    } catch (error) {
      console.error('❌ Failed to record flashcard attempt:', error.response?.data || error.message)
      // Don't block user experience if analytics fail
    }

    // Update stats
    stats.value.total++
    if (rating === 'again') {
      stats.value.incorrect++
    } else {
      stats.value.correct++
    }

    // Add flick out animation before moving to next card
    if (currentCardIndex.value < studyCards.value.length - 1) {
      // Trigger flick animation
      const cardElement = document.querySelector('.flashcard-card')
      if (cardElement) {
        cardElement.classList.add('flick-out')
        
        setTimeout(() => {
          currentCardIndex.value++
          // Reset the card to front side and remove animation
          setTimeout(() => {
            if (cardElement) {
              cardElement.classList.remove('flick-out')
            }
            flashcardRef.value?.reset()
          }, 50)
        }, 300) // Wait for flick animation to complete
      } else {
        currentCardIndex.value++
        setTimeout(() => {
          flashcardRef.value?.reset()
        }, 100)
      }
    } else {
      completeSession()
    }
  } catch (error) {
    console.error('Failed to rate card:', error)
    alert('Failed to save rating')
  }
}

const handleKeyPress = (e) => {
  if (loading.value || !currentCard.value) return
  
  // Space to flip
  if (e.code === 'Space') {
    e.preventDefault()
    flashcardRef.value?.flip()
  }
  
  // Number keys for rating (only if card is flipped)
  if (flashcardRef.value?.isFlipped.value) {
    if (e.code === 'Digit1') {
      e.preventDefault()
      handleRating('again')
    } else if (e.code === 'Digit2') {
      e.preventDefault()
      handleRating('hard')
    } else if (e.code === 'Digit3') {
      e.preventDefault()
      handleRating('good')
    } else if (e.code === 'Digit4') {
      e.preventDefault()
      handleRating('easy')
    }
  }
}

const completeSession = () => {
  completeModal.value?.showModal()
}

const exitStudy = () => {
  router.push('/flashcards')
}
</script>

<style scoped>
.study-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
}

.study-header {
  padding: 1.5rem 2rem;
  display: flex;
  align-items: center;
  gap: 2rem;
  background: rgba(15, 12, 41, 0.5);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(139, 182, 255, 0.2);
  animation: slideDown 0.5s ease-out;
}

.exit-button {
  background: rgba(255, 99, 99, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 99, 99, 0.3);
  color: #ff6363;
  width: 45px;
  height: 45px;
  border-radius: 12px;
  font-size: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.exit-button:hover {
  background: rgba(255, 99, 99, 0.2);
  border-color: rgba(255, 99, 99, 0.5);
  transform: scale(1.05);
}

.progress-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.session-stats {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.stat-icon {
  font-size: 1.2rem;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: rgba(15, 12, 41, 0.3);
  border-radius: 10px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #8bb6ff, #c4e0ff);
  border-radius: 10px;
  transition: width 0.5s ease;
  box-shadow: 0 0 20px rgba(139, 182, 255, 0.5);
}

.loading-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  animation: fadeIn 0.3s ease-out;
}

.loading-spinner {
  width: 60px;
  height: 60px;
  border: 4px solid rgba(139, 182, 255, 0.2);
  border-top: 4px solid #8bb6ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-text {
  margin-top: 2rem;
  color: rgba(255, 255, 255, 0.7);
  font-size: 1.2rem;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  animation: fadeIn 0.5s ease-out;
}

.empty-icon {
  font-size: 6rem;
  margin-bottom: 1.5rem;
  animation: bounce 2s ease-in-out infinite;
}

.empty-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
  background: linear-gradient(135deg, #8bb6ff, #c4e0ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.empty-description {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 0.5rem;
}

.empty-hint {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 2rem;
  font-style: italic;
}

.empty-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: center;
}

.cta-button {
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.3), rgba(196, 224, 255, 0.2));
  backdrop-filter: blur(20px);
  border: 1px solid rgba(139, 182, 255, 0.4);
  color: #8bb6ff;
  padding: 1rem 2.5rem;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cta-button:hover {
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.4), rgba(196, 224, 255, 0.3));
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(139, 182, 255, 0.3);
}

.cta-button.practice {
  background: linear-gradient(135deg, rgba(119, 221, 119, 0.3), rgba(152, 251, 152, 0.2));
  border: 1px solid rgba(119, 221, 119, 0.4);
  color: #77dd77;
}

.cta-button.practice:hover {
  background: linear-gradient(135deg, rgba(119, 221, 119, 0.4), rgba(152, 251, 152, 0.3));
  box-shadow: 0 8px 32px rgba(119, 221, 119, 0.3);
}

.cta-button.secondary {
  background: rgba(15, 12, 41, 0.3);
  border: 1px solid rgba(139, 182, 255, 0.2);
}

.cta-button.secondary:hover {
  background: rgba(15, 12, 41, 0.5);
  box-shadow: 0 8px 32px rgba(139, 182, 255, 0.2);
}

.study-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  animation: fadeIn 0.5s ease-out;
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
  max-width: 500px;
  width: 90%;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.glass-modal::backdrop {
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(10px);
}

.modal-content {
  padding: 2.5rem;
  text-align: center;
}

.modal-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 2rem;
  color: #8bb6ff;
}

.session-summary {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.summary-stat {
  background: rgba(15, 12, 41, 0.3);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(139, 182, 255, 0.2);
  border-radius: 16px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.summary-label {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.6);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.summary-value {
  font-size: 2rem;
  font-weight: 700;
  color: #8bb6ff;
}

.summary-value.correct {
  color: #77dd77;
}

.summary-value.incorrect {
  color: #ffc857;
}

.modal-actions {
  display: flex;
  justify-content: center;
  margin-top: 2rem;
}

.modal-button {
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.3), rgba(196, 224, 255, 0.2));
  border: 1px solid rgba(139, 182, 255, 0.4);
  color: #8bb6ff;
  padding: 1rem 3rem;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.modal-button:hover {
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.4), rgba(196, 224, 255, 0.3));
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(139, 182, 255, 0.3);
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

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

/* Flick Out Animation */
:deep(.flashcard-card.flick-out) {
  animation: flickOut 0.3s cubic-bezier(0.4, 0.0, 1, 1) forwards;
  pointer-events: none;
}

@keyframes flickOut {
  0% {
    transform: translateX(0) rotate(0deg);
    opacity: 1;
  }
  30% {
    transform: translateX(-20px) rotate(-5deg);
  }
  100% {
    transform: translateX(100vw) rotate(30deg);
    opacity: 0;
  }
}

@media (max-width: 768px) {
  .study-header {
    padding: 1rem;
    gap: 1rem;
  }
  
  .session-stats {
    gap: 1rem;
  }
  
  .stat-item {
    font-size: 0.9rem;
  }
  
  .session-summary {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    padding: 2rem 1.5rem;
  }
}
</style>
