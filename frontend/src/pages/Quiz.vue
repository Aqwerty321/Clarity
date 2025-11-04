<template>
  <div class="quiz-container">
    <QuickNav />
    <div class="header-section">
      <h1 class="page-title">
        <span class="title-icon">🎯</span>
        <span class="title-text">Quiz Center</span>
      </h1>
      <button @click="showCreateModal" class="create-button">
        <span class="button-icon">✨</span>
        <span>Generate Quiz</span>
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p class="loading-text">Loading your quizzes...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="quizzes.length === 0" class="empty-state">
      <div class="empty-icon">🎯</div>
      <h2 class="empty-title">No Quizzes Yet</h2>
      <p class="empty-description">Generate your first AI-powered quiz from your notebooks</p>
      <button @click="showCreateModal" class="cta-button">
        <span>Generate Your First Quiz</span>
        <span class="button-icon">→</span>
      </button>
    </div>

    <!-- Quizzes by Notebook -->
    <div v-else class="notebooks-container">
      <div
        v-for="(notebookGroup, index) in groupedQuizzes"
        :key="notebookGroup.notebookId || 'uncategorized'"
        class="notebook-folder"
        :style="{ animationDelay: `${index * 0.1}s` }"
      >
        <div 
          class="folder-header"
          @click="toggleFolder(notebookGroup.notebookId)"
        >
          <div class="folder-left">
            <span class="folder-icon">
              {{ expandedFolders[notebookGroup.notebookId] ? '📂' : '📁' }}
            </span>
            <h2 class="folder-title">{{ notebookGroup.notebookTitle || 'Uncategorized' }}</h2>
            <span class="quiz-count">{{ notebookGroup.quizzes.length }} {{ notebookGroup.quizzes.length === 1 ? 'quiz' : 'quizzes' }}</span>
          </div>
          <div class="folder-chevron" :class="{ expanded: expandedFolders[notebookGroup.notebookId] }">
            ▼
          </div>
        </div>

        <transition name="folder-expand">
          <div v-show="expandedFolders[notebookGroup.notebookId]" class="folder-content">
            <div class="quizzes-grid">
              <div
                v-for="(quiz, quizIndex) in notebookGroup.quizzes"
                :key="quiz.id"
                class="quiz-card"
                :style="{ animationDelay: `${quizIndex * 0.05}s` }"
                @click="reviewQuiz(quiz)"
              >
                <div class="card-glow"></div>
                <div class="quiz-header">
                  <div class="quiz-icon">📝</div>
                  <div class="difficulty-badge" :class="quiz.difficulty || 'medium'">
                    {{ quiz.difficulty || 'Medium' }}
                  </div>
                </div>
                <h3 class="quiz-title">{{ quiz.title }}</h3>
                <p class="quiz-topic">{{ quiz.topic || 'General Knowledge' }}</p>
                <div class="quiz-info">
                  <div class="info-item">
                    <span class="info-icon">❓</span>
                    <span>{{ quiz.questions?.length || 0 }} questions</span>
                  </div>
                  <div v-if="quiz.created_at" class="info-item">
                    <span class="info-icon">�</span>
                    <span>{{ formatDate(quiz.created_at) }}</span>
                  </div>
                </div>
                <div class="quiz-actions">
                  <button @click.stop="reviewQuiz(quiz)" class="action-button review">
                    <span>Review Quiz</span>
                  </button>
                </div>
                <div class="card-shine"></div>
              </div>
            </div>
          </div>
        </transition>
      </div>
    </div>

    <!-- Generate Quiz Modal -->
    <dialog ref="createModal" class="glass-modal" @click="handleModalClick">
      <div class="modal-content" @click.stop>
        <h3 class="modal-title">Generate Quiz</h3>
        <div class="form-group">
          <label class="form-label">Source Notebook</label>
          <select v-model="newQuiz.notebookId" class="glass-input">
            <option value="">Choose a notebook...</option>
            <option v-for="notebook in notebooks" :key="notebook.id" :value="notebook.id">
              {{ notebook.title }}
            </option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">Topic</label>
          <input
            v-model="newQuiz.topic"
            type="text"
            placeholder="e.g., Chemical Reactions, Machine Learning"
            class="glass-input"
          />
        </div>
        <div class="form-group">
          <label class="form-label">Number of Questions</label>
          <input
            v-model.number="newQuiz.numQuestions"
            type="number"
            min="3"
            max="20"
            class="glass-input"
          />
        </div>
        <div class="form-group">
          <label class="form-label">Difficulty</label>
          <div class="difficulty-options">
            <button
              v-for="level in ['easy', 'medium', 'hard']"
              :key="level"
              @click="newQuiz.difficulty = level"
              :class="['option-button', { active: newQuiz.difficulty === level }]"
            >
              {{ level.charAt(0).toUpperCase() + level.slice(1) }}
            </button>
          </div>
        </div>
        <div class="modal-actions">
          <button @click.stop="confirmGenerate" class="modal-button primary" :disabled="generating">
            <span v-if="!generating">Generate Quiz</span>
            <span v-else>Generating...</span>
            <span v-if="!generating" class="button-icon">✨</span>
          </button>
          <button @click.stop="closeCreateModal" class="modal-button secondary">Cancel</button>
        </div>
      </div>
    </dialog>

    <!-- Quiz Modal -->
    <QuizModal
      v-model="showQuizModal"
      :quiz="currentQuiz"
      :reviewMode="isReviewMode"
      @submit="handleQuizSubmit"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth0 } from '@auth0/auth0-vue'
