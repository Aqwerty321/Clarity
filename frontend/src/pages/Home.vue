<template>
  <div class="space-y-12">
    <!-- Hero Section -->
    <div class="hero-glass">
      <div class="hero-content">
        <div class="hero-inner">
          <div class="hero-icon">🔍</div>
          <h1 class="hero-title">
            Clarity
          </h1>
          <p class="hero-subtitle">Your Private AI Learning Assistant</p>
          <p class="hero-description">
            Local-first RAG pipeline that runs on your machine. Your documents never leave your computer.
          </p>
          <button
            v-if="!auth0.isAuthenticated.value"
            @click="getStarted"
            class="cta-button"
          >
            <span class="cta-text">Get Started</span>
            <span class="cta-icon">→</span>
          </button>
          <router-link
            v-else
            to="/notebooks"
            class="cta-button"
          >
            <span class="cta-text">Open Notebooks</span>
            <span class="cta-icon">→</span>
          </router-link>
        </div>
      </div>
    </div>

    <!-- Features Section -->
    <div class="features-section">
      <h2 class="section-title">Features</h2>
      <div class="features-grid">
        <div class="feature-card" v-for="(feature, index) in features" :key="index" :style="{ animationDelay: `${index * 0.1}s` }">
          <div class="feature-icon">{{ feature.icon }}</div>
          <h3 class="feature-title">{{ feature.title }}</h3>
          <p class="feature-description">{{ feature.description }}</p>
          <div class="feature-glow"></div>
        </div>
      </div>
    </div>

    <!-- Tech Stack Section -->
    <div class="tech-section">
      <h2 class="section-title">Built With Modern Tech</h2>
      <div class="tech-grid">
        <div class="tech-card" v-for="(tech, index) in techStack" :key="index" :style="{ animationDelay: `${index * 0.15}s` }">
          <div class="tech-icon">{{ tech.icon }}</div>
          <p class="tech-name">{{ tech.name }}</p>
          <p class="tech-category">{{ tech.category }}</p>
          <div class="tech-shine"></div>
        </div>
      </div>
    </div>

    <!-- CTA Section -->
    <div class="cta-section">
      <div class="cta-content">
        <h2 class="cta-title">Ready to Learn Smarter?</h2>
        <p class="cta-description">Start using Clarity today. Free, open-source, and privacy-focused.</p>
        <button
          v-if="!auth0.isAuthenticated.value"
          @click="getStarted"
          class="cta-button cta-button-large"
        >
          <span class="cta-text">Get Started Now</span>
          <span class="cta-icon">✨</span>
        </button>
        <router-link
          v-else
          to="/notebooks"
          class="cta-button cta-button-large"
        >
          <span class="cta-text">Go to Notebooks</span>
          <span class="cta-icon">✨</span>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuth0 } from '@auth0/auth0-vue'

const auth0 = useAuth0()

const features = [
  {
    icon: '🔒',
    title: 'Privacy First',
    description: 'All AI inference happens locally. Your documents stay on your device.'
  },
  {
    icon: '🤖',
    title: 'Smart RAG',
    description: 'Advanced retrieval-augmented generation with local embeddings and vector search.'
  },
  {
    icon: '📚',
    title: 'Document Upload',
    description: 'Upload PDFs, text files, and markdown. Automatic chunking and indexing.'
  },
  {
    icon: '❓',
    title: 'Ask Questions',
    description: 'Query your documents with natural language. Get answers with source citations.'
  },
  {
    icon: '🎓',
    title: 'Quiz Generation',
    description: 'Automatically generate quizzes and flashcards from your learning materials.'
  },
  {
    icon: '🧠',
    title: 'Mind Maps',
    description: 'AI-powered visual knowledge graphs. Interactive mind maps from your notes.'
  },
  {
    icon: '☁️',
    title: 'Optional Sync',
    description: 'Sync notebooks across devices. Your documents stay local; only metadata syncs.'
  }
]

const techStack = [
  { icon: '🖼️', name: 'Vue 3', category: 'Frontend' },
  { icon: '⚡', name: 'FastAPI', category: 'Backend' },
  { icon: '🎨', name: 'ChromaDB', category: 'Vector Store' },
  { icon: '🔐', name: 'Auth0', category: 'Authentication' }
]

const getStarted = () => {
  auth0.loginWithRedirect()
}
</script>

<style scoped>
/* Hero Section */
.hero-glass {
  background: linear-gradient(135deg, 
    rgba(139, 182, 255, 0.05) 0%, 
    rgba(168, 216, 255, 0.05) 100%
  );
  backdrop-filter: blur(30px);
  -webkit-backdrop-filter: blur(30px);
  border: 1px solid rgba(139, 182, 255, 0.2);
  border-radius: 24px;
  padding: 4rem 2rem;
  min-height: 60vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  animation: slideUp 0.8s ease-in-out;
}

.hero-glass::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(139, 182, 255, 0.1) 0%, transparent 70%);
  animation: rotate 20s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.hero-content {
  position: relative;
  z-index: 1;
  text-align: center;
}

.hero-inner {
  max-width: 42rem;
  margin: 0 auto;
}

