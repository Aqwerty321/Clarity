import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createAuth0 } from '@auth0/auth0-vue'
import App from './App.vue'
import router from './router'
import './style.css'
import './styles/glassmorphism.css'

const app = createApp(App)

// Debug: Log Auth0 configuration
console.log('Auth0 Config:', {
  domain: import.meta.env.VITE_AUTH0_DOMAIN,
  clientId: import.meta.env.VITE_AUTH0_CLIENT_ID,
  callbackUrl: import.meta.env.VITE_AUTH0_CALLBACK_URL,
  audience: import.meta.env.VITE_AUTH0_AUDIENCE,
})

app.use(createPinia())
app.use(router)

const auth0Config = {
  domain: import.meta.env.VITE_AUTH0_DOMAIN,
  clientId: import.meta.env.VITE_AUTH0_CLIENT_ID,
  authorizationParams: {
    redirect_uri: import.meta.env.VITE_AUTH0_CALLBACK_URL || window.location.origin + '/callback',
  },
}

// Only add audience if it's defined
if (import.meta.env.VITE_AUTH0_AUDIENCE) {
  auth0Config.authorizationParams.audience = import.meta.env.VITE_AUTH0_AUDIENCE
}

app.use(createAuth0(auth0Config))

app.mount('#app')
