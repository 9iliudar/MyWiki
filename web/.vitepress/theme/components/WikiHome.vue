<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { cleanDisplayName } from "../utils/displayTitle";

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
const tagsExpanded = ref(false);

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

const visibleTags = computed(() =>
  tagsExpanded.value ? allTagsList.value : allTagsList.value.slice(0, 12)
);

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

function clearFilters() {
  selectedTag.value = null;
  selectedCategory.value = null;
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

    <section class="filter-section">
      <div class="filter-row">
        <div class="filter-group">
          <span class="filter-label">Category</span>
          <div class="filter-chips">
            <button
              v-for="category in allCategories"
              :key="category"
              class="chip"
              :class="{ active: selectedCategory === category }"
              @click="toggleCategory(category)"
            >
              {{ category }}
            </button>
          </div>
        </div>
        <div class="filter-group tags-group">
          <span class="filter-label">Tags</span>
          <div class="tags-row">
            <div class="filter-chips" :class="{ expanded: tagsExpanded }">
              <button
                v-for="t in allTagsList"
                :key="t.tag"
                class="chip"
                :class="{ active: selectedTag === t.tag }"
                @click="toggleTag(t.tag)"
              >
                {{ t.tag }}
                <span class="chip-count">{{ t.count }}</span>
              </button>
            </div>
            <button
              v-if="allTagsList.length > 10"
              class="chip chip-toggle"
              @click="tagsExpanded = !tagsExpanded"
            >
              {{ tagsExpanded ? 'Less' : `+${allTagsList.length - 10}` }}
            </button>
          </div>
        </div>
        <button
          v-if="selectedTag || selectedCategory"
          class="filter-clear"
          @click="clearFilters"
        >
          Clear filters
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
          <div class="card-title">{{ cleanDisplayName(page.title) }}</div>
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
.wiki-home { max-width: 1080px; margin: 0 auto; padding: 1.5rem 1.5rem 3rem; font-family: system-ui, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
.search-section { text-align: center; padding: 1.5rem 0 1rem; }
.search-title { font-size: 1.6rem; font-weight: 700; color: var(--vp-c-text-1); margin: 0 0 0.8rem; }
.search-box { display: flex; align-items: center; gap: 0.6rem; max-width: 580px; margin: 0 auto 0.8rem; padding: 0.7rem 1rem; border: 1px solid var(--vp-c-divider); border-radius: 10px; background: var(--vp-c-bg-soft); cursor: pointer; }
.search-placeholder { flex: 1; text-align: left; color: var(--vp-c-text-3); font-size: 0.9rem; }
.search-kbd { font-size: 0.7rem; padding: 0.15rem 0.4rem; border: 1px solid var(--vp-c-divider); border-radius: 4px; background: var(--vp-c-bg); color: var(--vp-c-text-3); font-family: inherit; }
.pulse-row { display: flex; align-items: center; justify-content: center; gap: 0.8rem; font-size: 0.8rem; color: var(--vp-c-text-3); flex-wrap: wrap; }
.pulse-item strong { color: var(--vp-c-text-2); }
.pulse-sep { width: 3px; height: 3px; border-radius: 50%; background: var(--vp-c-divider); }

/* Filter section */
.filter-section { padding: 0.5rem 0 0.8rem; margin-bottom: 1rem; border-bottom: 1px solid var(--vp-c-divider); }
.filter-row { display: flex; flex-direction: column; gap: 0.5rem; }
.filter-group { display: flex; align-items: baseline; gap: 0.5rem; }
.filter-label { font-size: 0.72rem; font-weight: 600; color: var(--vp-c-text-3); text-transform: uppercase; letter-spacing: 0.04em; min-width: 56px; flex-shrink: 0; }
.tags-group { align-items: flex-start; }
.tags-row { display: flex; align-items: flex-start; gap: 0.4rem; min-width: 0; flex: 1; }
.filter-chips { display: flex; flex-wrap: wrap; gap: 0.3rem; }
.tags-row .filter-chips { flex-wrap: nowrap; overflow: hidden; min-width: 0; flex: 1; }
.tags-row .filter-chips.expanded { flex-wrap: wrap; overflow: visible; }
.chip { display: inline-flex; align-items: center; gap: 0.25rem; padding: 0.2rem 0.55rem; border: 1px solid var(--vp-c-divider); border-radius: 999px; background: var(--vp-c-bg-soft); color: var(--vp-c-text-2); font-size: 0.75rem; cursor: pointer; font-family: inherit; transition: background 0.15s, border-color 0.15s; white-space: nowrap; }
.chip:hover { border-color: var(--vp-c-text-3); }
.chip.active { background: var(--vp-c-brand-1); border-color: var(--vp-c-brand-1); color: #fff; }
.chip-count { font-size: 0.65rem; background: var(--vp-c-bg); color: var(--vp-c-text-3); padding: 0 0.3rem; border-radius: 999px; min-width: 1em; text-align: center; }
.chip.active .chip-count { background: rgba(255,255,255,0.2); color: #fff; }
.chip-toggle { color: var(--vp-c-text-3); border-style: dashed; flex-shrink: 0; margin-top: 0.05rem; }
.chip-toggle:hover { color: var(--vp-c-text-2); }
.filter-clear { align-self: flex-start; padding: 0.2rem 0.5rem; border: none; border-radius: 4px; background: transparent; color: var(--vp-c-text-3); font-size: 0.72rem; cursor: pointer; font-family: inherit; text-decoration: underline; }
.filter-clear:hover { color: var(--vp-c-text-1); }

/* Cards */
.section-title { font-size: 0.95rem; font-weight: 600; color: var(--vp-c-text-2); margin: 0; text-transform: uppercase; letter-spacing: 0.04em; }
.cards-section { padding: 0.8rem 0 0; }
.section-header { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.6rem; }
.cards-count { font-size: 0.78rem; color: var(--vp-c-text-3); }
.cards-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.7rem; }
@media (max-width: 900px) { .cards-grid { grid-template-columns: 1fr 1fr; } }
@media (max-width: 640px) { .cards-grid { grid-template-columns: 1fr; } .filter-group { flex-direction: column; } .filter-label { min-width: auto; } }
.card { display: flex; flex-direction: column; gap: 0.3rem; padding: 0.85rem 1rem; border: 1px solid var(--vp-c-divider); border-radius: 10px; background: var(--vp-c-bg-soft); text-decoration: none; transition: border-color 0.15s; }
.card:hover { border-color: var(--vp-c-text-3); }
.card-title { font-weight: 600; font-size: 0.92rem; color: var(--vp-c-text-1); }
.card-meta, .card-date, .card-evolution { font-size: 0.75rem; color: var(--vp-c-text-3); }
.card-tags { display: flex; gap: 0.25rem; flex-wrap: wrap; }
.card-tag { font-size: 0.68rem; padding: 0.08rem 0.4rem; border-radius: 4px; background: var(--vp-c-bg); color: var(--vp-c-text-3); border: 1px solid var(--vp-c-divider); }
.show-more { display: block; width: 100%; margin-top: 0.8rem; padding: 0.5rem; border: 1px dashed var(--vp-c-divider); border-radius: 8px; background: transparent; color: var(--vp-c-text-2); font-size: 0.82rem; cursor: pointer; font-family: inherit; }
</style>
