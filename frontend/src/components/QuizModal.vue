<template>
  <dialog ref="modal" class="modal" :class="{ 'modal-open': modelValue }">
    <div class="modal-box w-11/12 max-w-3xl">
      <h3 class="font-bold text-lg mb-4">{{ quiz?.title || 'Quiz' }}</h3>
      
      <div v-if="quiz?.questions && quiz.questions.length" class="space-y-6">
        <div
          v-for="(q, idx) in quiz.questions"
          :key="idx"
          class="p-4 bg-base-200 rounded-lg"
        >
          <div class="flex items-start justify-between mb-3">
            <div class="font-semibold flex-1 markdown-content" v-html="`${idx + 1}. ` + renderMarkdown(q.question)"></div>
            <button
              v-if="!reviewMode && q.hint && !showAnswers"
              @click="toggleHint(idx)"
              class="btn btn-xs btn-ghost tooltip tooltip-left"
              data-tip="Show hint"
            >
              💡
            </button>
          </div>

          <!-- Hint -->
          <div
            v-if="showHints[idx] && q.hint && !showAnswers"
            class="mb-3 p-2 bg-info/10 text-info rounded text-sm"
          >
            <strong>Hint:</strong> <span class="markdown-content" v-html="renderMarkdown(q.hint)"></span>
          </div>
          
          <div class="space-y-2">
            <div
              v-for="(option, optIdx) in q.options"
              :key="optIdx"
              @click="showAnswers ? inspectOption(idx, optIdx) : null"
              class="flex items-start gap-2 p-3 rounded border-2 transition-all"
              :class="{
                // Correct answer styling
                'bg-success/20 border-success cursor-default': showAnswers && optIdx === q.correctAnswer,
                // User's wrong answer
                'bg-error/20 border-error cursor-default': showAnswers && optIdx === answers[idx] && optIdx !== q.correctAnswer,
                // Other wrong options (clickable to see explanation)
                'border-base-300 hover:border-warning hover:bg-warning/5 cursor-pointer': showAnswers && optIdx !== q.correctAnswer && optIdx !== answers[idx],
                // Not submitted yet
                'border-base-300 hover:bg-base-300 cursor-pointer': !showAnswers
              }"
            >
              <input
                v-model="answers[idx]"
                type="radio"
                :name="`question-${idx}`"
                :value="optIdx"
                class="radio radio-primary mt-0.5 flex-shrink-0"
                :disabled="showAnswers"
              />
              <div class="flex-1">
                <span :class="{ 'font-semibold': showAnswers && optIdx === q.correctAnswer }">
                  {{ option }}
                </span>
                
                <!-- Show icon for clickable wrong answers -->
                <span v-if="showAnswers && optIdx !== q.correctAnswer && q.incorrectExplanations && q.incorrectExplanations[optIdx]" class="ml-2 text-xs opacity-60">
                  (click to see why)
                </span>
              </div>
            </div>
          </div>

          <!-- Answer feedback -->
          <div
            v-if="showAnswers && q.correctAnswer !== undefined"
            class="mt-3 space-y-2"
          >
            <div
              class="p-2 rounded"
              :class="answers[idx] === q.correctAnswer ? 'bg-success/20 text-success' : 'bg-error/20 text-error'"
            >
              <p v-if="answers[idx] === q.correctAnswer" class="font-semibold">✓ Correct!</p>
              <p v-else class="font-semibold">✗ Incorrect. The correct answer is: {{ q.options[q.correctAnswer] }}</p>
              <div v-if="q.explanation" class="text-sm mt-1 opacity-80 markdown-content">
                <strong>Explanation:</strong> <span v-html="renderMarkdown(q.explanation)"></span>
              </div>
            </div>

            <!-- Show why the inspected option is wrong -->
            <div
              v-if="inspectedOptions[idx] !== undefined && inspectedOptions[idx] !== q.correctAnswer && q.incorrectExplanations && q.incorrectExplanations[inspectedOptions[idx]]"
              class="p-2 bg-warning/10 border border-warning rounded text-sm"
            >
              <div class="flex items-start gap-2">
                <span class="text-lg">💡</span>
                <div>
                  <p class="font-semibold mb-1">Why "{{ q.options[inspectedOptions[idx]] }}" is incorrect:</p>
                  <div class="markdown-content" v-html="renderMarkdown(q.incorrectExplanations[inspectedOptions[idx]])"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="text-center py-8 text-base-content/50">
        No quiz available
      </div>

      <div class="modal-action">
        <button
          v-if="!reviewMode && !showAnswers"
          @click="submitQuiz"
          class="btn btn-primary"
          :disabled="!allAnswered"
        >
          Submit
        </button>
        <button
          v-if="!reviewMode && showAnswers"
          @click="resetQuiz"
          class="btn btn-ghost"
        >
          Try Again
        </button>
        <button @click="close" class="btn">Close</button>
      </div>
    </div>
    <form method="dialog" class="modal-backdrop">
      <button @click="close">close</button>
    </form>
  </dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { marked } from 'marked'

