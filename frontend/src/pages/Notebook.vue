<template>
  <div class="notebook-page">
    <QuickNav />

    <!-- Header -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <span class="title-icon">📚</span>
          {{ notebook.title }}
        </h1>
        <p class="page-subtitle">Ask questions and get AI-powered answers from your documents</p>
      </div>
      <div class="header-actions">
        <button @click="showUploadModal" class="action-button">
          <span class="button-icon">📤</span>
          Upload Document
        </button>
        <button @click="goBack" class="action-button secondary">
          <span class="button-icon">←</span>
          Back
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p class="loading-text">Loading notebook...</p>
    </div>

    <!-- Main Content -->
    <div v-else class="notebook-content">
      <!-- Left Column: Main Content -->
      <div class="main-column">
        <!-- Documents Section -->
        <div class="documents-section glass-card">
          <h3 class="section-title">
            <span class="section-icon">📄</span>
            Documents
          </h3>
          <div v-if="documents.length === 0" class="empty-message">
            No documents yet. Upload a PDF, TXT, or Markdown file to get started.
          </div>
          <div v-else class="documents-grid">
            <div v-for="doc in documents" :key="doc.id" class="document-card">
              <div class="doc-icon">📄</div>
              <div class="doc-info">
                <div class="doc-name">{{ doc.name }}</div>
                <div class="doc-meta">{{ doc.chunkCount }} chunks</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Ask Question Section -->
      <div class="question-section glass-card">
        <h3 class="section-title">
          <span class="section-icon">💭</span>
          Ask a Question
        </h3>
        <div class="question-form">
          <textarea
            v-model="question"
            placeholder="What would you like to know from your documents? (Press Ctrl+Enter to ask)"
            class="glass-textarea"
            rows="4"
            @keydown.ctrl.enter="askQuestion"
          ></textarea>
          <div class="form-controls">
            <label class="checkbox-label">
              <input
                v-model="useSummary"
                type="checkbox"
                class="glass-checkbox"
              />
              <span>Include summary</span>
            </label>
            <button
              @click="askQuestion"
              :disabled="!question.trim() || querying"
              class="ask-button"
            >
              <span v-if="querying" class="button-icon">⏳</span>
              <span v-else class="button-icon">✨</span>
              <span>{{ querying ? 'Thinking...' : 'Ask' }}</span>
            </button>
          </div>
        </div>

        <!-- Answer Display -->
        <div v-if="answer" class="answer-section">
          <div class="answer-header">
            <h4 class="answer-title">Answer</h4>
          </div>
          <div class="answer-content markdown-content" v-html="renderMarkdown(answer.text)"></div>
          
          <div v-if="answer.sources && answer.sources.length" class="sources-section">
            <h5 class="sources-title">
              <span class="section-icon">📚</span>
              Sources
            </h5>
            <div class="sources-grid">
              <div
                v-for="(source, idx) in answer.sources"
                :key="idx"
                class="source-card"
              >
                <div class="source-header">
                  <span class="source-badge">Score: {{ source.score.toFixed(3) }}</span>
                </div>
                <div class="source-text markdown-content" v-html="renderMarkdown(source.text.substring(0, 200) + '...')"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
      </div>

      <!-- Right Column: Conversation History Sidebar -->
      <div class="sidebar-column">
        <div class="history-sidebar glass-card">
          <div class="history-header">
            <h3 class="section-title">
              <span class="section-icon">💬</span>
              History
              <span class="history-count">({{ conversations.length }})</span>
            </h3>
            <div class="history-actions">
              <button @click="loadConversations" class="refresh-button" title="Refresh history" :disabled="loadingConversations">
                🔄
              </button>
              <button v-if="conversations.length > 0" @click="clearHistory" class="clear-history-button" title="Clear all history">
                🗑️
              </button>
            </div>
          </div>
          
          <div v-if="loadingConversations" class="loading-history">
            <div class="small-spinner"></div>
            <p>Loading history...</p>
          </div>
          
          <div v-else-if="conversations.length === 0" class="empty-message">
            <p>No history yet. Ask a question to start!</p>
            <div style="margin-top: 1rem; font-size: 0.75rem; opacity: 0.5;">
              Debug: Notebook ID: {{ route.params.id }}<br>
              User: {{ auth0.user.value?.sub || 'anonymous' }}
            </div>
          </div>
          
          <div v-else class="history-timeline">
            <div
              v-for="conv in conversations"
              :key="conv.id"
              class="history-item"
            >
              <div class="history-timestamp">
                {{ new Date(conv.createdAt).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) }}
              </div>
              <div class="history-question">
                <div class="history-label">Q:</div>
                <div class="history-text">{{ conv.question }}</div>
              </div>
              <div class="history-answer">
                <div class="history-label">A:</div>
                <div class="history-text markdown-content" v-html="renderMarkdown(conv.answer.substring(0, 150) + (conv.answer.length > 150 ? '...' : ''))"></div>
              </div>
              <button @click="deleteConversation(conv.id)" class="delete-conv-button" title="Delete this conversation">
                🗑️
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Upload Modal -->
    <dialog ref="uploadModal" class="glass-modal" @click="handleUploadModalClick">
      <div class="modal-content" @click.stop>
        <h3 class="modal-title">Upload Document</h3>
        
        <div class="form-group">
          <label class="form-label">Choose File</label>
          <input
            ref="fileInput"
            type="file"
            accept=".pdf,.txt,.md"
            class="glass-file-input"
            @change="handleFileSelect"
          />
          <p class="file-hint">Supported: PDF, TXT, Markdown</p>
        </div>

        <div v-if="uploading" class="upload-progress">
          <div class="progress-bar">
            <div class="progress-fill"></div>
          </div>
          <p class="upload-text">Uploading and processing...</p>
        </div>

        <div class="modal-actions">
          <button
            @click="uploadFile"
            class="modal-button primary"
            :disabled="!selectedFile || uploading"
          >
            <span>Upload</span>
            <span class="button-icon">📤</span>
          </button>
          <button @click="closeUploadModal" class="modal-button secondary" :disabled="uploading">
            Cancel
          </button>
        </div>
      </div>
    </dialog>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth0 } from '@auth0/auth0-vue'
