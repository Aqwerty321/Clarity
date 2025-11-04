<template>
  <div style="min-height: 100vh; background: linear-gradient(135deg, #1a1a2e 0%, #0f0f1e 100%); padding: 2rem; color: white;">
    <h1 style="color: white; font-size: 2rem;">Quiz Page Test</h1>
    <p style="color: white;">If you can see this, the route works!</p>
    <button @click="test" style="padding: 1rem; background: #8bb6ff; border: none; border-radius: 8px; color: white; cursor: pointer;">
      Test Button
    </button>
  </div>
</template>

<script setup>
const test = () => {
  alert('Button works!')
}
</script>
