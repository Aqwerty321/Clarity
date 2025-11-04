<template>
  <div>
    <button
      v-if="!auth0.isAuthenticated.value"
      @click="login"
      class="auth-login-button"
    >
      <span class="button-text">Log In</span>
      <span class="button-icon">→</span>
    </button>
    
    <div v-else class="user-menu">
      <button class="avatar-button" @click="toggleMenu">
        <div class="avatar-container">
          <img
            v-if="auth0.user.value?.picture"
            :src="auth0.user.value.picture"
            :alt="auth0.user.value?.name || 'User'"
            class="avatar-image"
          />
          <div v-else class="avatar-placeholder">
            <span class="avatar-initial">{{ userInitial }}</span>
          </div>
        </div>
        <div class="avatar-glow"></div>
      </button>
      <div v-if="menuOpen" class="dropdown-menu" @click="menuOpen = false">
        <router-link to="/notebooks" class="menu-item">
          <span class="menu-icon">📚</span>
          <span>My Notebooks</span>
        </router-link>
        <button @click="logout" class="menu-item logout">
          <span class="menu-icon">🚪</span>
          <span>Logout</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useAuth0 } from '@auth0/auth0-vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const auth0 = useAuth0()
const router = useRouter()
const userStore = useUserStore()
const menuOpen = ref(false)

const userInitial = computed(() => {
  const name = auth0.user.value?.name
  return name ? name.charAt(0).toUpperCase() : '?'
})

const login = () => {
  auth0.loginWithRedirect()
}

const logout = () => {
  userStore.logout()
  auth0.logout({ logoutParams: { returnTo: window.location.origin } })
}

const toggleMenu = () => {
  menuOpen.value = !menuOpen.value
}
</script>

<style scoped>
.auth-login-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.5rem;
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.2), rgba(168, 216, 255, 0.2));
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(139, 182, 255, 0.3);
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.95);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.4s ease-in-out;
  position: relative;
  overflow: hidden;
}

.auth-login-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  transition: left 0.5s ease-in-out;
}

.auth-login-button:hover::before {
  left: 100%;
}

.auth-login-button:hover {
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.3), rgba(168, 216, 255, 0.3));
  border-color: rgba(139, 182, 255, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(139, 182, 255, 0.3);
}

.button-icon {
  transition: transform 0.3s ease-in-out;
}

.auth-login-button:hover .button-icon {
  transform: translateX(3px);
}

/* User Menu */
.user-menu {
  position: relative;
}

.avatar-button {
  width: 2.75rem;
  height: 2.75rem;
  border-radius: 50%;
  cursor: pointer;
  position: relative;
  background: transparent;
  border: none;
  padding: 0;
  transition: all 0.3s ease-in-out;
}

.avatar-button:hover {
  transform: scale(1.1);
}

.avatar-container {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid rgba(139, 182, 255, 0.3);
  background: rgba(15, 12, 41, 0.5);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  transition: border-color 0.3s ease-in-out;
}

.avatar-button:hover .avatar-container {
  border-color: rgba(139, 182, 255, 0.6);
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.3), rgba(168, 216, 255, 0.3));
}

.avatar-initial {
  font-size: 1.25rem;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.95);
}

.avatar-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 100%;
  height: 100%;
  transform: translate(-50%, -50%);
  border-radius: 50%;
  background: radial-gradient(circle, rgba(139, 182, 255, 0.4) 0%, transparent 70%);
  opacity: 0;
  transition: opacity 0.3s ease-in-out;
  pointer-events: none;
}

.avatar-button:hover .avatar-glow {
  opacity: 1;
}

/* Dropdown Menu */
.dropdown-menu {
  position: absolute;
  top: calc(100% + 0.75rem);
  right: 0;
  min-width: 12rem;
  background: rgba(15, 12, 41, 0.95);
  backdrop-filter: blur(30px);
  -webkit-backdrop-filter: blur(30px);
  border: 1px solid rgba(139, 182, 255, 0.2);
  border-radius: 12px;
  padding: 0.5rem;
  z-index: 50;
  animation: dropdownSlide 0.3s ease-in-out;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
}

@keyframes dropdownSlide {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  color: rgba(200, 220, 255, 0.9);
  text-decoration: none;
  border-radius: 8px;
  transition: all 0.3s ease-in-out;
  cursor: pointer;
  border: none;
  background: transparent;
  width: 100%;
  text-align: left;
  font-size: 0.95rem;
}

.menu-item:hover {
  background: rgba(139, 182, 255, 0.15);
  color: rgba(255, 255, 255, 0.95);
  transform: translateX(4px);
}

.menu-item.logout:hover {
  background: rgba(255, 107, 107, 0.15);
}

.menu-icon {
  font-size: 1.125rem;
}
</style>