import { marked } from 'marked'
import QuickNav from '../components/QuickNav.vue'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const auth0 = useAuth0()

const loading = ref(true)
const querying = ref(false)
const uploading = ref(false)
const notebook = ref({ title: 'Loading...', id: null })
const documents = ref([])
const uploadModal = ref(null)
const fileInput = ref(null)
const selectedFile = ref(null)
const question = ref('')
const useSummary = ref(false)
const answer = ref(null)
const conversations = ref([])
const loadingConversations = ref(false)

// Markdown renderer
const renderMarkdown = (text) => {
  if (!text) return ''
  return marked.parse(text)
}

onMounted(async () => {
  if (!auth0.isAuthenticated.value) {
    router.push('/')
    return
  }

  await loadNotebook()
  await loadConversations()
})

const loadNotebook = async () => {
  loading.value = true
  try {
    const notebookId = route.params.id
    const userId = auth0.user.value?.sub || 'anonymous'
    
    // Fetch notebook details from API
    const notebookResponse = await axios.get(`/api/notebooks/${notebookId}`, {
      params: { user_id: userId }
    })
    
    notebook.value = {
      id: notebookResponse.data.id,
      title: notebookResponse.data.title,
    }
    
    // Fetch documents for this notebook
    const docsResponse = await axios.get(`/api/notebooks/${notebookId}/documents`, {
      params: { user_id: userId }
    })
    
    documents.value = docsResponse.data
    
    userStore.setCurrentNotebook(notebook.value)
  } catch (error) {
    console.error('Failed to load notebook:', error)
    // Fallback to store if API fails
    const existingNotebook = userStore.notebooks.find(nb => nb.id === route.params.id)
    if (existingNotebook) {
      notebook.value = {
        id: existingNotebook.id,
        title: existingNotebook.title,
      }
    } else {
      notebook.value = {
        id: route.params.id,
        title: 'Untitled Notebook',
      }
    }
    documents.value = []
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push('/notebooks')
}

const showUploadModal = () => {
  uploadModal.value?.showModal()
}

const closeUploadModal = () => {
  if (!uploading.value) {
    uploadModal.value?.close()
    selectedFile.value = null
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  }
}

const handleFileSelect = (event) => {
  const files = event.target.files
  if (files && files.length > 0) {
    selectedFile.value = files[0]
  }
}

const handleUploadModalClick = (e) => {
  // Close modal when clicking on backdrop
  if (e.target === uploadModal.value) {
    closeUploadModal()
  }
}

const uploadFile = async () => {
  if (!selectedFile.value) return

  uploading.value = true
  try {
    const notebookId = route.params.id
    const userId = auth0.user.value?.sub || 'anonymous'
    
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('user_id', userId)

    // Upload to notebook-specific endpoint
    const response = await axios.post(`/api/notebooks/${notebookId}/documents`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    // Add document to list
    documents.value.push(response.data)

    alert(`✅ Document uploaded! ${response.data.chunkCount} chunks created.`)
    closeUploadModal()
  } catch (error) {
    console.error('Failed to upload file:', error)
    const errorMsg = error.response?.data?.detail || error.message || 'Unknown error'
    alert(`Failed to upload file: ${errorMsg}`)
  } finally {
    uploading.value = false
  }
}

const loadConversations = async () => {
  loadingConversations.value = true
  try {
    console.log('[Notebook] Loading conversations for notebook:', route.params.id)
    console.log('[Notebook] User ID:', auth0.user.value?.sub)
    const response = await axios.get(`/api/conversations/${route.params.id}`, {
      headers: {
        'X-User-Id': auth0.user.value?.sub || 'anonymous'
      }
    })
    console.log('[Notebook] Conversations response:', response.data)
    if (response.data.success) {
      conversations.value = response.data.conversations
      console.log('[Notebook] ✅ Set conversations:', conversations.value.length, 'items')
      console.log('[Notebook] Conversations:', JSON.stringify(conversations.value, null, 2))
    }
  } catch (error) {
    console.error('[Notebook] ❌ Failed to load conversations:', error)
    console.error('[Notebook] Error details:', error.response?.data)
  } finally {
    loadingConversations.value = false
  }
}

const askQuestion = async () => {
  if (!question.value.trim()) return
  
  querying.value = true
  answer.value = null
  
  try {
    const response = await axios.post('/api/ask', {
      user_id: auth0.user.value?.sub || 'anonymous',
      notebook_id: route.params.id,
      question: question.value,
      top_k: 4,
      use_summary: useSummary.value,
    })

    answer.value = {
      text: response.data.answer,
      sources: response.data.source_chunks.map((chunk, idx) => ({
        id: chunk.id || idx.toString(),
        score: chunk.score || 0,
        text: chunk.text,
      })),
    }
    
    // Save conversation to history
    await saveConversation(question.value, response.data.answer, response.data.source_chunks)
    
    // Reload conversation history
    await loadConversations()
  } catch (error) {
    console.error('Failed to query:', error)
    alert('Failed to get answer. Please try again.')
  } finally {
    querying.value = false
  }
}

const saveConversation = async (q, a, sources) => {
  try {
    console.log('[Notebook] Saving conversation to notebook:', route.params.id)
    const formData = new FormData()
    formData.append('notebook_id', route.params.id)
    formData.append('question', q)
    formData.append('answer', a)
    formData.append('sources', JSON.stringify(sources))
    formData.append('used_summary', useSummary.value ? 'true' : 'false')
    
    const response = await axios.post('/api/conversations', formData, {
      headers: {
        'X-User-Id': auth0.user.value?.sub || 'anonymous'
      }
    })
    console.log('[Notebook] Conversation saved:', response.data)
  } catch (error) {
    console.error('[Notebook] Failed to save conversation:', error)
    console.error('[Notebook] Error details:', error.response?.data)
  }
}

const deleteConversation = async (conversationId) => {
  try {
    await axios.delete(`/api/conversations/${conversationId}`, {
      headers: {
        'X-User-Id': auth0.user.value?.sub || 'anonymous'
      }
    })
    await loadConversations()
  } catch (error) {
    console.error('Failed to delete conversation:', error)
  }
}

const clearHistory = async () => {
  if (!confirm('Are you sure you want to clear all conversation history for this notebook?')) {
    return
  }
  
  try {
    await axios.delete(`/api/conversations/notebook/${route.params.id}`, {
      headers: {
        'X-User-Id': auth0.user.value?.sub || 'anonymous'
      }
    })
    conversations.value = []
  } catch (error) {
    console.error('Failed to clear history:', error)
  }
}


</script>

<style scoped>
.notebook-page {
  min-height: 100vh;
  padding: 2rem 2rem 2rem 12rem;
  background: linear-gradient(135deg, #1a1a2e 0%, #0f0f1e 100%);
  color: white;
}

/* Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 3rem;
  gap: 2rem;
}

.header-content {
  flex: 1;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 800;
  margin: 0 0 0.5rem 0;
  background: linear-gradient(135deg, #8bb6ff, #c4e0ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.title-icon {
  font-size: 2.5rem;
  filter: drop-shadow(0 0 20px rgba(139, 182, 255, 0.6));
}

.page-subtitle {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.action-button {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1.5rem;
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.3), rgba(196, 224, 255, 0.2));
  border: 1px solid rgba(139, 182, 255, 0.4);
  border-radius: 14px;
  color: white;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(20px);
}

.action-button.secondary {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.2);
}

.action-button:hover {
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.4), rgba(196, 224, 255, 0.3));
  border-color: rgba(139, 182, 255, 0.6);
  box-shadow: 0 8px 32px rgba(139, 182, 255, 0.4);
  transform: translateY(-2px);
}

.action-button.secondary:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.3);
}

.button-icon {
  font-size: 1.25rem;
}

/* Loading */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 50vh;
  gap: 1.5rem;
}

.loading-spinner {
  width: 60px;
  height: 60px;
  border: 4px solid rgba(139, 182, 255, 0.2);
  border-top-color: #8bb6ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.7);
}

/* Content */
.notebook-content {
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: 2rem;
  align-items: start;
}

.main-column {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.sidebar-column {
  position: sticky;
  top: 2rem;
  max-height: calc(100vh - 220px);
  overflow: hidden;
}

.glass-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  padding: 2rem;
  backdrop-filter: blur(20px);
}

.section-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
  margin: 0 0 1.5rem 0;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.section-icon {
  font-size: 1.75rem;
  filter: drop-shadow(0 0 12px rgba(139, 182, 255, 0.5));
}

/* Documents Section */
.documents-section {
  height: fit-content;
}

.empty-message {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.95rem;
  text-align: center;
  padding: 2rem 1rem;
  line-height: 1.6;
}

.documents-grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.document-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: rgba(139, 182, 255, 0.05);
  border: 1px solid rgba(139, 182, 255, 0.15);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.document-card:hover {
  background: rgba(139, 182, 255, 0.1);
  border-color: rgba(139, 182, 255, 0.3);
  transform: translateX(4px);
}

.doc-icon {
  font-size: 2rem;
  filter: drop-shadow(0 0 8px rgba(139, 182, 255, 0.4));
}

.doc-info {
  flex: 1;
  min-width: 0;
}

.doc-name {
  font-weight: 600;
  color: white;
  font-size: 0.95rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.doc-meta {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.5);
  margin-top: 0.25rem;
}

/* Question Section */
.question-section {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.question-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.glass-textarea {
  width: 100%;
  padding: 1.25rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  color: white;
  font-size: 1rem;
  line-height: 1.6;
  resize: vertical;
  transition: all 0.3s ease;
  font-family: inherit;
}

.glass-textarea:focus {
  outline: none;
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(139, 182, 255, 0.5);
  box-shadow: 0 0 30px rgba(139, 182, 255, 0.3);
}

.glass-textarea::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.form-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.95rem;
  cursor: pointer;
}

.glass-checkbox {
  width: 20px;
  height: 20px;
  appearance: none;
  -webkit-appearance: none;
  background: rgba(139, 182, 255, 0.05);
  border: 2px solid rgba(139, 182, 255, 0.3);
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  transition: all 0.3s ease;
}

.glass-checkbox:hover {
  background: rgba(139, 182, 255, 0.1);
  border-color: rgba(139, 182, 255, 0.5);
  box-shadow: 0 0 12px rgba(139, 182, 255, 0.2);
}

.glass-checkbox:checked {
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.4), rgba(168, 216, 255, 0.3));
  border-color: rgba(139, 182, 255, 0.7);
  box-shadow: 0 0 15px rgba(139, 182, 255, 0.4);
}

