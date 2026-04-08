<script setup lang="ts">
import { ref, computed, onMounted } from "vue";

interface PageMeta {
  name: string;
  title: string;
  created: string;
  updated: string;
  evolution: string[];
}

const pages = ref<PageMeta[]>([]);

onMounted(async () => {
  try {
    const data = await import("../../../data/wiki-meta.json");
    pages.value = data.default || data;
  } catch {
    pages.value = [];
  }
});

const sortedPages = computed(() =>
  [...pages.value].sort((a, b) => (b.updated || "").localeCompare(a.updated || ""))
);
</script>

<template>
  <div class="timeline-view">
    <h1>知识时间线</h1>
    <div class="timeline">
      <div v-for="page in sortedPages" :key="page.name" class="timeline-item">
        <div class="date-col">{{ page.updated || page.created }}</div>
        <div class="content-col">
          <a :href="`/pages/${page.name}.html`" class="page-title">{{ page.title }}</a>
          <ul class="evo-list" v-if="page.evolution.length">
            <li v-for="(e, i) in page.evolution.slice().reverse().slice(0, 3)" :key="i">
              {{ e }}
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.timeline-view {
  max-width: 720px;
  margin: 0 auto;
  padding: 1rem;
  font-family: system-ui, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}
.timeline-item {
  display: flex;
  gap: 1rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--vp-c-divider);
}
.date-col {
  min-width: 100px;
  color: var(--vp-c-text-3);
  font-size: 0.8rem;
  padding-top: 0.15rem;
}
.page-title {
  font-weight: 500;
  font-size: 1rem;
  color: var(--vp-c-text-1);
  text-decoration: none;
}
.page-title:hover {
  color: var(--vp-c-brand-1);
}
.evo-list {
  list-style: none;
  padding: 0;
  margin: 0.3rem 0 0;
}
.evo-list li {
  font-size: 0.75rem;
  color: var(--vp-c-text-3);
  padding: 0.1rem 0;
}
</style>