.hero-icon {
  font-size: 5rem;
  margin-bottom: 1rem;
  animation: bounce 2s infinite ease-in-out;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.hero-title {
  font-size: 4rem;
  font-weight: 800;
  background: linear-gradient(135deg, #8bb6ff, #a8d8ff, #c4e0ff, #8bb6ff);
  background-size: 200% 200%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 1rem;
  animation: gradientShift 4s ease-in-out infinite;
}

@keyframes gradientShift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

.hero-subtitle {
  font-size: 1.75rem;
  color: rgba(200, 220, 255, 0.95);
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.hero-description {
  font-size: 1.125rem;
  color: rgba(200, 220, 255, 0.75);
  margin-bottom: 2rem;
  line-height: 1.6;
}

/* CTA Button */
.cta-button {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 2rem;
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.2), rgba(168, 216, 255, 0.2));
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 2px solid rgba(139, 182, 255, 0.3);
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.95);
  font-size: 1.125rem;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.4s ease-in-out;
  position: relative;
  overflow: hidden;
}

.cta-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  transition: left 0.5s ease-in-out;
}

.cta-button:hover::before {
  left: 100%;
}

.cta-button:hover {
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.3), rgba(168, 216, 255, 0.3));
  border-color: rgba(139, 182, 255, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 15px 40px rgba(139, 182, 255, 0.3);
}

.cta-button:active {
  transform: translateY(0);
}

.cta-icon {
  font-size: 1.25rem;
  transition: transform 0.4s ease-in-out;
}

.cta-button:hover .cta-icon {
  transform: translateX(4px);
}

/* Section Title */
.section-title {
  font-size: 2.5rem;
  font-weight: 700;
  text-align: center;
  margin-bottom: 3rem;
  background: linear-gradient(135deg, #8bb6ff, #c4e0ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: fadeIn 0.6s ease-in-out;
}

/* Features Section */
.features-section {
  animation: fadeIn 0.8s ease-in-out;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.feature-card {
  background: rgba(15, 12, 41, 0.1);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(139, 182, 255, 0.15);
  border-radius: 16px;
  padding: 2rem;
  position: relative;
  overflow: hidden;
  transition: all 0.4s ease-in-out;
  animation: slideUp 0.6s ease-in-out both;
}

.feature-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(139, 182, 255, 0.5), transparent);
  transform: translateX(-100%);
  transition: transform 0.6s ease-in-out;
}

.feature-card:hover::before {
  transform: translateX(100%);
}

.feature-card:hover {
  background: rgba(15, 12, 41, 0.15);
  border-color: rgba(139, 182, 255, 0.3);
  transform: translateY(-8px);
  box-shadow: 0 20px 60px rgba(139, 182, 255, 0.2);
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  animation: pulse 2s infinite ease-in-out;
}

.feature-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: rgba(200, 220, 255, 0.95);
  margin-bottom: 0.75rem;
}

.feature-description {
  color: rgba(200, 220, 255, 0.7);
  line-height: 1.6;
}

.feature-glow {
  position: absolute;
  bottom: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(139, 182, 255, 0.1) 0%, transparent 70%);
  opacity: 0;
  transition: opacity 0.4s ease-in-out;
}

.feature-card:hover .feature-glow {
  opacity: 1;
}

/* Tech Stack Section */
.tech-section {
  animation: fadeIn 1s ease-in-out;
}

.tech-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.tech-card {
  background: rgba(15, 12, 41, 0.1);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(139, 182, 255, 0.15);
  border-radius: 16px;
  padding: 2rem;
  text-align: center;
  position: relative;
  overflow: hidden;
  transition: all 0.4s ease-in-out;
  animation: slideUp 0.6s ease-in-out both;
}

.tech-card:hover {
  background: rgba(15, 12, 41, 0.15);
  border-color: rgba(139, 182, 255, 0.3);
  transform: translateY(-6px) scale(1.05);
  box-shadow: 0 15px 50px rgba(139, 182, 255, 0.2);
}

.tech-icon {
  font-size: 3.5rem;
  margin-bottom: 1rem;
  animation: rotate3d 3s infinite ease-in-out;
}

@keyframes rotate3d {
  0%, 100% { transform: rotateY(0deg); }
  50% { transform: rotateY(180deg); }
}

.tech-name {
  font-size: 1.25rem;
  font-weight: 600;
  color: rgba(200, 220, 255, 0.95);
  margin-bottom: 0.25rem;
}

.tech-category {
  font-size: 0.875rem;
  color: rgba(200, 220, 255, 0.6);
}

.tech-shine {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.05), transparent);
  transform: rotate(45deg);
  transition: all 0.5s ease-in-out;
}

.tech-card:hover .tech-shine {
  left: 100%;
}

/* CTA Section */
.cta-section {
  background: linear-gradient(135deg, 
    rgba(139, 182, 255, 0.05) 0%, 
    rgba(168, 216, 255, 0.05) 100%
  );
  backdrop-filter: blur(30px);
  -webkit-backdrop-filter: blur(30px);
  border: 1px solid rgba(139, 182, 255, 0.2);
  border-radius: 24px;
  padding: 4rem 2rem;
  text-align: center;
  position: relative;
  overflow: hidden;
  animation: slideUp 1.2s ease-in-out;
}

.cta-section::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(139, 182, 255, 0.1) 0%, transparent 70%);
  animation: rotate 20s linear infinite;
}

.cta-content {
  position: relative;
  z-index: 1;
}

.cta-title {
  font-size: 2.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, #8bb6ff, #c4e0ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 1rem;
}

.cta-description {
  font-size: 1.125rem;
  color: rgba(200, 220, 255, 0.8);
  margin-bottom: 2rem;
}

.cta-button-large {
  font-size: 1.25rem;
  padding: 1.25rem 2.5rem;
}
</style>
