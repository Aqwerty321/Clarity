<template>
  <div class="flip-card" :class="{ flipped: isFlipped }" @click="flip">
    <div class="flip-card-inner">
      <!-- Front Side -->
      <div class="flip-card-front">
        <div class="card-indicator">Front</div>
        <div class="card-content">
          <p class="card-text">{{ card.front }}</p>
        </div>
        <div class="flip-hint">
          <span class="hint-icon">🔄</span>
          <span>Click to flip</span>
        </div>
      </div>

      <!-- Back Side -->
      <div class="flip-card-back">
        <div class="card-indicator">Back</div>
        <div class="card-content">
          <p class="card-text">{{ card.back }}</p>
        </div>
        <div v-if="showControls" class="difficulty-controls">
          <button
            @click.stop="$emit('rate', 'again')"
            class="difficulty-button again"
          >
            <span class="button-label">Again</span>
            <span class="button-time">< 1 min</span>
          </button>
          <button
            @click.stop="$emit('rate', 'hard')"
            class="difficulty-button hard"
          >
            <span class="button-label">Hard</span>
            <span class="button-time">< 6 min</span>
          </button>
          <button
            @click.stop="$emit('rate', 'good')"
            class="difficulty-button good"
          >
            <span class="button-label">Good</span>
            <span class="button-time">< 10 min</span>
          </button>
          <button
            @click.stop="$emit('rate', 'easy')"
            class="difficulty-button easy"
          >
            <span class="button-label">Easy</span>
            <span class="button-time">4 days</span>
          </button>
        </div>
      </div>
    </div>
    <div class="card-glow"></div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  card: {
    type: Object,
    required: true
  },
  showControls: {
    type: Boolean,
    default: false
  }
})

defineEmits(['rate'])

const isFlipped = ref(false)

const flip = () => {
  isFlipped.value = !isFlipped.value
}

const reset = () => {
  isFlipped.value = false
}

// Expose methods and state for parent component
defineExpose({ 
  reset,
  flip,
  isFlipped
})
</script>

<style scoped>
.flip-card {
  width: 100%;
  max-width: 600px;
  aspect-ratio: 3/2;
  perspective: 1000px;
  cursor: pointer;
  position: relative;
}

.flip-card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  transition: transform 0.6s ease-in-out;
  transform-style: preserve-3d;
}

.flip-card.flipped .flip-card-inner {
  transform: rotateY(180deg);
}

.flip-card-front,
.flip-card-back {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  background: rgba(15, 12, 41, 0.1);
  backdrop-filter: blur(30px);
  -webkit-backdrop-filter: blur(30px);
  border: 1px solid rgba(139, 182, 255, 0.2);
  border-radius: 20px;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  overflow: hidden;
}

.flip-card-back {
  transform: rotateY(180deg);
}

.card-indicator {
  position: absolute;
  top: 1rem;
  right: 1rem;
  padding: 0.375rem 0.75rem;
  background: rgba(139, 182, 255, 0.2);
  border: 1px solid rgba(139, 182, 255, 0.3);
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  color: rgba(200, 220, 255, 0.9);
}

.card-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.card-text {
  font-size: 1.5rem;
  line-height: 1.6;
  color: rgba(200, 220, 255, 0.95);
  text-align: center;
  word-wrap: break-word;
  max-width: 100%;
}

.flip-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  color: rgba(200, 220, 255, 0.6);
  font-size: 0.875rem;
  animation: pulse 2s infinite ease-in-out;
}

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

.hint-icon {
  font-size: 1.125rem;
  animation: rotate 3s infinite ease-in-out;
}

@keyframes rotate {
  0%, 100% { transform: rotateY(0deg); }
  50% { transform: rotateY(180deg); }
}

.difficulty-controls {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.5rem;
  margin-top: auto;
}

.difficulty-button {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  padding: 0.75rem 0.5rem;
  border-radius: 10px;
  border: 1px solid;
  cursor: pointer;
  transition: all 0.3s ease-in-out;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.button-label {
  font-weight: 600;
  font-size: 0.875rem;
}

.button-time {
  font-size: 0.75rem;
  opacity: 0.7;
}

.difficulty-button.again {
  background: rgba(255, 107, 107, 0.15);
  border-color: rgba(255, 107, 107, 0.3);
  color: rgba(255, 150, 150, 0.95);
}

.difficulty-button.again:hover {
  background: rgba(255, 107, 107, 0.25);
  border-color: rgba(255, 107, 107, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(255, 107, 107, 0.3);
}

.difficulty-button.hard {
  background: rgba(255, 178, 107, 0.15);
  border-color: rgba(255, 178, 107, 0.3);
  color: rgba(255, 200, 150, 0.95);
}

.difficulty-button.hard:hover {
  background: rgba(255, 178, 107, 0.25);
  border-color: rgba(255, 178, 107, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(255, 178, 107, 0.3);
}

.difficulty-button.good {
  background: rgba(139, 182, 255, 0.15);
  border-color: rgba(139, 182, 255, 0.3);
  color: rgba(170, 210, 255, 0.95);
}

.difficulty-button.good:hover {
  background: rgba(139, 182, 255, 0.25);
  border-color: rgba(139, 182, 255, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(139, 182, 255, 0.3);
}

.difficulty-button.easy {
  background: rgba(107, 255, 178, 0.15);
  border-color: rgba(107, 255, 178, 0.3);
  color: rgba(150, 255, 200, 0.95);
}

.difficulty-button.easy:hover {
  background: rgba(107, 255, 178, 0.25);
  border-color: rgba(107, 255, 178, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(107, 255, 178, 0.3);
}

.card-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at center, rgba(139, 182, 255, 0.15) 0%, transparent 70%);
  opacity: 0;
  transition: opacity 0.3s ease-in-out;
  pointer-events: none;
  border-radius: 20px;
}

.flip-card:hover .card-glow {
  opacity: 1;
}
</style>
