# 操作日志

> 记录正式知识的 ingest、promote、update 等操作。

## 2026-04-09 22:46

**操作**: ingest
**素材**: 2026-04-09_sdd-spec-schema-prompt.md
**影响页面**: SDD, Spec-Schema-Prompt
**摘要**: 用户通过对话深入理解了 SDD（Spec-Driven Development）方法论及其三个核心执行层次，明确了 Spec、Schema、Prompt 三者的分工关系，并将其正式内化进 AI 分类。

## 2026-04-09 23:35

**操作**: promote
**素材**: 2026-04-09_sdd-spec-schema-prompt.md
**影响页面**: Spec, Schema, Prompt
**摘要**: 用户确认已分别掌握 Spec、Schema、Prompt 三个概念，因此将它们从组合总览页中提升为独立正式页面，同时保留总览页作为三者关系页。

## 2026-04-10 11:55

**操作**: update
**素材**: conversation
**影响页面**: SDD
**摘要**: 补充了 SDD 与 Vibe Coding 的关系：Vibe Coding 降低实现成本，SDD 降低偏航成本；在 AI 开发中，真实产品开发通常更适合采用 SDD + AI 的组合方式。

## 2026-04-10 12:18

**操作**: create
**素材**: conversation
**影响页面**: Digital-Twin
**摘要**: 用户已掌握数字孪生的核心概念、与 IoT/仿真/3D 的区别、常见失败原因、项目技术栈结构，以及从 0 到 1 构建最小可行数字孪生项目的基本步骤，因此将其内化为 IoT 分类下的正式页面。

## 2026-04-10 23:03

**操作**: ingest
**素材**: 2026-04-10_threejs-for-digital-twin.md
**影响页面**: Three.js
**摘要**: 这轮对话明确了 Three.js /θriː dʒeɪ ɛs/ 在数字孪生项目中的定位：它不是建模工具，而是 Web 端 3D 渲染与交互引擎，负责把模型在浏览器里「活起来」。用户掌握了 Three.js 与 Blender、UE 的分工边界，以及本地最小实践路径：Blender 建模 → 导出 glTF/GLB → Three.js 加载渲染 → Vue 做 UI 和数据联动。这是数字孪生技术栈中可视化层的核心选型逻辑。

## 2026-04-14 16:06

**操作**: ingest
**素材**: 2026-04-14_mastered-digital-twin-stack.md
**影响页面**: Digital-Twin-Architecture, Redis-Message-Queue
**摘要**: 用户在这轮对话中探讨了数字孪生系统的完整技术栈架构。核心讨论集中在如何用 MQTT、FastAPI、Redis、WebSocket 和 Three.js 构建实时数据流动的数字孪生系统。用户明确了 Redis 作为消息队列的角色，理解了 PostgreSQL + TimescaleDB 的时序数据存储方案，并定义了 MVP 范围：从设备数据采集到可视化呈现的完整链路。这是一次架构设计层面的深度实践。

## 2026-04-14 16:08

**操作**: ingest
**素材**: 2026-04-14_mastered-digital-twin-stack-part2.md
**影响页面**: PostgreSQL-TimescaleDB, MVP-Scope-Definition
**摘要**: 用户在数字孪生项目第二阶段中，明确了技术栈选型的两个核心决策：一是选择 PostgreSQL + TimescaleDB 作为时序数据存储方案，理解了 TimescaleDB 作为 PostgreSQL 扩展的本质，以及它与 Redis 在架构中的分工；二是定义了 MVP 范围，梳理出完整的数据流路径（MQTT → FastAPI → Redis → WebSocket → 前端），并明确了分阶段实现策略。这两个决策为项目的技术实现奠定了清晰的基础架构。
