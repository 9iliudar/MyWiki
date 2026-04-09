---
created: '2026-04-09'
evolution:
- '2026-04-09: 初始创建'
related: []
sources:
- sources/archived/2026-04-09_harness-engineering.md
tags: []
title: 价值稳定输出（Stable Value Delivery）
updated: '2026-04-09'
---

# 价值稳定输出（Stable Value Delivery）

[[Harness-Engineering]] 三大支柱之一，强调 AI 系统的可靠性和一致性。

## 定义

价值稳定输出是指 AI 系统能够持续、可靠地交付价值，而不是偶尔产生惊艳但不可复现的结果。核心原则是：可复现性优于偶发精彩。

## 核心理念

- 目标不是 AI 偶尔惊艳，而是每次都能用
- 稳定的 80 分优于不稳定的 95 分
- 用户需要的是可预测的行为，而非随机的惊喜

## 实现策略

### 标准化接口
- 通过 [[MCP]] 协议统一工具调用
- 定义清晰的输入输出契约
- 不依赖用户的具体措辞方式

### 操作原子化
- 将复杂任务分解为标准操作（如 [[Ingest-Operation]]、[[Query-Operation]]、[[Lint-Operation]]）
- 每个操作有明确的职责和预期结果
- 操作可组合但各自独立

### 质量保证
- 自动化测试和验证
- 持续的质量检查（Lint）
- 错误处理和降级策略

### 文档驱动
- 通过 CLAUDE.md/AGENTS.md 明确 AI 行为
- [[Schema-Layer]] 作为系统宪法
- 所有规则可查询、可验证

## 在 LLM Wiki 中的应用

- MCP 工具标准化 ingest/query/lint 操作
- Schema 层确保所有 AI 遵循相同规则
- Frontmatter 规范保证页面结构一致
- 双链机制确保知识图谱的完整性