<script setup lang="ts">
import DefaultTheme from "vitepress/theme";
import WikiSidebar from "./components/WikiSidebar.vue";
import { useData } from "vitepress";

const { Layout } = DefaultTheme;
const { frontmatter, page } = useData();
</script>

<template>
  <Layout>
    <template #aside-outline-after>
      <WikiSidebar v-if="page.relativePath.startsWith('pages/')" />
    </template>
  </Layout>
</template>

<style>
/* Center wiki detail page content */
.VPDoc.has-aside .container {
  max-width: 784px !important;
  margin: 0 auto !important;
  justify-content: center !important;
}

/* Override sidebar-induced left offset */
.VPContent.has-sidebar {
  padding-left: 0 !important;
}

.VPSidebar {
  display: none !important;
}

/* Make doc area full width so centering works */
.VPDoc.has-aside {
  padding: 0 32px !important;
}

/* Keep aside (outline + WikiSidebar) but position it relative to centered content */
.VPDoc.has-aside .container {
  display: flex !important;
  justify-content: center !important;
  gap: 2rem;
}
</style>
