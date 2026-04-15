---
category: AI
created: '2026-04-09'
evolution:
- '2026-04-09: 从 Spec-Schema-Prompt 总览中拆分为独立正式概念页'
- '2026-04-10: 补充英文术语音标规范'
related:
- '[[SDD]]'
- '[[Spec]]'
- '[[Schema]]'
- '[[Spec-Schema-Prompt]]'
sources:
- sources/archived/2026-04-09_sdd-spec-schema-prompt.md
tags:
- AI
- LLM
- 提示工程
title: Prompt /prɑːmpt/
updated: '2026-04-10'
---

# Prompt /prɑːmpt/

## 定义

Prompt /prɑːmpt/ 可以理解为给模型的即时操作指令。它负责把抽象的规格要求和结构约束，翻译成模型当前这次任务要执行的具体命令。

## 核心作用

- 下达任务：告诉模型这次要完成什么
- 传递约束：把 Spec 和 Schema 的要求带入执行
- 控制输出：规定输出方式、格式和重点
- 缩小歧义：减少模型自由发挥带来的偏差

## 它回答的问题

- 这次任务具体要怎么做
- 模型应该优先关注什么
- 应该按什么格式交付
- 哪些限制必须在执行时遵守

## 与其他概念的关系

- [[Spec]]：Prompt 会落实 Spec 中的目标、边界和验收要求
- [[Schema]]：Prompt 会落实 Schema 中的字段和结构要求
- [[SDD]]：Prompt 是 SDD 三层执行结构中的执行层

## 一句话

Prompt 管执行，也就是把原则和结构翻译成模型可以直接执行的指令。
