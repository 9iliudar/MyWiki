---
category: IoT
created: '2026-04-14'
evolution:
- '2026-04-14: 初始创建'
mastery: solid
related:
- '[[Digital-Twin-Architecture]]'
- '[[Redis-Message-Queue]]'
sources:
- sources/archived/2026-04-14_mastered-digital-twin-stack-part2.md
tags:
- 数据库
- 时序数据
- IoT
- Digital-Twin
title: PostgreSQL + TimescaleDB 时序数据方案
updated: '2026-04-14'
---

## 核心定位

TimescaleDB /ˈtaɪmˌskeɪl diː biː/ 是 PostgreSQL /ˈpoʊstɡres/ 的一个扩展（extension），专门优化时序数据的存储和查询性能。它不是独立数据库，而是在 PostgreSQL 基础上增强了时间序列数据的处理能力。

## 架构角色

在数字孪生系统中，PostgreSQL + TimescaleDB 负责持久化存储历史时序数据，与 Redis 形成互补分工：

- **TimescaleDB**：存储长期历史数据，支持复杂时间范围查询和聚合分析
- **Redis**：缓存最新状态和实时消息队列，提供毫秒级读写性能

## 技术特性

- **自动分区**：按时间自动创建 hypertable，优化大规模时序数据查询
- **压缩存储**：历史数据自动压缩，节省存储空间
- **SQL 兼容**：完全兼容 PostgreSQL 生态，可使用标准 SQL 和现有工具链
- **聚合函数**：内置时间窗口聚合、降采样等时序专用函数

## 使用场景

适用于需要长期保存、复杂查询和数据分析的 IoT 场景，如设备状态历史追溯、趋势分析、异常检测等。对于实时性要求极高的场景（如 WebSocket 推送），仍需配合 Redis 等内存数据库。