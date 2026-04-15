---
category: IoT
created: '2026-04-14'
evolution:
- '2026-04-14: 基于产品经理视角进行单概念入库'
- '2026-04-14: 补充音标与概念边界说明'
- '2026-04-14: 改为概念词典口径，移除具象案例化注解'
mastery: solid
related:
- '[[TimescaleDB]]'
- '[[Redis]]'
- '[[Digital-Twin]]'
sources:
- sources/archived/2026-04-14_pm-tech-stack-understanding.md
tags:
- 数据库
- 关系型数据库
- 主数据
title: PostgreSQL /ˈpoʊstɡrɛs kjuː ˈɛl/
updated: '2026-04-14'
---

# PostgreSQL /ˈpoʊstɡrɛs kjuː ˈɛl/

## 定义

PostgreSQL 是开源关系型数据库，强调事务一致性、结构化建模和复杂查询能力。

## 核心能力

- ACID 事务保障
- 关系模型与约束管理
- SQL 查询与扩展生态

## 在分层架构中的角色

- 存放主数据与关系数据
- 存放配置、权限与规则类数据
- 作为持久化基础，与 [[TimescaleDB]] / [[Redis]] 协同

## 常见误解

- 误解：单一关系库可最优覆盖全部时序和缓存场景
- 修正：时序与缓存通常需要专门分层能力配合

## 一句话

`PostgreSQL 是结构化业务数据的稳定底座。`
