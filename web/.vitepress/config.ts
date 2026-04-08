import { defineConfig } from "vitepress";

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

  markdown: {
    config: (md) => {
      const wikilinkRe = /\[\[([^\]]+)\]\]/g;
      const defaultRender = md.renderer.rules.text || ((tokens, idx) => tokens[idx].content);
      md.renderer.rules.text = (tokens, idx, options, env, self) => {
        const content = tokens[idx].content;
        if (wikilinkRe.test(content)) {
          wikilinkRe.lastIndex = 0;
          return content.replace(wikilinkRe, (_, pageName) => {
            const slug = pageName.trim();
            return `<a href="/pages/${slug}.html">${slug}</a>`;
          });
        }
        return defaultRender(tokens, idx, options, env, self);
      };
    },
  },
});
