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

约束设计是 [[Harness-Engineering|AI 驾驭工程]]的第一大支柱，核心理念是给 AI 划定明确的边界：什么能做、什么不能做、输出格式是什么。

## 核心理念

不是训练马跑得更快，而是修好赛道和护栏。约束设计的目标不是提升 AI 的能力上限，而是确保 AI 在可控范围内稳定运行。

## 实践方式

### 行为约束
- CLAUDE.md/AGENTS.md 文件告诉 AI 在项目中该如何行为
- 定义 AI 的角色、职责和操作权限
- 明确禁止的操作和输出类型

### 结构约束
- [[Schema-Layer|Schema 层]]定义 Wiki 的运行规则
- JSON Schema 约束输出格式
- Frontmatter 规范约束页面元数据

### 输出约束
- 定义明确的输出格式（如 JSON、Markdown）
- 设置输出长度和结构要求
- 规定必填字段和可选字段

## 与其他概念的关系

约束设计是 [[Boundary-Design|边界设计]]的具体实现，通过对输出、权限、流程和质量等维度施加明确限制来实现对 AI 行为的全面控制。配合 [[Entropy-Management|熵管理]]，约束设计能够有效降低 AI 输出的不确定性。

## 设计原则

1. **明确性**：约束必须清晰、无歧义
2. **可验证性**：约束必须可以通过程序验证
3. **最小化**：只设置必要的约束，避免过度限制
4. **分层性**：不同层次的约束相互配合，形成完整的约束体系
