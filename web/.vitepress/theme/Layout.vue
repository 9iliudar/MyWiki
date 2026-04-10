<script setup lang="ts">
import DefaultTheme from "vitepress/theme";
import WikiSidebar from "./components/WikiSidebar.vue";
import { useData } from "vitepress";

const { Layout } = DefaultTheme;
const { page } = useData();
</script>

<template>
  <Layout />
  <WikiSidebar
    v-if="page.relativePath.startsWith('pages/')"
    class="wiki-detail-rail"
  />
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

.VPSidebar,
.VPDoc .aside {
  display: none !important;
}

/* Make doc area full width so centering works */
.VPDoc.has-aside {
  padding: 24px 32px 0 !important;
}

/* Keep centered content width stable */
.VPDoc.has-aside .container {
  display: flex !important;
  justify-content: center !important;
  gap: 48px !important;
}

@media (min-width: 960px) {
  .VPDoc.has-aside .content {
    transform: translateX(-30px);
  }
}

.wiki-detail-rail {
  display: none;
}

@media (min-width: 960px) {
  .wiki-detail-rail {
    position: fixed;
    top: calc(var(--vp-nav-height, 64px) + 32px);
    right: max(24px, calc((100vw - 1180px) / 2));
    display: block;
    width: 248px;
    max-height: calc(100vh - var(--vp-nav-height, 64px) - 48px);
    overflow-y: auto;
    z-index: 20;
  }
}

/* Keep the detail page title vertically balanced */
.VPDoc.has-aside .vp-doc > h1:first-child,
.VPDoc.has-aside .vp-doc > div > h1:first-child {
  margin-top: 32px !important;
  margin-bottom: 32px !important;
}
</style>
