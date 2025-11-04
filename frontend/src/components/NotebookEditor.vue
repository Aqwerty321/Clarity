<template>
  <div class="space-y-4">
    <!-- Toolbar -->
    <div class="flex justify-between items-center">
      <input
        v-model="localTitle"
        @blur="updateTitle"
        type="text"
        placeholder="Untitled Notebook"
        class="input input-ghost text-2xl font-bold flex-1"
      />
      <div class="flex gap-2">
        <button @click="$emit('upload')" class="btn btn-primary">
          Upload Document
        </button>
        <button @click="$emit('sync')" class="btn btn-ghost">
          Sync
        </button>
      </div>
    </div>

    <!-- Document List -->
    <div class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <h3 class="card-title">Documents</h3>
        <div v-if="documents.length === 0" class="text-center text-base-content/50 py-8">
          No documents yet. Upload a PDF, TXT, or Markdown file to get started.
        </div>
        <ul v-else class="menu">
          <li v-for="doc in documents" :key="doc.id">
            <a @click="selectDocument(doc.id)">
              <span class="flex-1">{{ doc.name }}</span>
              <span class="badge">{{ doc.chunkCount }} chunks</span>
            </a>
          </li>
        </ul>
      </div>
    </div>

    <!-- Query Interface -->
    <div class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <h3 class="card-title">Ask a Question</h3>
        <div class="form-control">
          <textarea
            v-model="question"
            placeholder="What would you like to know from your documents?"
            class="textarea textarea-bordered h-24"
            @keydown.ctrl.enter="askQuestion"
          ></textarea>
          <div class="flex justify-between items-center mt-2">
            <label class="label cursor-pointer gap-2">
              <input
                v-model="useSummary"
                type="checkbox"
                class="checkbox checkbox-sm"
              />
              <span class="label-text">Include summary</span>
            </label>
            <button
              @click="askQuestion"
              :disabled="!question.trim() || loading"
              class="btn btn-primary"
            >
              <span v-if="loading" class="loading loading-spinner"></span>
              Ask
            </button>
          </div>
        </div>

        <!-- Answer Display -->
        <div v-if="answer" class="mt-4 p-4 bg-base-200 rounded-lg">
          <h4 class="font-bold mb-2">Answer:</h4>
          <div class="markdown-content" v-html="renderMarkdown(answer.text)"></div>
          
          <div v-if="answer.sources && answer.sources.length" class="mt-4">
            <h5 class="font-semibold mb-2">Sources:</h5>
            <div class="space-y-2">
              <div
                v-for="(source, idx) in answer.sources"
                :key="idx"
                class="text-sm p-2 bg-base-300 rounded"
              >
                <p class="text-xs text-base-content/50 mb-1">
                  Score: {{ source.score.toFixed(3) }}
                </p>
                <div class="text-xs markdown-content" v-html="renderMarkdown(source.text.substring(0, 200) + '...')"></div>
              </div>
            </div>
          </div>

          <div class="flex gap-2 mt-4">
            <button @click="generateQuiz" class="btn btn-sm btn-outline">
              Generate Quiz
            </button>
            <button @click="exportFlashcards" class="btn btn-sm btn-outline">
              Export Flashcards
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { marked } from 'marked'

// Configure marked for safe rendering
marked.setOptions({
  breaks: true,
  gfm: true,
})

const props = defineProps({
  title: {
    type: String,
    default: 'Untitled Notebook',
  },
  documents: {
    type: Array,
    default: () => [],
  },
  loading: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits([
  'updateTitle',
  'upload',
  'sync',
  'ask',
  'generateQuiz',
  'exportFlashcards',
])

const localTitle = ref(props.title)
const question = ref('')
const useSummary = ref(true)
const answer = ref(null)

watch(() => props.title, (newTitle) => {
  localTitle.value = newTitle
})

const updateTitle = () => {
  if (localTitle.value !== props.title) {
    emit('updateTitle', localTitle.value)
  }
}

const selectDocument = (docId) => {
  console.log('Selected document:', docId)
}

const askQuestion = () => {
  if (!question.value.trim()) return
  
  emit('ask', {
    question: question.value,
    useSummary: useSummary.value,
  })
}

const generateQuiz = () => {
  emit('generateQuiz', { answer: answer.value })
}

const exportFlashcards = () => {
  emit('exportFlashcards', { answer: answer.value })
}

const renderMarkdown = (text) => {
  if (!text) return ''
  return marked.parse(text)
}

// Expose method to set answer from parent
defineExpose({
  setAnswer: (newAnswer) => {
    answer.value = newAnswer
  },
})
</script>

<style scoped>
.markdown-content {
  line-height: 1.7;
}

.markdown-content :deep(p) {
  margin: 0 0 0.75rem 0;
}

.markdown-content :deep(p:last-child) {
  margin-bottom: 0;
}

.markdown-content :deep(strong) {
  font-weight: 700;
  color: hsl(var(--p));
}

.markdown-content :deep(em) {
  font-style: italic;
  opacity: 0.9;
}

.markdown-content :deep(code) {
  background: hsl(var(--b3));
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
}

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
}

.markdown-content :deep(li) {
  margin: 0.25rem 0;
}

.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3),
.markdown-content :deep(h4) {
  font-weight: 600;
  margin: 0.75rem 0 0.5rem 0;
}

.markdown-content :deep(h1) {
  font-size: 1.3rem;
}

.markdown-content :deep(h2) {
  font-size: 1.2rem;
}

.markdown-content :deep(h3) {
  font-size: 1.1rem;
}
</style>
