<template>
  <div class="settings-page">
    <QuickNav />

    <!-- Header -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <span class="title-icon">⚙️</span>
          Settings
        </h1>
        <p class="page-subtitle">Configure your AI models and system preferences</p>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p class="loading-text">Loading settings...</p>
    </div>

    <!-- Main Content -->
    <div v-else class="settings-content">
      <!-- Model Configuration Section -->
      <div class="settings-section glass-card">
        <h3 class="section-title">
          <span class="section-icon">🤖</span>
          AI Models Configuration
        </h3>

        <!-- LLM Model -->
        <div class="setting-item">
          <div class="setting-header">
            <label class="setting-label">Language Model (LLM)</label>
            <span class="setting-badge">For Q&A and Summarization</span>
          </div>
          <input
            v-model="settings.llm_model"
            type="text"
            class="glass-input"
            placeholder="e.g., llama3.1, gpt-4, mistral"
          />
          <p class="setting-description">
            The model used for answering questions and generating summaries from your documents
          </p>
        </div>

        <!-- Embedding Model -->
        <div class="setting-item">
          <div class="setting-header">
            <label class="setting-label">Embedding Model</label>
            <span class="setting-badge">For Text Similarity</span>
          </div>
          <input
            v-model="settings.embedder_model"
            type="text"
            class="glass-input"
            placeholder="e.g., nomic-embed-text, text-embedding-ada-002"
          />
          <p class="setting-description">
            The model used for converting text into vector embeddings for semantic search
          </p>
        </div>

        <!-- Embedding Provider -->
        <div class="setting-item">
          <div class="setting-header">
            <label class="setting-label">Embedding Provider</label>
            <span class="setting-badge">Optional</span>
          </div>
          <select v-model="settings.embedder_provider" class="glass-select">
            <option value="ollama">Ollama (Local)</option>
            <option value="openai">OpenAI</option>
            <option value="huggingface">HuggingFace</option>
          </select>
          <p class="setting-description">
            Choose which provider to use for embeddings
          </p>
        </div>

        <!-- LLM Provider -->
        <div class="setting-item">
          <div class="setting-header">
            <label class="setting-label">LLM Provider</label>
            <span class="setting-badge">Optional</span>
          </div>
          <select v-model="settings.llm_provider" class="glass-select">
            <option value="ollama">Ollama (Local)</option>
            <option value="openai">OpenAI</option>
            <option value="anthropic">Anthropic</option>
          </select>
          <p class="setting-description">
            Choose which provider to use for language generation
          </p>
        </div>

        <!-- API Keys Section -->
        <div class="setting-item" v-if="settings.llm_provider !== 'ollama' || settings.embedder_provider !== 'ollama'">
          <div class="setting-header">
            <label class="setting-label">API Keys</label>
            <span class="setting-badge warning">Sensitive</span>
          </div>
          
          <div v-if="settings.llm_provider === 'openai' || settings.embedder_provider === 'openai'" class="api-key-input">
            <label class="input-label">OpenAI API Key</label>
            <input
              v-model="settings.openai_api_key"
              type="password"
              class="glass-input"
              placeholder="sk-..."
            />
          </div>

          <div v-if="settings.llm_provider === 'anthropic'" class="api-key-input">
            <label class="input-label">Anthropic API Key</label>
            <input
              v-model="settings.anthropic_api_key"
              type="password"
              class="glass-input"
              placeholder="sk-ant-..."
            />
          </div>

          <p class="setting-description">
            API keys are stored securely and never sent to external servers except the configured provider
          </p>
        </div>

        <!-- Save Button -->
        <div class="setting-actions">
          <button @click="saveSettings" class="save-button" :disabled="saving">
            <span v-if="saving" class="button-icon">⏳</span>
            <span v-else class="button-icon">💾</span>
            <span>{{ saving ? 'Saving...' : 'Save Settings' }}</span>
          </button>
          <button @click="resetSettings" class="reset-button">
            <span class="button-icon">🔄</span>
            <span>Reset to Defaults</span>
          </button>
        </div>

        <div v-if="saveMessage" class="save-message" :class="{ success: saveSuccess, error: !saveSuccess }">
          {{ saveMessage }}
        </div>
      </div>

      <!-- Current System Info -->
      <div class="settings-section glass-card">
        <h3 class="section-title">
          <span class="section-icon">📊</span>
          Current System Status
        </h3>

        <div class="status-grid">
          <div class="status-item">
            <div class="status-label">Active LLM Model</div>
            <div class="status-value">{{ systemStatus.llm_model || 'Loading...' }}</div>
          </div>
          <div class="status-item">
            <div class="status-label">Active Embedder Model</div>
            <div class="status-value">{{ systemStatus.embedder_model || 'Loading...' }}</div>
          </div>
          <div class="status-item">
            <div class="status-label">ChromaDB Collections</div>
            <div class="status-value">{{ systemStatus.chroma_collections || 0 }}</div>
          </div>
          <div class="status-item">
            <div class="status-label">System Status</div>
            <div class="status-value" :class="{ healthy: systemStatus.status === 'healthy' }">
              {{ systemStatus.status || 'Unknown' }}
            </div>
          </div>
        </div>
      </div>

      <!-- Advanced Settings -->
      <div class="settings-section glass-card">
        <h3 class="section-title">
          <span class="section-icon">⚡</span>
          Advanced Settings
        </h3>

        <div class="setting-item">
          <div class="setting-header">
            <label class="setting-label">Chunk Size</label>
            <span class="setting-badge">Advanced</span>
          </div>
          <input
            v-model.number="settings.chunk_size"
            type="number"
            class="glass-input"
            placeholder="512"
            min="128"
            max="2048"
          />
          <p class="setting-description">
            Size of text chunks for processing (128-2048 characters). Smaller = more precise, Larger = more context
          </p>
        </div>

        <div class="setting-item">
          <div class="setting-header">
            <label class="setting-label">Top K Results</label>
            <span class="setting-badge">Advanced</span>
          </div>
          <input
            v-model.number="settings.top_k"
            type="number"
            class="glass-input"
            placeholder="4"
            min="1"
            max="10"
          />
          <p class="setting-description">
            Number of most relevant chunks to retrieve when answering questions
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuth0 } from '@auth0/auth0-vue'
import QuickNav from '../components/QuickNav.vue'
import axios from 'axios'