.glass-checkbox:checked::after {
  content: '✓';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 14px;
  font-weight: bold;
}

.ask-button {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 2.5rem;
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.3), rgba(196, 224, 255, 0.2));
  border: 1px solid rgba(139, 182, 255, 0.4);
  border-radius: 14px;
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(20px);
}

.ask-button:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.4), rgba(196, 224, 255, 0.3));
  border-color: rgba(139, 182, 255, 0.6);
  box-shadow: 0 8px 32px rgba(139, 182, 255, 0.4);
  transform: translateY(-2px);
}

.ask-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Answer Section */
.answer-section {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.answer-header {
  margin-bottom: 1.5rem;
}

.answer-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: white;
  margin: 0;
}

.answer-content {
  padding: 1.5rem;
  background: rgba(139, 182, 255, 0.05);
  border: 1px solid rgba(139, 182, 255, 0.15);
  border-radius: 16px;
  font-size: 1.05rem;
  line-height: 1.8;
  color: rgba(255, 255, 255, 0.95);
}

/* Sources */
.sources-section {
  margin-top: 2rem;
}

.sources-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: white;
  margin: 0 0 1rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.sources-grid {
  display: grid;
  gap: 1rem;
}

.source-card {
  padding: 1rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.source-card:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(139, 182, 255, 0.2);
}

