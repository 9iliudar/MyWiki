<script setup lang="ts">
import { ref, computed, onMounted } from "vue";

interface PageMeta {
  name: string;
  title: string;
  tags: string[];
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

const recentPages = computed(() =>
  [...pages.value]
    .sort((a, b) => (b.updated || "").localeCompare(a.updated || ""))
    .slice(0, 10)
);

const totalPages = computed(() => pages.value.length);

const allTags = computed(() => {
  const tags = new Set<string>();
  pages.value.forEach((p) => p.tags.forEach((t) => tags.add(t)));
  return tags.size;
});

const latestUpdate = computed(() => {
  if (!pages.value.length) return "暂无";
  return recentPages.value[0]?.updated || "暂无";
});
</script>

<template>
  <div class="wiki-home">
    <div class="pulse">
      <span class="pulse-item">{{ totalPages }} 页面</span>
      <span class="pulse-item">{{ allTags }} 标签</span>
      <span class="pulse-item">最近更新 {{ latestUpdate }}</span>
    </div>

    <h2>最近进化</h2>
    <ul class="recent-list">
      <li v-for="page in recentPages" :key="page.name" class="recent-item">
        <a :href="`/pages/${page.name}.html`">{{ page.title }}</a>
        <span class="date">{{ page.updated }}</span>
        <span class="evolution" v-if="page.evolution.length">
          — {{ page.evolution[page.evolution.length - 1] }}
        </span>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.wiki-home {
  max-width: 720px;
  margin: 0 auto;
  padding: 2rem 1rem;
  font-family: system-ui, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}
.pulse {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 2rem;
  padding: 1rem 1.2rem;
  background: var(--vp-c-bg-soft);
  border-radius: 8px;
  font-size: 0.9rem;
  color: var(--vp-c-text-2);
}
.pulse-item::before {
  content: "·";
  margin-right: 0.3rem;
  color: var(--vp-c-text-3);
}
.pulse-item:first-child::before {
  content: "";
  margin-right: 0;
}
.recent-list {
  list-style: none;
  padding: 0;
}
.recent-item {
  padding: 0.6rem 0;
  border-bottom: 1px solid var(--vp-c-divider);
}
.recent-item a {
  font-weight: 500;
  color: var(--vp-c-text-1);
  text-decoration: none;
}
.recent-item a:hover {
  color: var(--vp-c-brand-1);
}
.date {
  color: var(--vp-c-text-3);
  font-size: 0.8rem;
  margin-left: 0.5rem;
}
.evolution {
  color: var(--vp-c-text-3);
  font-size: 0.8rem;
}
</style>
