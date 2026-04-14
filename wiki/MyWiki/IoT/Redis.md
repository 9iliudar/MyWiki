---
category: IoT
created: '2026-04-14'
evolution:
- '2026-04-14: 基于产品经理视角进行单概念入库'
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
title: Redis
updated: '2026-04-14'
---

# Redis

## 定义

Redis 是高性能内存数据库，适合高频读写的实时场景。

## 在数字孪生项目中的担当

Redis 主要承担“实时层”职责：

- 缓存设备最新状态
- 保存短期会话与在线连接信息
- 作为高频消息缓冲与削峰层

## 与持久化库的分工

- 持久历史和结构化数据交给 [[PostgreSQL]] / [[TimescaleDB]]
- Redis 负责“快”和“当前态”

这样可同时兼顾实时响应与历史可追溯。
