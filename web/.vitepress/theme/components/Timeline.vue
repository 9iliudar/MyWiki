<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import routeMap from "../../../data/route-map.json";

interface PageMeta {
  name: string;
  title: string;
  created: string;
  updated: string;
  tags: string[];
  evolution: string[];
  route?: string;
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

const collapsedDates = ref<Set<string>>(new Set());

function toggleCollapse(date: string) {
  if (collapsedDates.value.has(date)) {
    collapsedDates.value.delete(date);
  } else {
    collapsedDates.value.add(date);
  }
  // trigger reactivity
  collapsedDates.value = new Set(collapsedDates.value);
}

const groupedByDate = computed(() => {
  const sorted = [...pages.value].sort((a, b) =>
    (b.updated || "").localeCompare(a.updated || "")
  );
  const groups: { date: string; pages: PageMeta[] }[] = [];
  let currentDate = "";
  for (const page of sorted) {
    const date = page.updated || page.created || "Unknown";
    if (date !== currentDate) {
      currentDate = date;
      groups.push({ date, pages: [] });
    }
    groups[groups.length - 1].pages.push(page);
  }
  return groups;
});

function routeForPage(page: PageMeta) {
  return (
    page.route ||
    (routeMap as any).routeByName?.[page.name] ||
    (routeMap as any).routeByTitle?.[page.title] ||
    `/pages/${page.name}.html`
  );
}
</script>

<template>
  <div class="timeline-view">
    <h1 class="timeline-heading">Knowledge Timeline</h1>
    <div class="timeline">
      <div v-for="group in groupedByDate" :key="group.date" class="date-group">
        <div class="date-header" @click="toggleCollapse(group.date)">
          <span class="date-dot"></span>
          <span class="date-label">{{ group.date }}</span>
          <span class="date-count">{{ group.pages.length }}</span>
          <span class="collapse-icon" :class="{ collapsed: collapsedDates.has(group.date) }">&#9662;</span>
        </div>
        <div
          v-show="!collapsedDates.has(group.date)"
          v-for="page in group.pages"
          :key="page.name"
          class="timeline-item"
        >
          <div class="item-dot"></div>
          <div class="item-content">
            <a :href="routeForPage(page)" class="page-title">
              {{ page.title }}
            </a>
            <div v-if="page.tags && page.tags.length" class="item-tags">
              <span v-for="tag in page.tags.slice(0, 4)" :key="tag" class="item-tag">
                {{ tag }}
              </span>
            </div>
            <ul class="evo-list" v-if="page.evolution.length">
              <li
                v-for="(e, i) in page.evolution.slice().reverse().slice(0, 3)"
                :key="i"
              >
                {{ e }}
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.timeline-view {
  max-width: 680px;
  margin: 0 auto;
  padding: 2rem 1.5rem 3rem;
  font-family: system-ui, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

.timeline-heading {
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--vp-c-text-1);
  margin: 0 0 2rem 1.8rem;
}

.timeline {
  position: relative;
  padding-left: 2rem;
}

/* Vertical line */
.timeline::before {
  content: "";
  position: absolute;
  left: 7px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: var(--vp-c-divider);
}

/* Date group */
.date-group {
  margin-bottom: 0.5rem;
}

.date-header {
  position: relative;
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
  margin-left: -2rem;
  cursor: pointer;
  user-select: none;
}

.date-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--vp-c-brand-1, #8b5cf6);
  border: 3px solid var(--vp-c-bg);
  box-shadow: 0 0 0 2px var(--vp-c-brand-1, #8b5cf6);
  flex-shrink: 0;
  z-index: 1;
}

.date-label {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--vp-c-text-1);
  margin-left: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.date-count {
  font-size: 0.7rem;
  color: var(--vp-c-text-3);
  margin-left: 0.5rem;
  background: var(--vp-c-bg-soft);
  padding: 0 0.4rem;
  border-radius: 999px;
  border: 1px solid var(--vp-c-divider);
}

.collapse-icon {
  font-size: 0.7rem;
  color: var(--vp-c-text-3);
  margin-left: 0.4rem;
  transition: transform 0.2s;
}

.collapse-icon.collapsed {
  transform: rotate(-90deg);
}

/* Timeline items */
.timeline-item {
  position: relative;
  display: flex;
  align-items: flex-start;
  padding: 0.5rem 0;
  margin-left: -2rem;
}

.item-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--vp-c-text-3);
  margin-top: 0.45rem;
  margin-left: 4px;
  flex-shrink: 0;
  z-index: 1;
}

.item-content {
  margin-left: calc(2rem - 12px + 0.8rem);
  flex: 1;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--vp-c-divider);
}

.page-title {
  font-weight: 600;
  font-size: 1.05rem;
  color: var(--vp-c-text-1);
  text-decoration: none;
  line-height: 1.4;
}

.page-title:hover {
  color: var(--vp-c-brand-1);
}

.item-tags {
  display: flex;
  gap: 0.3rem;
  margin-top: 0.25rem;
  flex-wrap: wrap;
}

.item-tag {
  font-size: 0.7rem;
  padding: 0.08rem 0.4rem;
  border-radius: 4px;
  background: var(--vp-c-bg-soft);
  color: var(--vp-c-text-3);
  border: 1px solid var(--vp-c-divider);
}

.evo-list {
  list-style: none;
  padding: 0;
  margin: 0.4rem 0 0;
}

.evo-list li {
  font-size: 0.82rem;
  color: var(--vp-c-text-2);
  padding: 0.15rem 0 0.15rem 1rem;
  position: relative;
  line-height: 1.5;
}

.evo-list li::before {
  content: "";
  position: absolute;
  left: 0;
  top: 0.6rem;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--vp-c-divider);
}
</style>