.source-header {
  margin-bottom: 0.75rem;
}

.source-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background: rgba(139, 182, 255, 0.15);
  border: 1px solid rgba(139, 182, 255, 0.25);
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
}

.source-text {
  font-size: 0.9rem;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.75);
}

/* Markdown Styles */
.markdown-content {
  line-height: 1.8;
}

.markdown-content strong {
  color: #c4e0ff;
  font-weight: 700;
}

.markdown-content em {
  color: #a8d8ff;
  font-style: italic;
}

.markdown-content code {
  background: rgba(139, 182, 255, 0.15);
  padding: 0.2em 0.4em;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
  color: #c4e0ff;
}

.markdown-content pre {
  background: rgba(15, 12, 41, 0.6);
  padding: 1rem;
  border-radius: 8px;
  overflow-x: auto;
  border: 1px solid rgba(139, 182, 255, 0.2);
}

.markdown-content ul,
.markdown-content ol {
  margin-left: 1.5rem;
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
}

.markdown-content li {
  margin: 0.25rem 0;
}

.markdown-content h1,
.markdown-content h2,
.markdown-content h3 {
  color: #c4e0ff;
  margin-top: 1rem;
  margin-bottom: 0.5rem;
  font-weight: 700;
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

.glass-file-input {
  width: 100%;
  padding: 0.75rem;
  background: rgba(139, 182, 255, 0.05);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(139, 182, 255, 0.2);
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.95);
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease-in-out;
}