import QuickNav from '../components/QuickNav.vue'
import QuizModal from '../components/QuizModal.vue'
import axios from 'axios'

const router = useRouter()
const auth0 = useAuth0()

const loading = ref(true)
const generating = ref(false)
const quizzes = ref([])
const notebooks = ref([])
const createModal = ref(null)
const showQuizModal = ref(false)
const currentQuiz = ref(null)
const expandedFolders = ref({})
const isReviewMode = ref(false)

const newQuiz = ref({
  notebookId: '',
  topic: '',
  numQuestions: 5,
  difficulty: 'medium'
})

// Group quizzes by notebook
const groupedQuizzes = computed(() => {
  const groups = {}
  
  quizzes.value.forEach(quiz => {
    const notebookId = quiz.notebook_id || 'uncategorized'
    if (!groups[notebookId]) {
      groups[notebookId] = {
        notebookId,
        notebookTitle: quiz.notebookTitle || 'Uncategorized',
        quizzes: []
      }
    }
    groups[notebookId].quizzes.push(quiz)
  })
  
  // Sort quizzes within each group by creation date (newest first)
  Object.values(groups).forEach(group => {
    group.quizzes.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  })
  
  return Object.values(groups)
})

onMounted(async () => {
  if (!auth0.isAuthenticated.value) {
    router.push('/')
    return
  }

  await loadNotebooks()
  await loadQuizzes()
  
  // Expand all folders by default
  groupedQuizzes.value.forEach(group => {
    expandedFolders.value[group.notebookId] = true
  })
  
  loading.value = false
})

const loadNotebooks = async () => {
  try {
    const userId = auth0.user.value?.sub || 'anonymous'
    const response = await axios.get(`/api/notebooks?user_id=${userId}`)
    notebooks.value = response.data
  } catch (error) {
    console.error('Failed to load notebooks:', error)
  }
}

const loadQuizzes = async () => {
  try {
    const userId = auth0.user.value?.sub || 'anonymous'
    // Try to load quizzes - endpoint might not exist yet
    const response = await axios.get(`/api/quizzes?user_id=${userId}`)
    
    // Enrich with notebook titles
    quizzes.value = await Promise.all(response.data.map(async (quiz) => {
      if (quiz.notebook_id) {
        const notebook = notebooks.value.find(n => n.id === quiz.notebook_id)
        return { ...quiz, notebookTitle: notebook?.title }
      }
      return quiz
    }))
  } catch (error) {
    console.warn('Could not load quizzes:', error)
    quizzes.value = []
  }
}

const showCreateModal = () => {
  createModal.value?.showModal()
}

const closeCreateModal = () => {
  createModal.value?.close()
  newQuiz.value = {
    notebookId: '',
    topic: '',
    numQuestions: 5,
    difficulty: 'medium'
  }
}

const handleModalClick = (e) => {
  if (e.target === createModal.value) {
    closeCreateModal()
  }
}

