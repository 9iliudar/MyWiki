---
category: IoT
created: '2026-04-14'
evolution:
- '2026-04-14: 基于产品经理视角进行单概念入库'
- '2026-04-14: 补充音标与概念边界说明'
- '2026-04-14: 改为概念词典口径，移除具象案例化注解'
mastery: solid
related:
- '[[PostgreSQL]]'
- '[[Redis]]'
- '[[Digital-Twin]]'
sources:
- sources/archived/2026-04-14_pm-tech-stack-understanding.md
tags:
- 时序数据库
- PostgreSQL
- IoT
title: TimescaleDB /ˈtaɪmˌskeɪl diː biː/
updated: '2026-04-14'
---

# TimescaleDB /ˈtaɪmˌskeɪl diː biː/

## 定义

TimescaleDB 是 PostgreSQL 的时序扩展，用于优化时间序列数据的写入、压缩和聚合查询。

## 核心能力

- 基于时间分片的数据组织
- 面向时序查询的聚合效率优化
- 与 PostgreSQL 生态兼容

## 在分层架构中的角色

- 承接历史时序数据
- 支撑趋势分析与时间窗口统计
- 与 [[Redis]] 形成“历史层 + 实时层”分工

## 常见误解

- 误解：TimescaleDB 是完全独立于 PostgreSQL 的平级数据库
- 修正：它通常作为 PostgreSQL 的能力增强层使用

## 一句话

`TimescaleDB 是 PostgreSQL 的时序能力扩展。`
