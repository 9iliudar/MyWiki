---
created: '2026-04-09'
evolution:
- '2026-04-09: 初始创建'
related: []
sources:
- sources/archived/2026-04-09_harness-engineering.md
tags: []
title: 结构化 Prompt（Structured Prompt）
updated: '2026-04-09'
---

# 结构化 Prompt（Structured Prompt）

一种通过明确格式和结构来减少 AI 输出随机性的提示工程技术。

## 定义

结构化 Prompt 是指使用明确的格式、清晰的指令和具体的示例来引导 AI 输出，减少解释空间和歧义。这是实现 [[熵管理]] 的重要手段。

## 核心要素

### 明确的指令格式
- 使用编号列表或分节结构
- 每个指令独立且具体
- 避免模糊或多义的表达

### 输出格式定义
- 明确要求 JSON、Markdown 等格式
- 提供完整的输出示例
- 使用 Schema 定义数据结构

### 约束条件
- 明确什么能做、什么不能做
- 定义输出的边界和限制
- 提供具体的判断标准

### 示例驱动
- 提供正确输出的示例
- 展示边界情况的处理
- 通过示例传达隐含规则

## 在 LLM Wiki 中的应用

### Schema 文档
- [[Schema-Layer]] 本身就是结构化 Prompt
- 明确定义 Ingest/Query/Lint 的行为
- 提供 JSON 输出格式示例

### 操作指令
- [[Ingest-Operation]] 有清晰的步骤列表
- 要求输出特定的 JSON 结构
- 定义页面创建 vs 更新的判断标准

## 与传统 Prompt 的区别

| 传统 Prompt | 结构化 Prompt |
|------------|---------------|
| 自然语言描述 | 格式化指令 |
| 依赖 AI 理解 | 明确定义行为 |
| 输出格式自由 | 强制输出格式 |
| 高随机性 | 低随机性 |

## 价值

- 减少 AI 输出的随机性
- 提高输出的一致性
- 降低解析失败率
- 支持 [[价值稳定输出]]