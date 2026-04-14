---
candidate_count: 4
category: IoT
created: 2026-04-14 16:06
mastered_pages:
- Digital-Twin-Architecture
- Redis-Message-Queue
source: 2026-04-14_mastered-digital-twin-stack.md
status: pending_review
---

# 候选概念

摘要：用户在这轮对话中探讨了数字孪生系统的完整技术栈架构。核心讨论集中在如何用 MQTT、FastAPI、Redis、WebSocket 和 Three.js 构建实时数据流动的数字孪生系统。用户明确了 Redis 作为消息队列的角色，理解了 PostgreSQL + TimescaleDB 的时序数据存储方案，并定义了 MVP 范围：从设备数据采集到可视化呈现的完整链路。这是一次架构设计层面的深度实践。

已自动内化：Digital-Twin-Architecture, Redis-Message-Queue

## PostgreSQL + TimescaleDB 时序数据库方案

- readiness: partial
- name: PostgreSQL-TimescaleDB
- reason: 用户理解了 TimescaleDB 是 PostgreSQL 扩展，知道它用于时序数据存储，但尚未深入掌握其分区策略、压缩机制、查询优化等细节。建议在实际使用后再正式内化。

## MQTT 协议

- readiness: mentioned
- name: MQTT-Protocol
- reason: 用户知道 MQTT 用于设备通信，但对其 QoS 级别、主题通配符、遗嘱消息等特性的理解还停留在概念层面，未深入实践。

## WebSocket 实时推送

- readiness: mentioned
- name: WebSocket-Push
- reason: 用户知道 WebSocket 用于服务器到前端的实时推送，但对其连接管理、心跳机制、断线重连等工程细节尚未掌握。

## FastAPI 后端开发

- readiness: partial
- name: FastAPI-Backend
- reason: 用户理解 FastAPI 在架构中的位置，但对其异步编程模型、依赖注入、中间件等高级特性的掌握程度不明确。