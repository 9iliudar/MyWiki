---
category: AI
created: '2026-04-09'
evolution:
- '2026-04-09: 从 Spec-Schema-Prompt 总览中拆分为独立正式概念页'
- '2026-04-10: 补充英文术语音标规范'
related:
- '[[SDD]]'
- '[[Spec]]'
- '[[Prompt]]'
- '[[Spec-Schema-Prompt]]'
sources:
- sources/archived/2026-04-09_sdd-spec-schema-prompt.md
tags:
- AI
- 数据结构
- 内容建模
title: Schema /ˈskiːmə/
updated: '2026-04-10'
---

# Schema /ˈskiːmə/

## 定义

Schema /ˈskiːmə/ 可以理解为结构规则，描述某类数据或内容允许长成什么样。它关注的是对象内部的组织方式，而不是系统整体目标。

## 核心作用

- 定义字段：有哪些字段
- 约束类型：字段是什么类型
- 规定结构：字段如何组合和嵌套
- 支撑校验：判断内容结构是否合法

## 它回答的问题

- 一个对象内部应该如何组织
- 哪些字段是必须的
- 字段类型和格式是什么
- 这份数据或内容是否结构合规

## 与其他概念的关系

- [[Spec]]：Spec 定义做什么才对，Schema 定义长什么才对
- [[Prompt]]：Prompt 会要求模型按 Schema 返回结构化结果
- [[SDD]]：Schema 是 SDD 三层执行结构中的结构层

## 一句话

Schema 管结构，也就是定义数据或内容该长成什么样。
