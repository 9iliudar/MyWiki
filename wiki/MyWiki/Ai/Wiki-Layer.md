---
created: '2026-04-08'
evolution:
- '2026-04-08: 初始创建'
related:
- '[[Ingest-Operation]]'
- '[[Lint-Operation]]'
- '[[Markdown]]'
- '[[Query-Operation]]'
- '[[Three-Layer-Architecture]]'
sources:
- sources/archived/2026-04-07_karpathy-llm-wiki.md
tags: []
title: 知识层
updated: '2026-04-08'
---

## 定义

知识层是 [[三层架构]] 的中间层，由 LLM 生成和维护的结构化知识库，以 [[Markdown]] 文件集合的形式存在。

## 核心特征

- **LLM 完全维护**：所有内容由 LLM 自动生成和更新
- **结构化表示**：使用 Markdown 格式和 Frontmatter 元数据
- **网络化组织**：通过双链（[[]]）建立页面间关联
- **持续演化**：随着新素材输入和查询不断丰富

## 内容组成

- 概念和实体页面
- 摘要和要点提取
- 交叉引用和关系说明
- 元数据和演化历史

## 维护方式

通过三种核心操作维护：
- [[Ingest操作]]：消化新素材，创建和更新页面
- [[Query操作]]：回答问题，生成新页面
- [[Lint操作]]：健康检查，修复问题