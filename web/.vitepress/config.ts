import fs from "fs";
import path from "path";
import { defineConfig } from "vitepress";

const routeMapPath = path.resolve(__dirname, "../data/route-map.json");

function loadRouteMap() {
  if (!fs.existsSync(routeMapPath)) {
    return { routeByName: {}, routeByTitle: {} };
  }
  return JSON.parse(fs.readFileSync(routeMapPath, "utf-8"));
}

export default defineConfig({
  title: "MyWiki",
  description: "个人知识进化引擎",
  lang: "zh-CN",
  srcDir: ".",
  outDir: ".vitepress/dist",

  themeConfig: {
    nav: [
      { text: "首页", link: "/" },
      { text: "探索", link: "/explore" },
      { text: "时间线", link: "/timeline" },
    ],
    search: {
      provider: "local",
    },
    outline: {
      level: [2, 3],
      label: "目录",
    },
  },

  transformPageData(pageData) {
    if (pageData.relativePath.startsWith("pages/") && pageData.frontmatter.title) {
      pageData.title = pageData.frontmatter.title;
    }
  },

  markdown: {
    config: (md) => {
      const wikilinkRe = /\[\[([^\]]+)\]\]/g;
      const defaultRender = md.renderer.rules.text || ((tokens, idx) => tokens[idx].content);
      md.renderer.rules.text = (tokens, idx, options, env, self) => {
        const content = tokens[idx].content;
        if (!wikilinkRe.test(content)) {
          return defaultRender(tokens, idx, options, env, self);
        }

        wikilinkRe.lastIndex = 0;
        const routeMap = loadRouteMap();
        return content.replace(wikilinkRe, (_, pageName) => {
          const slug = pageName.trim();
          const href = routeMap.routeByName[slug] || routeMap.routeByTitle[slug] || `/pages/${slug}.html`;
          return `<a href="${href}">${slug}</a>`;
        });
      };
    },
  },
});