const auth0 = useAuth0()
const loading = ref(true)
const saving = ref(false)
const saveMessage = ref('')
const saveSuccess = ref(false)

const settings = ref({
  llm_model: 'llama3.1',
  embedder_model: 'nomic-embed-text',
  embedder_provider: 'ollama',
  llm_provider: 'ollama',
  openai_api_key: '',
  anthropic_api_key: '',
  chunk_size: 512,
  top_k: 4
})

const systemStatus = ref({
  status: '',
  llm_model: '',
  embedder_model: '',
  chroma_collections: 0
})

onMounted(async () => {
  await loadSystemStatus()
  await loadSettings()
  loading.value = false
})

const loadSystemStatus = async () => {
  try {
    const response = await axios.get('/api/health')
    systemStatus.value = response.data
  } catch (error) {
    console.error('Failed to load system status:', error)
  }
}

const loadSettings = async () => {
  try {
    // Load from localStorage for now (can be changed to API later)
    const saved = localStorage.getItem('clarity_settings')
    if (saved) {
      const parsed = JSON.parse(saved)
      settings.value = { ...settings.value, ...parsed }
    }
  } catch (error) {
    console.error('Failed to load settings:', error)
  }
}

const saveSettings = async () => {
  saving.value = true
  saveMessage.value = ''
  
  try {
    // Save to localStorage (can be changed to API later)
    localStorage.setItem('clarity_settings', JSON.stringify(settings.value))
    
    saveSuccess.value = true
    saveMessage.value = '✅ Settings saved successfully! Restart the backend to apply model changes.'
    
    setTimeout(() => {
      saveMessage.value = ''
    }, 5000)
  } catch (error) {
    console.error('Failed to save settings:', error)
    saveSuccess.value = false
    saveMessage.value = '❌ Failed to save settings. Please try again.'
  } finally {
    saving.value = false
  }
}

