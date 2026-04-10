<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { stripIpaFromTitle } from "../utils/displayTitle";

interface PageMeta {
  name: string;
  title: string;
  route: string;
  category: string;
  tags: string[];
  updated: string;
  evolution: string[];
}

const pages = ref<PageMeta[]>([]);
const selectedTag = ref<string | null>(null);
const selectedCategory = ref<string | null>(null);
const showAll = ref(false);

onMounted(async () => {
  try {
    const data = await import("../../../data/wiki-meta.json");
    pages.value = data.default || data;
  } catch {
    pages.value = [];
  }
});

const totalPages = computed(() => pages.value.length);
const allCategories = computed(() =>
  Array.from(new Set(pages.value.map((p) => p.category))).sort()
);

const groupedByCategory = computed(() => {
  const groups: Record<string, PageMeta[]> = {};
  for (const page of filteredPages.value) {
    if (!groups[page.category]) groups[page.category] = [];
    groups[page.category].push(page);
  }
  return Object.entries(groups).map(([category, items]) => ({
    category,
    items: showAll.value ? items : items.slice(0, 8),
    total: items.length,
  }));
});

const allTagsList = computed(() => {
  const tagCount: Record<string, number> = {};
  pages.value.forEach((p) =>
    p.tags.forEach((t) => {
      tagCount[t] = (tagCount[t] || 0) + 1;
    })
  );
  return Object.entries(tagCount)
    .sort((a, b) => b[1] - a[1])
    .map(([tag, count]) => ({ tag, count }));
});

const totalTags = computed(() => allTagsList.value.length);
const latestUpdate = computed(() => {
  if (!pages.value.length) return "";
  const sorted = [...pages.value].sort((a, b) => (b.updated || "").localeCompare(a.updated || ""));
  return sorted[0]?.updated || "";
});

const filteredPages = computed(() => {
  let result = [...pages.value].sort((a, b) => (b.updated || "").localeCompare(a.updated || ""));
  if (selectedTag.value) result = result.filter((p) => p.tags.includes(selectedTag.value!));
  if (selectedCategory.value) result = result.filter((p) => p.category === selectedCategory.value);
  return result;
});

function toggleTag(tag: string) {
  selectedTag.value = selectedTag.value === tag ? null : tag;
  showAll.value = false;
}

function toggleCategory(category: string) {
  selectedCategory.value = selectedCategory.value === category ? null : category;
  showAll.value = false;
}

function triggerSearch() {
  const event = new KeyboardEvent("keydown", {
    key: "k",
    ctrlKey: true,
    bubbles: true,
  });
  document.dispatchEvent(event);
}
</script>

<template>
  <div class="wiki-home">
    <section class="search-section">
      <h1 class="search-title">Knowledge Hub</h1>
      <div class="search-box" @click="triggerSearch">
        <span class="search-placeholder">Search knowledge...</span>
        <kbd class="search-kbd">Ctrl K</kbd>
      </div>
      <div class="pulse-row">
        <span class="pulse-item"><strong>{{ totalPages }}</strong> pages</span>
        <span class="pulse-sep"></span>
        <span class="pulse-item"><strong>{{ allCategories.length }}</strong> categories</span>
        <span class="pulse-sep"></span>
        <span class="pulse-item"><strong>{{ totalTags }}</strong> tags</span>
        <span class="pulse-sep"></span>
        <span class="pulse-item">Updated <strong>{{ latestUpdate }}</strong></span>
      </div>
    </section>

    <section v-if="allCategories.length" class="tags-section">
      <h2 class="section-title">Categories</h2>
      <div class="tag-cloud">
        <button
          v-for="category in allCategories"
          :key="category"
          class="tag-chip"
          :class="{ active: selectedCategory === category }"
          @click="toggleCategory(category)"
        >
          {{ category }}
        </button>
      </div>
    </section>

    <section v-if="allTagsList.length" class="tags-section">
      <h2 class="section-title">Tags</h2>
      <div class="tag-cloud">
        <button
          v-for="t in allTagsList"
          :key="t.tag"
          class="tag-chip"
          :class="{ active: selectedTag === t.tag }"
          @click="toggleTag(t.tag)"
        >
          {{ t.tag }}
          <span class="tag-count">{{ t.count }}</span>
        </button>
      </div>
    </section>

    <section class="cards-section" v-for="group in groupedByCategory" :key="group.category">
      <div class="section-header">
        <h2 class="section-title">{{ group.category }}</h2>
        <span class="cards-count">{{ group.total }} pages</span>
      </div>
      <div class="cards-grid">
        <a
          v-for="page in group.items"
          :key="page.route"
          :href="page.route"
          class="card"
        >
          <div class="card-title">{{ stripIpaFromTitle(page.title) }}</div>
          <div class="card-meta">{{ page.category }}</div>
          <div v-if="page.tags.length" class="card-tags">
            <span v-for="tag in page.tags.slice(0, 3)" :key="tag" class="card-tag">{{ tag }}</span>
          </div>
          <div v-if="page.evolution.length" class="card-evolution">{{ page.evolution[page.evolution.length - 1] }}</div>
          <div class="card-date">{{ page.updated }}</div>
        </a>
      </div>
    </section>

    <button
      v-if="filteredPages.length > 8"
      class="show-more"
      @click="showAll = !showAll"
    >
      {{ showAll ? "Show less" : "Show more" }}
    </button>
  </div>
