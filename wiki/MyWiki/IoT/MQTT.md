---
category: IoT
created: '2026-04-14'
evolution:
- '2026-04-14: 基于产品经理视角进行单概念入库'
- '2026-04-14: 补充音标与概念边界说明'
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
title: MQTT /ˌɛm kjuː tiː tiː/
updated: '2026-04-14'
---

# MQTT /ˌɛm kjuː tiː tiː/

## 定义

MQTT 是轻量级发布-订阅消息协议，常用于设备、网关、PLC 与平台之间的实时通信。

## 产品经理可用表述

- MQTT 适合设备侧低带宽、弱网和高并发接入。
- 它把“设备通信”从业务接口中解耦出来。

## 在本项目中的担当

- 设备状态上报（telemetry）
- 控制指令下发（command）
- 状态/执行回执（ack）

## 常见误区

- 误区：MQTT 就能直接替代前端实时推送。
- 修正：设备侧用 MQTT，页面侧通常仍通过 [[WebSocket]] 推送。

## 一句话边界

`MQTT 负责设备接入，FastAPI 负责业务编排。`
