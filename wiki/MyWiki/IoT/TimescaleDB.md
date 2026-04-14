---
category: IoT
created: '2026-04-14'
evolution:
- '2026-04-14: 基于产品经理视角进行单概念入库'
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
title: TimescaleDB
updated: '2026-04-14'
---

# TimescaleDB

## 定义

TimescaleDB 是 PostgreSQL 的时序扩展，面向时间序列数据的写入、存储和查询进行了优化。

## 在数字孪生项目中的担当

TimescaleDB 负责“历史时序数据”：

- 速度、温度、能耗等连续采样数据
- 告警历史和状态变化历史
- 时间窗口聚合与趋势分析

## 关键理解

TimescaleDB 通常不是与 PostgreSQL 完全平级的另一套数据库，而是“基于 PostgreSQL 的时序能力增强”。
