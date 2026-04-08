# MCP Server + VitePress Web UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expose the Wiki engine as an MCP Server for VS Code integration, and build a static VitePress site for wiki.iliudar.com.

**Architecture:** MCP Server wraps existing pipelines (IngestPipeline, QueryPipeline, LintPipeline) as stdio tools callable from VS Code Copilot/Claude Code. VitePress reads wiki/pages/*.md at build time and renders a static site with search, knowledge graph, and timeline.

**Tech Stack:** Python `mcp` SDK (stdio transport), VitePress 1.x, Vue 3, D3.js, TypeScript

---

## File Structure

### Phase 2: MCP Server
```
engine/mcp_server.py       — MCP Server entry point, registers 3 tools (NEW)
tests/test_mcp_server.py   — Unit tests for MCP tool handlers (NEW)
.vscode/mcp.json           — VS Code MCP configuration (NEW)
requirements.txt            — Add mcp dependency (MODIFY)
```

### Phase 3: VitePress Web UI
```
web/package.json                               — Node.js project config (NEW)
web/.vitepress/config.ts                       — VitePress site configuration (NEW)
web/.vitepress/theme/index.ts                  — Custom theme registration (NEW)
web/.vitepress/theme/Layout.vue                — Custom layout with sidebar (NEW)
web/.vitepress/theme/components/WikiHome.vue   — Home page: search + pulse + recent (NEW)
web/.vitepress/theme/components/WikiSidebar.vue — Page sidebar: related + sources + history (NEW)
web/.vitepress/theme/components/KnowledgeGraph.vue — D3.js force graph (NEW)
web/.vitepress/theme/components/Timeline.vue   — Timeline view (NEW)
web/.vitepress/plugins/wikilinks.ts            — [[双链]] → markdown link transformer (NEW)
web/scripts/prepare.ts                         — Build-time: copy pages + generate metadata (NEW)
web/index.md                                   — Home page entry (NEW)
web/explore.md                                 — Explore page entry (NEW)
web/timeline.md                                — Timeline page entry (NEW)
web/tsconfig.json                              — TypeScript config (NEW)
web/.gitignore                                 — Ignore node_modules, dist, generated pages (NEW)
```

---

## Phase 2: MCP Server

### Task 1: MCP Server Core

**Files:**
- Create: `engine/mcp_server.py`
- Create: `tests/test_mcp_server.py`
- Modify: `requirements.txt`

- [ ] **Step 1: Add mcp dependency**

Add `mcp>=1.0.0` to `requirements.txt`:

```
anthropic>=0.40.0
openai>=1.50.0
qdrant-client>=1.12.0
python-frontmatter>=1.1.0
PyYAML>=6.0.2
watchdog>=5.0.0
pytest>=8.0.0
mcp>=1.0.0
```

- [ ] **Step 2: Install the dependency**

Run: `pip install mcp>=1.0.0`
Expected: Successfully installed mcp

- [ ] **Step 3: Write the test file**

```python
# tests/test_mcp_server.py
import json
import pytest
from unittest.mock import MagicMock, patch
from engine.mcp_server import handle_ingest, handle_query, handle_lint


class MockLLM:
    def complete(self, prompt, context=""):
        return json.dumps({
            "summary": "测试摘要",
            "pages": [
                {"name": "Test-Page", "title": "测试页面", "tags": [], "related": [],
                 "content": "测试内容。", "is_new": True}
            ],
            "index_updates": "",
        })


class MockEmbedder:
    def embed(self, text):
        return [0.1] * 4


class MockVectorStore:
    def __init__(self):
        self.stored = {}
    def upsert(self, page_id, vector, metadata):
        self.stored[page_id] = {"vector": vector, "metadata": metadata}
    def search(self, query_vector, top_k=10):
        return []
    def count(self):
        return 0


@pytest.fixture
def wiki_env(tmp_path):
    pages_dir = tmp_path / "wiki" / "pages"
    pages_dir.mkdir(parents=True)
    inbox = tmp_path / "sources" / "inbox"
    inbox.mkdir(parents=True)
    archive = tmp_path / "sources" / "archived"
    archive.mkdir(parents=True)
    index_path = tmp_path / "wiki" / "index.md"
    index_path.write_text("# 导航\n", encoding="utf-8")
    log_path = tmp_path / "wiki" / "log.md"
    log_path.write_text("# 日志\n", encoding="utf-8")
    schema_path = tmp_path / "schema.md"
    schema_path.write_text("测试 schema", encoding="utf-8")
    return {
        "pages_dir": str(pages_dir),
        "index_path": str(index_path),
        "log_path": str(log_path),
        "schema_path": str(schema_path),
        "inbox_dir": str(inbox),
        "archive_dir": str(archive),
        "tmp_path": tmp_path,
    }


def test_handle_ingest(wiki_env):
    result = handle_ingest(
        content="RAG 是检索增强生成的缩写。",
        title="RAG 笔记",
        llm=MockLLM(),
        embedder=MockEmbedder(),
        vector_store=MockVectorStore(),
        wiki_env=wiki_env,
    )
    assert "Test-Page" in result
    assert "测试摘要" in result


def test_handle_query(wiki_env):
    result = handle_query(
        question="什么是 RAG？",
        llm=MockLLM(),
        embedder=MockEmbedder(),
        vector_store=MockVectorStore(),
        wiki_env=wiki_env,
    )
    # Query returns an answer string
    assert isinstance(result, str)


def test_handle_lint(wiki_env):
    result = handle_lint(
        llm=MockLLM(),
        embedder=MockEmbedder(),
        vector_store=MockVectorStore(),
        wiki_env=wiki_env,
    )
    assert "0" in result or "发现" in result
```

- [ ] **Step 4: Run tests to verify they fail**

Run: `python -m pytest tests/test_mcp_server.py -v`
Expected: FAIL with `ModuleNotFoundError` or `ImportError` (mcp_server.py doesn't exist yet)

- [ ] **Step 5: Implement mcp_server.py**

```python
# engine/mcp_server.py
"""MCP Server exposing Wiki engine tools for VS Code integration."""
import sys
import tempfile
from datetime import datetime
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from engine.config import load_config
from engine.llm import create_llm_provider
from engine.embed import VectorStore, Embedder
from engine.wiki_io import WikiIO
from engine.ingest import IngestPipeline
from engine.query import QueryPipeline
from engine.lint import LintPipeline

mcp = FastMCP("wiki-engine", instructions="LLM Wiki 知识进化引擎。提供知识消化(ingest)、查询(query)和巡检(lint)三个工具。当对话中出现新知识时调用 wiki_ingest，当用户询问已有知识时调用 wiki_query。")

# Lazy-loaded components
_components = {}


def _get_components():
    if not _components:
        config = load_config()
        _components["config"] = config
        _components["llm"] = create_llm_provider(config)
        _components["embedder"] = Embedder(
            api_key=config["embedding"].get("api_key", ""),
            model=config["embedding"]["model"],
            base_url=config["embedding"].get("base_url"),
            provider=config["embedding"].get("provider", "local"),
        )
        _components["vector_store"] = VectorStore(
            path=config["qdrant"]["path"],
            dimension=config["embedding"].get("dimensions", 1536),
        )
        _components["wiki"] = WikiIO(
            pages_dir=config["wiki"]["pages_dir"],
            index_path=config["wiki"]["index_path"],
            log_path=config["wiki"]["log_path"],
        )
    return _components


def handle_ingest(content: str, title: str = "", llm=None, embedder=None, vector_store=None, wiki_env: dict = None) -> str:
    """Core ingest logic, testable without MCP."""
    if wiki_env:
        wiki = WikiIO(wiki_env["pages_dir"], wiki_env["index_path"], wiki_env["log_path"])
        pipeline = IngestPipeline(
            llm=llm, embedder=embedder, vector_store=vector_store, wiki=wiki,
            schema_path=wiki_env["schema_path"],
            inbox_dir=wiki_env["inbox_dir"],
            archive_dir=wiki_env["archive_dir"],
        )
    else:
        c = _get_components()
        llm, embedder, vector_store = c["llm"], c["embedder"], c["vector_store"]
        wiki = c["wiki"]
        config = c["config"]
        pipeline = IngestPipeline(
            llm=llm, embedder=embedder, vector_store=vector_store, wiki=wiki,
            schema_path=config["wiki"]["schema_path"],
            inbox_dir=config["sources"]["inbox_dir"],
            archive_dir=config["sources"]["archive_dir"],
        )

    if not title:
        title = f"conversation-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    inbox_dir = Path(wiki_env["inbox_dir"] if wiki_env else _components["config"]["sources"]["inbox_dir"])
    source_file = inbox_dir / f"{title}.md"
    source_file.write_text(
        f"---\ntitle: {title}\ndate_added: {datetime.now().strftime('%Y-%m-%d')}\ntype: conversation\nstatus: raw\n---\n\n{content}",
        encoding="utf-8",
    )

    result = pipeline.ingest_file(str(source_file))
    pages = ", ".join(result["pages_affected"])
    return f"已消化，更新了 {len(result['pages_affected'])} 个页面：{pages}\n摘要：{result['summary']}"


def handle_query(question: str, llm=None, embedder=None, vector_store=None, wiki_env: dict = None) -> str:
    """Core query logic, testable without MCP."""
    if wiki_env:
        wiki = WikiIO(wiki_env["pages_dir"], wiki_env["index_path"], wiki_env["log_path"])
        pipeline = QueryPipeline(llm=llm, embedder=embedder, vector_store=vector_store, wiki=wiki)
    else:
        c = _get_components()
        pipeline = QueryPipeline(llm=c["llm"], embedder=c["embedder"], vector_store=c["vector_store"], wiki=c["wiki"])

    result = pipeline.query(question)
    answer = result["answer"]
    if result.get("saved_page"):
        answer += f"\n\n📝 已保存新页面：{result['saved_page']}"
    if result.get("sources"):
        answer += f"\n📖 参考页面：{', '.join(result['sources'])}"
    return answer


def handle_lint(llm=None, embedder=None, vector_store=None, wiki_env: dict = None) -> str:
    """Core lint logic, testable without MCP."""
    if wiki_env:
        wiki = WikiIO(wiki_env["pages_dir"], wiki_env["index_path"], wiki_env["log_path"])
        pipeline = LintPipeline(llm=llm, embedder=embedder, vector_store=vector_store, wiki=wiki)
    else:
        c = _get_components()
        pipeline = LintPipeline(llm=c["llm"], embedder=c["embedder"], vector_store=c["vector_store"], wiki=c["wiki"])

    result = pipeline.run()
    lines = [f"发现 {len(result['findings'])} 个问题，修正了 {result['fixes_applied']} 个。"]
    for f in result.get("findings", []):
        lines.append(f"  - [{f.get('type', '未知')}] {f.get('description', '')}")
    return "\n".join(lines)


@mcp.tool()
def wiki_ingest(content: str, title: str = "") -> str:
    """消化新知识到 Wiki。当对话中出现值得记录的新知识、概念或见解时调用此工具。

    Args:
        content: 要消化的知识内容（文本）
        title: 来源标题（可选，默认自动生成）
    """
    return handle_ingest(content, title)


@mcp.tool()
def wiki_query(question: str) -> str:
    """基于 Wiki 已有知识回答问题。当用户询问之前学过的内容、想查阅已有知识时调用此工具。

    Args:
        question: 自然语言问题
    """
    return handle_query(question)


@mcp.tool()
def wiki_lint() -> str:
    """Wiki 健康检查。检查知识库的矛盾、孤岛页面、缺失引用等问题并自动修复。"""
    return handle_lint()


if __name__ == "__main__":
    mcp.run(transport="stdio")
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `python -m pytest tests/test_mcp_server.py -v`
Expected: 3 tests PASS

- [ ] **Step 7: Run all existing tests to verify no regressions**

Run: `python -m pytest tests/ -v`
Expected: 28 tests PASS (25 existing + 3 new)

- [ ] **Step 8: Commit**

```bash
git add engine/mcp_server.py tests/test_mcp_server.py requirements.txt
git commit -m "feat: add MCP Server wrapping wiki engine tools"
```

### Task 2: VS Code MCP Configuration

**Files:**
- Create: `.vscode/mcp.json`

- [ ] **Step 1: Create .vscode directory if needed**

Run: `ls .vscode/ 2>/dev/null || mkdir .vscode`

- [ ] **Step 2: Create the MCP config file**

```json
{
  "servers": {
    "wiki-engine": {
      "command": "python",
      "args": ["engine/mcp_server.py"],
      "cwd": "D:/Project/MyWiki"
    }
  }
}
```

- [ ] **Step 3: Verify MCP server starts without errors**

Run: `echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"0.1.0"}}}' | python engine/mcp_server.py`
Expected: JSON response containing `"serverInfo"` with name `"wiki-engine"`

- [ ] **Step 4: Commit**

```bash
git add .vscode/mcp.json
git commit -m "feat: add VS Code MCP configuration for wiki engine"
```

---

## Phase 3: VitePress Web UI

### Task 3: VitePress Project Scaffold

**Files:**
- Create: `web/package.json`
- Create: `web/tsconfig.json`
- Create: `web/.gitignore`
- Create: `web/.vitepress/config.ts`

- [ ] **Step 1: Initialize the web project**

```json
// web/package.json
{
  "name": "mywiki-web",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "prepare": "ts-node scripts/prepare.ts",
    "dev": "npm run prepare && vitepress dev",
    "build": "npm run prepare && vitepress build",
    "preview": "vitepress preview"
  },
  "devDependencies": {
    "vitepress": "^1.6.0",
    "vue": "^3.5.0",
    "ts-node": "^10.9.0",
    "typescript": "^5.7.0",
    "d3": "^7.9.0",
    "@types/d3": "^7.4.0",
    "gray-matter": "^4.0.3"
  }
}
```

- [ ] **Step 2: Create tsconfig.json**

```json
// web/tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "jsx": "preserve"
  },
  "include": ["**/*.ts", "**/*.vue"]
}
```

- [ ] **Step 3: Create .gitignore**

```
# web/.gitignore
node_modules/
.vitepress/dist/
.vitepress/cache/
pages/
data/
```

- [ ] **Step 4: Create VitePress config**

```typescript
// web/.vitepress/config.ts
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
      // [[双链]] plugin
      const wikilinkRe = /\[\[([^\]]+)\]\]/g;
      const defaultRender =
        md.renderer.rules.text ||
        ((tokens, idx) => tokens[idx].content);

      md.renderer.rules.text = (tokens, idx, options, env, self) => {
        const content = tokens[idx].content;
        if (wikilinkRe.test(content)) {
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
```

- [ ] **Step 5: Install dependencies**

Run: `cd web && npm install`
Expected: node_modules created, no errors

- [ ] **Step 6: Commit**

```bash
git add web/package.json web/tsconfig.json web/.gitignore web/.vitepress/config.ts
git commit -m "feat: scaffold VitePress project for wiki web UI"
```

### Task 4: Build-Time Prepare Script

**Files:**
- Create: `web/scripts/prepare.ts`

- [ ] **Step 1: Create the prepare script**

```typescript
// web/scripts/prepare.ts
import * as fs from "fs";
import * as path from "path";
import matter from "gray-matter";

const WIKI_PAGES_DIR = path.resolve(__dirname, "../../wiki/pages");
const WEB_PAGES_DIR = path.resolve(__dirname, "../pages");
const DATA_DIR = path.resolve(__dirname, "../data");

interface PageMeta {
  name: string;
  title: string;
  tags: string[];
  related: string[];
  sources: string[];
  created: string;
  updated: string;
  evolution: string[];
}

function ensureDir(dir: string) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

function main() {
  ensureDir(WEB_PAGES_DIR);
  ensureDir(DATA_DIR);

  const files = fs.readdirSync(WIKI_PAGES_DIR).filter((f) => f.endsWith(".md"));
  const allMeta: PageMeta[] = [];

  for (const file of files) {
    const srcPath = path.join(WIKI_PAGES_DIR, file);
    const content = fs.readFileSync(srcPath, "utf-8");
    const { data } = matter(content);

    const name = file.replace(/\.md$/, "");
    allMeta.push({
      name,
      title: data.title || name,
      tags: data.tags || [],
      related: data.related || [],
      sources: data.sources || [],
      created: data.created || "",
      updated: data.updated || "",
      evolution: data.evolution || [],
    });

    // Copy file to web/pages/
    fs.copyFileSync(srcPath, path.join(WEB_PAGES_DIR, file));
  }

  // Write metadata JSON for Vue components
  fs.writeFileSync(
    path.join(DATA_DIR, "wiki-meta.json"),
    JSON.stringify(allMeta, null, 2),
    "utf-8"
  );

  // Build graph data (nodes + edges from related fields)
  const nodes = allMeta.map((p) => ({ id: p.name, title: p.title, tags: p.tags }));
  const edges: { source: string; target: string }[] = [];
  for (const page of allMeta) {
    for (const rel of page.related) {
      // related may be "[[PageName]]" or just "PageName"
      const target = rel.replace(/^\[\[/, "").replace(/\]\]$/, "");
      if (allMeta.some((p) => p.name === target)) {
        edges.push({ source: page.name, target });
      }
    }
  }
  fs.writeFileSync(
    path.join(DATA_DIR, "graph.json"),
    JSON.stringify({ nodes, edges }, null, 2),
    "utf-8"
  );

  console.log(`Prepared ${files.length} pages, ${edges.length} edges`);
}

main();
```

- [ ] **Step 2: Test the prepare script**

Run: `cd web && npx ts-node scripts/prepare.ts`
Expected: Output like `Prepared 11 pages, X edges`. Check that `web/pages/` has 11 .md files and `web/data/wiki-meta.json` exists.

- [ ] **Step 3: Commit**

```bash
git add web/scripts/prepare.ts
git commit -m "feat: add build-time prepare script for copying wiki pages"
```

### Task 5: Home Page

**Files:**
- Create: `web/index.md`
- Create: `web/.vitepress/theme/index.ts`
- Create: `web/.vitepress/theme/components/WikiHome.vue`

- [ ] **Step 1: Create custom theme entry**

```typescript
// web/.vitepress/theme/index.ts
import DefaultTheme from "vitepress/theme";
import WikiHome from "./components/WikiHome.vue";
import WikiSidebar from "./components/WikiSidebar.vue";
import type { Theme } from "vitepress";

const theme: Theme = {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component("WikiHome", WikiHome);
    app.component("WikiSidebar", WikiSidebar);
  },
};

export default theme;
```

- [ ] **Step 2: Create WikiHome component**

```vue
<!-- web/.vitepress/theme/components/WikiHome.vue -->
<script setup lang="ts">
import { ref, computed, onMounted } from "vue";

interface PageMeta {
  name: string;
  title: string;
  tags: string[];
  updated: string;
  evolution: string[];
}

const pages = ref<PageMeta[]>([]);

onMounted(async () => {
  try {
    const data = await import("../../../data/wiki-meta.json");
    pages.value = data.default || data;
  } catch {
    pages.value = [];
  }
});

const recentPages = computed(() =>
  [...pages.value]
    .sort((a, b) => (b.updated || "").localeCompare(a.updated || ""))
    .slice(0, 10)
);

const totalPages = computed(() => pages.value.length);

const allTags = computed(() => {
  const tags = new Set<string>();
  pages.value.forEach((p) => p.tags.forEach((t) => tags.add(t)));
  return tags.size;
});

const latestUpdate = computed(() => {
  if (!pages.value.length) return "暂无";
  return recentPages.value[0]?.updated || "暂无";
});
</script>

<template>
  <div class="wiki-home">
    <div class="pulse">
      <span>📄 {{ totalPages }} 页面</span>
      <span>🏷️ {{ allTags }} 标签</span>
      <span>🕐 最近更新 {{ latestUpdate }}</span>
    </div>

    <h2>最近进化</h2>
    <ul class="recent-list">
      <li v-for="page in recentPages" :key="page.name">
        <a :href="`/pages/${page.name}.html`">{{ page.title }}</a>
        <span class="date">{{ page.updated }}</span>
        <span class="evolution" v-if="page.evolution.length">
          — {{ page.evolution[page.evolution.length - 1] }}
        </span>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.wiki-home {
  max-width: 720px;
  margin: 0 auto;
  padding: 2rem 1rem;
}
.pulse {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 2rem;
  padding: 1rem;
  background: var(--vp-c-bg-soft);
  border-radius: 8px;
  font-size: 0.95rem;
}
.recent-list {
  list-style: none;
  padding: 0;
}
.recent-list li {
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--vp-c-divider);
}
.recent-list a {
  font-weight: 500;
}
.date {
  color: var(--vp-c-text-2);
  font-size: 0.85rem;
  margin-left: 0.5rem;
}
.evolution {
  color: var(--vp-c-text-3);
  font-size: 0.85rem;
}
</style>
```

- [ ] **Step 3: Create home page entry**

```markdown
---
layout: home
title: MyWiki - 个人知识进化引擎
---

<WikiHome />
```

- [ ] **Step 4: Test locally**

Run: `cd web && npm run dev`
Expected: VitePress dev server starts. Open the URL in browser, see the home page with knowledge pulse and recent pages list.

- [ ] **Step 5: Commit**

```bash
git add web/index.md web/.vitepress/theme/index.ts web/.vitepress/theme/components/WikiHome.vue
git commit -m "feat: add wiki home page with knowledge pulse and recent pages"
```

### Task 6: Page Sidebar Component

**Files:**
- Create: `web/.vitepress/theme/components/WikiSidebar.vue`
- Create: `web/.vitepress/theme/Layout.vue`

- [ ] **Step 1: Create WikiSidebar component**

```vue
<!-- web/.vitepress/theme/components/WikiSidebar.vue -->
<script setup lang="ts">
import { computed } from "vue";
import { useData } from "vitepress";

const { frontmatter } = useData();

const related = computed(() => {
  const list = frontmatter.value.related || [];
  return list.map((r: string) => {
    const name = r.replace(/^\[\[/, "").replace(/\]\]$/, "");
    return { name, href: `/pages/${name}.html` };
  });
});

const sources = computed(() => frontmatter.value.sources || []);
const tags = computed(() => frontmatter.value.tags || []);
const evolution = computed(() => (frontmatter.value.evolution || []).slice().reverse());
</script>

<template>
  <aside class="wiki-sidebar" v-if="frontmatter.title">
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
}
.wiki-sidebar h4 {
  margin: 1rem 0 0.5rem;
  font-size: 0.9rem;
  color: var(--vp-c-text-2);
}
.wiki-sidebar ul {
  list-style: none;
  padding: 0;
}
.wiki-sidebar li {
  padding: 0.2rem 0;
}
.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}
.tag {
  background: var(--vp-c-bg-soft);
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
}
.source {
  color: var(--vp-c-text-3);
  font-size: 0.8rem;
}
.evolution li {
  color: var(--vp-c-text-3);
  border-left: 2px solid var(--vp-c-divider);
  padding-left: 0.5rem;
  margin-bottom: 0.3rem;
}
</style>
```

- [ ] **Step 2: Create custom Layout**

```vue
<!-- web/.vitepress/theme/Layout.vue -->
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
```

- [ ] **Step 3: Update theme to use custom Layout**

Update `web/.vitepress/theme/index.ts`:

```typescript
// web/.vitepress/theme/index.ts
import DefaultTheme from "vitepress/theme";
import Layout from "./Layout.vue";
import WikiHome from "./components/WikiHome.vue";
import type { Theme } from "vitepress";

const theme: Theme = {
  extends: DefaultTheme,
  Layout,
  enhanceApp({ app }) {
    app.component("WikiHome", WikiHome);
  },
};

export default theme;
```

- [ ] **Step 4: Test by viewing a wiki page**

Run: `cd web && npm run dev`
Expected: Navigate to a page like `/pages/LLM-Wiki.html`. See the markdown content rendered with the sidebar showing tags, related pages, sources, and evolution history.

- [ ] **Step 5: Commit**

```bash
git add web/.vitepress/theme/components/WikiSidebar.vue web/.vitepress/theme/Layout.vue web/.vitepress/theme/index.ts
git commit -m "feat: add wiki page sidebar with related, sources, and evolution"
```

### Task 7: Knowledge Graph (Explore Page)

**Files:**
- Create: `web/.vitepress/theme/components/KnowledgeGraph.vue`
- Create: `web/explore.md`

- [ ] **Step 1: Create KnowledgeGraph component**

```vue
<!-- web/.vitepress/theme/components/KnowledgeGraph.vue -->
<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";
import * as d3 from "d3";

interface GraphNode extends d3.SimulationNodeDatum {
  id: string;
  title: string;
  tags: string[];
}

interface GraphEdge {
  source: string | GraphNode;
  target: string | GraphNode;
}

const container = ref<HTMLDivElement | null>(null);
let simulation: d3.Simulation<GraphNode, GraphEdge> | null = null;

onMounted(async () => {
  if (!container.value) return;

  let graphData: { nodes: GraphNode[]; edges: GraphEdge[] };
  try {
    const data = await import("../../../data/graph.json");
    graphData = data.default || data;
  } catch {
    return;
  }

  const width = container.value.clientWidth;
  const height = 500;

  const svg = d3
    .select(container.value)
    .append("svg")
    .attr("width", width)
    .attr("height", height)
    .attr("viewBox", [0, 0, width, height]);

  // Count connections per node for sizing
  const connectionCount: Record<string, number> = {};
  graphData.nodes.forEach((n) => (connectionCount[n.id] = 0));
  graphData.edges.forEach((e) => {
    const src = typeof e.source === "string" ? e.source : e.source.id;
    const tgt = typeof e.target === "string" ? e.target : e.target.id;
    connectionCount[src] = (connectionCount[src] || 0) + 1;
    connectionCount[tgt] = (connectionCount[tgt] || 0) + 1;
  });

  simulation = d3
    .forceSimulation<GraphNode>(graphData.nodes)
    .force(
      "link",
      d3
        .forceLink<GraphNode, GraphEdge>(graphData.edges)
        .id((d) => d.id)
        .distance(80)
    )
    .force("charge", d3.forceManyBody().strength(-200))
    .force("center", d3.forceCenter(width / 2, height / 2));

  const link = svg
    .append("g")
    .selectAll("line")
    .data(graphData.edges)
    .join("line")
    .attr("stroke", "var(--vp-c-divider)")
    .attr("stroke-width", 1);

  const node = svg
    .append("g")
    .selectAll("circle")
    .data(graphData.nodes)
    .join("circle")
    .attr("r", (d) => 5 + (connectionCount[d.id] || 0) * 2)
    .attr("fill", "var(--vp-c-brand-1)")
    .attr("cursor", "pointer")
    .on("click", (_, d) => {
      window.location.href = `/pages/${d.id}.html`;
    })
    .call(
      d3
        .drag<SVGCircleElement, GraphNode>()
        .on("start", (event, d) => {
          if (!event.active) simulation!.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on("drag", (event, d) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on("end", (event, d) => {
          if (!event.active) simulation!.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        })
    );

  const label = svg
    .append("g")
    .selectAll("text")
    .data(graphData.nodes)
    .join("text")
    .text((d) => d.title)
    .attr("font-size", "11px")
    .attr("dx", 10)
    .attr("dy", 4)
    .attr("fill", "var(--vp-c-text-1)");

  simulation.on("tick", () => {
    link
      .attr("x1", (d: any) => d.source.x)
      .attr("y1", (d: any) => d.source.y)
      .attr("x2", (d: any) => d.target.x)
      .attr("y2", (d: any) => d.target.y);
    node.attr("cx", (d: any) => d.x).attr("cy", (d: any) => d.y);
    label.attr("x", (d: any) => d.x).attr("y", (d: any) => d.y);
  });
});

onUnmounted(() => {
  simulation?.stop();
});
</script>

<template>
  <div class="knowledge-graph">
    <h1>知识图谱</h1>
    <div ref="container" class="graph-container"></div>
  </div>
</template>

<style scoped>
.knowledge-graph {
  max-width: 960px;
  margin: 0 auto;
  padding: 1rem;
}
.graph-container {
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  overflow: hidden;
  min-height: 500px;
}
</style>
```

- [ ] **Step 2: Create explore page**

```markdown
---
layout: page
title: 探索知识图谱
---

<script setup>
import KnowledgeGraph from './.vitepress/theme/components/KnowledgeGraph.vue'
</script>

<KnowledgeGraph />
```

- [ ] **Step 3: Register KnowledgeGraph in theme**

Update `web/.vitepress/theme/index.ts`:

```typescript
// web/.vitepress/theme/index.ts
import DefaultTheme from "vitepress/theme";
import Layout from "./Layout.vue";
import WikiHome from "./components/WikiHome.vue";
import KnowledgeGraph from "./components/KnowledgeGraph.vue";
import type { Theme } from "vitepress";

const theme: Theme = {
  extends: DefaultTheme,
  Layout,
  enhanceApp({ app }) {
    app.component("WikiHome", WikiHome);
    app.component("KnowledgeGraph", KnowledgeGraph);
  },
};

export default theme;
```

- [ ] **Step 4: Test the explore page**

Run: `cd web && npm run dev`
Expected: Navigate to `/explore`. See an interactive force-directed graph with wiki page nodes and edges. Nodes are clickable and draggable.

- [ ] **Step 5: Commit**

```bash
git add web/.vitepress/theme/components/KnowledgeGraph.vue web/explore.md web/.vitepress/theme/index.ts
git commit -m "feat: add knowledge graph explore page with D3.js"
```

### Task 8: Timeline Page

**Files:**
- Create: `web/.vitepress/theme/components/Timeline.vue`
- Create: `web/timeline.md`

- [ ] **Step 1: Create Timeline component**

```vue
<!-- web/.vitepress/theme/components/Timeline.vue -->
<script setup lang="ts">
import { ref, computed, onMounted } from "vue";

interface PageMeta {
  name: string;
  title: string;
  created: string;
  updated: string;
  evolution: string[];
}

const pages = ref<PageMeta[]>([]);

onMounted(async () => {
  try {
    const data = await import("../../../data/wiki-meta.json");
    pages.value = data.default || data;
  } catch {
    pages.value = [];
  }
});

const sortedPages = computed(() =>
  [...pages.value].sort((a, b) => (b.updated || "").localeCompare(a.updated || ""))
);
</script>

<template>
  <div class="timeline-view">
    <h1>知识时间线</h1>
    <div class="timeline">
      <div v-for="page in sortedPages" :key="page.name" class="timeline-item">
        <div class="date-col">{{ page.updated || page.created }}</div>
        <div class="content-col">
          <a :href="`/pages/${page.name}.html`" class="page-title">{{ page.title }}</a>
          <ul class="evo-list" v-if="page.evolution.length">
            <li v-for="(e, i) in page.evolution.slice().reverse().slice(0, 3)" :key="i">
              {{ e }}
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.timeline-view {
  max-width: 720px;
  margin: 0 auto;
  padding: 1rem;
}
.timeline-item {
  display: flex;
  gap: 1rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--vp-c-divider);
}
.date-col {
  min-width: 100px;
  color: var(--vp-c-text-2);
  font-size: 0.85rem;
  padding-top: 0.15rem;
}
.page-title {
  font-weight: 500;
  font-size: 1rem;
}
.evo-list {
  list-style: none;
  padding: 0;
  margin: 0.3rem 0 0;
}
.evo-list li {
  font-size: 0.8rem;
  color: var(--vp-c-text-3);
  padding: 0.1rem 0;
}
</style>
```

- [ ] **Step 2: Create timeline page**

```markdown
---
layout: page
title: 知识时间线
---

<script setup>
import Timeline from './.vitepress/theme/components/Timeline.vue'
</script>

<Timeline />
```

- [ ] **Step 3: Register Timeline in theme**

Update `web/.vitepress/theme/index.ts`:

```typescript
// web/.vitepress/theme/index.ts
import DefaultTheme from "vitepress/theme";
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
```

- [ ] **Step 4: Test the timeline page**

Run: `cd web && npm run dev`
Expected: Navigate to `/timeline`. See all wiki pages listed by update date with evolution history.

- [ ] **Step 5: Commit**

```bash
git add web/.vitepress/theme/components/Timeline.vue web/timeline.md web/.vitepress/theme/index.ts
git commit -m "feat: add timeline page showing knowledge evolution"
```

### Task 9: Full Build Test + Vercel Config

**Files:**
- Create: `web/vercel.json` (optional, for explicit config)

- [ ] **Step 1: Run full build**

Run: `cd web && npm run build`
Expected: Build completes without errors. Output in `web/.vitepress/dist/`.

- [ ] **Step 2: Preview the built site**

Run: `cd web && npm run preview`
Expected: Opens a preview server. Navigate through all pages:
- Home page: search box, knowledge pulse, recent pages
- A wiki page (e.g., /pages/LLM-Wiki): content rendered, sidebar visible
- Explore: knowledge graph renders with interactive nodes
- Timeline: pages listed by date

- [ ] **Step 3: Commit the full web project**

```bash
git add web/
git commit -m "feat: complete VitePress web UI with home, explore, timeline"
```

### Task 10: E2E Integration Test

- [ ] **Step 1: Test MCP ingest → Obsidian → Web flow**

1. Start MCP server manually to test:
```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"0.1.0"}}}' | python engine/mcp_server.py
```
Expected: Server responds with initialization confirmation.

2. Verify wiki/pages/ has content (already has 11 pages from Phase 1).

3. Run web build:
```bash
cd web && npm run build
```
Expected: 11 pages rendered, graph.json has nodes and edges.

4. Preview and check all four page types work.

- [ ] **Step 2: Run all Python tests**

Run: `python -m pytest tests/ -v`
Expected: All tests pass (25 existing + 3 MCP = 28 total).

- [ ] **Step 3: Final commit**

```bash
git add -A
git commit -m "feat: complete Phase 2 (MCP) and Phase 3 (Web UI) implementation"
```
