import { createRouter, createWebHistory } from 'vue-router'
import Home from './pages/Home.vue'
import LoginCallback from './pages/LoginCallback.vue'
import Notebooks from './pages/Notebooks.vue'
import Notebook from './pages/Notebook.vue'
import Flashcards from './pages/Flashcards.vue'
import FlashcardDeck from './pages/FlashcardDeck.vue'
import FlashcardStudy from './pages/FlashcardStudy.vue'
import Quiz from './pages/Quiz.vue'
import MindMaps from './pages/MindMaps.vue'
import MindMap from './pages/MindMap.vue'
import Analytics from './pages/Analytics.vue'
import Marketplace from './pages/Marketplace.vue'
import Settings from './pages/Settings.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
  },
  {
    path: '/callback',
    name: 'LoginCallback',
    component: LoginCallback,
  },
  {
    path: '/notebooks',
    name: 'Notebooks',
    component: Notebooks,
    meta: { requiresAuth: true },
  },
  {
    path: '/notebook/:id',
    name: 'Notebook',
    component: Notebook,
    meta: { requiresAuth: true },
  },
  {
    path: '/flashcards',
    name: 'Flashcards',
    component: Flashcards,
    meta: { requiresAuth: true },
  },
  {
    path: '/flashcard-deck/:id',
    name: 'FlashcardDeck',
    component: FlashcardDeck,
    meta: { requiresAuth: true },
  },
  {
    path: '/flashcard-deck/:id/study',
    name: 'FlashcardStudy',
    component: FlashcardStudy,
    meta: { requiresAuth: true },
  },
  {
    path: '/quiz',
    name: 'Quiz',
    component: Quiz,
    meta: { requiresAuth: true },
  },
  {
    path: '/mind-maps',
    name: 'MindMaps',
    component: MindMaps,
    meta: { requiresAuth: true },
  },
  {
    path: '/mind-maps/:id',
    name: 'MindMap',
    component: MindMap,
    meta: { requiresAuth: true },
  },
  {
    path: '/analytics',
    name: 'Analytics',
    component: Analytics,
    meta: { requiresAuth: true },
  },
  {
    path: '/marketplace',
    name: 'Marketplace',
    component: Marketplace,
    meta: { requiresAuth: true },
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings,
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
