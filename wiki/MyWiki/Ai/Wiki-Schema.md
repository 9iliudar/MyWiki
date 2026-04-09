---
created: '2026-04-09'
evolution:
- '2026-04-09: 初始创建'
related:
- '[[Ingest-Operation]]'
- '[[Lint-Operation]]'
- '[[Schema-Layer]]'
- '[[Wiki-Layer]]'
sources:
- sources/archived/2026-04-09_knowledge-evolution-system.md
tags: []
title: Wiki Schema（Wiki 宪法）
updated: '2026-04-09'
---

## 定义

Wiki Schema 是知识进化系统的宪法文件，定义了所有 LLM 操作的指令依据和执行规范。它规定了页面格式、操作流程、质量标准等核心规则。

## 核心规范

### 语言规范
- Wiki 页面统一使用中文撰写
- 技术术语保留英文原文，首次出现时附中文翻译
- 原始素材语言不限，消化后统一为中文

### Frontmatter 规范
每个页面必须包含：
- title：页面标题
- created/updated：创建和更新时间
- sources：关联的原始素材路径
- related：相关页面的双链列表
- tags：分类标签
- evolution：变更历史记录

### 页面内容规范
- 简明定义（2-3 句话）
- 核心要点列表
- 与其他概念的关系说明
- 来源引用

## 操作规则

### Ingest 规则
- 生成 3-5 句话摘要
- 识别核心概念和实体
- 创建或更新 10-15 个相关页面
- 所有新页面至少有一个双链
- 更新导航结构和操作日志

### 页面创建 vs 更新
- 标题相同或语义高度相似的概念应合并为同一页面
- 更新时追加新信息到 sources 和 evolution

## 与其他概念的关系

Wiki Schema 是 [[Schema-Layer]] 的核心组成部分，指导 [[Ingest-Operation]] 和 [[Lint-Operation]] 的执行。它确保 [[Wiki-Layer]] 中的所有页面符合统一的质量标准。