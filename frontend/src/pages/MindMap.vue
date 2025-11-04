<template>
  <div class="mind-map-page">
    <!-- Header -->
    <div class="page-header">
      <button @click="router.back()" class="back-button">
        <span class="button-icon">←</span>
        Back
      </button>
      
      <div class="header-content">
        <h1 class="page-title">{{ mindMap?.title || 'Loading...' }}</h1>
        <p v-if="mindMap?.description" class="page-subtitle">{{ mindMap.description }}</p>
      </div>

      <div class="header-actions">
        <button @click="resetZoom" class="action-button" title="Reset View">
          <span>🎯</span>
        </button>
        <button @click="togglePhysics" class="action-button" :class="{ active: physicsEnabled }">
          <span>{{ physicsEnabled ? '⚡' : '⏸️' }}</span>
        </button>
        <button @click="exportImage" class="action-button" title="Export">
          <span>📸</span>
        </button>
      </div>
    </div>

    <!-- Mind Map Canvas -->
    <div class="map-container">
      <!-- Cosmic Background -->
      <div class="cosmic-background">
        <div class="stars"></div>
        <div class="nebula nebula-1"></div>
        <div class="nebula nebula-2"></div>
        <div class="nebula nebula-3"></div>
      </div>
      
      <div ref="mapCanvas" class="map-canvas"></div>
      
      <!-- Legend -->
      <div class="map-legend glass-panel">
        <div class="legend-title">Legend</div>
        <div class="legend-items">
          <div class="legend-item">
            <div class="legend-node level-0"></div>
            <span>Main Topic</span>
          </div>
          <div class="legend-item">
            <div class="legend-node level-1"></div>
            <span>Subtopic</span>
          </div>
          <div class="legend-item">
            <div class="legend-node level-2"></div>
            <span>Detail</span>
          </div>
        </div>
      </div>

      <!-- Detail Panel -->
      <div v-if="selectedNode" class="detail-panel glass-panel">
        <div class="detail-header">
          <div class="detail-title-section">
            <h2>{{ selectedNode.label }}</h2>
            <span class="detail-badge">{{ nodeDetails?.source || 'loading' }}</span>
          </div>
          <button @click="closeDetails" class="close-btn">✕</button>
        </div>
        
        <div class="detail-body">
          <!-- Loading State -->
          <div v-if="loadingDetails" class="detail-loading">
            <div class="loading-spinner-small"></div>
            <p>Loading details...</p>
          </div>

          <!-- Content -->
          <div v-else-if="nodeDetails" class="detail-content">
            <!-- Summary -->
            <div class="detail-section">
              <h3 class="section-title">
                <span class="section-icon">📝</span>
                Summary
              </h3>
              <div class="summary-text markdown-content" v-html="renderMarkdown(nodeDetails.summary || 'No summary available')"></div>
            </div>

            <!-- Stats -->
            <div class="detail-section detail-stats">
              <div class="stat-card">
                <span class="stat-icon">📊</span>
                <div class="stat-info">
                  <span class="stat-label">Level</span>
                  <span class="stat-value">{{ selectedNode.depth }}</span>
                </div>
              </div>
              <div class="stat-card">
                <span class="stat-icon">🔗</span>
                <div class="stat-info">
                  <span class="stat-label">Links</span>
                  <span class="stat-value">{{ selectedNode.connections || 0 }}</span>
                </div>
              </div>
              <div class="stat-card">
                <span class="stat-icon">📚</span>
                <div class="stat-info">
                  <span class="stat-label">Sources</span>
                  <span class="stat-value">{{ nodeDetails.details?.length || 0 }}</span>
                </div>
              </div>
            </div>

            <!-- Detailed Content from Document -->
            <div v-if="nodeDetails.details && nodeDetails.details.length > 0" class="detail-section">
              <h3 class="section-title">
                <span class="section-icon">📖</span>
                Content from Document
              </h3>
              <div class="content-chunks">
                <div 
                  v-for="(detail, index) in nodeDetails.details" 
                  :key="index"
                  class="content-chunk"
                  :class="{ 'high-relevance': detail.relevance > 0.8 }"
                >
                  <div class="chunk-header">
                    <span class="chunk-source">{{ detail.source }}</span>
                    <span v-if="detail.page" class="chunk-page">Page {{ detail.page }}</span>
                    <span class="relevance-badge" :style="{ opacity: detail.relevance }">
                      {{ Math.round(detail.relevance * 100) }}% relevant
                    </span>
                  </div>
                  <div class="chunk-content markdown-content" v-html="renderMarkdown(detail.content)"></div>
                </div>
              </div>
            </div>

            <!-- No detailed content -->
            <div v-else class="detail-section no-content">
              <p>💡 This node was generated by AI. No source document content available.</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading Overlay -->
      <div v-if="loading" class="loading-overlay">
        <div class="loading-spinner"></div>
        <p>Generating mind map...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuth0 } from '@auth0/auth0-vue'
