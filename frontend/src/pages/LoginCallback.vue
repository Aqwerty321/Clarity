<template>
  <div class="flex items-center justify-center min-h-[60vh]">
    <div class="text-center">
      <div class="loading loading-spinner loading-lg mb-4"></div>
      <p class="text-xl">Processing authentication...</p>
      <p class="text-sm opacity-70 mt-2">You will be redirected shortly.</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuth0 } from '@auth0/auth0-vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const auth0 = useAuth0()
const router = useRouter()
const userStore = useUserStore()

onMounted(async () => {
  try {
    // Auth0 SDK handles the callback automatically
    // Wait a moment for it to complete
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    if (auth0.isAuthenticated.value) {
      // Get the access token
      const token = await auth0.getAccessTokenSilently()
      userStore.setAccessToken(token)
      userStore.setUser(auth0.user.value)
      
      // Redirect to notebooks
      router.push('/notebooks')
    } else {
      // If not authenticated, go back to home
      router.push('/')
    }
  } catch (error) {
    console.error('Authentication error:', error)
    router.push('/')
  }
})
</script>
