---
candidate_count: 3
category: IoT
created: 2026-04-14 16:08
mastered_pages:
- PostgreSQL-TimescaleDB
- MVP-Scope-Definition
source: 2026-04-14_mastered-digital-twin-stack-part2.md
status: pending_review
---

# 候选概念

摘要：用户在数字孪生项目第二阶段中，明确了技术栈选型的两个核心决策：一是选择 PostgreSQL + TimescaleDB 作为时序数据存储方案，理解了 TimescaleDB 作为 PostgreSQL 扩展的本质，以及它与 Redis 在架构中的分工；二是定义了 MVP 范围，梳理出完整的数据流路径（MQTT → FastAPI → Redis → WebSocket → 前端），并明确了分阶段实现策略。这两个决策为项目的技术实现奠定了清晰的基础架构。

已自动内化：PostgreSQL-TimescaleDB, MVP-Scope-Definition

## Hypertable（TimescaleDB 超表）

- readiness: mentioned
- name: Hypertable
- reason: 只是作为 TimescaleDB 的技术特性被提及，用户尚未深入理解其内部机制和使用场景，暂不独立建页

## 数据管道（Data Pipeline）

- readiness: partial
- name: Data-Pipeline
- reason: 在 MVP 定义中提到了数据流路径，但用户对数据管道的设计模式、错误处理、监控等深层概念尚未完全掌握

## WebSocket 实时通信

- readiness: mentioned
- name: WebSocket
- reason: 作为架构中的一个组件被提及，但用户对 WebSocket 协议细节、连接管理、消息可靠性等核心知识点未展开讨论