import axios from 'axios'
import * as d3 from 'd3'
import { marked } from 'marked'

const router = useRouter()
const route = useRoute()
const auth0 = useAuth0()

// Configure marked for safe rendering
marked.setOptions({
  breaks: true,
  gfm: true,
})

const mindMap = ref(null)
const mapCanvas = ref(null)
const loading = ref(true)
const selectedNode = ref(null)
const nodeDetails = ref(null)
const loadingDetails = ref(false)
const physicsEnabled = ref(true)

let simulation = null
let svg = null
let g = null

const loadMindMap = async () => {
  try {
    const userId = auth0.user.value?.sub || 'anonymous'
    const response = await axios.get(`/api/mind-maps/${route.params.id}?user_id=${userId}`)
    mindMap.value = response.data
    
    console.log('Loaded mind map:', mindMap.value)
    
    // Initialize visualization after data loads
    await initVisualization()
  } catch (error) {
    console.error('Failed to load mind map:', error)
    alert('Failed to load mind map: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const loadNodeDetails = async (node) => {
  selectedNode.value = node
  nodeDetails.value = null
  loadingDetails.value = true

  try {
    const userId = auth0.user.value?.sub || 'anonymous'
    const response = await axios.get(
      `/api/mind-maps/${route.params.id}/node-details/${node.id}?user_id=${userId}`
    )
    nodeDetails.value = response.data
    console.log('Loaded node details:', nodeDetails.value)
  } catch (error) {
    console.error('Failed to load node details:', error)
    // Fallback to basic node info
    nodeDetails.value = {
      node_id: node.id,
      label: node.label,
      summary: node.content || 'No details available',
      details: [],
      source: 'generated'
    }
  } finally {
    loadingDetails.value = false
  }
}

const closeDetails = () => {
  selectedNode.value = null
  nodeDetails.value = null
  loadingDetails.value = false
}

const renderMarkdown = (text) => {
  if (!text) return ''
  return marked.parse(text)
}

const initVisualization = async () => {
  if (!mapCanvas.value || !mindMap.value?.nodes) return

  const container = mapCanvas.value
  const width = container.clientWidth
  const height = container.clientHeight

  // Clear existing SVG
  d3.select(container).selectAll('*').remove()

  // Create SVG
  svg = d3.select(container)
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .style('background', 'transparent')

  // Add definitions for gradients and glows
  const defs = svg.append('defs')
  
  // Glow filter
  const filter = defs.append('filter')
    .attr('id', 'glow')
    .attr('x', '-50%')
    .attr('y', '-50%')
    .attr('width', '200%')
    .attr('height', '200%')
  
  filter.append('feGaussianBlur')
    .attr('stdDeviation', '4')
    .attr('result', 'coloredBlur')
  
  const feMerge = filter.append('feMerge')
  feMerge.append('feMergeNode').attr('in', 'coloredBlur')
  feMerge.append('feMergeNode').attr('in', 'SourceGraphic')

  // Add zoom behavior
  const zoom = d3.zoom()
    .scaleExtent([0.1, 4])
    .on('zoom', (event) => {
      g.attr('transform', event.transform)
    })

  svg.call(zoom)

  // Create main group
  g = svg.append('g')

  // Prepare data
  const nodes = mindMap.value.nodes.map(node => ({
    ...node,
    x: width / 2 + (Math.random() - 0.5) * 200,
    y: height / 2 + (Math.random() - 0.5) * 200
  }))

  const links = mindMap.value.edges.map(edge => ({
    source: edge.from,
    target: edge.to,
    label: edge.label
  }))

  // Create force simulation
  simulation = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(links).id(d => d.id).distance(150))
    .force('charge', d3.forceManyBody().strength(-300))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide().radius(60))

  // Draw links
  const link = g.append('g')
    .selectAll('line')
    .data(links)
    .join('line')
    .attr('class', 'link')
    .attr('stroke', 'rgba(139, 182, 255, 0.3)')
    .attr('stroke-width', 2)
    .style('filter', 'url(#glow)')

  // Draw link labels
  const linkLabel = g.append('g')
    .selectAll('text')
    .data(links)
    .join('text')
    .attr('class', 'link-label')
    .attr('text-anchor', 'middle')
    .attr('fill', 'rgba(255, 255, 255, 0.6)')
    .attr('font-size', '10px')
    .text(d => d.label || '')

  // Draw nodes
  const node = g.append('g')
    .selectAll('g')
    .data(nodes)
    .join('g')
    .attr('class', 'node')
    .call(drag(simulation))
    .on('click', async (event, d) => {
      event.stopPropagation()
      await loadNodeDetails(d)
    })

  // Node circles
  node.append('circle')
    .attr('r', d => 30 + d.depth * 5)
    .attr('fill', d => getNodeColor(d.depth))
    .attr('stroke', d => getNodeStroke(d.depth))
    .attr('stroke-width', 3)
    .style('filter', 'url(#glow)')
    .style('cursor', 'pointer')
    .on('mouseenter', function() {
      d3.select(this)
        .transition()
        .duration(200)
        .attr('r', d => 35 + d.depth * 5)
    })
    .on('mouseleave', function() {
      d3.select(this)
        .transition()
        .duration(200)
        .attr('r', d => 30 + d.depth * 5)
    })

  // Node labels
  node.append('text')
    .attr('text-anchor', 'middle')
    .attr('dy', '0.35em')
    .attr('fill', 'rgba(255, 255, 255, 0.95)')
    .attr('font-size', '12px')
    .attr('font-weight', '600')
    .attr('pointer-events', 'none')
    .text(d => truncateText(d.label, 15))
    .each(function(d) {
      const text = d3.select(this)
      const words = d.label.split(' ')
      if (words.length > 2) {
        text.text('')
        const tspan1 = text.append('tspan')
          .attr('x', 0)
          .attr('dy', '-0.3em')
          .text(words.slice(0, 2).join(' '))
        const tspan2 = text.append('tspan')
          .attr('x', 0)
          .attr('dy', '1.2em')
          .text(words.slice(2).join(' ').substring(0, 15))
      }
    })

  // Update positions on tick
  simulation.on('tick', () => {
    link
      .attr('x1', d => d.source.x)
      .attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x)
      .attr('y2', d => d.target.y)

    linkLabel
      .attr('x', d => (d.source.x + d.target.x) / 2)
      .attr('y', d => (d.source.y + d.target.y) / 2)

    node.attr('transform', d => `translate(${d.x},${d.y})`)
  })

  // Initial zoom to fit
  setTimeout(() => {
    const bounds = g.node().getBBox()
    const fullWidth = width
    const fullHeight = height
    const midX = bounds.x + bounds.width / 2
    const midY = bounds.y + bounds.height / 2
    const scale = 0.8 / Math.max(bounds.width / fullWidth, bounds.height / fullHeight)
    const translate = [fullWidth / 2 - scale * midX, fullHeight / 2 - scale * midY]

    svg.transition()
      .duration(750)
      .call(zoom.transform, d3.zoomIdentity.translate(translate[0], translate[1]).scale(scale))
  }, 100)
}

