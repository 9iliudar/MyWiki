---
category: IoT
created: '2026-04-14'
evolution:
- '2026-04-14: 基于产品经理视角进行单概念入库'
mastery: solid
related:
- '[[FastAPI]]'
- '[[WebSocket]]'
- '[[Digital-Twin]]'
sources:
- sources/archived/2026-04-14_pm-tech-stack-understanding.md
tags:
- IoT
- 通信协议
- 设备接入
title: MQTT
updated: '2026-04-14'
---

# MQTT

## 定义

MQTT 是轻量级发布-订阅消息协议，常用于设备、网关、PLC 与平台之间的数据上报和指令下发。

## 在数字孪生项目中的担当

MQTT 负责“设备侧通信”：

- 设备状态上报
- 平台控制指令下发
- 弱网环境下的低带宽消息传输

## 关键边界

MQTT 不直接替代页面推送。常见架构是：

`设备 -> MQTT -> FastAPI -> WebSocket -> 前端`

即 MQTT 连设备，WebSocket 连浏览器，两者协同而非互斥。
