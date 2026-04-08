# MCP Server + 静态 Web UI 设计文档

> Phase 2（MCP Server 对话入口）和 Phase 3（VitePress 静态 Web UI）的联合设计。

## 1. 背景与目标

Phase 1 已完成 Wiki 引擎核心（ingest/query/lint），但用户需要通过 CLI 命令手动操作。目标是：

- **Phase 2**：将引擎包装为 MCP Server，在 VS Code 中通过 Copilot / Claude Code 插件无感调用
- **Phase 3**：将 wiki/pages/ 渲染为静态网站，部署到 wiki.iliudar.com

### 核心体验

```
VS Code 对话（任意模型）
  → AI 自动判断是否有新知识
  → 调用 MCP 工具写入 Wiki
  → 回复末尾通知用户"已更新 XX.md"
  → Obsidian 实时看到更新
  → git push → wiki.iliudar.com 自动更新
```

## 2. Phase 2: MCP Server

### 2.1 架构

使用 Python stdio 传输的 MCP Server。VS Code 在打开项目时自动启动进程，关闭时自动停止。

```
VS Code
  ├── GitHub Copilot ──┐
  └── Claude Code ─────┤
                       ▼
              MCP Server (stdio)
              engine/mcp_server.py
                ├── wiki_ingest()  → IngestPipeline
                ├── wiki_query()   → QueryPipeline
                └── wiki_lint()    → LintPipeline
                        ▼
                  wiki/pages/ + vectors/ + log.md
```

### 2.2 MCP 工具定义

#### wiki_ingest

消化新知识到 Wiki。

- **输入参数**：
  - `content` (string, 必填): 要消化的知识内容
  - `title` (string, 可选): 来源标题，默认自动生成
- **行为**：
  1. 将 content 写入临时 .md 文件到 sources/inbox/
  2. 调用 IngestPipeline.ingest_file()
  3. 返回结果
- **返回**：影响的页面列表 + 摘要
- **返回示例**：`"已消化，更新了 3 个页面：RAG.md、向量数据库.md（新建）、LLM.md"`
- **AI 调用时机**：对话中出现新知识、新概念、新见解时

#### wiki_query

基于 Wiki 已有知识回答问题。

- **输入参数**：
  - `question` (string, 必填): 自然语言问题
- **行为**：
  1. 调用 QueryPipeline.query()
  2. 语义搜索相关页面 + LLM 合成回答
  3. 如有新知识自动写回 Wiki
- **返回**：答案 + 引用的页面列表
- **AI 调用时机**：用户问"我之前学过的 XX"、"Wiki 里有 XX 吗"

#### wiki_lint

Wiki 健康检查。

- **输入参数**：无
- **行为**：调用 LintPipeline.run()
- **返回**：发现的问题数 + 修复数 + 详情
- **AI 调用时机**：用户说"检查 Wiki"、"Wiki 状态怎么样"

### 2.3 MCP 配置

项目级配置文件 `.vscode/mcp.json`：

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

GitHub Copilot 和 Claude Code 插件均读取此配置，一次配置两个都可用。

### 2.4 通知机制

MCP 工具返回结构化结果后，AI 在回复末尾自然提及。不弹窗、不打断对话流。

示例：
```
用户：今天研究了 RAG，发现检索质量比生成质量更重要...
AI：关于 RAG，你说的对...（正常讨论）
    📝 已更新 Wiki：RAG.md 补充了检索质量分析
```

### 2.5 兜底路径

如果使用不支持 MCP 的 AI 工具：
- 手动将文件放入 `sources/inbox/`
- watch.py 自动检测并消化（已在 Phase 1 实现）

### 2.6 技术依赖

- `mcp` Python SDK（官方包）
- 复用 Phase 1 全部引擎代码（IngestPipeline, QueryPipeline, LintPipeline, LLMProvider, Embedder, VectorStore, WikiIO）

### 2.7 新增文件

```
engine/mcp_server.py     MCP Server 入口，注册三个工具
.vscode/mcp.json         VS Code MCP 配置
```

## 3. Phase 3: VitePress 静态 Web UI

### 3.1 架构

纯静态站。构建时从 wiki/pages/ 读取 .md 文件，渲染为 HTML，部署到 Vercel。

```
wiki/pages/*.md
      ↓ (构建时复制)
web/pages/*.md
      ↓ (VitePress build)
静态 HTML/CSS/JS
      ↓ (Vercel 部署)
wiki.iliudar.com
```

无后端、无 API、无数据库、无服务器。

### 3.2 页面结构

#### 首页 (/)

- **搜索框**：VitePress 内置 minisearch，全文搜索，零配置
- **最近进化**：从各页面 frontmatter 的 `updated` + `evolution` 字段提取，展示最近更新的页面
- **知识脉搏**：页面总数、标签总数、最近更新时间

#### 页面视图 (/pages/XXX)

- VitePress 自动渲染 Markdown 正文
- 侧边栏展示 frontmatter 信息：
  - 关联页面（`related` 字段，可点击跳转）
  - 来源溯源（`sources` 字段）
  - 标签（`tags` 字段）
  - 进化历史（`evolution` 字段）
