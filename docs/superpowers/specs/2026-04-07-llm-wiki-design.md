# LLM Wiki - 个人知识进化引擎设计文档

> 基于 Andrej Karpathy 的 LLM Wiki 思想，构建一个自驱动、自进化的个人知识管理系统。

## 1. 核心理念

Wiki 不是文档仓库，是一个**活的知识有机体**。LLM 扮演"知识园丁"角色，负责所有人类不愿做的 bookkeeping 工作：摘要、交叉引用、矛盾检测、空白填补。

核心原则：
- **原始素材不可变** — sources 是事实源，永不修改
- **Wiki 持续进化** — 每次 ingest/query/lint 都让知识更完整
- **LLM 可插拔** — 不绑定任何一个模型，Claude/OpenAI/本地模型均可
- **Obsidian 优先** — Wiki 文件 100% 兼容 Obsidian，双链原生支持

## 2. 三层架构

### 2.1 第一层：Raw Sources（原始素材）

不可变的知识输入。两种入库方式：
- **对话式**：通过 Claude Code 或其他 LLM 对话粘贴/讨论
- **文件夹监听**：将文件放入 `sources/inbox/`，脚本自动检测

每个素材文件带 frontmatter：

```yaml
---
title: Karpathy - LLM Wiki
source_url: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
date_added: 2026-04-07
type: article          # article / paper / note / conversation / video / book
status: raw            # raw → digested
---
原文内容...
```

### 2.2 第二层：The Wiki（知识层）

LLM 维护的知识页面集合。这是整个系统的心脏。

页面 frontmatter 规范：

```yaml
---
title: RAG（检索增强生成）
created: 2026-04-07
updated: 2026-04-07
sources:
  - sources/archived/2026-04-07_karpathy-llm-wiki.md
related:
  - "[[向量数据库]]"
  - "[[LangChain]]"
  - "[[GraphRAG]]"
tags: [AI, 检索, 架构模式]
evolution:
  - "2026-04-07: 初始创建，来源于 Karpathy LLM Wiki 文章"
  - "2026-04-10: Lint 补充了与 GraphRAG 的对比分析"
---
```

两个特殊文件：
- **`index.md`** — 按内容主题组织的导航目录，LLM 每次操作后自动更新
- **`log.md`** — append-only 操作日志，记录每次 ingest/query/lint 的时间、操作内容、影响的页面

### 2.3 第三层：Schema（Wiki 宪法）

`schema.md` 定义 Wiki 的运行规则，是所有 LLM 操作的指令依据：
- 页面分类与 frontmatter 规范
- Ingest 处理流程和输出模板
- 页面间引用规则（何时创建新页面 vs 更新已有页面）
- Lint 检查清单（矛盾、孤岛、空白、过时、重复）
- 语言规范（中文为主）

## 3. 三条驱动线

### 3.1 输入驱动：Ingest（消化）

新素材进入系统时触发：

```
素材进入 sources/inbox/
  → watch.py 检测到新文件（或手动触发）
  → ingest.py 读取素材
  → 调 LLM 消化：
    1. 生成素材摘要
    2. 创建或更新 10-15 个相关 wiki 页面
    3. 补充 [[双链]] 交叉引用
    4. 更新 index.md 导航
    5. 追加 log.md 记录
  → embed.py 将新/更新页面向量化存入 Qdrant
  → 素材移入 sources/archived/，status 改为 digested
```

触发机制：
- **自动**：watch.py 监听 inbox 文件夹，检测到新文件触发
- **定时**：每小时批量扫描 inbox，合并处理（省 token）
- **手动**：Claude Code 中说"消化新素材"或运行命令

### 3.2 交互驱动：Query（查询反哺）

用户提问时触发：

```
用户提问
  → query.py 用 Qdrant 语义搜索相关 wiki 页面
  → 将相关页面作为上下文喂给 LLM
  → LLM 合成回答（带溯源引用）
  → 如果回答包含新知识：
    · 自动写回 wiki 成为新页面或更新已有页面
    · 更新向量索引
    · 追加 log.md
```

### 3.3 自驱进化：Lint（巡检）

定期自动运行，无需任何输入：

```
定时任务触发（每天或每周）
  → lint.py 遍历所有 wiki 页面
  → LLM 审视全局：
    · 矛盾检测 → 标注并修正
    · 孤岛页面（无入链） → 补充关联
    · 浅层页面（内容过薄） → 深化内容
    · 重复页面 → 合并
    · 知识空白 → 标注 gaps，创建占位页面
    · 过时信息 → 标记待更新
  → 更新 index.md + log.md
  → 更新向量索引
```

## 4. 目录结构

