---
created: '2026-04-09'
evolution:
- '2026-04-09: 初始创建'
related:
- '[[Obsidian]]'
- '[[Markdown]]'
- '[[Knowledge-Evolution-System]]'
sources:
- sources/archived/2026-04-07_karpathy-llm-wiki.md
tags:
- 工具
- 实现
- 技术栈
title: Wiki 实现工具
updated: '2026-04-09'
---

# Wiki 实现工具

## 定义

LLM Wiki 系统的实现依赖一系列工具和技术，形成完整的知识管理技术栈。这些工具各司其职，共同支撑知识的创建、维护和访问。

## 核心工具

### Obsidian

**角色**：人类交互和可视化层

**功能**：
- 提供图形化界面浏览 Wiki
- 支持双向链接可视化
- 实时预览 Markdown 内容
- 提供搜索和导航功能

### Markdown

**角色**：内容格式标准

**优势**：
- 纯文本格式，易于版本控制
- 人类可读，LLM 友好
- 支持丰富的格式化能力
- 广泛的工具生态支持

### index.md

**角色**：面向内容的导航入口

**功能**：
- 提供主题分类导航
- 展示知识结构概览
- 引导用户发现相关内容

### log.md

**角色**：时间线记录

**特性**：
- 只追加（append-only）的操作日志
- 记录每次 Ingest、Query、Lint 操作
- 提供知识演化的历史轨迹
- 支持审计和回溯

## 可选增强工具

### 搜索引擎（如 qmd）

**适用场景**：更大规模的 Wiki

**功能**：
- 全文搜索
- 语义搜索
- 快速定位相关内容

## 工具协同

这些工具形成完整的工作流：LLM 生成 Markdown 内容，Obsidian 提供人类友好的访问界面，index.md 和 log.md 提供不同维度的导航，搜索引擎支持大规模检索。
