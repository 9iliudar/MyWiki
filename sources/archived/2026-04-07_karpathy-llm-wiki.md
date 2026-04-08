---
date_added: 2026-04-07
source_url: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
status: digested
title: Karpathy - LLM Wiki
type: article
---

# LLM Wiki: A Personal Knowledge System Pattern

Andrej Karpathy 提出了一种利用 LLM 维护个人知识库的方法。核心思想是：wiki 是一个持久的、不断积累的知识产物，随着每次新素材的输入和每次查询而变得更丰富。

## 三层架构

**Raw Sources（原始素材）** — 不可变的原始文档，包括文章、论文、图片等。

**The Wiki（知识层）** — LLM 生成和维护的 Markdown 文件集合，包含摘要、实体页面和交叉引用。LLM 完全负责这一层的维护。

**The Schema（规则层）** — 配置文件，定义 wiki 的结构和工作流程。

## 核心操作

**Ingest（消化）**：当添加新素材时，LLM 阅读素材，讨论要点，撰写摘要，并在一次操作中更新 10-15 个相关 wiki 页面。

**Query（查询）**：LLM 不是从零开始推导答案，而是先搜索 wiki 已有页面，基于已有知识合成回答，并将有价值的回答写回 wiki 成为新页面。

**Lint（巡检）**：定期健康检查，识别矛盾内容、孤岛页面、缺失的交叉引用和知识空白。

## 为什么这种方法有效

这种方法解决了知识管理的真正瓶颈：「繁琐的部分不是阅读或思考——而是记录和整理。」LLM 擅长的恰好是人类容易放弃的维护工作。

## 实现工具

- Obsidian 作为人类交互和可视化层
- index.md 提供面向内容的导航
- log.md 创建只追加的时间线记录
- 可选：搜索引擎（如 qmd）用于更大的 wiki

## 社区反馈

评论者提出了重要的局限性：随时间的错误累积、摘要导致的信息丢失、幻觉连接、操作复杂性。共识是将 wiki 作为导航层，同时保持对原始素材的访问。