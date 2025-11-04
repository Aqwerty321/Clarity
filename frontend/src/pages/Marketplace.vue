<template>
  <div class="marketplace-container">
    <QuickNav />
    
    <!-- Header with User Stats -->
    <div class="marketplace-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="page-title">
            <span class="title-icon">🏪</span>
            <span class="title-text">Premium Marketplace</span>
          </h1>
          <p class="subtitle">Unlock exclusive scholarly content with your streak points</p>
        </div>
        
        <div class="user-stats-card">
          <div class="stat-item streak">
            <span class="stat-icon">🔥</span>
            <div class="stat-details">
              <div class="stat-value">{{ userStreak.currentStreak }}</div>
              <div class="stat-label">Day Streak</div>
            </div>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item points">
            <span class="stat-icon">💎</span>
            <div class="stat-details">
              <div class="stat-value">{{ userStreak.availablePoints }}</div>
              <div class="stat-label">Points</div>
            </div>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item best">
            <span class="stat-icon">👑</span>
            <div class="stat-details">
              <div class="stat-value">{{ userStreak.longestStreak }}</div>
              <div class="stat-label">Best Streak</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Filter Tabs -->
      <div class="filter-tabs">
        <button 
          v-for="cat in categories" 
          :key="cat.value"
          @click="selectedCategory = cat.value"
          class="tab-button"
          :class="{ active: selectedCategory === cat.value }"
        >
          <span class="tab-icon">{{ cat.icon }}</span>
          <span>{{ cat.label }}</span>
        </button>
      </div>
    </div>

    <!-- Featured Items Carousel -->
    <div v-if="featuredItems.length > 0 && selectedCategory === 'all'" class="featured-section">
      <h2 class="section-title">⭐ Featured This Week</h2>
      <div class="featured-carousel">
        <div 
          v-for="item in featuredItems" 
          :key="item.id"
          class="featured-card"
          :class="`rarity-${item.rarity}`"
          @click="openItemModal(item)"
        >
          <div class="featured-badge">FEATURED</div>
          <div class="rarity-badge" :class="`rarity-${item.rarity}`">{{ item.rarity.toUpperCase() }}</div>
          <h3 class="featured-title">{{ item.title }}</h3>
          <p class="featured-author">{{ item.author }}</p>
          <p class="featured-description">{{ item.description }}</p>
          <div class="featured-footer">
            <div class="item-price">
              <span class="price-icon">💎</span>
              <span class="price-value">{{ item.price }}</span>
            </div>
            <button class="view-button">View Details →</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Marketplace Grid -->
    <div class="marketplace-content">
      <h2 class="section-title">
        {{ selectedCategory === 'all' ? '🎁 All Items' : categories.find(c => c.value === selectedCategory)?.label }}
      </h2>
      
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p class="loading-text">Loading marketplace...</p>
      </div>
      
      <div v-else-if="filteredItems.length === 0" class="empty-state">
        <div class="empty-icon">📦</div>
        <h3 class="empty-title">No items found</h3>
        <p class="empty-description">Check back later for new content!</p>
      </div>
      
      <div v-else class="items-grid">
        <div 
          v-for="item in filteredItems" 
          :key="item.id"
          class="item-card"
          :class="`rarity-${item.rarity}`"
          @click="openItemModal(item)"
        >
          <div class="rarity-indicator" :class="`rarity-${item.rarity}`"></div>
          <div class="item-header">
            <span class="category-badge">{{ getCategoryIcon(item.category) }} {{ item.category.replace('_', ' ') }}</span>
            <span class="rarity-badge" :class="`rarity-${item.rarity}`">{{ item.rarity }}</span>
          </div>
          
          <h3 class="item-title">{{ item.title }}</h3>
          <p class="item-author">{{ item.author }}</p>
          <p class="item-description">{{ truncate(item.description, 120) }}</p>
          
          <div class="item-meta">
            <span v-if="item.year" class="meta-item">📅 {{ item.year }}</span>
            <span v-if="item.source" class="meta-item">📚 {{ item.source }}</span>
          </div>
          
          <div class="item-footer">
            <div class="item-price">
              <span class="price-icon">💎</span>
              <span class="price-value">{{ item.price }}</span>
            </div>
            <button 
              class="purchase-button"
              :class="{ owned: ownedItems.includes(item.id) }"
              :disabled="ownedItems.includes(item.id)"
            >
              {{ ownedItems.includes(item.id) ? '✓ Owned' : 'View' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Item Detail Modal -->
    <dialog ref="itemModal" class="glass-modal item-modal">
      <div class="modal-content" v-if="selectedItem">
        <button @click="closeItemModal" class="modal-close">✕</button>
        
        <div class="modal-header" :class="`rarity-${selectedItem.rarity}`">
          <div class="modal-rarity-badge" :class="`rarity-${selectedItem.rarity}`">
            {{ selectedItem.rarity.toUpperCase() }}
          </div>
          <h2 class="modal-title">{{ selectedItem.title }}</h2>
          <p class="modal-author">{{ selectedItem.author }}</p>
        </div>
        
        <div class="modal-body">
          <div class="modal-meta-row">
            <span class="meta-tag">{{ getCategoryIcon(selectedItem.category) }} {{ selectedItem.category.replace('_', ' ') }}</span>
            <span v-if="selectedItem.year" class="meta-tag">📅 {{ selectedItem.year }}</span>
            <span v-if="selectedItem.source" class="meta-tag">📚 {{ selectedItem.source }}</span>
          </div>
          
          <p class="modal-description">{{ selectedItem.description }}</p>
          
          <div v-if="selectedItem.previewText" class="preview-section">
            <h3 class="preview-title">📖 Preview</h3>
            <p class="preview-text">{{ selectedItem.previewText }}</p>
          </div>
          
          <div class="modal-footer">
            <div class="price-section">
              <div class="price-display">
                <span class="price-icon">💎</span>
                <span class="price-value">{{ selectedItem.price }} points</span>
              </div>
              <div class="balance-info">
                Your balance: {{ userStreak.availablePoints }} points
              </div>
            </div>
            
            <button 
              v-if="!ownedItems.includes(selectedItem.id)"
              @click="purchaseItem(selectedItem.id)"
              class="purchase-button-large"
              :disabled="userStreak.availablePoints < selectedItem.price || purchasing"
              :class="{ insufficient: userStreak.availablePoints < selectedItem.price }"
            >
              {{ purchasing ? 'Processing...' : userStreak.availablePoints < selectedItem.price ? 'Insufficient Points' : 'Purchase Now' }}
            </button>
            
            <div v-else class="owned-message">
              <span class="owned-icon">✓</span>
              <span>You own this item</span>
            </div>
          </div>
        </div>
      </div>
    </dialog>

    <!-- Purchase Success Modal -->
    <dialog ref="successModal" class="glass-modal success-modal">
      <div class="modal-content">
        <div class="success-animation">
          <div class="success-icon">🎉</div>
        </div>
        <h2 class="success-title">Purchase Successful!</h2>
        <p class="success-message">You've unlocked premium content</p>
        <div class="success-details" v-if="lastPurchase">
          <p class="item-name">{{ lastPurchase.itemTitle }}</p>
          <p class="points-spent">-{{ lastPurchase.pricePaid }} points</p>
          <p class="points-remaining">{{ userStreak.availablePoints }} points remaining</p>
        </div>
        <button @click="closeSuccessModal" class="cta-button">Continue</button>
      </div>
    </dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuth0 } from '@auth0/auth0-vue'
import axios from 'axios'
import QuickNav from '../components/QuickNav.vue'

const auth0 = useAuth0()

const loading = ref(true)
const purchasing = ref(false)
const selectedCategory = ref('all')
const userStreak = ref({
  currentStreak: 0,
  longestStreak: 0,
  availablePoints: 0
})
const allItems = ref([])
const ownedItems = ref([])
const selectedItem = ref(null)
const lastPurchase = ref(null)
const itemModal = ref(null)
const successModal = ref(null)

const categories = [
  { value: 'all', label: 'All Items', icon: '🎁' },
  { value: 'research_paper', label: 'Research Papers', icon: '📄' },
  { value: 'study_guide', label: 'Study Guides', icon: '📚' },
  { value: 'tool', label: 'Tools', icon: '🛠️' },
  { value: 'powerup', label: 'Powerups', icon: '⚡' }
]

const featuredItems = computed(() => {
  return allItems.value.filter(item => item.isFeatured)
})

const filteredItems = computed(() => {
  if (selectedCategory.value === 'all') {
    return allItems.value
  }
  return allItems.value.filter(item => item.category === selectedCategory.value)
})

const getCategoryIcon = (category) => {
  const icons = {
    research_paper: '📄',
    study_guide: '📚',
    tool: '🛠️',
    powerup: '⚡'
  }
  return icons[category] || '📦'
}

const truncate = (text, length) => {
  if (text.length <= length) return text
  return text.substring(0, length) + '...'
}

const loadUserStreak = async () => {
  try {
    const userId = auth0.user.value?.sub || 'anonymous'
    const response = await axios.get(`/api/streak/${userId}`)
    userStreak.value = response.data
  } catch (error) {
    console.error('Failed to load user streak:', error)
  }
}

const loadMarketplace = async () => {
  try {
    const response = await axios.get('/api/marketplace')
    allItems.value = response.data
  } catch (error) {
    console.error('Failed to load marketplace:', error)
  }
}

const loadPurchases = async () => {
  try {
    const userId = auth0.user.value?.sub || 'anonymous'
    const response = await axios.get(`/api/purchases/${userId}`)
    ownedItems.value = response.data.map(p => p.itemId)
  } catch (error) {
    console.error('Failed to load purchases:', error)
  }
}

const openItemModal = (item) => {
  selectedItem.value = item
  itemModal.value?.showModal()
}

const closeItemModal = () => {
  itemModal.value?.close()
  selectedItem.value = null
}

const purchaseItem = async (itemId) => {
  purchasing.value = true
  
  try {
    const userId = auth0.user.value?.sub || 'anonymous'
    const response = await axios.post('/api/marketplace/purchase', null, {
      params: { user_id: userId, item_id: itemId }
    })
    
    if (response.data.success) {
      lastPurchase.value = response.data.purchase
      userStreak.value.availablePoints = response.data.remainingPoints
      ownedItems.value.push(itemId)
      
      closeItemModal()
      successModal.value?.showModal()
    }
  } catch (error) {
    console.error('Purchase failed:', error)
    alert(error.response?.data?.detail || 'Purchase failed')
  } finally {
    purchasing.value = false
  }
}

const closeSuccessModal = () => {
  successModal.value?.close()
  lastPurchase.value = null
}

onMounted(async () => {
  loading.value = true
  await Promise.all([
    loadUserStreak(),
    loadMarketplace(),
    loadPurchases()
  ])
  loading.value = false
})
</script>

<style scoped>
.marketplace-container {
  animation: fadeIn 0.6s ease-in-out;
  padding-left: 10rem;
  min-height: 100vh;
}

@media (max-width: 768px) {
  .marketplace-container {
    padding-left: 1rem;
    padding-top: 6rem;
  }
}

.marketplace-header {
  padding: 2rem;
  margin-bottom: 2rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  gap: 2rem;
  flex-wrap: wrap;
}

.title-section {
  flex: 1;
  min-width: 300px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  background: linear-gradient(135deg, #ffd700, #ffed4e);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.title-icon {
  font-size: 2.5rem;
  filter: drop-shadow(0 4px 8px rgba(255, 215, 0, 0.3));
}

.subtitle {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.7);
}

.user-stats-card {
  display: flex;
  gap: 2rem;
  padding: 1.5rem 2rem;
  background: rgba(15, 12, 41, 0.4);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(139, 182, 255, 0.3);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-icon {
  font-size: 2.5rem;
  filter: drop-shadow(0 4px 8px rgba(255, 215, 0, 0.3));
}

.stat-details {
  text-align: left;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 0.25rem;
}

.stat-item.streak .stat-value {
  background: linear-gradient(135deg, #ff6b6b, #ff8e53);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-item.points .stat-value {
  background: linear-gradient(135deg, #4facfe, #00f2fe);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-item.best .stat-value {
  background: linear-gradient(135deg, #ffd700, #ffed4e);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-label {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.6);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-divider {
  width: 1px;
  height: 50px;
  background: rgba(139, 182, 255, 0.2);
}

.filter-tabs {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.tab-button {
  padding: 0.75rem 1.5rem;
  background: rgba(15, 12, 41, 0.3);
  border: 1px solid rgba(139, 182, 255, 0.2);
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tab-button:hover {
  background: rgba(15, 12, 41, 0.5);
  border-color: rgba(139, 182, 255, 0.4);
  transform: translateY(-2px);
}

.tab-button.active {
  background: rgba(139, 182, 255, 0.2);
  border-color: rgba(139, 182, 255, 0.5);
  color: #8bb6ff;
}

.tab-icon {
  font-size: 1.2rem;
}

.featured-section {
  padding: 0 2rem 2rem;
}

.section-title {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  color: #fff;
}

.featured-carousel {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
}

.featured-card {
  position: relative;
  padding: 2rem;
  background: rgba(15, 12, 41, 0.4);
  backdrop-filter: blur(20px);
  border: 2px solid;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
}

.featured-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #ffd700, #ffed4e, #ffd700);
  background-size: 200% 100%;
  animation: shimmer 3s linear infinite;
}

.featured-card.rarity-legendary {
  border-color: rgba(255, 215, 0, 0.5);
  box-shadow: 0 8px 32px rgba(255, 215, 0, 0.2);
}

.featured-card.rarity-epic {
  border-color: rgba(163, 53, 238, 0.5);
  box-shadow: 0 8px 32px rgba(163, 53, 238, 0.2);
}

.featured-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.4);
}

.featured-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background: linear-gradient(135deg, #ffd700, #ffed4e);
  color: #000;
  font-size: 0.75rem;
  font-weight: 700;
  border-radius: 6px;
  margin-bottom: 1rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.featured-title {
  font-size: 1.4rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  color: #fff;
}

.featured-author {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 1rem;
}

.featured-description {
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.6;
  margin-bottom: 1.5rem;
}

.featured-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.view-button {
  padding: 0.75rem 1.5rem;
  background: rgba(139, 182, 255, 0.2);
  border: 1px solid rgba(139, 182, 255, 0.4);
  border-radius: 12px;
  color: #8bb6ff;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.view-button:hover {
  background: rgba(139, 182, 255, 0.3);
  transform: translateX(4px);
}

.marketplace-content {
  padding: 0 2rem 4rem;
}

.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
}

.item-card {
  position: relative;
  padding: 1.5rem;
  background: rgba(15, 12, 41, 0.4);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(139, 182, 255, 0.2);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
}

.item-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: var(--rarity-color);
  opacity: 0.6;
}

.item-card.rarity-legendary {
  --rarity-color: #ffd700;
}

.item-card.rarity-epic {
  --rarity-color: #a335ee;
}

.item-card.rarity-rare {
  --rarity-color: #0070dd;
}

.item-card.rarity-common {
  --rarity-color: #9d9d9d;
}

.item-card:hover {
  transform: translateY(-4px);
  border-color: rgba(139, 182, 255, 0.4);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.3);
}

.rarity-indicator {
  position: absolute;
  top: 0;
  right: 0;
  width: 60px;
  height: 60px;
  background: var(--rarity-color);
  opacity: 0.1;
  clip-path: polygon(100% 0, 0 0, 100% 100%);
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  gap: 0.5rem;
}

.category-badge {
  padding: 0.25rem 0.75rem;
  background: rgba(139, 182, 255, 0.1);
  border: 1px solid rgba(139, 182, 255, 0.3);
  border-radius: 6px;
  font-size: 0.75rem;
  color: #8bb6ff;
  text-transform: capitalize;
}

.rarity-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 6px;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.rarity-badge.rarity-legendary {
  background: rgba(255, 215, 0, 0.2);
  color: #ffd700;
  border: 1px solid rgba(255, 215, 0, 0.4);
}

.rarity-badge.rarity-epic {
  background: rgba(163, 53, 238, 0.2);
  color: #a335ee;
  border: 1px solid rgba(163, 53, 238, 0.4);
}

.rarity-badge.rarity-rare {
  background: rgba(0, 112, 221, 0.2);
  color: #0070dd;
  border: 1px solid rgba(0, 112, 221, 0.4);
}

.rarity-badge.rarity-common {
  background: rgba(157, 157, 157, 0.2);
  color: #9d9d9d;
  border: 1px solid rgba(157, 157, 157, 0.4);
}

.item-title {
  font-size: 1.2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  color: #fff;
  line-height: 1.3;
}

.item-author {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 0.75rem;
}

.item-description {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.5;
  margin-bottom: 1rem;
}

.item-meta {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.meta-item {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.5);
}

.item-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid rgba(139, 182, 255, 0.1);
}

.item-price {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.price-icon {
  font-size: 1.5rem;
}

.price-value {
  font-size: 1.3rem;
  font-weight: 700;
  background: linear-gradient(135deg, #4facfe, #00f2fe);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.purchase-button {
  padding: 0.5rem 1.25rem;
  background: rgba(139, 182, 255, 0.2);
  border: 1px solid rgba(139, 182, 255, 0.4);
  border-radius: 8px;
  color: #8bb6ff;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.purchase-button:hover:not(:disabled) {
  background: rgba(139, 182, 255, 0.3);
  transform: translateX(4px);
}

.purchase-button.owned {
  background: rgba(119, 221, 119, 0.2);
  border-color: rgba(119, 221, 119, 0.4);
  color: #77dd77;
  cursor: default;
}

.purchase-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Modal Styles */
.item-modal .modal-content {
  max-width: 700px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  position: relative;
  padding: 2rem;
  margin: -2rem -2rem 2rem;
  border-bottom: 1px solid rgba(139, 182, 255, 0.2);
}

.modal-header.rarity-legendary {
  background: linear-gradient(135deg, rgba(255, 215, 0, 0.1), transparent);
}

.modal-header.rarity-epic {
  background: linear-gradient(135deg, rgba(163, 53, 238, 0.1), transparent);
}

.modal-rarity-badge {
  display: inline-block;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 700;
  margin-bottom: 1rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.modal-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  color: #fff;
}

.modal-author {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.6);
}

.modal-body {
  padding: 0 2rem 2rem;
}

.modal-meta-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.meta-tag {
  padding: 0.5rem 1rem;
  background: rgba(139, 182, 255, 0.1);
  border: 1px solid rgba(139, 182, 255, 0.3);
  border-radius: 8px;
  font-size: 0.85rem;
  color: #8bb6ff;
}

.modal-description {
  font-size: 1.05rem;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.8;
  margin-bottom: 2rem;
}

.preview-section {
  padding: 1.5rem;
  background: rgba(15, 12, 41, 0.4);
  border: 1px solid rgba(139, 182, 255, 0.2);
  border-radius: 12px;
  margin-bottom: 2rem;
}

.preview-title {
  font-size: 1.1rem;
  font-weight: 700;
  margin-bottom: 1rem;
  color: #8bb6ff;
}

.preview-text {
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.7;
  font-style: italic;
}

.modal-footer {
  padding-top: 2rem;
  border-top: 1px solid rgba(139, 182, 255, 0.2);
}

.price-section {
  margin-bottom: 1.5rem;
}

.price-display {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.balance-info {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.6);
}

.purchase-button-large {
  width: 100%;
  padding: 1rem 2rem;
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.3), rgba(196, 224, 255, 0.2));
  border: 1px solid rgba(139, 182, 255, 0.5);
  border-radius: 12px;
  color: #8bb6ff;
  font-size: 1.2rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
}

