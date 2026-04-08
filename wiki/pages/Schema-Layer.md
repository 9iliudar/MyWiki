---
created: '2026-04-08'
evolution:
- '2026-04-08: 初始创建'
related: []
sources:
- sources/archived/2026-04-07_karpathy-llm-wiki.md
tags: []
title: 规则层
updated: '2026-04-08'
---

## 定义

规则层（Schema）是 [[三层架构]] 的顶层，定义 Wiki 系统的运行规则和工作流程，相当于系统的「宪法」。

## 核心功能

- 定义页面结构和 Frontmatter 规范
- 规定 [[Ingest操作]]、[[Query操作]]、[[Lint操作]] 的执行规则
- 指定语言规范和格式要求
- 设定页面创建和更新的判断标准

## 配置内容

- 语言规范（如统一使用中文）
- 元数据结构（created, updated, sources, related 等）
- 操作流程定义
- 质量检查标准
- 页面内容规范

## 设计价值

- 提供一致性保证
- 使 LLM 行为可预测和可控
- 支持系统的可配置性和扩展性
- 作为所有 LLM 操作的指令依据