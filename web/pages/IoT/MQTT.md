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

MQTT 是轻量级发布-订阅消息协议，常用于资源受限设备与服务端之间的消息通信。

## 核心能力

- 主题订阅模型（topic-based pub/sub）
- 低带宽开销与弱网适应
- QoS 等级控制消息投递语义

## 在系统中的角色

- 设备侧数据上报与指令下发
- 设备通信域与业务处理域解耦
- 与接口服务和实时推送通道协同工作

## 常见误解

- 误解：MQTT 可直接替代所有实时前端通信
- 修正：MQTT侧重设备通信，前端实时展示通常由 [[WebSocket]] 承担

## 一句话

`MQTT 是 IoT 设备通信的轻量级消息协议。`
