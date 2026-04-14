---
category: IoT
created: '2026-04-14'
evolution:
- '2026-04-14: 基于产品经理视角进行单概念入库'
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
title: PostgreSQL
updated: '2026-04-14'
---

# PostgreSQL

## 定义

PostgreSQL 是功能完整的开源关系型数据库，适合事务型业务和结构化数据管理。

## 在数字孪生项目中的担当

PostgreSQL 负责“主数据与关系数据”：

- 园区/厂房/车间/产线/设备台账
- 用户、角色、权限、规则配置
- 需要一致性和关联查询的业务数据

## 与 TimescaleDB、Redis 的关系

- [[TimescaleDB]]：承接历史时序数据
- [[Redis]]：承接最新态和高频缓存

PostgreSQL 是稳定底座，时序与缓存层围绕它补齐能力。