.purchase-button-large:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.4), rgba(196, 224, 255, 0.3));
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(139, 182, 255, 0.3);
}

.purchase-button-large:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.purchase-button-large.insufficient {
  background: rgba(255, 99, 99, 0.2);
  border-color: rgba(255, 99, 99, 0.4);
  color: #ff6363;
}

.owned-message {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 1rem;
  background: rgba(119, 221, 119, 0.2);
  border: 1px solid rgba(119, 221, 119, 0.4);
  border-radius: 12px;
  color: #77dd77;
  font-size: 1.1rem;
  font-weight: 600;
}

.owned-icon {
  font-size: 1.5rem;
}

/* Success Modal */
.success-modal .modal-content {
  text-align: center;
  padding: 3rem;
}

.success-animation {
  margin-bottom: 2rem;
}

.success-icon {
  font-size: 5rem;
  animation: bounce 1s ease-in-out infinite;
}

.success-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 1rem;
  background: linear-gradient(135deg, #77dd77, #98fb98);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.success-message {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 2rem;
}

.success-details {
  padding: 1.5rem;
  background: rgba(15, 12, 41, 0.4);
  border: 1px solid rgba(139, 182, 255, 0.2);
  border-radius: 12px;
  margin-bottom: 2rem;
}

.item-name {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #fff;
}

.points-spent {
  font-size: 1.5rem;
  font-weight: 700;
  color: #ff6b6b;
  margin-bottom: 0.5rem;
}

.points-remaining {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.6);
}

.cta-button {
  padding: 1rem 3rem;
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.3), rgba(196, 224, 255, 0.2));
  border: 1px solid rgba(139, 182, 255, 0.5);
  border-radius: 12px;
  color: #8bb6ff;
  font-size: 1.1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cta-button:hover {
  background: linear-gradient(135deg, rgba(139, 182, 255, 0.4), rgba(196, 224, 255, 0.3));
  transform: translateY(-2px);
}

.loading-container,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.loading-spinner {
  width: 60px;
  height: 60px;
  border: 4px solid rgba(139, 182, 255, 0.2);
  border-top: 4px solid #8bb6ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-text {
  margin-top: 2rem;
  color: rgba(255, 255, 255, 0.7);
  font-size: 1.2rem;
}

.empty-icon {
  font-size: 5rem;
  margin-bottom: 1.5rem;
  opacity: 0.5;
}

.empty-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  color: #fff;
}

.empty-description {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.6);
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
