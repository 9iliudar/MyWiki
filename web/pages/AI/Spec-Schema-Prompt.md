---
category: AI
created: '2026-04-09'
evolution:
- '2026-04-09: 初始创建'
- '2026-04-10: 补充英文术语音标规范'
related:
- '[[SDD]]'
- '[[Spec]]'
- '[[Schema]]'
- '[[Prompt]]'
sources:
- sources/archived/2026-04-09_sdd-spec-schema-prompt.md
tags:
- AI
- 概念模型
- 工程实践
title: Spec-Schema-Prompt 三层模型
updated: '2026-04-10'
---

# Spec-Schema-Prompt 三层模型

## 定义

这是 [[SDD]] 方法论中的核心执行框架，通过三个层次把抽象需求转化为可执行的模型指令。金句是：**Spec /spek/ 管原则，Schema /ˈskiːmə/ 管结构，Prompt /prɑːmpt/ 管执行。**

## 三层详解

### Spec /spek/

- 职责：管原则
- 视角：偏黑盒，关注外部行为和验收结果
- 回答问题：系统应该做什么，做到什么程度才算对

### Schema /ˈskiːmə/

- 职责：管结构
- 视角：偏白盒，关注内部字段和组织方式
- 回答问题：数据或内容该长成什么样，结构是否合法

### Prompt /prɑːmpt/

- 职责：管执行
- 视角：偏任务执行层，面向当前这次模型调用
- 回答问题：这次任务具体要怎么做，按什么格式交付

## 三层协作逻辑

```text
Spec（定义目标和规则）
  ->
Schema（约束结构和格式）
  ->
Prompt（驱动模型执行）
```

- Spec 提供“做什么”的原则
- Schema 提供“长什么样”的标准
- Prompt 提供“怎么做”的执行指令

三者共同构成从需求到执行的完整链条，确保开发过程可控、可验证、可复用。

## 实践价值

- 减少歧义：每一层职责清晰，避免混淆
- 提高复用：Spec 和 Schema 可以跨任务复用，只需调整 Prompt
- 便于验证：每一层都有明确检查点
- 支持迭代：可以独立优化某一层而不破坏整体结构