const getNodeColor = (depth) => {
  const colors = [
    'rgba(139, 182, 255, 0.4)',
    'rgba(196, 224, 255, 0.4)',
    'rgba(168, 216, 255, 0.4)',
    'rgba(180, 200, 255, 0.4)',
  ]
  return colors[Math.min(depth, colors.length - 1)]
}

const getNodeStroke = (depth) => {
  const strokes = [
    'rgba(139, 182, 255, 0.9)',
    'rgba(196, 224, 255, 0.9)',
    'rgba(168, 216, 255, 0.9)',
    'rgba(180, 200, 255, 0.9)',
  ]
  return strokes[Math.min(depth, strokes.length - 1)]
}

const truncateText = (text, maxLength) => {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

const drag = (simulation) => {
  const dragstarted = (event, d) => {
    if (!event.active) simulation.alphaTarget(0.3).restart()
    d.fx = d.x
    d.fy = d.y
  }

  const dragged = (event, d) => {
    d.fx = event.x
    d.fy = event.y
  }

  const dragended = (event, d) => {
    if (!event.active) simulation.alphaTarget(0)
    d.fx = null
    d.fy = null
  }

  return d3.drag()
    .on('start', dragstarted)
    .on('drag', dragged)
    .on('end', dragended)
}

const resetZoom = () => {
  if (!svg) return
  const width = mapCanvas.value.clientWidth
  const height = mapCanvas.value.clientHeight
  
  svg.transition()
    .duration(750)
    .call(d3.zoom().transform, d3.zoomIdentity.translate(width / 2, height / 2).scale(1))
}

const togglePhysics = () => {
  physicsEnabled.value = !physicsEnabled.value
  if (simulation) {
    if (physicsEnabled.value) {
      simulation.alphaTarget(0.3).restart()
    } else {
      simulation.stop()
    }
  }
}

const exportImage = () => {
  if (!svg) return
  
  const svgElement = mapCanvas.value.querySelector('svg')
  const serializer = new XMLSerializer()
  const svgString = serializer.serializeToString(svgElement)
  const blob = new Blob([svgString], { type: 'image/svg+xml' })
  const url = URL.createObjectURL(blob)
  
  const link = document.createElement('a')
  link.href = url
  link.download = `${mindMap.value?.title || 'mind-map'}.svg`
  link.click()
  
  URL.revokeObjectURL(url)
}

onMounted(() => {
  loadMindMap()
  
  // Handle window resize
  window.addEventListener('resize', () => {
    if (mindMap.value) {
      initVisualization()
    }
  })
})

onBeforeUnmount(() => {
  if (simulation) {
    simulation.stop()
  }
})
</script>

<style scoped>
.mind-map-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* Animated background */
.mind-map-page::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 30% 40%, rgba(139, 182, 255, 0.08) 0%, transparent 50%),
              radial-gradient(circle at 70% 60%, rgba(196, 224, 255, 0.08) 0%, transparent 50%);
  animation: pulse 15s ease-in-out infinite;
  pointer-events: none;
}

