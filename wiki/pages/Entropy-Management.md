---
created: '2026-04-09'
evolution:
- '2026-04-09: 初始创建'
related: []
sources:
- sources/archived/2026-04-09_harness-engineering.md
tags: []
title: 熵管理（Entropy Management）
updated: '2026-04-09'
---

# 熵管理（Entropy Management）

[[Harness-Engineering]] 三大支柱之一，专注于控制 AI 输出的随机性和偏差累积。

## 定义

熵管理是指通过工程手段控制 AI 系统的不确定性。AI 每次输出都有随机性，多轮对话后偏差会放大，熵管理的目标是防止这种偏差累积导致系统失控。

## 核心问题

- AI 输出具有内在随机性
- 多轮交互会导致偏差累积
- 上下文漂移会使 AI 偏离预期行为
- 输出质量难以保证一致性

## 对策

### 结构化 Prompt
- 使用明确的指令格式
- 提供具体的输出示例
- 减少解释空间和歧义

### 输出校验
- JSON Schema 验证输出格式
- 类型检查和数据验证
- 自动拒绝不符合规范的输出

### 反馈闭环
- 检测到偏差时及时纠正
- 通过 [[Lint-Operation]] 持续检查质量
- 建立错误恢复机制

### 多级 Fallback
- 主解析失败时尝试备用方案
- 逐级降级但保证基本功能
- 在 LLM Wiki 中实现了 3 级 fallback 解析

## 在 LLM Wiki 中的应用

- `json_utils.py` 的 3 级 fallback 机制
- JSON Schema 严格校验 LLM 输出
- Frontmatter 规范确保元数据一致性
- Evolution 字段追踪页面变更历史