- `[[双链]]` 转换为可点击链接

#### 探索视图 (/explore)

- **知识图谱**：Vue 组件 + D3.js force-directed graph
  - 节点 = 页面，边 = related 关系
  - 节点大小 = 关联数量
  - 点击节点跳转到页面
- **标签筛选**：从所有页面的 tags 聚合，点击标签过滤页面列表

#### 时间线 (/timeline)

- 所有页面按 `updated` 倒序排列
- 展示每个页面的 evolution 历史
- 可视化知识的生长轨迹

### 3.3 双链解析

自定义 markdown-it 插件，在 VitePress 构建时将 `[[页面名]]` 转换为标准 Markdown 链接：

```
[[RAG]] → [RAG](/pages/RAG)
[[三层架构]] → [三层架构](/pages/Three-Layer-Architecture)
```

映射规则：Wiki 页面文件名即为链接名（如 `RAG.md` 对应 `[[RAG]]`，`Three-Layer-Architecture.md` 对应 `[[Three-Layer-Architecture]]`）。frontmatter 的 `title` 字段用于页面显示标题。`prepare.ts` 构建时生成文件名→标题的映射表，供双链插件将 `[[文件名]]` 转换为 `[显示标题](/pages/文件名)`。

### 3.4 项目结构

```
web/
├── package.json
├── .vitepress/
│   ├── config.ts              VitePress 配置（站点标题、导航、搜索）
│   ├── theme/
│   │   ├── index.ts           自定义主题（扩展默认主题）
│   │   ├── Layout.vue         自定义布局（首页 + 页面侧边栏）
│   │   └── components/
│   │       ├── WikiHome.vue       首页组件（搜索+脉搏+最近进化）
│   │       ├── WikiSidebar.vue    页面侧边栏（关联+溯源+历史）
│   │       ├── KnowledgeGraph.vue 知识图谱（D3.js）
│   │       └── Timeline.vue      时间线组件
│   └── plugins/
│       └── wikilinks.ts       [[双链]] 解析插件
├── index.md                   首页
├── explore.md                 探索页
├── timeline.md                时间线页
├── pages/                     ← 构建时从 wiki/pages/ 复制
└── scripts/
    └── prepare.ts             构建前复制 wiki/pages/ 并生成元数据索引
```

### 3.5 构建流程

```bash
# package.json scripts
{
  "prepare": "ts-node scripts/prepare.ts",    # 复制 wiki/pages/ → web/pages/ + 生成元数据
  "dev": "npm run prepare && vitepress dev",
  "build": "npm run prepare && vitepress build"
}
```

`prepare.ts` 做两件事：
1. 复制 `wiki/pages/*.md` 到 `web/pages/`
2. 从所有页面的 frontmatter 提取元数据，生成 `data/wiki-meta.json`（供首页、图谱、时间线使用）

### 3.6 部署

- **平台**：Vercel 免费套餐
- **域名**：wiki.iliudar.com（在 Vercel 或 DNS 中配置 CNAME）
- **触发**：git push 到 GitHub → Vercel Webhook 自动构建部署
- **Vercel 配置**：
  - Root Directory: `web`
  - Build Command: `npm run build`
  - Output Directory: `.vitepress/dist`

### 3.7 不做什么

- 不做在线编辑（本地对话负责写入）
- 不做文件上传 / 入库功能
- 不做 AI 对话界面
- 不做后端 API
- 不做用户登录 / 权限系统
- 不做服务端渲染（SSR）

## 4. 整体数据流

```
用户在 VS Code 与 AI 对话
        │
        ▼
AI 判断有新知识 → 调用 MCP wiki_ingest
        │
        ▼
MCP Server → IngestPipeline
        │
        ├── wiki/pages/*.md 更新
        ├── vectors/ 更新
        └── wiki/log.md 追加记录
        │
        ▼
Obsidian 打开 wiki/pages/ → 实时查看（本地）
        │
        ▼
用户 git push → GitHub
        │
        ▼
Vercel 自动构建 VitePress → wiki.iliudar.com 更新（远程）
```

## 5. 与 Phase 1 的关系

Phase 2 和 Phase 3 完全复用 Phase 1 的引擎代码，不修改任何已有模块：

| Phase 1（已完成） | Phase 2（MCP） | Phase 3（Web UI） |
|---|---|---|
| IngestPipeline | MCP 工具调用它 | 不涉及 |
| QueryPipeline | MCP 工具调用它 | 不涉及 |
| LintPipeline | MCP 工具调用它 | 不涉及 |
| wiki/pages/*.md | 被 MCP 写入 | 被 VitePress 读取 |
| LLMProvider | 被 MCP 使用 | 不涉及 |
| Embedder + VectorStore | 被 MCP 使用 | 不涉及 |

新增代码：
- Phase 2: `engine/mcp_server.py` + `.vscode/mcp.json`（约 100 行）
- Phase 3: `web/` 目录（VitePress 项目，约 500 行）