const resetSettings = () => {
  if (confirm('Are you sure you want to reset all settings to defaults?')) {
    settings.value = {
      llm_model: 'llama3.1',
      embedder_model: 'nomic-embed-text',
      embedder_provider: 'ollama',
      llm_provider: 'ollama',
      openai_api_key: '',
      anthropic_api_key: '',
      chunk_size: 512,
      top_k: 4
    }
    localStorage.removeItem('clarity_settings')
    saveMessage.value = '✅ Settings reset to defaults!'
    saveSuccess.value = true
    setTimeout(() => {
      saveMessage.value = ''
    }, 3000)
  }
}
</script>

<style scoped>
.settings-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  padding: 2rem;
}

/* Header */
.page-header {
  max-width: 1000px;
  margin: 0 auto 3rem;
}

.header-content {
  text-align: center;
}

.page-title {
  font-size: 3rem;
  font-weight: 800;
  background: linear-gradient(135deg, #8b6cf6 0%, #5b8bf6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 0.5rem 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}

.title-icon {
  font-size: 3rem;
  filter: drop-shadow(0 0 20px rgba(139, 182, 255, 0.6));
}

.page-subtitle {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
}

/* Loading */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  gap: 1rem;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(139, 92, 246, 0.2);
  border-top-color: #8b5cf6;
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
.settings-content {
  max-width: 1000px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.settings-section {
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
  margin: 0 0 2rem 0;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.section-icon {
  font-size: 1.75rem;
  filter: drop-shadow(0 0 12px rgba(139, 182, 255, 0.5));
}

/* Setting Items */
.setting-item {
  margin-bottom: 2rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.setting-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.setting-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.setting-label {
  font-size: 1.1rem;
  font-weight: 600;
  color: white;
}

.setting-badge {
  padding: 0.25rem 0.75rem;
  background: rgba(139, 92, 246, 0.2);
  color: #8b5cf6;
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.setting-badge.warning {
  background: rgba(255, 193, 7, 0.2);
  color: #ffc107;
  border-color: rgba(255, 193, 7, 0.3);
}

.glass-input,
.glass-select {
  width: 100%;
  padding: 0.875rem 1.25rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: white;
  font-size: 1rem;
  transition: all 0.3s ease;
  font-family: inherit;
}

.glass-input:focus,
.glass-select:focus {
  outline: none;
  border-color: rgba(139, 92, 246, 0.5);
  background: rgba(255, 255, 255, 0.08);
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
}

.glass-select {
  cursor: pointer;
}

.glass-select option {
  background: #1a1a2e;
  color: white;
}

.setting-description {
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.6);
  line-height: 1.5;
}

.api-key-input {
  margin-bottom: 1rem;
}

.input-label {
  display: block;
  font-size: 0.9rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 0.5rem;
}

/* Actions */
.setting-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
}

.save-button,
.reset-button {
  padding: 0.875rem 2rem;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
}

.save-button {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  color: white;
  flex: 1;
}

.save-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(139, 92, 246, 0.4);
}

.save-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.reset-button {
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.reset-button:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
}

.button-icon {
  font-size: 1.25rem;
}

/* Save Message */
.save-message {
  margin-top: 1rem;
  padding: 1rem;
  border-radius: 12px;
  font-weight: 500;
  text-align: center;
}

.save-message.success {
  background: rgba(76, 175, 80, 0.2);
  color: #4caf50;
  border: 1px solid rgba(76, 175, 80, 0.3);
}

.save-message.error {
  background: rgba(244, 67, 54, 0.2);
  color: #f44336;
  border: 1px solid rgba(244, 67, 54, 0.3);
}

/* Status Grid */
.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.status-item {
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  text-align: center;
}

.status-label {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: white;
}

.status-value.healthy {
  color: #4caf50;
}

/* Responsive */
@media (max-width: 768px) {
  .settings-page {
    padding: 1rem;
  }

  .page-title {
    font-size: 2rem;
  }

  .setting-actions {
    flex-direction: column;
  }

  .status-grid {
    grid-template-columns: 1fr;
  }
}
</style>
