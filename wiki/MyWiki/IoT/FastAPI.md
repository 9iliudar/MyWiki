---
category: IoT
created: '2026-04-14'
evolution:
- '2026-04-14: 基于产品经理视角进行单概念入库'
- '2026-04-14: 补充音标与概念边界说明'
mastery: solid
related:
- '[[MQTT]]'
- '[[WebSocket]]'
- '[[Digital-Twin]]'
sources:
- sources/archived/2026-04-14_pm-tech-stack-understanding.md
tags:
- Python
- 后端
- API
title: FastAPI /ˌfæst ˌeɪpiːˈaɪ/
updated: '2026-04-14'
---

# FastAPI /ˌfæst ˌeɪpiːˈaɪ/

## 定义

FastAPI 是 Python Web 框架，强调开发效率、异步能力和接口文档自动化。

## 产品经理可用表述

- FastAPI 是后端编排中枢，不只是“开接口工具”。
- 它让 MVP 阶段的联调和改接口成本更低。

## 在本项目中的担当

- 提供配置、控制、查询等 REST 接口
- 承接设备消息后的校验、去重和规则处理
- 协调 [[MQTT]]（设备侧）与 [[WebSocket]]（前端侧）

## 常见误区

- 误区：FastAPI 只负责 CRUD。
- 修正：在数字孪生中它还承担实时链路编排和状态确认逻辑。

## 一句话边界

`FastAPI 是业务与实时链路的后端中枢。`
