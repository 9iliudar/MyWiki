---
category: IoT
created: '2026-04-14'
evolution:
- '2026-04-14: 基于产品经理视角进行单概念入库'
mastery: solid
related:
- '[[ECharts]]'
- '[[TimescaleDB]]'
- '[[PostgreSQL]]'
sources:
- sources/archived/2026-04-14_pm-tech-stack-understanding.md
tags:
- 监控
- 运维
- 可观测性
title: Grafana
updated: '2026-04-14'
---

# Grafana

## 定义

Grafana 是开源监控与可视化平台，支持多数据源接入、仪表盘配置和告警通知。

## 在数字孪生项目中的担当

Grafana 负责“运维与可观测看板”：

- 服务与链路健康监控
- 设备在线率、告警趋势与系统性能指标
- 阈值告警与通知路由

## 与 ECharts 的边界

- [[ECharts]] 面向业务交互和产品前台
- Grafana 面向运维监控和后台观测

分层使用能降低开发成本，同时保留业务页面定制能力。