// Configure marked for safe rendering
marked.setOptions({
  breaks: true,
  gfm: true,
})

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  quiz: {
    type: Object,
    default: () => ({ questions: [] }),
  },
  reviewMode: {
    type: Boolean,
    default: false, // Default to quiz mode (interactive)
  },
})

const emit = defineEmits(['update:modelValue', 'submit'])

const modal = ref(null)
const answers = ref({})
const showAnswers = ref(false)
const showHints = ref({})
const inspectedOptions = ref({})

const allAnswered = computed(() => {
  if (!props.quiz?.questions) return false
  const questionCount = props.quiz.questions.length
  return Object.keys(answers.value).length === questionCount
})

const toggleHint = (idx) => {
  showHints.value[idx] = !showHints.value[idx]
}

const inspectOption = (questionIdx, optionIdx) => {
  // Toggle inspection of the clicked option
  if (inspectedOptions.value[questionIdx] === optionIdx) {
    inspectedOptions.value[questionIdx] = undefined
  } else {
    inspectedOptions.value[questionIdx] = optionIdx
  }
}

watch(() => props.modelValue, (isOpen) => {
  if (isOpen) {
    if (props.reviewMode) {
      // In review mode, show user's actual submitted answers
      initializeReviewMode()
    } else {
      // In quiz mode, start fresh
      resetQuiz()
    }
  }
})

const initializeReviewMode = () => {
  // Pre-fill with user's actual submitted answers (not correct answers)
  answers.value = {}
  if (props.quiz?.userAnswers) {
    // Use the user's actual answers from their attempt
    answers.value = { ...props.quiz.userAnswers }
  } else if (props.quiz?.questions) {
    // Fallback: if no user answers, show empty (they haven't attempted yet)
    props.quiz.questions.forEach((q, idx) => {
      answers.value[idx] = undefined
    })
  }
  showAnswers.value = true
  showHints.value = {}
  inspectedOptions.value = {}
}

const submitQuiz = () => {
  showAnswers.value = true
  const { score, correctCount } = calculateScore()
  emit('submit', { answers: answers.value, score, correctCount })
}

const calculateScore = () => {
  if (!props.quiz?.questions || props.quiz.questions.length === 0) return { score: 0, correctCount: 0 }
  
  let correct = 0
  props.quiz.questions.forEach((q, idx) => {
    if (answers.value[idx] === q.correctAnswer) {
      correct++
    }
  })
  
  return {
    score: (correct / props.quiz.questions.length) * 100,
    correctCount: correct
  }
}

const resetQuiz = () => {
  answers.value = {}
  showAnswers.value = false
  showHints.value = {}
  inspectedOptions.value = {}
}

const renderMarkdown = (text) => {
  if (!text) return ''
  return marked.parse(text)
}

const close = () => {
  emit('update:modelValue', false)
}
</script>

<style scoped>
/* Ensure modal is above all other elements */
.modal {
  z-index: 300 !important;
}

.modal-backdrop {
  z-index: 299 !important;
}

.modal-box {
  z-index: 301 !important;
  position: relative;
}

.markdown-content {
  display: inline;
  line-height: 1.6;
}

.markdown-content :deep(p) {
  display: inline;
  margin: 0;
}

.markdown-content :deep(strong) {
  font-weight: 700;
}

.markdown-content :deep(em) {
  font-style: italic;
}

.markdown-content :deep(code) {
  background: hsl(var(--b3));
  padding: 0.15rem 0.3rem;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
}

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  margin: 0.25rem 0;
  padding-left: 1.5rem;
}

.markdown-content :deep(li) {
  margin: 0.15rem 0;
}
</style>