.glass-file-input:hover {
  background: rgba(139, 182, 255, 0.1);
  border-color: rgba(139, 182, 255, 0.4);
  box-shadow: 0 4px 15px rgba(139, 182, 255, 0.15);
}

.glass-file-input::file-selector-button {
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.25), rgba(168, 216, 255, 0.2));
  border: 1px solid rgba(139, 182, 255, 0.4);
  color: rgba(255, 255, 255, 0.95);
  padding: 0.5rem 1rem;
  border-radius: 8px;
  margin-right: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 600;
}

.glass-file-input::file-selector-button:hover {
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.35), rgba(168, 216, 255, 0.3));
  border-color: rgba(139, 182, 255, 0.6);
  box-shadow: 0 4px 20px rgba(139, 182, 255, 0.3);
  transform: translateY(-1px);
}

.file-hint {
  margin-top: 0.5rem;
  font-size: 0.85rem;
  color: rgba(200, 220, 255, 0.6);
}

.upload-progress {
  margin-bottom: 1.5rem;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: rgba(15, 12, 41, 0.3);
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 0.75rem;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #8bb6ff, #c4e0ff);
  border-radius: 10px;
  animation: progressPulse 1.5s ease-in-out infinite;
}

@keyframes progressPulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.upload-text {
  text-align: center;
  font-size: 0.9rem;
  color: rgba(200, 220, 255, 0.8);
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

.modal-button.primary:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.4), rgba(168, 216, 255, 0.4));
  border-color: rgba(139, 182, 255, 0.6);
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(139, 182, 255, 0.3);
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

