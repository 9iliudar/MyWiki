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
