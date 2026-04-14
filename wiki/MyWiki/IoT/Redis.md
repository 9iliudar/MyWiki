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
- '[[TimescaleDB]]'
- '[[WebSocket]]'
sources:
- sources/archived/2026-04-14_pm-tech-stack-understanding.md
tags:
- 缓存
- 实时系统
- 内存数据库
title: Redis /ˈrɛdɪs/
updated: '2026-04-14'
---

# Redis /ˈrɛdɪs/

## 定义

Redis 是内存数据库，强调高吞吐、低延迟和多数据结构支持。

## 核心能力

- 高频读写与热点缓存
- 短周期状态管理
- 轻量消息分发与缓冲

## 在分层架构中的角色

- 承接实时状态层
- 降低核心数据库读写压力
- 与 [[PostgreSQL]] / [[TimescaleDB]] 配合形成冷热分层

## 常见误解

- 误解：Redis 可直接替代长期持久化数据库
- 修正：长期事实数据仍应由持久化数据库承担

## 一句话

`Redis 负责实时态与高频访问层。`
