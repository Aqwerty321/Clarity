import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const accessToken = ref(null)
  const notebooks = ref([])
  const currentNotebook = ref(null)

  const isAuthenticated = computed(() => !!user.value)

  function setUser(userData) {
    user.value = userData
  }

  function setAccessToken(token) {
    accessToken.value = token
    if (token) {
      localStorage.setItem('clarity_access_token', token)
    } else {
      localStorage.removeItem('clarity_access_token')
    }
  }

  function setNotebooks(notebookList) {
    notebooks.value = notebookList
  }

  function addNotebook(notebook) {
    notebooks.value.push(notebook)
  }

  function updateNotebook(id, updates) {
    const index = notebooks.value.findIndex(n => n.id === id)
    if (index !== -1) {
      notebooks.value[index] = { ...notebooks.value[index], ...updates }
    }
  }

  function deleteNotebook(id) {
    notebooks.value = notebooks.value.filter(n => n.id !== id)
  }

  function setCurrentNotebook(notebook) {
    currentNotebook.value = notebook
  }

  function logout() {
    user.value = null
    accessToken.value = null
    notebooks.value = []
    currentNotebook.value = null
    localStorage.clear()
  }

  // Initialize from localStorage
  const storedToken = localStorage.getItem('clarity_access_token')
  if (storedToken) {
    accessToken.value = storedToken
  }

  return {
    user,
    accessToken,
    notebooks,
    currentNotebook,
    isAuthenticated,
    setUser,
    setAccessToken,
    setNotebooks,
    addNotebook,
    updateNotebook,
    deleteNotebook,
    setCurrentNotebook,
    logout,
  }
})