.modal-button.secondary:hover:not(:disabled) {
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

/* Responsive */
@media (max-width: 1024px) {
  .notebook-page {
    padding: 2rem;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-actions {
    width: 100%;
    justify-content: flex-start;
  }

  .notebook-content {
    grid-template-columns: 1fr;
  }

  .documents-section {
    position: static;
  }
}

@media (max-width: 640px) {
  .page-title {
    font-size: 2rem;
  }

  .header-actions {
    flex-direction: column;
  }

  .action-button {
    width: 100%;
    justify-content: center;
  }
}

/* Conversation History Sidebar */
.history-sidebar {
  display: flex;
  flex-direction: column;
  height: 100%;
  max-height: calc(100vh - 220px);
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  flex-shrink: 0;
}

.history-header .section-title {
  margin: 0;
  font-size: 1.25rem;
}

.history-count {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 400;
}

.history-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.refresh-button {
  padding: 0.5rem 0.75rem;
  background: rgba(139, 92, 246, 0.1);
  color: #8b5cf6;
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 8px;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  line-height: 1;
}

.refresh-button:hover:not(:disabled) {
  background: rgba(139, 92, 246, 0.2);
  border-color: rgba(139, 92, 246, 0.5);
  transform: rotate(180deg);
}

.refresh-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.clear-history-button {
  padding: 0.5rem 0.75rem;
  background: rgba(255, 107, 107, 0.1);
  color: #ff6b6b;
  border: 1px solid rgba(255, 107, 107, 0.3);
  border-radius: 8px;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  line-height: 1;
}

.clear-history-button:hover {
  background: rgba(255, 107, 107, 0.2);
  border-color: rgba(255, 107, 107, 0.5);
}

.history-sidebar .empty-message {
  text-align: center;
  padding: 2rem 1rem;
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.9rem;
}

.loading-history {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem 1rem;
  gap: 0.75rem;
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.9rem;
}

.small-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid rgba(139, 92, 246, 0.2);
  border-top-color: #8b5cf6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.history-timeline {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  overflow-y: auto;
  overflow-x: hidden;
  flex: 1;
  padding-right: 0.5rem;
}

.history-timeline::-webkit-scrollbar {
  width: 6px;
}

.history-timeline::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 3px;
}

.history-timeline::-webkit-scrollbar-thumb {
  background: rgba(139, 92, 246, 0.3);
  border-radius: 3px;
}

.history-timeline::-webkit-scrollbar-thumb:hover {
  background: rgba(139, 92, 246, 0.5);
}

.history-item {
  padding: 1rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  position: relative;
  transition: all 0.2s ease;
  cursor: pointer;
}

.history-item:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(139, 92, 246, 0.3);
  transform: translateX(-2px);
}

.history-timestamp {
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.4);
  margin-bottom: 0.75rem;
  font-weight: 500;
}

.history-question,
.history-answer {
  margin-bottom: 0.75rem;
}

.history-label {
  font-size: 0.7rem;
  font-weight: 700;
  color: #8b5cf6;
  margin-bottom: 0.35rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.history-text {
  font-size: 0.85rem;
  line-height: 1.5;
  color: rgba(255, 255, 255, 0.85);
  word-wrap: break-word;
}

.history-question .history-text {
  font-weight: 600;
  color: rgba(255, 255, 255, 0.95);
}

.history-answer .history-text {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.delete-conv-button {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  padding: 0.25rem 0.5rem;
  background: rgba(255, 107, 107, 0.1);
  color: #ff6b6b;
  border: 1px solid rgba(255, 107, 107, 0.2);
  border-radius: 6px;
  font-size: 0.85rem;
  cursor: pointer;
  opacity: 0;
  transition: all 0.2s ease;
  line-height: 1;
}

.history-item:hover .delete-conv-button {
  opacity: 1;
}

.delete-conv-button:hover {
  background: rgba(255, 107, 107, 0.2);
  border-color: rgba(255, 107, 107, 0.5);
  transform: scale(1.05);
}

/* Responsive Design */
@media (max-width: 1024px) {
  .notebook-content {
    grid-template-columns: 1fr;
  }
  
  .sidebar-column {
    position: static;
    max-height: 500px;
  }
  
  .history-sidebar {
    max-height: 500px;
  }
}

@media (max-width: 640px) {
  .delete-conv-button {
    opacity: 1;
    position: static;
    margin-top: 0.75rem;
    width: 100%;
    justify-content: center;
    display: flex;
  }
  
  .history-item:hover .delete-conv-button {
    opacity: 1;
  }
  
  .sidebar-column {
    max-height: 400px;
  }
}
</style>
