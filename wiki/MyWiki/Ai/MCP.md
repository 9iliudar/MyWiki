---
created: '2026-04-09'
evolution:
- '2026-04-09: 初始创建'
related:
- '[[Harness-Engineering]]'
- '[[Ingest-Operation]]'
- '[[LLM-Wiki]]'
- '[[Lint-Operation]]'
- '[[Query-Operation]]'
sources:
- sources/archived/2026-04-09_harness-engineering.md
tags: []
title: MCP（Model Context Protocol）
updated: '2026-04-09'
---

# MCP（Model Context Protocol）

一种标准化 AI 工具调用的协议，在 [[LLM-Wiki]] 中用于实现 [[价值稳定输出]]。

## 定义

MCP 是一种协议，用于标准化 AI 模型与外部工具之间的交互。通过 MCP，可以将复杂操作封装为标准化的工具调用，使 AI 的行为更可预测和可靠。

## 在 LLM Wiki 中的作用

MCP 是实现 [[Harness-Engineering]] 的关键技术手段：

### 标准化操作
- [[Ingest-Operation]]：消化原始素材
- [[Query-Operation]]：查询知识库
- [[Lint-Operation]]：检查质量

### 约束实现
- 工具定义明确了 AI 能做什么
- 参数 schema 限制了输入格式
- 返回值规范确保输出一致性

### 降低依赖
- 不依赖用户的具体措辞
- AI 通过工具名称理解意图
- 减少自然语言的歧义性

## 优势

- **可预测性**：工具行为明确定义
- **可组合性**：工具可以组合使用
- **可测试性**：工具可以独立测试
- **可维护性**：工具逻辑集中管理

## 与约束设计的关系

MCP 是 [[约束设计]] 的具体实现方式，通过工具接口将 AI 的能力限制在预定义的操作集合内。