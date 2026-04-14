---
category: IoT
created: '2026-04-14'
evolution:
- '2026-04-14: 基于产品经理视角进行单概念入库'
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
title: WebSocket
updated: '2026-04-14'
---

# WebSocket

## 定义

WebSocket 是浏览器与服务器之间的持久双向通信协议，建立连接后可持续推送数据，无需反复轮询。

## 在数字孪生项目中的担当

WebSocket 负责“前端实时通道”：

- 把设备状态变化实时推送到页面
- 让 3D 场景和图表及时联动
- 支持前后端双向事件通信

## 与 MQTT 的边界

- [[MQTT]] 主要面向设备侧接入
- WebSocket 主要面向浏览器侧展示

它们通常由 [[FastAPI]] 协调，形成“设备世界到页面世界”的实时链路。
