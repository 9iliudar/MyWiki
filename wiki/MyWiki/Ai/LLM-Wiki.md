---
created: '2026-04-08'
evolution:
- '2026-04-08: 初始创建'
related:
- '[[Andrej-Karpathy]]'
- '[[Ingest-Operation]]'
- '[[Lint-Operation]]'
- '[[Query-Operation]]'
- '[[Three-Layer-Architecture]]'
sources:
- sources/archived/2026-04-07_karpathy-llm-wiki.md
tags: []
title: LLM Wiki
updated: '2026-04-08'
---

## 定义

LLM Wiki 是一种利用大语言模型（LLM）维护个人知识库的系统化方法，由 [[Andrej Karpathy]] 提出。它将知识管理视为一个持久的、不断积累的过程，通过 LLM 自动化完成知识的提取、组织和维护工作。

## 核心理念

- Wiki 是一个持久的知识产物，随着每次新素材输入和每次查询而变得更丰富
- LLM 负责人类最容易放弃的部分：记录和整理
- 知识以结构化的 Markdown 文件集合形式存在
- 通过交叉引用和双链建立知识网络

## 系统组成

采用 [[三层架构]]：
- Raw Sources（原始素材层）
- The Wiki（知识层）
- The Schema（规则层）

## 核心操作

- [[Ingest操作]]：消化新素材，更新相关页面
- [[Query操作]]：基于已有知识回答问题
- [[Lint操作]]：定期健康检查和维护

## 价值主张

解决了知识管理的真正瓶颈：「繁琐的部分不是阅读或思考——而是记录和整理。」LLM 擅长的恰好是人类容易放弃的维护工作。