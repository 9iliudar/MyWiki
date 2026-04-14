---
category: IoT
created: '2026-04-14'
evolution:
- '2026-04-14: 基于产品经理视角进行单概念入库'
- '2026-04-14: 补充音标与概念边界说明'
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

TimescaleDB 是 PostgreSQL 的时序扩展，针对时间序列数据提供高效写入与聚合查询能力。

## 产品经理可用表述

- 它不是与 PostgreSQL 完全平级的独立栈。
- 它适合承接历史曲线、趋势分析和按时间窗口统计。

## 在本项目中的担当

- 存储速度、温度、能耗等连续采样数据
- 存储状态变化与告警历史
- 支撑按小时/天/周的趋势和对比查询

## 常见误区

- 误区：TimescaleDB 可以替代缓存层。
- 修正：最新态和超高频读写仍应由 [[Redis]] 承担。

## 一句话边界

`TimescaleDB 管历史时序，Redis 管最新状态。`
