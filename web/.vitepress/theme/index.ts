import DefaultTheme from "vitepress/theme";
import "./custom.css";
import Layout from "./Layout.vue";
import WikiHome from "./components/WikiHome.vue";
import KnowledgeGraph from "./components/KnowledgeGraph.vue";
import Timeline from "./components/Timeline.vue";
import type { Theme } from "vitepress";

const theme: Theme = {
  extends: DefaultTheme,
  Layout,
  enhanceApp({ app }) {
    app.component("WikiHome", WikiHome);
    app.component("KnowledgeGraph", KnowledgeGraph);
    app.component("Timeline", Timeline);
  },
};

export default theme;
