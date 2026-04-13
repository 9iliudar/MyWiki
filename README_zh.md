# MyWiki

[English](README.md) | **中文**

MyWiki 是一个个人知识消化追踪系统。

它不是笔记仓库，不是知识库整理工具。它的目的是把你在对话、阅读、思考中**真正消化了的知识**变成一个可搜索、可发布的知识网络。

## 核心理念

这是一个**个人知识消化追踪器**，不是知识库整理工具。

关键区别：这个系统**不默认你已经理解了被输入的素材**。它追踪的是你通过对话、提问、反思真正消化了的知识——只有这些才能进入正式 wiki。

如果你把一堆文章丢进去让 AI 总结，你得到的是一个 AI 理解了但你没理解的 wiki。那毫无意义。这个项目存在的目的就是防止这件事发生。

原则：

`聊天 = 输入，wiki = 我真正理解的东西，web = 可读的输出`

具体来说：

- 一个概念只有在你展示出理解后才能进入正式 wiki
- 被提到的概念不会自动变成页面
- 知识网络缓慢、审慎、按掌握程度增长——而不是按数量
- wiki 在任何时间点都反映你的真实认知状态

这是整个仓库最重要的设计决策。

## 解决什么问题

大多数笔记系统最终变成仓库：

- 概念太多
- 浅层页面太多
- 想法之间的关联很弱
- 无法区分"提到过"和"已掌握"

MyWiki 通过区分以下三者来解决这个问题：

- 用户已经掌握的
- 用户只是接触过的
- 对话中仅仅被提到的

结果是一个更小但质量更高的知识网络。

## 知识增长哲学

本仓库遵循以下规则：

- 深度优于广度
- 只有真正理解了才内化一个概念
- 每轮对话默认最多 1-2 个正式概念
- 衍生概念留在候选层，直到被明确确认
- 只有在掌握程度明确后才把独立概念拆成单独页面

一句话：**精不求多，消化一个，进一个。**

## 系统架构

系统有四个主要层次。

### 1. 输入层

原始素材来源：

- 直接对话内化
- 放入 `sources/inbox/` 的 Markdown 文件
- MCP 工具调用

消化后，源文件归档到 `sources/archived/`。

### 2. 内化层

Python 引擎读取源素材，让 LLM 消化，决定：

- 哪些概念正式化为 wiki 页面
- 哪些概念保持候选状态
- 哪些已有页面应该更新而不是重复创建

核心模块：

- `engine/ingest.py` — 消化管线
- `engine/prompts.py` — LLM 提示词模板
- `engine/json_utils.py` — 健壮的 JSON 解析
- `engine/wiki_io.py` — Wiki 文件读写

### 3. 知识存储层

正式知识以带 frontmatter 的 Markdown 存储：

- `wiki/MyWiki/<Category>/` — 正式页面
- `wiki/candidates/<Category>/` — 候选概念

这个分离是刻意的：正式页面代表已掌握的知识，候选页面代表可能的未来知识。

### 4. 检索与发布层

- 通过本地 embedding + Qdrant 进行语义检索
- CLI 查询
- VitePress WebUI 发布
- Obsidian 直接浏览同一套 Markdown 文件

核心模块：

- `engine/query.py` — 查询管线（按掌握程度加权）
- `engine/embed.py` — 本地 embedding（fastembed）+ 向量库
- `web/scripts/prepare.js` — Web 数据生成

## 目录结构

```text
wiki/
  MyWiki/           # 正式知识页面
    AI/
    Finance/
    IoT/
    ...
  candidates/       # 候选概念
  index.md          # 导航目录
  log.md            # 操作日志

sources/
  inbox/            # 待消化素材
  archived/         # 已消化素材

vectors/            # Qdrant 本地向量库

engine/             # Python 引擎
web/                # VitePress Web UI
```

## 标准工作流

### 1. 聊天与理解

和 AI 讨论一个概念，直到真正理解。

### 2. 预览（认知评估）

消化前，调用 `wiki_preview` 生成认知快照，评估你展示出理解了什么：

- **mastered** — 用自己的话解释了，或者提出了深度问题
- **likely** — 说了"明白了"但没有展开
- **unconfirmed** — AI 解释了但你没有回应

### 3. 确认并内化

你审查快照，确认哪些概念要入库。只有确认的概念才进入正式 wiki。每个页面获得一个掌握程度：

- `deep` — 能给别人讲明白，理解边界情况
- `solid` — 理解核心原理，能在实践中使用
- `surface` — 知道是什么，细节模糊

掌握程度只升不降。

### 4. 归档

原始对话快照或源素材归档到 `sources/archived/`。

### 5. 重建 Web 数据

Wiki 页面变更后，重建 WebUI 数据：

```powershell
node web\scripts\prepare.js
```

### 6. 在 Obsidian 或 WebUI 中查看

Obsidian 直接读取 `wiki/MyWiki` 的 Markdown 结构。WebUI 读取 `web/data` 的元数据和 `web/pages` 的生成页面。

## MCP 工具

引擎作为 MCP 服务器运行，集成 Claude Code / VS Code：

| 工具 | 说明 |
|------|------|
| `wiki_preview(content)` | 认知评估 — 评估用户理解了什么，返回快照。不写入任何文件。 |
| `wiki_ingest(content, title?, category?)` | 将确认的知识消化为 wiki 页面，带掌握程度追踪。 |
| `wiki_query(question)` | 搜索 wiki 并回答问题。结果按掌握程度加权。 |
| `wiki_lint()` | 健康检查 — 发现矛盾、孤岛、空白并自动修复。 |

## CLI 命令

```powershell
# 消化单个文件
python -m engine.cli ingest --file sources\inbox\example.md --category AI

# 消化 inbox 中所有文件
python -m engine.cli ingest --category AI

# 查询知识库
python -m engine.cli query "关于边界设计我已经知道什么？"

# 巡检
python -m engine.cli lint

# 监听 inbox
python -m engine.cli watch
```

## Web 发布

WebUI 是 wiki 的发布投影，不是数据源头。

数据源头：`wiki/MyWiki/`

生成产物：`web/pages/`、`web/data/wiki-meta.json`、`web/data/route-map.json`、`web/data/graph.json`

```powershell
node web\scripts\prepare.js
git add wiki web && git commit -m "update wiki" && git push
```

自动部署到 wiki.aibc.fans（Vercel）。

## 已实现的关键成果

- 按分类的 wiki 存储 + 单一 Obsidian 仓库
- 候选层缓冲，防止知识爆炸
- **认知预览** — 入库前两步确认
- **掌握程度追踪** — `deep` / `solid` / `surface`，只升不降
- **掌握程度加权查询** — 回答优先引用深度理解的知识
- 带知识图谱的 WebUI（节点携带掌握程度）
- Claude Code / VS Code 的 MCP 服务器集成
- 本地 embedding（fastembed）+ Qdrant 向量搜索

## 核心决策规则

**如果用户没有明确理解它，就不要把它提升到正式 wiki 中。**

这条规则保护整个系统。
