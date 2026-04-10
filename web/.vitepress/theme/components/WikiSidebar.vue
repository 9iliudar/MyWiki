<script setup lang="ts">
import { computed } from "vue";
import { useData } from "vitepress";
import routeMap from "../../../data/route-map.json";

const { frontmatter, page } = useData();

const related = computed(() => {
  const list = frontmatter.value.related || [];
  return list.map((r: string) => {
    const name = r.replace(/^\[\[/, "").replace(/\]\]$/, "");
    const href =
      (routeMap as any).routeByName?.[name] ||
      (routeMap as any).routeByTitle?.[name] ||
      `/pages/${name}.html`;
    return { name, href };
  });
});

const sources = computed(() => frontmatter.value.sources || []);
const tags = computed(() => frontmatter.value.tags || []);
const evolution = computed(() => (frontmatter.value.evolution || []).slice().reverse());
const category = computed(() => frontmatter.value.category || "");
const headers = computed(() =>
  (page.value.headers || []).filter((header: any) => (header.level || 0) <= 3)
);
</script>

<template>
  <aside class="wiki-sidebar" v-if="frontmatter.title">
    <section v-if="headers.length">
      <h4>目录</h4>
      <ul>
        <li v-for="header in headers" :key="header.slug">
          <a :href="`#${header.slug}`">{{ header.title }}</a>
        </li>
      </ul>
    </section>

    <section v-if="category">
      <h4>分类</h4>
      <div class="category-chip">{{ category }}</div>
    </section>

    <section v-if="tags.length">
      <h4>标签</h4>
      <div class="tags">
        <span v-for="tag in tags" :key="tag" class="tag">{{ tag }}</span>
      </div>
    </section>

    <section v-if="related.length">
      <h4>关联页面</h4>
      <ul>
        <li v-for="r in related" :key="r.name">
          <a :href="r.href">{{ r.name }}</a>
        </li>
      </ul>
    </section>

    <section v-if="sources.length">
      <h4>来源</h4>
      <ul>
        <li v-for="src in sources" :key="src" class="source">{{ src }}</li>
      </ul>
    </section>

    <section v-if="evolution.length">
      <h4>进化历史</h4>
      <ul class="evolution">
        <li v-for="(e, i) in evolution" :key="i">{{ e }}</li>
      </ul>
    </section>
  </aside>
</template>

<style scoped>
.wiki-sidebar {
  padding: 1rem;
  font-size: 0.85rem;
  font-family: system-ui, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  background: var(--vp-c-bg);
}

.wiki-sidebar h4 {
  margin: 1rem 0 0.5rem;
  font-size: 0.85rem;
  color: var(--vp-c-text-2);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.wiki-sidebar ul {
  list-style: none;
  padding: 0;
}

.wiki-sidebar li {
  padding: 0.2rem 0;
}

.wiki-sidebar a {
  color: var(--vp-c-text-1);
  text-decoration: none;
}

.wiki-sidebar a:hover {
  color: var(--vp-c-brand-1);
}

.category-chip,
.tag {
  background: var(--vp-c-bg-soft);
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  color: var(--vp-c-text-2);
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.source {
  color: var(--vp-c-text-3);
  font-size: 0.75rem;
  overflow-wrap: anywhere;
}

.evolution li {
  color: var(--vp-c-text-3);
  border-left: 2px solid var(--vp-c-divider);
  padding-left: 0.5rem;
  margin-bottom: 0.3rem;
  font-size: 0.8rem;
}
</style>
