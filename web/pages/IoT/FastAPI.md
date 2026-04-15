---
category: IoT
created: '2026-04-14'
evolution:
- '2026-04-14: 基于产品经理视角进行单概念入库'
- '2026-04-14: 补充音标与概念边界说明'
- '2026-04-14: 改为概念词典口径，移除具象案例化注解'
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

FastAPI 是 Python Web 框架，强调接口开发效率、异步处理能力和标准化文档输出。

## 核心能力

- 快速构建 REST API
- 基于类型提示的参数校验
- 自动生成 OpenAPI 文档

## 在系统中的角色

- 承担接口层与业务编排层
- 连接数据层、消息层和实时推送层
- 统一处理鉴权、校验、错误响应与服务契约

## 常见误解

- 误解：FastAPI 只是“快速 CRUD 工具”
- 修正：在工程中它同样承担服务边界管理和业务流程编排

## 一句话

`FastAPI 是高效率的 Python 服务接口与编排框架。`