@keyframes pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

/* Header */
.page-header {
  display: flex;
  align-items: center;
  gap: 2rem;
  padding: 1.5rem 2rem;
  background: rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
  z-index: 10;
}

.back-button {
  padding: 0.75rem 1.5rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.back-button:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateX(-4px);
  border-color: rgba(139, 182, 255, 0.4);
}

.button-icon {
  font-size: 1.2rem;
}

.header-content {
  flex: 1;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.95);
  margin: 0 0 0.25rem 0;
  text-shadow: 0 0 20px rgba(139, 182, 255, 0.4);
}

.page-subtitle {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

.action-button {
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 1.5rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.action-button:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(139, 182, 255, 0.4);
  transform: scale(1.1);
  box-shadow: 0 8px 24px rgba(139, 182, 255, 0.3);
}

.action-button.active {
  background: rgba(139, 182, 255, 0.2);
  border-color: rgba(139, 182, 255, 0.5);
}

/* Map Container */
.map-container {
  flex: 1;
  position: relative;
  overflow: hidden;
}

/* Cosmic Background */
.cosmic-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  pointer-events: none;
}

/* Twinkling Stars */
.stars {
  position: absolute;
  width: 100%;
  height: 100%;
  background-image: 
    radial-gradient(2px 2px at 20% 30%, rgba(255, 255, 255, 0.9), transparent),
    radial-gradient(2px 2px at 60% 70%, rgba(255, 255, 255, 0.8), transparent),
    radial-gradient(1px 1px at 50% 50%, rgba(255, 255, 255, 0.7), transparent),
    radial-gradient(1px 1px at 80% 10%, rgba(255, 255, 255, 0.9), transparent),
    radial-gradient(2px 2px at 90% 60%, rgba(255, 255, 255, 0.8), transparent),
    radial-gradient(1px 1px at 33% 80%, rgba(255, 255, 255, 0.7), transparent),
    radial-gradient(1px 1px at 15% 90%, rgba(255, 255, 255, 0.8), transparent),
    radial-gradient(2px 2px at 70% 20%, rgba(196, 224, 255, 0.9), transparent),
    radial-gradient(1px 1px at 40% 60%, rgba(196, 224, 255, 0.7), transparent),
    radial-gradient(1px 1px at 25% 45%, rgba(255, 255, 255, 0.8), transparent);
  background-size: 200% 200%, 180% 180%, 220% 220%, 190% 190%, 210% 210%, 
                   230% 230%, 200% 200%, 240% 240%, 220% 220%, 210% 210%;
  background-position: 0% 0%, 0% 0%, 0% 0%, 0% 0%, 0% 0%, 0% 0%, 0% 0%, 0% 0%, 0% 0%, 0% 0%;
  animation: 
    twinkle1 4s ease-in-out infinite,
    drift1 120s linear infinite;
}

