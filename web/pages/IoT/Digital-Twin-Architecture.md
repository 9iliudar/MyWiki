---
category: IoT
created: '2026-04-14'
evolution:
- '2026-04-14: 初始创建'
mastery: solid
related:
- '[[Digital-Twin]]'
- '[[Three.js]]'
- '[[MVP-Scope-Definition]]'
sources:
- sources/archived/2026-04-14_mastered-digital-twin-stack.md
tags:
- IoT
- Architecture
- Real-time
title: Digital Twin Architecture 数字孪生架构
updated: '2026-04-14'
---


# Digital Twin Architecture 数字孪生架构

## 定义

数字孪生架构是指构建数字孪生系统的完整技术栈和数据流设计。它不仅包括可视化层面的 3D 渲染，更重要的是如何实现物理设备与数字模型之间的实时双向同步。

## 核心组件

一个典型的数字孪生架构包含以下层次：

**设备层**：物理设备通过 MQTT 协议发布传感器数据和状态信息。MQTT 的轻量级特性和 QoS 机制保证了 IoT 场景下的可靠传输。

**接入层**：FastAPI 作为后端服务，订阅 MQTT 主题，接收设备数据并进行初步处理（验证、转换、路由）。

**消息队列层**：Redis 充当消息队列角色，解耦数据接收和消费。它支持发布/订阅模式，让多个消费者（如存储服务、实时推送服务）并行处理同一份数据。

**存储层**：PostgreSQL + TimescaleDB 负责时序数据的持久化。TimescaleDB 作为 PostgreSQL 扩展，专门优化了时间序列数据的写入和查询性能。Redis 则缓存最新状态，供快速读取。

**推送层**：FastAPI 通过 WebSocket 将实时数据推送到前端，保持长连接，实现毫秒级延迟。

**可视化层**：Three.js 渲染 3D 场景，接收 WebSocket 数据后更新模型状态（位置、颜色、动画等）。

## MVP 范围

在实际落地时，建议先实现最小可行产品：
- 单一设备 + 简化数据模型
- 完整数据链路：MQTT → FastAPI → Redis → WebSocket → 前端
- 基础功能：实时监控、历史查询、简单可视化、告警通知
- 暂不实现：多租户、复杂规则引擎、AI 预测

这种架构的优势在于各层职责清晰，易于扩展和维护。