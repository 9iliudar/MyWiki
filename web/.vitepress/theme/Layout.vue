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
/* Center wiki page content */
.VPDoc .container {
  max-width: 100% !important;
  display: flex !important;
  justify-content: center !important;
}
.VPDoc .content-container {
  max-width: 784px !important;
  margin: 0 auto !important;
}
/* Hide empty sidebar space on wiki pages to allow true centering */
.VPContent.has-sidebar .VPDoc {
  padding-left: 0 !important;
}
</style>