@keyframes twinkle1 {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

@keyframes drift1 {
  0% { transform: translate(0, 0); }
  100% { transform: translate(-5%, 5%); }
}

/* Nebulae */
.nebula {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.15;
  animation: float 30s ease-in-out infinite;
}

.nebula-1 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(139, 182, 255, 0.5), rgba(139, 182, 255, 0) 70%);
  top: 10%;
  left: 15%;
  animation: float1 25s ease-in-out infinite, rotate1 40s linear infinite;
}

.nebula-2 {
  width: 350px;
  height: 350px;
  background: radial-gradient(circle, rgba(196, 224, 255, 0.4), rgba(196, 224, 255, 0) 70%);
  top: 60%;
  right: 20%;
  animation: float2 30s ease-in-out infinite, rotate2 50s linear infinite;
}

.nebula-3 {
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(168, 216, 255, 0.3), rgba(168, 216, 255, 0) 70%);
  bottom: 20%;
  left: 50%;
  animation: float3 35s ease-in-out infinite, rotate3 45s linear infinite;
}

@keyframes float1 {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(30px, -20px) scale(1.1);
  }
  66% {
    transform: translate(-20px, 30px) scale(0.9);
  }
}

@keyframes float2 {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(-40px, 25px) scale(1.15);
  }
  66% {
    transform: translate(25px, -30px) scale(0.95);
  }
}

@keyframes float3 {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(35px, 30px) scale(0.9);
  }
  66% {
    transform: translate(-30px, -25px) scale(1.1);
  }
}

@keyframes rotate1 {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes rotate2 {
  from { transform: rotate(360deg); }
  to { transform: rotate(0deg); }
}

@keyframes rotate3 {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.map-canvas {
  width: 100%;
  position: relative;
  z-index: 1;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
}

/* Glass Panels */
.glass-panel {
  position: absolute;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 20px;
  padding: 1.5rem;
  backdrop-filter: blur(30px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  z-index: 5;
}

/* Legend */
.map-legend {
  bottom: 2rem;
  left: 2rem;
  min-width: 200px;
}

.legend-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.95);
  margin-bottom: 1rem;
}

.legend-items {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
}

.legend-node {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 2px solid;
  box-shadow: 0 0 12px currentColor;
}

.legend-node.level-0 {
  background: rgba(139, 182, 255, 0.4);
  border-color: rgba(139, 182, 255, 0.9);
}

.legend-node.level-1 {
  background: rgba(196, 224, 255, 0.4);
  border-color: rgba(196, 224, 255, 0.9);
}

.legend-node.level-2 {
  background: rgba(168, 216, 255, 0.4);
  border-color: rgba(168, 216, 255, 0.9);
}

/* Detail Panel */
.detail-panel {
  top: 2rem;
  right: 2rem;
  width: 500px;
  max-height: calc(100vh - 8rem);
  overflow-y: auto;
  animation: slideIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  background: rgba(15, 12, 41, 0.85);
  border: 1px solid rgba(139, 182, 255, 0.3);
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.4),
    0 0 80px rgba(139, 182, 255, 0.15),
    inset 0 0 60px rgba(139, 182, 255, 0.03);
}

.detail-panel::-webkit-scrollbar {
  width: 8px;
}

.detail-panel::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
}

.detail-panel::-webkit-scrollbar-thumb {
  background: rgba(139, 182, 255, 0.3);
  border-radius: 10px;
}

.detail-panel::-webkit-scrollbar-thumb:hover {
  background: rgba(139, 182, 255, 0.5);
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(30px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateX(0) scale(1);
  }
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(139, 182, 255, 0.2);
}

.detail-title-section {
  flex: 1;
}

.detail-title-section h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.98);
  margin: 0 0 0.5rem 0;
  text-shadow: 0 2px 10px rgba(139, 182, 255, 0.3);
}

.detail-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background: rgba(139, 182, 255, 0.15);
  border: 1px solid rgba(139, 182, 255, 0.3);
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  color: rgba(139, 182, 255, 0.95);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.close-btn {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 10px;
  width: 36px;
  height: 36px;
  font-size: 1.3rem;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.close-btn:hover {
  background: rgba(255, 100, 100, 0.2);
  border-color: rgba(255, 100, 100, 0.4);
  transform: rotate(90deg);
  color: rgba(255, 150, 150, 0.95);
}

.detail-body {
  min-height: 200px;
}

.detail-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 0;
  gap: 1rem;
}

