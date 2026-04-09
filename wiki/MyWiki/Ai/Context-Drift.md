---
created: '2026-04-09'
evolution:
- '2026-04-09: 初始创建'
related: []
sources:
- sources/archived/2026-04-09_harness-engineering.md
tags: []
title: 上下文漂移（Context Drift）
updated: '2026-04-09'
---

# 上下文漂移（Context Drift）

[[高熵系统]] 中的常见现象，指 AI 在多轮对话中逐渐偏离原始意图或规则的问题。

## 定义

上下文漂移是指在长对话或多轮交互中，AI 的理解和行为逐渐偏离初始设定的现象。这是 AI 系统熵增的典型表现。

## 产生原因

### 上下文窗口限制
- 早期指令可能被挤出上下文
- AI 逐渐