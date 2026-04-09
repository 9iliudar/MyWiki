---
status: digested
---

# AI 驾驭工程（Harness Engineering）

一种驾驭 AI 的工程方法论。宗旨：设计好约束，管理好熵增，让 AI 在安全的边界内稳定输出价值。

## 核心思想

AI 本身是高熵的（不确定、不可控），工程师的工作不是写代码让 AI 更聪明，而是设计约束让 AI 更可靠。

## 三大支柱

### 1. 约束设计（Constraint Design）
- 给 AI 划定边界：什么能做、什么不能做、输出格式是什么
- 类比：不是训练马跑得更快，而是修好赛道和护栏
- 实践：CLAUDE.md/AGENTS.md 告诉 AI 在项目中该怎么行为；Schema 层定义 Wiki 的运行规则

### 2. 熵管理（Entropy Management）
- AI 每次输出都有随机性，多轮对话后偏差会放大
- 对策：结构化 prompt、校验输出、反馈闭环
- 实践：JSON schema 校验 LLM 输出，3 级 fallback 解析确保鲁棒性

### 3. 价值稳定输出（Stable Value Delivery）
- 目标不是 AI 偶尔惊艳，而是每次都能用
- 可复现 > 偶发精彩
- 实践：MCP 工具标准化 ingest/query/lint，不依赖用户措辞方式

## 与 LLM Wiki 的关系

LLM Wiki 项目本身就是驾驭工程的实践案例：
- Schema 层 = 约束设计
- json_utils.py 的 3 级 fallback = 熵管理
- MCP + CLAUDE.md + AGENTS.md = 让任何 AI 在边界内稳定输出