const confirmGenerate = async () => {
  if (!newQuiz.value.notebookId || !newQuiz.value.topic) {
    alert('Please select a notebook and enter a topic')
    return
  }

  generating.value = true
  try {
    const userId = auth0.user.value?.sub || 'anonymous'
    
    // Generate quiz
    const genResponse = await axios.post('/api/generate-quiz', {
      user_id: userId,
      notebook_id: newQuiz.value.notebookId,
      topic: newQuiz.value.topic,
      num_questions: newQuiz.value.numQuestions,
      difficulty: newQuiz.value.difficulty,
    })

    const quizData = {
      title: genResponse.data.title || `Quiz: ${newQuiz.value.topic}`,
      topic: newQuiz.value.topic,
      difficulty: newQuiz.value.difficulty,
      questions: genResponse.data.questions.map(q => ({
        question: q.question,
        options: q.options,
        correctAnswer: q.correct_answer,
        hint: q.hint,
        explanation: q.explanation,
        incorrectExplanations: q.incorrect_explanations,
      })),
    }

    // Save quiz to database
    const formData = new FormData()
    formData.append('user_id', userId)
    formData.append('notebook_id', newQuiz.value.notebookId)
    formData.append('title', quizData.title)
    formData.append('topic', newQuiz.value.topic)
    formData.append('difficulty', newQuiz.value.difficulty)
    formData.append('questions', JSON.stringify(quizData.questions))

    const saveResponse = await axios.post('/api/quizzes', formData)
    
    // Add notebook title for display
    const notebook = notebooks.value.find(n => n.id === newQuiz.value.notebookId)
    const savedQuiz = {
      ...saveResponse.data,
      notebookTitle: notebook?.title,
      questions: quizData.questions
    }
    
    quizzes.value.unshift(savedQuiz)
    currentQuiz.value = savedQuiz

    closeCreateModal()
    isReviewMode.value = false // Set to quiz mode for newly generated quiz
    showQuizModal.value = true
  } catch (error) {
    console.error('Failed to generate quiz:', error)
    alert('Failed to generate quiz: ' + (error.response?.data?.detail || error.message))
  } finally {
    generating.value = false
  }
}

const toggleFolder = (notebookId) => {
  expandedFolders.value[notebookId] = !expandedFolders.value[notebookId]
}

const reviewQuiz = async (quiz) => {
  try {
    // Load the user's last attempt for this quiz
    const userId = auth0.user.value?.sub || 'anonymous'
    const response = await axios.get(`/api/quiz-attempts/latest/${quiz.id}`, {
      params: { user_id: userId }
    })
    
    // Attach the user's answers to the quiz
    currentQuiz.value = {
      ...quiz,
      userAnswers: response.data.answers, // User's submitted answers
      attemptScore: response.data.score,
      attemptedAt: response.data.attempted_at
    }
    isReviewMode.value = true
    showQuizModal.value = true
  } catch (error) {
    console.error('Failed to load quiz attempt:', error)
    // If no attempt exists, just show the quiz without pre-filled answers
    currentQuiz.value = quiz
    isReviewMode.value = true
    showQuizModal.value = true
  }
}

const handleQuizSubmit = async (results) => {
  console.log('Quiz completed:', results)
  
  // Save quiz attempt to backend for analytics and update streak
  try {
    const userId = auth0.user.value?.sub || 'anonymous'
    const quiz = currentQuiz.value
    
    const formData = new FormData()
    formData.append('user_id', userId)
    formData.append('quiz_id', quiz.id)
    formData.append('notebook_id', quiz.notebook_id || '')
    formData.append('topic', quiz.topic || '')
    formData.append('difficulty', quiz.difficulty || 'medium')
    formData.append('answers', JSON.stringify(results.answers))
    formData.append('score', results.score.toString())
    formData.append('correct_count', results.correctCount.toString())
    formData.append('total_questions', quiz.questions.length.toString())
    
    const response = await axios.post('/api/quiz-attempts', formData)
    console.log('Quiz attempt saved for analytics')
    
    // Show streak rewards if earned
    if (response.data.pointsEarned > 0) {
      const message = response.data.milestone 
        ? `${response.data.milestone}\n+${response.data.pointsEarned} points earned!`
        : `+${response.data.pointsEarned} points earned! 🔥 ${response.data.streak.currentStreak} day streak!`
      
      // Show a nice toast notification
      showStreakNotification(message, response.data.pointsEarned)
    }
  } catch (error) {
    console.error('Failed to save quiz attempt:', error)
    // Don't block user experience if analytics fail
  }
}

