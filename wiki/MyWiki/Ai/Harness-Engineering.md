---
created: '2026-04-09'
evolution:
- '2026-04-09: 初始创建'
related:
- '[[MCP]]'
sources:
- sources/archived/2026-04-09_harness-engineering.md
tags: []
title: AI 驾驭工程（Harness Engineering）
updated: '2026-04-09'
---

# AI 驾驭工程（Harness Engineering）

一种驾驭 AI 的工程方法论。核心宗旨：设计好约束，管理好熵增，让 AI 在安全的边界内稳定输出价值。

## 核心思想

AI 本身是高熵的（不确定、不可控），工程师的工作不是写代码让 AI 更聪明，而是设计约束让 AI 更可靠。这种方法论强调通过工程手段驾驭 AI 的不确定性，而非对抗它。

## 三大支柱

### 1. [[Constraint-Design|约束设计]]
给 AI 划定边界：什么能做、什么不能做、输出格式是什么。类比：不是训练马跑得更快，而是修好赛道和护栏。

### 2. [[Entropy-Management|熵管理]]
AI 每次输出都有随机性，多轮对话后偏差会放大。需要通过结构化 prompt、校验输出、反馈闭环来管理熵增。

### 3. [[Stable-Value-Delivery|价值稳定输出]]
目标不是 AI 偶尔惊艳，而是每次都能用。可复现性优于偶发精彩。

## 与 LLM Wiki 的关系

LLM Wiki 项目本身就是驾驭工程的实践案例：
- [[Schema-Layer|Schema 层]] = 约束设计
- json_utils.py 的 3 级 fallback = 熵管理
- [[MCP]] + CLAUDE.md + AGENTS.md = 让任何 AI 在边界内稳定输出

## 实践意义

驾驭工程强调的是工程化思维：通过系统设计而非算法优化来提升 AI 系统的可靠性。这种方法论特别适用于需要将 AI 能力集成到生产环境的场景。