---
category: IoT
created: '2026-04-14'
evolution:
- '2026-04-14: 基于产品经理视角进行单概念入库'
- '2026-04-14: 补充音标与概念边界说明'
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

Redis 是高性能内存数据库，适合承载实时状态、短期缓存和高频读写场景。

## 产品经理可用表述

- Redis 的核心价值是“快”，不是“全量历史存档”。
- 它常作为实时层，提升页面与服务响应速度。

## 在本项目中的担当

- 缓存设备最新状态
- 保存在线会话、短期去重窗口
- 对高频消息做缓冲与削峰

## 常见误区

- 误区：把 Redis 当长期事实库使用。
- 修正：长期历史应落在 [[PostgreSQL]] / [[TimescaleDB]]。

## 一句话边界

`Redis 管实时态，不管长期历史。`
