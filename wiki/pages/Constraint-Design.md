---
created: '2026-04-09'
evolution:
- '2026-04-09: 初始创建'
related: []
sources:
- sources/archived/2026-04-09_harness-engineering.md
tags: []
title: 约束设计（Constraint Design）
updated: '2026-04-09'
---

# 约束设计（Constraint Design）

[[Harness-Engineering]] 三大支柱之一，通过为 AI 划定明确边界来提升可靠性。

## 定义

约束设计是指为 AI 系统明确定义：什么能做、什么不能做、输出格式是什么。目标是通过预设规则和边界，将 AI 的行为限制在可控范围内。

## 核心思想

不是让 AI 更聪明，而是让 AI 在明确的边界内运行。类比：不是训练马跑得更快，而是修好赛道和护栏。

## 实践方法

### 行为约束
- 通过 CLAUDE.md/AGENTS.md 等文档告诉 AI 在项目中的行为规范
- 定义 AI 的角色、权限和责任范围
- 明确禁止的操作和输出类型

### 格式约束
- 使用 JSON Schema 定义输出结构
- 强制要求特定的数据格式
- 通过 [[Schema-Layer]] 规范化所有交互

### 流程约束
- 设计标准化的操作流程（如 [[Ingest-Operation]]、[[Query-Operation]]）
- 限制 AI 的决策空间
- 通过 [[MCP]] 工具封装标准操作

## 在 LLM Wiki 中的应用

- Schema 层定义 Wiki 的运行规则
- Frontmatter 规范约束页面结构
- Ingest/Query/Lint 操作标准化 AI 行为
- 双链机制强制页面间关联