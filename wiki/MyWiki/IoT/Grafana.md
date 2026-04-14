---
category: IoT
created: '2026-04-14'
evolution:
- '2026-04-14: 基于产品经理视角进行单概念入库'
- '2026-04-14: 补充音标与概念边界说明'
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
title: Grafana /ɡrəˈfɑːnə/
updated: '2026-04-14'
---

# Grafana /ɡrəˈfɑːnə/

## 定义

Grafana 是开源监控与可视化平台，支持多数据源接入、仪表盘配置和告警通知。

## 产品经理可用表述

- Grafana 面向运维与可观测性团队，搭建速度快。
- 它更适合系统健康和告警视角，不是业务前台替代品。

## 在本项目中的担当

- 设备在线率、链路延迟、错误率监控
- 历史趋势大盘与告警阈值配置
- 对接 [[TimescaleDB]] / [[PostgreSQL]] 数据源

## 常见误区

- 误区：Grafana 可以替代业务页面全部图表需求。
- 修正：业务交互图表仍建议用 [[ECharts]] 自研。

## 一句话边界

`Grafana 管可观测性，ECharts 管业务交互。`
