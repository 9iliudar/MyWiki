---
category: IoT
created: '2026-04-14'
evolution:
- '2026-04-14: 基于产品经理视角进行单概念入库'
- '2026-04-14: 补充音标与概念边界说明'
- '2026-04-14: 改为概念词典口径，移除具象案例化注解'
mastery: solid
related:
- '[[FastAPI]]'
- '[[MQTT]]'
- '[[Digital-Twin]]'
sources:
- sources/archived/2026-04-14_pm-tech-stack-understanding.md
tags:
- 实时通信
- 前端
- 后端
title: WebSocket /ˈwɛbˌsɒkɪt/
updated: '2026-04-14'
---

# WebSocket /ˈwɛbˌsɒkɪt/

## 定义

WebSocket 是建立在 TCP 之上的持久双向通信协议，用于浏览器与服务端之间的实时数据传输。

## 核心能力

- 单连接双向通信
- 低延迟事件推送
- 减少高频轮询开销

## 在系统中的角色

- 承接前端实时状态同步
- 传递实时事件和反馈结果
- 作为实时交互通道，而非离线消息存储

## 常见误解

- 误解：WebSocket 天然保证强一致和零丢失
- 修正：可靠性仍取决于应用层确认机制与后端设计

## 一句话

`WebSocket 是面向实时交互的长连接通信通道。`
