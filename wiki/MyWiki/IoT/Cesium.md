---
category: IoT
created: '2026-04-14'
evolution:
- '2026-04-14: 基于产品经理视角进行单概念入库'
- '2026-04-14: 补充音标与概念边界说明'
mastery: solid
related:
- '[[Digital-Twin]]'
- '[[Three.js]]'
- '[[ECharts]]'
sources:
- sources/archived/2026-04-14_pm-tech-stack-understanding.md
tags:
- GIS
- 3D可视化
- 数字孪生
title: Cesium /ˈsiːziəm/
updated: '2026-04-14'
---

# Cesium /ˈsiːziəm/

## 定义

Cesium 是面向地理空间的 Web 3D 引擎，擅长处理经纬度坐标、地形和大范围地图场景。

## 产品经理可用表述

- Cesium 解决“园区对象在哪里”，不是“设备部件怎么动”。
- 它适合做园区级总览、导航和空间定位。

## 在本项目中的担当

- 渲染园区边界、道路、厂区分区与点位
- 支撑鸟瞰视角、缩放漫游和区域切换
- 与 [[Three.js]] 协同：总览层用 Cesium，车间层用 Three.js

## 常见误区

- 误区：Cesium 可以直接替代所有车间动画需求。
- 修正：车间精细动画和部件交互通常交给 [[Three.js]]。

## 一句话边界

`Cesium 管地理空间定位，Three.js 管车间精细动态。`
