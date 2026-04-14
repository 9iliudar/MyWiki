---
category: IoT
created: '2026-04-14'
evolution:
- '2026-04-14: 基于产品经理视角进行单概念入库'
mastery: solid
related:
- '[[Grafana]]'
- '[[Digital-Twin]]'
- '[[Three.js]]'
sources:
- sources/archived/2026-04-14_pm-tech-stack-understanding.md
tags:
- 可视化
- 前端
- 图表
title: ECharts
updated: '2026-04-14'
---

# ECharts

## 定义

ECharts 是前端可视化图表库，适合在业务页面中实现定制化交互图表。

## 在数字孪生项目中的担当

ECharts 负责“业务视角图表”：

- 产线实时指标曲线
- 统计图和趋势图
- 与 3D 场景联动的业务分析面板

## 与 Grafana 的边界

- ECharts：产品页面里的定制化交互图表
- [[Grafana]]：监控平台里的运维看板和告警

两者通常是协同关系，不是二选一。
