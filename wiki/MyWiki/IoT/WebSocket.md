---
category: IoT
created: '2026-04-14'
evolution:
- '2026-04-14: 基于产品经理视角进行单概念入库'
- '2026-04-14: 补充音标与概念边界说明'
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

WebSocket 是浏览器与服务器之间的持久双向通信协议，适合低延迟实时推送。

## 产品经理可用表述

- WebSocket 让页面“被动接收更新”，而不是不断轮询。
- 它是前端实时体验的主通道。

## 在本项目中的担当

- 向前端推送设备状态、告警和回执
- 驱动 3D 场景与图表的实时联动
- 与 [[FastAPI]] 配合完成连接管理和事件分发

## 常见误区

- 误区：WebSocket 天然保证毫秒级和零丢失。
- 修正：端到端延迟和可靠性还取决于后端、网络和消息策略。

## 一句话边界

`MQTT 连设备，WebSocket 连浏览器。`
