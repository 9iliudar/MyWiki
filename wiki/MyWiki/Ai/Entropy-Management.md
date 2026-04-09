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

熵管理是 [[Harness-Engineering|AI 驾驭工程]]的第二大支柱，专注于管理 AI 系统的不确定性和随机性。

## 核心问题

AI 每次输出都有随机性（高熵特性），多轮对话后偏差会放大，导致输出质量下降和 [[Context-Drift|上下文漂移]]。

## 管理策略

### 1. 结构化 Prompt
使用 [[Structured-Prompt|结构化提示词]]来减少输入的模糊性，明确任务目标和输出要求。

### 2. 输出校验
- JSON Schema 校验 LLM 输出格式
- 语义校验确保内容符合预期
- 自动化检测异常输出

### 3. 反馈闭环
- 将校验结果反馈给 AI
- 支持多次重试和修正
- 记录失败案例用于改进

### 4. [[Fallback-Mechanism|降级机制]]
- 3 级 fallback 解析确保鲁棒性
- 当主要解析失败时，使用备用方案
- 最终降级到安全的默认行为

## 实践案例

在 LLM Wiki 项目中：
- `json_utils.py` 实现了 3 级 fallback 解析
- Schema 层定义了严格的输出格式
- Lint 操作提供自动化校验

## 与其他概念的关系

熵管理是应对 [[High-Entropy-System|高熵系统]]的核心手段，通过 [[Constraint-Design|约束设计]]来限制熵的增长空间，最终实现 [[Stable-Value-Delivery|价值稳定输出]]。

## 关键指标

- **输出一致性**：相同输入产生相似输出的概率
- **错误率**：输出不符合预期的频率
- **恢复能力**：系统从错误中恢复的速度