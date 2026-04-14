---
category: IoT
created: '2026-04-14'
evolution:
- '2026-04-14: 基于产品经理视角进行单概念入库'
- '2026-04-14: 补充音标与概念边界说明'
mastery: solid
related:
- '[[TimescaleDB]]'
- '[[Redis]]'
- '[[Digital-Twin]]'
sources:
- sources/archived/2026-04-14_pm-tech-stack-understanding.md
tags:
- 数据库
- 关系型数据库
- 主数据
title: PostgreSQL /ˈpoʊstɡrɛs kjuː ˈɛl/
updated: '2026-04-14'
---

# PostgreSQL /ˈpoʊstɡrɛs kjuː ˈɛl/

## 定义

PostgreSQL 是开源关系型数据库，擅长事务一致性、结构化建模和复杂关联查询。

## 产品经理可用表述

- PostgreSQL 负责“对象和关系”，是业务主数据底座。
- 它保证配置、权限、台账等关键数据的稳定性。

## 在本项目中的担当

- 园区/厂房/车间/产线/设备台账
- 用户、角色、权限、规则配置
- 与 [[TimescaleDB]] 和 [[Redis]] 协同分层

## 常见误区

- 误区：PostgreSQL 也可直接承载全部时序场景，无需分层。
- 修正：高频时序建议交给 [[TimescaleDB]]，最新态交给 [[Redis]]。

## 一句话边界

`PostgreSQL 管主数据与关系数据。`