.loading-spinner-small {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(139, 182, 255, 0.2);
  border-top-color: rgba(139, 182, 255, 0.9);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.detail-loading p {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.95rem;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.detail-section {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 1.25rem;
  backdrop-filter: blur(10px);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.1rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.95);
  margin: 0 0 1rem 0;
}

.section-icon {
  font-size: 1.3rem;
}

.summary-text {
  color: rgba(255, 255, 255, 0.85);
  line-height: 1.7;
  margin: 0;
  font-size: 0.95rem;
}

.detail-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
  padding: 1rem;
}

.stat-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: rgba(139, 182, 255, 0.08);
  border: 1px solid rgba(139, 182, 255, 0.2);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.stat-card:hover {
  background: rgba(139, 182, 255, 0.15);
  border-color: rgba(139, 182, 255, 0.4);
  transform: translateY(-2px);
}

.stat-icon {
  font-size: 1.5rem;
}

.stat-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.stat-label {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  color: rgba(139, 182, 255, 0.95);
  font-weight: 700;
  font-size: 1.2rem;
}

.content-chunks {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.content-chunk {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 1rem;
  transition: all 0.3s ease;
}

.content-chunk:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(139, 182, 255, 0.3);
  transform: translateX(4px);
  box-shadow: -4px 0 20px rgba(139, 182, 255, 0.15);
}

.content-chunk.high-relevance {
  border-color: rgba(139, 182, 255, 0.4);
  background: rgba(139, 182, 255, 0.08);
}

.chunk-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
  flex-wrap: wrap;
}

.chunk-source {
  color: rgba(139, 182, 255, 0.9);
  font-size: 0.85rem;
  font-weight: 600;
}

.chunk-page {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.8rem;
  padding: 0.15rem 0.5rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 6px;
}

.relevance-badge {
  margin-left: auto;
  padding: 0.2rem 0.6rem;
  background: rgba(139, 182, 255, 0.15);
  border: 1px solid rgba(139, 182, 255, 0.3);
  border-radius: 12px;
  font-size: 0.75rem;
  color: rgba(139, 182, 255, 0.95);
  font-weight: 600;
}

.chunk-content {
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.7;
  font-size: 0.9rem;
  white-space: pre-wrap;
}

.no-content {
  text-align: center;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.02);
}

.no-content p {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.95rem;
  margin: 0;
}

/* Loading Overlay */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 12, 41, 0.8);
  backdrop-filter: blur(10px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 20;
}

.loading-spinner {
  width: 80px;
  height: 80px;
  border: 4px solid rgba(139, 182, 255, 0.2);
  border-top-color: rgba(139, 182, 255, 0.9);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1.5rem;
  box-shadow: 0 0 30px rgba(139, 182, 255, 0.5);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-overlay p {
  color: rgba(255, 255, 255, 0.9);
  font-size: 1.2rem;
  font-weight: 600;
}

/* Markdown Content Styling */
.markdown-content {
  line-height: 1.7;
}

.markdown-content p {
  margin: 0 0 0.75rem 0;
}

.markdown-content p:last-child {
  margin-bottom: 0;
}

.markdown-content strong {
  color: rgba(139, 182, 255, 0.95);
  font-weight: 700;
}

.markdown-content em {
  color: rgba(196, 224, 255, 0.9);
  font-style: italic;
}

.markdown-content code {
  background: rgba(255, 255, 255, 0.1);
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
  color: rgba(255, 200, 150, 0.95);
}

.markdown-content ul,
.markdown-content ol {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
}

.markdown-content li {
  margin: 0.25rem 0;
}

.markdown-content h1,
.markdown-content h2,
.markdown-content h3,
.markdown-content h4 {
  color: rgba(255, 255, 255, 0.95);
  margin: 0.75rem 0 0.5rem 0;
  font-weight: 600;
}

.markdown-content h1 {
  font-size: 1.3rem;
}

.markdown-content h2 {
  font-size: 1.2rem;
}

.markdown-content h3 {
  font-size: 1.1rem;
}

/* D3 Enhancements */
:deep(.node circle) {
  transition: r 0.2s ease;
}

:deep(.link) {
  opacity: 0.6;
  transition: opacity 0.3s ease, stroke-width 0.3s ease;
}

:deep(.node:hover ~ .link) {
  opacity: 1;
  stroke-width: 3px;
}
</style>
