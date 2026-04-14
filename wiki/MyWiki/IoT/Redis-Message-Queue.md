---
category: IoT
created: '2026-04-14'
evolution:
- '2026-04-14: 初始创建'
mastery: solid
related:
- '[[Digital-Twin-Architecture]]'
sources:
- sources/archived/2026-04-14_mastered-digital-twin-stack.md
tags:
- Redis
- Message-Queue
- Architecture
title: Redis Message Queue Redis 消息队列
updated: '2026-04-14'
---

## 定义

Redis 消息队列是指利用 Redis 的发布/订阅（Pub/Sub）或 Stream 数据结构实现的轻量级消息队列系统。它在数字孪生等实时系统中扮演关键角色，用于解耦数据生产者和消费者。

## 核心特性

**发布/订阅模式**：生产者发布消息到频道（channel），多个消费者可以订阅同一频道，实现一对多的消息分发。这种模式适合实时广播场景，但消息不持久化，订阅者离线时会丢失消息。

**Stream 数据结构**：Redis 5.0 引入的 Stream 提供了更强大的消息队列能力，支持消息持久化、消费者组、消息确认机制，类似 Kafka 但更轻量。

**性能优势**：Redis 基于内存，读写速度极快，适合高频实时数据场景。相比 RabbitMQ 或 Kafka，Redis 部署更简单，延迟更低。

## 在数字孪生中的应用

在数字孪生架构中，Redis 消息队列承担以下职责：
- FastAPI 接收 MQTT 数据后，发布到 Redis 频道
- 存储服务订阅该频道，将数据写入 TimescaleDB
- WebSocket 推送服务订阅该频道，实时推送到前端
- 告警服务订阅该频道，根据规则触发通知

这种设计让各服务独立演进，避免了紧耦合。

## 与 MQTT 的区别

MQTT 是设备到服务器的协议，专为 IoT 设计，支持 QoS、遗嘱消息等机制。Redis 消息队列是服务器内部的消息分发机制，两者职责不同，通常配合使用：MQTT 负责设备接入，Redis 负责后端服务间通信。