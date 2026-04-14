---
layout: page
title: 探索知识图谱
---

<script setup>
import { ref } from 'vue'
import KnowledgeGraph from './.vitepress/theme/components/KnowledgeGraph.vue'
import ConceptUniverse from './.vitepress/theme/components/ConceptUniverse.vue'

const view = ref('graph')
const universeOpen = ref(false)

function switchTo(v) {
  if (v === 'universe') {
    universeOpen.value = true
    view.value = 'universe'
  } else {
    universeOpen.value = false
    view.value = 'graph'
  }
}
</script>

<style>
.VPDoc .container,
.VPDoc .content-container,
.VPDoc .content {
  max-width: 100% !important;
  padding: 0 !important;
  margin: 0 !important;
}
.VPDoc {
  padding: 0 !important;
}
.VPContent.has-sidebar {
  padding-left: 0 !important;
}
.VPDoc .aside,
.VPDocFooter {
  display: none !important;
}

.view-toggle {
  position: fixed;
  top: calc(var(--vp-nav-height, 64px) + 12px);
  right: 16px;
  z-index: 30;
  display: flex;
  gap: 2px;
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  padding: 3px;
}

.view-toggle button {
  padding: 5px 12px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: var(--vp-c-text-2);
  font-size: 0.8rem;
  cursor: pointer;
  font-family: inherit;
  transition: background 0.15s, color 0.15s;
}

.view-toggle button:hover {
  color: var(--vp-c-text-1);
}

.view-toggle button.active {
  background: #8b5cf6;
  color: #fff;
}
</style>

<div class="view-toggle">
  <button :class="{ active: view === 'graph' }" @click="switchTo('graph')">Graph</button>
  <button :class="{ active: view === 'universe' }" @click="switchTo('universe')">Universe</button>
</div>

<KnowledgeGraph v-show="view === 'graph'" />
<ConceptUniverse :open="universeOpen" @close="switchTo('graph')" />
