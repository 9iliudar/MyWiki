---
category: IoT
created: '2026-04-14'
evolution:
- '2026-04-14: 基于产品经理视角进行单概念入库'
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
title: FastAPI
updated: '2026-04-14'
---

# FastAPI

## 定义

FastAPI 是基于 Python 的现代 Web 框架，适合快速构建 API 服务，支持异步处理并自带 OpenAPI 文档生成。

## 在数字孪生项目中的担当

FastAPI 在系统中通常是后端中枢：

- 对外提供 REST 接口（配置、控制、查询）
- 承接设备消息后的业务校验与规则处理
- 协调 [[MQTT]] 与 [[WebSocket]] 的数据流转

## 价值

对产品迭代来说，FastAPI 的价值在于“开发快、改动快、联调快”，适合 MVP 阶段快速验证数据闭环。