const showStreakNotification = (message, points) => {
  // Create a temporary notification element
  const notification = document.createElement('div')
  notification.className = 'streak-notification'
  notification.innerHTML = `
    <div class="streak-notification-content">
      <div class="streak-icon">🔥</div>
      <div class="streak-message">${message}</div>
      <div class="streak-points">+${points} 💎</div>
    </div>
  `
  document.body.appendChild(notification)
  
  // Animate in
  setTimeout(() => notification.classList.add('show'), 100)
  
  // Remove after 4 seconds
  setTimeout(() => {
    notification.classList.remove('show')
    setTimeout(() => document.body.removeChild(notification), 300)
  }, 4000)
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}
</script>

<style scoped>
.quiz-container {
  animation: fadeIn 0.6s ease-in-out;
  padding-left: 10rem;
}

@media (max-width: 1024px) {
  .quiz-container {
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

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.empty-icon {
  font-size: 5rem;
  margin-bottom: 1rem;
  animation: bounce 2s infinite ease-in-out;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.8; }
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

/* Notebook Folders */
.notebooks-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.notebook-folder {
  background: rgba(15, 12, 41, 0.1);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(139, 182, 255, 0.15);
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.4s ease-in-out;
  animation: cardSlideUp 0.6s ease-in-out both;
}

.folder-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease-in-out;
  user-select: none;
}

.folder-header:hover {
  background: rgba(139, 182, 255, 0.05);
}

.folder-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.folder-icon {
  font-size: 2rem;
  transition: transform 0.3s ease-in-out;
}

.folder-header:hover .folder-icon {
  transform: scale(1.1);
}

.folder-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: rgba(200, 220, 255, 0.95);
  margin: 0;
}

.quiz-count {
  padding: 0.25rem 0.75rem;
  background: rgba(139, 182, 255, 0.15);
  border: 1px solid rgba(139, 182, 255, 0.3);
  border-radius: 12px;
  color: rgba(200, 220, 255, 0.8);
  font-size: 0.875rem;
  font-weight: 600;
}

.folder-chevron {
  font-size: 1rem;
  color: rgba(200, 220, 255, 0.6);
  transition: transform 0.3s ease-in-out;
}

.folder-chevron.expanded {
  transform: rotate(180deg);
}

.folder-content {
  padding: 0 1.5rem 1.5rem 1.5rem;
}

/* Folder expand/collapse transition */
.folder-expand-enter-active,
.folder-expand-leave-active {
  transition: all 0.4s ease-in-out;
  overflow: hidden;
}

.folder-expand-enter-from,
.folder-expand-leave-to {
  opacity: 0;
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
}

.folder-expand-enter-to,
.folder-expand-leave-from {
  opacity: 1;
  max-height: 5000px;
}

/* Quizzes Grid */
.quizzes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.quiz-card {
  background: rgba(15, 12, 41, 0.2);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(139, 182, 255, 0.15);
  border-radius: 16px;
  padding: 1.5rem;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.4s ease-in-out;
  animation: cardSlideUp 0.4s ease-in-out both;
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

.quiz-card::before {
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

.quiz-card:hover::before {
  transform: translateX(100%);
}

.quiz-card:hover {
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
  transition: opacity 0.4s;
  pointer-events: none;
}

.quiz-card:hover .card-glow {
  opacity: 1;
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

.quiz-card:hover .card-shine {
  left: 100%;
}

.quiz-card:hover .card-shine {
  left: 100%;
}

.quiz-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.quiz-icon {
  font-size: 3rem;
  filter: drop-shadow(0 0 15px rgba(139, 182, 255, 0.6));
}

.difficulty-badge {
  padding: 0.5rem 1rem;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.difficulty-badge.easy {
  background: rgba(34, 197, 94, 0.2);
  color: #4ade80;
  border: 1px solid rgba(34, 197, 94, 0.4);
}

.difficulty-badge.medium {
  background: rgba(234, 179, 8, 0.2);
  color: #fbbf24;
  border: 1px solid rgba(234, 179, 8, 0.4);
}

.difficulty-badge.hard {
  background: rgba(239, 68, 68, 0.2);
  color: #f87171;
  border: 1px solid rgba(239, 68, 68, 0.4);
}

.quiz-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
  margin: 0 0 0.5rem 0;
}

.quiz-topic {
  font-size: 1rem;
  color: rgba(139, 182, 255, 0.8);
  margin: 0 0 1.5rem 0;
}

.quiz-info {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.95rem;
}

.info-icon {
  font-size: 1.2rem;
  filter: drop-shadow(0 0 8px rgba(139, 182, 255, 0.5));
}

.quiz-actions {
  display: flex;
  gap: 0.75rem;
}

.action-button {
  flex: 1;
  padding: 0.75rem 1rem;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
}

.action-button.review {
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.3), rgba(168, 216, 255, 0.2));
  border: 1px solid rgba(139, 182, 255, 0.4);
  color: white;
}

.action-button.review:hover {
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.5), rgba(168, 216, 255, 0.3));
  box-shadow: 0 5px 20px rgba(139, 182, 255, 0.4);
  transform: translateY(-2px);
}