```
MyWiki/
├── sources/                    # 第一层：原始素材（不可变）
│   ├── inbox/                  # 待消化队列
│   └── archived/               # 已消化归档
│
├── wiki/                       # 第二层：LLM 维护的知识层
│   ├── pages/                  # 知识页面（LLM 自行组织子目录）
│   ├── index.md                # 内容导航目录
│   └── log.md                  # append-only 操作日志
│
├── vectors/                    # Qdrant 本地向量存储
│
├── schema.md                   # 第三层：Wiki 宪法
│
├── engine/                     # 驱动引擎（Python）
│   ├── ingest.py               # 消化模块
│   ├── query.py                # 查询模块
│   ├── lint.py                 # 巡检模块
│   ├── watch.py                # 文件夹监听
│   ├── embed.py                # embedding + Qdrant 操作
│   ├── llm.py                  # LLM 适配层（可插拔）
│   └── config.yaml             # 引擎配置
│
└── web/                        # Web UI（Phase 3）
    └── ...                     # wiki.iliudar.com, Next.js
```

## 5. LLM 适配层

统一接口，切换模型只改配置：

```python
class LLMProvider:
    def complete(self, prompt: str, context: str) -> str: ...

class ClaudeProvider(LLMProvider): ...     # Anthropic API
class OpenAIProvider(LLMProvider): ...     # OpenAI / 兼容 API
class LocalProvider(LLMProvider): ...      # Ollama / vLLM 本地模型
```

配置：

```yaml
# engine/config.yaml
llm:
  provider: claude               # claude / openai / local
  model: claude-sonnet-4-6
  api_key_env: ANTHROPIC_API_KEY

embedding:
  provider: openai               # 或本地 embedding 模型
  model: text-embedding-3-small

qdrant:
  path: ./vectors                # 本地持久化，无需服务
```

## 6. 搜索层：Qdrant

使用 Qdrant 本地持久化模式，零服务依赖：

```python
from qdrant_client import QdrantClient
client = QdrantClient(path="./vectors")
```

- Ingest 时：页面内容 → embedding → 存入 Qdrant
- Query 时：问题 → embedding → 语义搜索 → 返回相关页面
- 页面更新时：同步更新对应向量

## 7. 与 Obsidian 的关系

- Obsidian 直接打开 `wiki/` 文件夹作为 Vault
- 所有 `[[双链]]` 原生兼容，图谱视图直接可用
- Obsidian 中手动编辑的内容，git push 后全系统同步
- Obsidian 是人类的主要交互界面，Web UI 是补充

## 8. 交互架构

### 8.0 核心交互理念（2026-04-08 共识）

**对话即输入，Wiki 自动进化，用户无感。**

用户日常流程：
1. **本地对话** — 和 AI 自由聊天、讨论、脑暴、喂资料
2. **引擎自动处理** — 对话结束后，引擎自动判断并执行 ingest/query/更新
3. **知识自动沉淀** — wiki/pages/ 实时更新，Obsidian 打开即最新
4. **Web UI 远程查看** — git push 后 Vercel 自动部署，随时随地浏览

三个入口的分工：

| | 本地对话 | Obsidian | Web UI |
|---|---|---|---|
| 核心动词 | 聊、喂、问、脑暴 | 浏览、思考、关联 | 搜、览、探 |
| 读写 | 写入（通过引擎） | 只读（查看成果） | 只读（远程展示） |
| 场景 | 日常知识工作 | 深度阅读和图谱探索 | 手机/外出时查阅 |

**关键决策：**
- CLI 命令（ingest/query/lint）是底层 API，用户不直接使用
- 本地对话是唯一的"写入"入口
- Web UI 是纯静态展示站，无后端、无 API、无上传功能
- Web UI 数据来源：构建时从 GitHub 拉取 wiki/pages/ 的 .md 文件
- Vercel 免费套餐完全够用

数据流：
```
本地对话 → 引擎(ingest/query/lint) → wiki/pages/ 更新
                                         ↓
                                   Obsidian（实时本地查看）
                                         ↓
                                   git push → GitHub → Vercel 自动部署
                                         ↓
                                   wiki.iliudar.com（远程查看）
```

### 8.1 Web UI 定位

Web UI 是纯静态 Markdown 渲染站，不是 Obsidian 的在线版。

| | Obsidian | Web UI |
|---|---|---|
| 核心动词 | 浏览、深度阅读、图谱探索 | 搜、览、探 |
| 用户状态 | 沉浸式工作 | 碎片化使用 |
| 访问场景 | 坐在电脑前 | 手机、其他设备、随时随地 |

Web 端的核心目的：**让你在任何设备上，用最短路径触达知识、感知全局。**

### 8.2 四个核心页面

#### 首页：搜索 + 脉搏

```
┌─────────────────────────────────────────┐
│                                         │
│         🔍 搜索你的知识...               │
│         [______________________]        │
│                                         │
│  ─── 最近进化 ──────────────────────     │
│  · RAG.md — 补充了 GraphRAG 对比 (2h前) │
│  · Agent.md — Lint 发现知识空白 (5h前)  │
│  · 新增 3 个页面 (昨天)                  │
│                                         │
│  ─── 知识脉搏 ──────────────────────     │
│  📄 127 页面  🔗 342 链接  🕐 上次Lint 2h前│
│                                         │
└─────────────────────────────────────────┘
```

