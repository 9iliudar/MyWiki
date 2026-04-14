---
title: 2026-04-14_pm-tech-stack-understanding
date_added: 2026-04-14
type: conversation
category: IoT
status: digested
---

Cesium，这个开源的3D引擎JS库，我理解了；FastAPI，这个基于Python的web快速后端接口的实现框架，自带文档，支持异步，开发快，运行也快，我有了解了；Three.js：通用的WebGL图形库，一般用来做轻量的3D渲染引擎，我也了解了；WebSocket，一般用作前端的实时通道，长连接，用于浏览器和服务器之间持久的双向实时通信；MQTT，设备端的通信协议，轻量级，工业现场设备/PLC通常通过MQTT上报状态/接收指令，发布-订阅式通信协议，低带宽、低功耗；PostgreSQL，业务基础数据存储，主数据存储，空间数据也合适；TimescaleDB，时序数据库的一种，通常配合PostgreSQL使用，用来高效存储和查询设备、传感器产生的海量时间戳数据；Redis，基于内存的高性能键值数据库，常用来做缓存、会话存储、消息队列和实时计数器；ECharts，前端绘图组件，适合做实时数据仪表盘和统计分析；Grafana，是开源的数据可视化与监控平台，能接多种数据库快速搭建仪表盘，支持告警通知。

上述概念按单概念方式入库，作为产品经理视角可用认知。