/* Modal */
.glass-modal {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: transparent;
  border: none;
  padding: 0;
  max-width: 550px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  z-index: 200;
}

.glass-modal::backdrop {
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(10px);
  z-index: 199;
}

.modal-content {
  background: rgba(15, 12, 41, 0.95);
  backdrop-filter: blur(40px);
  border: 2px solid rgba(139, 182, 255, 0.3);
  border-radius: 24px;
  padding: 2.5rem;
  animation: modalSlide 0.4s cubic-bezier(0.4, 0, 0.2, 1);
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
  font-size: 2rem;
  font-weight: 800;
  background: linear-gradient(135deg, #8bb6ff, #c4e0ff);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0 0 2rem 0;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-label {
  display: block;
  color: rgba(200, 220, 255, 0.9);
  font-weight: 600;
  margin-bottom: 0.75rem;
  font-size: 0.95rem;
}

.glass-input {
  width: 100%;
  padding: 1rem;
  background: rgba(139, 182, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(139, 182, 255, 0.2);
  border-radius: 12px;
  color: white;
  font-size: 1rem;
  transition: all 0.3s;
  font-family: inherit;
}

.glass-input:focus {
  outline: none;
  background: rgba(139, 182, 255, 0.1);
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

.difficulty-options {
  display: flex;
  gap: 0.75rem;
}

.option-button {
  flex: 1;
  padding: 0.875rem 1rem;
  background: rgba(139, 182, 255, 0.05);
  border: 1px solid rgba(139, 182, 255, 0.2);
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.option-button.active {
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.3), rgba(168, 216, 255, 0.2));
  border-color: rgba(139, 182, 255, 0.5);
  color: white;
  box-shadow: 0 5px 20px rgba(139, 182, 255, 0.3);
}

.option-button:hover:not(.active) {
  background: rgba(139, 182, 255, 0.1);
  border-color: rgba(139, 182, 255, 0.3);
}

.modal-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
}

.modal-button {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 1rem 1.5rem;
  border-radius: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
  font-size: 1rem;
}

.modal-button.primary {
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.3), rgba(168, 216, 255, 0.2));
  border: 1px solid rgba(139, 182, 255, 0.4);
  color: white;
}

.modal-button.primary:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.5), rgba(168, 216, 255, 0.3));
  box-shadow: 0 8px 30px rgba(139, 182, 255, 0.4);
  transform: translateY(-2px);
}

.modal-button.primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal-button.secondary {
  background: rgba(139, 182, 255, 0.05);
  border: 1px solid rgba(139, 182, 255, 0.2);
  color: rgba(200, 220, 255, 0.9);
}

/* Streak Notification */
:deep(.streak-notification) {
  position: fixed;
  top: 2rem;
  right: 2rem;
  z-index: 10000;
  opacity: 0;
  transform: translateX(100%);
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

:deep(.streak-notification.show) {
  opacity: 1;
  transform: translateX(0);
}

:deep(.streak-notification-content) {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem 2rem;
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.95), rgba(255, 142, 83, 0.95));
  backdrop-filter: blur(20px);
  border: 2px solid rgba(255, 215, 0, 0.5);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), 0 0 20px rgba(255, 215, 0, 0.3);
  color: white;
  min-width: 300px;
}

:deep(.streak-icon) {
  font-size: 2.5rem;
  animation: bounce 0.6s ease-in-out infinite;
}

:deep(.streak-message) {
  flex: 1;
  font-size: 1rem;
  font-weight: 600;
  line-height: 1.4;
  white-space: pre-line;
}

:deep(.streak-points) {
  font-size: 1.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, #ffd700, #ffed4e);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.modal-button.secondary:hover {
  background: rgba(139, 182, 255, 0.1);
  border-color: rgba(139, 182, 255, 0.3);
}

/* Responsive */
@media (max-width: 1024px) {
  .quiz-container {
    padding-left: 2rem;
  }

  .header-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 1.5rem;
  }

  .quizzes-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .page-title {
    font-size: 2rem;
  }

  .title-icon {
    font-size: 2.5rem;
  }
}
</style>