- **搜索框**是绝对主角，语义搜索（Qdrant），输入自然语言即可
- **最近进化**：从 log.md 提取，展示 Wiki 的"心跳"——它最近做了什么
- **知识脉搏**：页面总数、链接总数、最近 Lint 时间，一眼感知 Wiki 的健康状态

#### 页面视图：阅读 + 溯源

```
┌─────────────────────────────────────────┐
│  RAG（检索增强生成）                      │
│  标签: AI · 检索 · 架构模式               │
│  ─────────────────────────────────────   │
│                                         │
│  正文内容...                             │
│                                         │
│  ─── 关联页面 ──────────────────────     │
│  [[向量数据库]] [[LangChain]] [[GraphRAG]]│
│                                         │
│  ─── 溯源 ──────────────────────────     │
│  📎 来自: karpathy-llm-wiki.md (原文链接) │
│                                         │
│  ─── 进化历史 ──────────────────────     │
│  2026-04-10  Lint 补充 GraphRAG 对比     │
│  2026-04-07  初始创建                    │
└─────────────────────────────────────────┘
```

- 正文渲染 Markdown
- 关联页面可点击跳转，形成浏览流
- **溯源**：每个知识点都能追溯到原始素材，解决"这个结论从哪来的"
- **进化历史**：展示这个页面怎么一步步变丰富的

#### 探索视图：图谱 + 标签

```
┌─────────────────────────────────────────┐
│  [图谱] [标签] [时间线]                   │
│  ─────────────────────────────────────   │
│                                         │
│        ○ LLM                            │
│       / | \                             │
│    RAG  Agent  Prompt Engineering       │
│     |     |                             │
│  向量DB  CrewAI                         │
│                                         │
│  (节点大小 = 关联数，颜色 = 标签分类)      │
│                                         │
└─────────────────────────────────────────┘
```

三个子视图切换：
- **图谱**：交互式知识图谱，节点是页面，边是双链关系。点击节点跳转到页面。节点大小反映关联密度，一眼看出核心概念
- **标签**：按标签分组的卡片墙，快速筛选某个领域的所有知识
- **时间线**：按创建/更新时间排列，看知识的生长轨迹

#### ~~入库~~ (已移除)

> **2026-04-08 决策：** 入库功能不再放在 Web UI。所有知识写入通过本地对话完成，Web UI 保持纯展示。

### 8.3 技术方案

- **框架**：Next.js，静态生成（SSG）
- **部署**：Vercel 免费套餐，`wiki.iliudar.com`
- **数据源**：构建时从 GitHub 仓库拉取 `wiki/pages/` 下所有 .md 文件
- **搜索**：构建时从 .md 文件生成客户端搜索索引（如 flexsearch / fuse.js），纯前端搜索
- **图谱渲染**：从 .md 文件的 frontmatter 提取 related 字段构建图数据，用 D3.js 或 react-force-graph 渲染
- **更新机制**：本地 git push → GitHub Webhook → Vercel 自动重新构建
- **无后端**：不需要 API、不需要数据库、不需要服务器

### 8.4 不做什么

- 不做在线编辑（Obsidian 负责浏览）
- 不做文件上传/入库（本地对话负责写入）
- 不做 AI 对话界面（本地对话负责）
- 不做用户系统/登录（个人 Wiki）
- 不做评论/协作（单人使用）
- 不做后端 API（纯静态站）

## 9. 建设阶段

### Phase 1：Wiki 引擎核心 ✅ 已完成（2026-04-07~08）
- 搭建目录结构
- 编写 schema.md
- 实现 engine/（llm.py, embed.py, ingest.py, query.py, lint.py, json_utils.py）
- Qdrant 本地向量存储（fastembed + bge-small-zh-v1.5）
- CLI 入口（ingest/query/lint/watch）
- 25 个单元测试全部通过
- E2E 真实 LLM 测试通过（ingest/query/lint 三项）

### Phase 2：本地对话入口（下一步）
- 交互式对话 REPL，包装引擎为自然对话体验
- 意图识别：AI 自动判断 ingest/query/闲聊
- 对话结束后自动沉淀知识到 wiki/pages/
- watch.py 文件夹监听（已实现）
- 定时 Lint 任务

### Phase 3：静态 Web UI
- wiki.iliudar.com 纯静态展示站
- Next.js SSG + Vercel 免费部署
- Markdown 渲染 + 双链导航 + 客户端搜索 + 知识图谱
- 数据来源：构建时从 GitHub 拉取 .md 文件
- 无后端、无 API、无上传

## 10. 与 Ai123 的关系

两者完全独立：
- `ai123.iliudar.com` — AI 工具导航站，保持现状
- `wiki.iliudar.com` — 个人知识进化引擎，独立演进
- 未来如有需要，可通过链接互通，但架构上不耦合
