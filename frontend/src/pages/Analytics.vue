<template>
  <div class="analytics-container">
    <QuickNav />
    
    <div class="header-section">
      <div class="header-left">
        <h1 class="page-title">
          <span class="title-icon">📊</span>
          <span class="title-text">Performance & Knowledge Graphs</span>
        </h1>
        <button @click="refreshAnalytics" class="refresh-btn" :class="{ refreshing: loading }">
          <span class="refresh-icon">🔄</span>
          <span>Refresh</span>
        </button>
      </div>
      <select v-model="selectedNotebook" class="notebook-filter glass-input">
        <option value="">All Notebooks</option>
        <option v-for="notebook in notebooks" :key="notebook.id" :value="notebook.id">
          {{ notebook.title }}
        </option>
      </select>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p class="loading-text">Analyzing your performance...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="!hasData" class="empty-state">
      <div class="empty-icon">📊</div>
      <h2 class="empty-title">No Data Yet</h2>
      <p class="empty-description">Complete quizzes and review flashcards to see your analytics</p>
    </div>

    <!-- Analytics Dashboard -->
    <div v-else class="dashboard">
      <!-- Overview Cards -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">🎯</div>
          <div class="stat-content">
            <div class="stat-value">{{ analytics.overall_accuracy }}%</div>
            <div class="stat-label">Overall Accuracy</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📝</div>
          <div class="stat-content">
            <div class="stat-value">{{ analytics.total_quizzes }}</div>
            <div class="stat-label">Quizzes Completed</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🎴</div>
          <div class="stat-content">
            <div class="stat-value">{{ analytics.total_flashcard_reviews }}</div>
            <div class="stat-label">Cards Reviewed</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">✅</div>
          <div class="stat-content">
            <div class="stat-value">{{ analytics.total_correct_answers }}/{{ analytics.total_questions_answered }}</div>
            <div class="stat-label">Correct Answers</div>
          </div>
        </div>
      </div>

      <!-- Charts Section -->
      <div class="charts-grid">
        <!-- Topic Coverage Chart -->
        <div class="chart-card">
          <h3 class="chart-title">📚 Topic Coverage</h3>
          <p class="chart-subtitle">Which topics you've studied most</p>
          <div class="chart-wrapper">
            <Pie :data="topicChartData" :options="chartOptions" />
          </div>
          <div class="topic-legend">
            <div
              v-for="(topic, index) in Object.keys(analytics.topic_coverage).slice(0, 5)"
              :key="topic"
              class="legend-item"
            >
              <span class="legend-color" :style="{ backgroundColor: topicColors[index] }"></span>
              <span class="legend-label">{{ topic }}</span>
              <span class="legend-value">
                {{ analytics.topic_coverage[topic].quiz_count + analytics.topic_coverage[topic].flashcard_count }} items
              </span>
            </div>
          </div>
        </div>

        <!-- Difficulty Distribution Chart -->
        <div class="chart-card">
          <h3 class="chart-title">⚡ Difficulty Breakdown</h3>
          <p class="chart-subtitle">Performance by difficulty level</p>
          <div class="chart-wrapper">
            <Doughnut :data="difficultyChartData" :options="chartOptions" />
          </div>
          <div class="difficulty-stats">
            <div
              v-for="(diff, key) in analytics.difficulty_distribution"
              :key="key"
              class="diff-stat"
            >
              <div class="diff-header">
                <span class="diff-badge" :class="key">{{ key }}</span>
                <span class="diff-accuracy">
                  {{ getDifficultyAccuracy(diff) }}% accuracy
                </span>
              </div>
              <div class="diff-bar">
                <div
                  class="diff-bar-fill correct"
                  :style="{ width: getDifficultyPercentage(diff, 'correct') + '%' }"
                ></div>
                <div
                  class="diff-bar-fill incorrect"
                  :style="{ width: getDifficultyPercentage(diff, 'incorrect') + '%' }"
                ></div>
              </div>
              <div class="diff-counts">
                <span class="correct-count">✓ {{ diff.correct }}</span>
                <span class="incorrect-count">✗ {{ diff.incorrect }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Topic Mastery Heatmap -->
        <div class="chart-card full-width">
          <h3 class="chart-title">🔥 Topic Mastery</h3>
          <p class="chart-subtitle">Your accuracy across different topics</p>
          <div class="mastery-grid">
            <div
              v-for="(stats, topic) in analytics.topic_coverage"
              :key="topic"
              class="mastery-item"
              :class="getMasteryLevel(stats)"
            >
              <div class="mastery-topic">{{ topic }}</div>
              <div class="mastery-accuracy">
                {{ getTopicAccuracy(stats) }}%
              </div>
              <div class="mastery-count">
                {{ stats.total_questions }} questions
              </div>
              <div class="mastery-bar">
                <div
                  class="mastery-bar-fill"
                  :style="{ width: getTopicAccuracy(stats) + '%' }"
                ></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Progress by Notebook (if filtered) -->
        <div v-if="selectedNotebook" class="chart-card full-width">
          <h3 class="chart-title">📖 Notebook Progress</h3>
          <p class="chart-subtitle">{{ getNotebookTitle(selectedNotebook) }}</p>
          <div class="progress-section">
            <div class="progress-item">
              <div class="progress-label">
                <span>Quiz Completion</span>
                <span class="progress-value">{{ analytics.total_quizzes }} quizzes</span>
              </div>
              <div class="progress-bar-wrapper">
                <div class="progress-bar">
                  <div
                    class="progress-bar-fill"
                    :style="{ width: Math.min(100, analytics.total_quizzes * 10) + '%' }"
                  ></div>
                </div>
              </div>
            </div>
            <div class="progress-item">
              <div class="progress-label">
                <span>Flashcard Mastery</span>
                <span class="progress-value">{{ analytics.total_flashcard_reviews }} reviews</span>
              </div>
              <div class="progress-bar-wrapper">
                <div class="progress-bar">
                  <div
                    class="progress-bar-fill flashcard"
                    :style="{ width: Math.min(100, analytics.total_flashcard_reviews * 2) + '%' }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useAuth0 } from '@auth0/auth0-vue'
import { useRouter } from 'vue-router'
import { Pie, Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  Title
} from 'chart.js'
import QuickNav from '../components/QuickNav.vue'
import axios from 'axios'

ChartJS.register(ArcElement, Tooltip, Legend, Title)

const router = useRouter()
const auth0 = useAuth0()

const loading = ref(true)
const analytics = ref({
  topic_coverage: {},
  difficulty_distribution: {},
  overall_accuracy: 0,
  total_quizzes: 0,
  total_flashcard_reviews: 0,
  total_questions_answered: 0,
  total_correct_answers: 0
})
const notebooks = ref([])
const selectedNotebook = ref('')

const topicColors = [
  '#8bb6ff',
  '#a8d8ff',
  '#6bffb2',
  '#ffb26b',
  '#ff6b9d',
  '#c084fc',
  '#fbbf24',
  '#f87171',
  '#34d399',
  '#60a5fa'
]

const hasData = computed(() => {
  return analytics.value.total_quizzes > 0 || analytics.value.total_flashcard_reviews > 0
})

const topicChartData = computed(() => {
  const topics = Object.keys(analytics.value.topic_coverage)
  const data = topics.map(topic => {
    const stats = analytics.value.topic_coverage[topic]
    return stats.quiz_count + stats.flashcard_count
  })

  return {
    labels: topics,
    datasets: [{
      data: data,
      backgroundColor: topicColors.slice(0, topics.length),
      borderColor: 'rgba(15, 12, 41, 0.5)',
      borderWidth: 2
    }]
  }
})

const difficultyChartData = computed(() => {
  const difficulties = Object.keys(analytics.value.difficulty_distribution)
  const data = difficulties.map(diff => {
    const stats = analytics.value.difficulty_distribution[diff]
    return stats.correct + stats.incorrect
  })

  return {
    labels: difficulties.map(d => d.charAt(0).toUpperCase() + d.slice(1)),
    datasets: [{
      data: data,
      backgroundColor: ['#6bffb2', '#fbbf24', '#ff6b9d'],
      borderColor: 'rgba(15, 12, 41, 0.5)',
      borderWidth: 2
    }]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: true,
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      backgroundColor: 'rgba(15, 12, 41, 0.95)',
      titleColor: 'rgba(255, 255, 255, 0.95)',
      bodyColor: 'rgba(200, 220, 255, 0.9)',
      borderColor: 'rgba(139, 182, 255, 0.3)',
      borderWidth: 1,
      padding: 12,
      cornerRadius: 8
    }
  }
}

onMounted(async () => {
  if (!auth0.isAuthenticated.value) {
    router.push('/')
    return
  }

  await loadNotebooks()
  await loadAnalytics()
  loading.value = false
})

watch(selectedNotebook, async () => {
  loading.value = true
  await loadAnalytics()
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

const loadAnalytics = async () => {
  try {
    const userId = auth0.user.value?.sub || 'anonymous'
    const params = { user_id: userId }
    if (selectedNotebook.value) {
      params.notebook_id = selectedNotebook.value
    }

    const response = await axios.get('/api/analytics/overview', { params })
    analytics.value = response.data
  } catch (error) {
    console.error('Failed to load analytics:', error)
  }
}

const getDifficultyAccuracy = (diff) => {
  const total = diff.correct + diff.incorrect
  return total > 0 ? Math.round((diff.correct / total) * 100) : 0
}

const getDifficultyPercentage = (diff, type) => {
  const total = diff.correct + diff.incorrect
  return total > 0 ? (diff[type] / total) * 100 : 0
}

const getTopicAccuracy = (stats) => {
  const total = stats.total_questions
  return total > 0 ? Math.round((stats.correct_answers / total) * 100) : 0
}

const getMasteryLevel = (stats) => {
  const accuracy = getTopicAccuracy(stats)
  if (accuracy >= 80) return 'master'
  if (accuracy >= 60) return 'proficient'
  if (accuracy >= 40) return 'learning'
  return 'beginner'
}

const getNotebookTitle = (notebookId) => {
  const notebook = notebooks.value.find(n => n.id === notebookId)
  return notebook?.title || 'Unknown'
}

const refreshAnalytics = async () => {
  loading.value = true
  await Promise.all([loadAnalytics(), loadNotebooks()])
  loading.value = false
}
</script>

<style scoped>
.analytics-container {
  animation: fadeIn 0.6s ease-in-out;
  padding-left: 10rem;
}

@media (max-width: 1024px) {
  .analytics-container {
    padding-left: 1rem;
    padding-top: 6rem;
  }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
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
  animation: slideDown 0.6s ease-in-out;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgba(139, 182, 255, 0.1);
  border: 1px solid rgba(139, 182, 255, 0.3);
  border-radius: 8px;
  color: #8bb6ff;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.refresh-btn:hover {
  background: rgba(139, 182, 255, 0.2);
  border-color: rgba(139, 182, 255, 0.5);
  transform: translateY(-2px);
}

.refresh-btn.refreshing .refresh-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
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
  animation: pulse 2s infinite ease-in-out;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.title-text {
  background: linear-gradient(135deg, #8bb6ff, #c4e0ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.notebook-filter {
  min-width: 250px;
}

.glass-input {
  width: 100%;
  padding: 0.75rem 1rem;
  background: rgba(139, 182, 255, 0.05);
  border: 1px solid rgba(139, 182, 255, 0.2);
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.95);
  font-size: 1rem;
  transition: all 0.3s ease-in-out;
  cursor: pointer;
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg width='12' height='8' viewBox='0 0 12 8' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1.5L6 6.5L11 1.5' stroke='rgba(139,182,255,0.8)' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 1rem center;
  background-size: 12px;
  padding-right: 3rem;
}

.glass-input:hover {
  background: rgba(139, 182, 255, 0.08);
  border-color: rgba(139, 182, 255, 0.4);
}

.glass-input:focus {
  outline: none;
  background: rgba(139, 182, 255, 0.1);
  border-color: rgba(139, 182, 255, 0.4);
  box-shadow: 0 0 20px rgba(139, 182, 255, 0.2);
}

.glass-input option {
  background: rgba(15, 12, 41, 0.98);
  color: rgba(255, 255, 255, 0.95);
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
  border: 1px solid rgba(139, 182, 255, 0.15);
  border-radius: 16px;
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
  border: 1px solid rgba(139, 182, 255, 0.15);
  border-radius: 16px;
  text-align: center;
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
}

/* Dashboard */
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 1.5rem;
  background: rgba(15, 12, 41, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(139, 182, 255, 0.15);
  border-radius: 16px;
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

.stat-card:hover {
  background: rgba(15, 12, 41, 0.15);
  border-color: rgba(139, 182, 255, 0.3);
  transform: translateY(-4px);
  box-shadow: 0 15px 40px rgba(139, 182, 255, 0.15);
}

.stat-icon {
  font-size: 3rem;
  animation: float 3s infinite ease-in-out;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.95);
  margin-bottom: 0.25rem;
}

.stat-label {
  color: rgba(200, 220, 255, 0.7);
  font-size: 0.875rem;
}

/* Charts Grid */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
  gap: 2rem;
}

.chart-card {
  padding: 2rem;
  background: rgba(15, 12, 41, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(139, 182, 255, 0.15);
  border-radius: 16px;
  animation: cardSlideUp 0.6s ease-in-out both;
}

.chart-card.full-width {
  grid-column: 1 / -1;
}

.chart-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: rgba(200, 220, 255, 0.95);
  margin: 0 0 0.5rem 0;
}

.chart-subtitle {
  color: rgba(200, 220, 255, 0.6);
  font-size: 0.875rem;
  margin-bottom: 1.5rem;
}

.chart-wrapper {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.5rem;
}

/* Topic Legend */
.topic-legend {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  background: rgba(139, 182, 255, 0.05);
  border-radius: 8px;
}

.legend-color {
  width: 1rem;
  height: 1rem;
  border-radius: 4px;
}

.legend-label {
  flex: 1;
  color: rgba(200, 220, 255, 0.9);
  font-size: 0.875rem;
}

.legend-value {
  color: rgba(200, 220, 255, 0.7);
  font-size: 0.875rem;
  font-weight: 600;
}

/* Difficulty Stats */
.difficulty-stats {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.diff-stat {
  padding: 1rem;
  background: rgba(139, 182, 255, 0.05);
  border-radius: 12px;
}

.diff-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.diff-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
}

.diff-badge.easy {
  background: rgba(107, 255, 178, 0.2);
  color: #6bffb2;
  border: 1px solid rgba(107, 255, 178, 0.3);
}

.diff-badge.medium {
  background: rgba(251, 191, 36, 0.2);
  color: #fbbf24;
  border: 1px solid rgba(251, 191, 36, 0.3);
}

.diff-badge.hard {
  background: rgba(255, 107, 157, 0.2);
  color: #ff6b9d;
  border: 1px solid rgba(255, 107, 157, 0.3);
}

.diff-accuracy {
  color: rgba(200, 220, 255, 0.9);
  font-size: 0.875rem;
  font-weight: 600;
}

.diff-bar {
  height: 8px;
  background: rgba(139, 182, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
  display: flex;
  margin-bottom: 0.5rem;
}

.diff-bar-fill {
  height: 100%;
  transition: width 0.6s ease-in-out;
}

.diff-bar-fill.correct {
  background: linear-gradient(90deg, #6bffb2, #34d399);
}

.diff-bar-fill.incorrect {
  background: linear-gradient(90deg, #ff6b9d, #f87171);
}

.diff-counts {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
}

.correct-count {
  color: #6bffb2;
}

.incorrect-count {
  color: #ff6b9d;
}

/* Mastery Grid */
.mastery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}

.mastery-item {
  padding: 1.5rem;
  background: rgba(139, 182, 255, 0.05);
  border: 2px solid rgba(139, 182, 255, 0.2);
  border-radius: 12px;
  transition: all 0.3s ease-in-out;
}

.mastery-item:hover {
  background: rgba(139, 182, 255, 0.08);
  border-color: rgba(139, 182, 255, 0.4);
  transform: translateY(-2px);
}

.mastery-item.master {
  border-color: rgba(107, 255, 178, 0.5);
  background: rgba(107, 255, 178, 0.05);
}

.mastery-item.proficient {
  border-color: rgba(139, 182, 255, 0.5);
  background: rgba(139, 182, 255, 0.05);
}

.mastery-item.learning {
  border-color: rgba(251, 191, 36, 0.5);
  background: rgba(251, 191, 36, 0.05);
}

.mastery-item.beginner {
  border-color: rgba(255, 107, 157, 0.5);
  background: rgba(255, 107, 157, 0.05);
}

.mastery-topic {
  font-size: 1.125rem;
  font-weight: 700;
  color: rgba(200, 220, 255, 0.95);
  margin-bottom: 0.5rem;
}

.mastery-accuracy {
  font-size: 2rem;
  font-weight: 800;
  color: rgba(255, 255, 255, 0.95);
  margin-bottom: 0.25rem;
}

.mastery-count {
  color: rgba(200, 220, 255, 0.6);
  font-size: 0.875rem;
  margin-bottom: 0.75rem;
}

.mastery-bar {
  height: 6px;
  background: rgba(139, 182, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.mastery-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #8bb6ff, #6bffb2);
  transition: width 0.6s ease-in-out;
}

/* Progress Section */
.progress-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.progress-item {
  padding: 1.5rem;
  background: rgba(139, 182, 255, 0.05);
  border-radius: 12px;
}

.progress-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  color: rgba(200, 220, 255, 0.9);
  font-size: 1rem;
  font-weight: 600;
}

.progress-value {
  color: rgba(200, 220, 255, 0.7);
  font-size: 0.875rem;
}

.progress-bar-wrapper {
  height: 12px;
  background: rgba(139, 182, 255, 0.1);
  border-radius: 6px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: rgba(139, 182, 255, 0.1);
  border-radius: 6px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #8bb6ff, #a8d8ff);
  transition: width 0.8s ease-in-out;
}

.progress-bar-fill.flashcard {
  background: linear-gradient(90deg, #ff6b9d, #ffb26b);
}
</style>
