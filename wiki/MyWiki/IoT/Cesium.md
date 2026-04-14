---
category: IoT
created: '2026-04-14'
evolution:
- '2026-04-14: 基于产品经理视角进行单概念入库'
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
title: Cesium
updated: '2026-04-14'
---

# Cesium

## 定义

Cesium 是面向地理空间的 Web 3D 引擎，核心能力是地理坐标、地形、影像瓦片和大范围场景渲染。

## 在数字孪生项目中的担当

在园区层面，Cesium 负责“宏观地图框架”：

- 园区边界、道路、厂区分区和点位定位
- 鸟瞰视角和跨区域缩放
- 地理空间语义一致的场景导航

## 与 Three.js 的边界

- Cesium：解决“园区里对象在哪里”
- Three.js：解决“车间里对象怎么动”

常见做法是总览层用 Cesium，进入车间后切到 [[Three.js]] 做精细设备动画。

## 选型提示

若项目不需要真实地理语义（经纬度、地形、GIS 叠加），可不强制引入 Cesium；若要做园区级空间定位，Cesium 通常更稳妥。
