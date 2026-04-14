---
category: IoT
created: '2026-04-14'
evolution:
- '2026-04-14: 基于产品经理视角进行单概念入库'
- '2026-04-14: 补充音标与概念边界说明'
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
title: ECharts /ˈiː tʃɑːrts/
updated: '2026-04-14'
---

# ECharts /ˈiː tʃɑːrts/

## 定义

ECharts 是前端图表库，适合在业务页面中构建可交互、可定制的数据可视化。

## 产品经理可用表述

- ECharts 面向业务用户，强调页面交互和视觉统一。
- 它适合与 3D 场景联动展示业务指标。

## 在本项目中的担当

- 产线实时曲线与统计图
- 设备状态分布与趋势图
- 与 [[Three.js]] 场景状态联动

## 常见误区

- 误区：ECharts 等同于监控平台。
- 修正：运维监控与告警平台通常交给 [[Grafana]]。

## 一句话边界

`ECharts 管业务可视化，Grafana 管运维监控。`