</template>

<style scoped>
.wiki-home { max-width: 1080px; margin: 0 auto; padding: 2rem 1.5rem 3rem; font-family: system-ui, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
.search-section { text-align: center; padding: 2.5rem 0 1.5rem; }
.search-title { font-size: 1.8rem; font-weight: 700; color: var(--vp-c-text-1); margin: 0 0 1.2rem; }
.search-box { display: flex; align-items: center; gap: 0.6rem; max-width: 680px; margin: 0 auto 1.2rem; padding: 0.85rem 1.2rem; border: 1px solid var(--vp-c-divider); border-radius: 12px; background: var(--vp-c-bg-soft); cursor: pointer; }
.search-placeholder { flex: 1; text-align: left; color: var(--vp-c-text-3); font-size: 0.95rem; }
.search-kbd { font-size: 0.7rem; padding: 0.15rem 0.4rem; border: 1px solid var(--vp-c-divider); border-radius: 4px; background: var(--vp-c-bg); color: var(--vp-c-text-3); font-family: inherit; }
.pulse-row { display: flex; align-items: center; justify-content: center; gap: 0.8rem; font-size: 0.85rem; color: var(--vp-c-text-3); flex-wrap: wrap; }
.pulse-item strong { color: var(--vp-c-text-2); }
.pulse-sep { width: 3px; height: 3px; border-radius: 50%; background: var(--vp-c-divider); }
.tags-section { padding: 1rem 0; }
.section-title { font-size: 1rem; font-weight: 600; color: var(--vp-c-text-2); margin: 0 0 0.8rem; text-transform: uppercase; letter-spacing: 0.04em; }
.tag-cloud { display: flex; flex-wrap: wrap; gap: 0.4rem; }
.tag-chip { display: inline-flex; align-items: center; gap: 0.3rem; padding: 0.3rem 0.7rem; border: 1px solid var(--vp-c-divider); border-radius: 999px; background: var(--vp-c-bg-soft); color: var(--vp-c-text-2); font-size: 0.8rem; cursor: pointer; font-family: inherit; }
.tag-chip.active { background: var(--vp-c-brand-1); border-color: var(--vp-c-brand-1); color: #fff; }
.tag-count { font-size: 0.7rem; background: var(--vp-c-bg); color: var(--vp-c-text-3); padding: 0 0.35rem; border-radius: 999px; min-width: 1.2em; text-align: center; }
.cards-section { padding: 1rem 0 0; }
.section-header { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.8rem; }
.cards-count { font-size: 0.8rem; color: var(--vp-c-text-3); }
.cards-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.8rem; }
@media (max-width: 900px) { .cards-grid { grid-template-columns: 1fr 1fr; } }
@media (max-width: 640px) { .cards-grid { grid-template-columns: 1fr; } }
.card { display: flex; flex-direction: column; gap: 0.35rem; padding: 1rem 1.1rem; border: 1px solid var(--vp-c-divider); border-radius: 10px; background: var(--vp-c-bg-soft); text-decoration: none; }
.card-title { font-weight: 600; font-size: 0.95rem; color: var(--vp-c-text-1); }
.card-meta, .card-date, .card-evolution { font-size: 0.78rem; color: var(--vp-c-text-3); }
.card-tags { display: flex; gap: 0.3rem; flex-wrap: wrap; }
.card-tag { font-size: 0.7rem; padding: 0.1rem 0.45rem; border-radius: 4px; background: var(--vp-c-bg); color: var(--vp-c-text-3); border: 1px solid var(--vp-c-divider); }
.show-more { display: block; width: 100%; margin-top: 1rem; padding: 0.6rem; border: 1px dashed var(--vp-c-divider); border-radius: 8px; background: transparent; color: var(--vp-c-text-2); font-size: 0.85rem; cursor: pointer; font-family: inherit; }
</style>
