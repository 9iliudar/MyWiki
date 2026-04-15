---
category: AI
created: '2026-04-09'
evolution:
- '2026-04-09: 从 Spec-Schema-Prompt 总览中拆分为独立正式概念页'
- '2026-04-10: 补充英文术语音标规范'
related:
- '[[SDD]]'
- '[[Schema]]'
- '[[Prompt]]'
- '[[Spec-Schema-Prompt]]'
sources:
- sources/archived/2026-04-09_sdd-spec-schema-prompt.md
tags:
- AI
- 开发方法论
- 规格说明
title: Spec /spek/
updated: '2026-04-10'
---

# Spec /spek/

## 定义

Spec /spek/ 是 `Specification` /ˌspesɪfɪˈkeɪʃən/ 的简称，表示规格说明。它的作用不是泛泛描述需求，而是把需求转化为明确的执行标准和验收依据。

## 核心作用

- 明确目标：说明系统要做什么
- 收紧边界：说明系统不做什么
- 约束规则：说明关键约束和行为要求
- 支撑验收：说明做到什么程度才算正确

## 它回答的问题

- 这个系统到底应该完成什么
- 输入输出应该满足什么要求
- 关键边界和限制是什么
- 什么标准可以作为开发和测试的依据

## 与其他概念的关系

- [[SDD]]：Spec 是规格驱动开发中的上层约束
- [[Schema]]：Schema 负责结构，Spec 负责原则和结果约定
- [[Prompt]]：Prompt 会把 Spec 转译为模型可执行的任务指令

## 一句话

Spec 管原则，也就是把需求变成执行标准和验收依据。
