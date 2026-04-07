---
title: 摘要 — 你不知道的 Agent：原理、架构与工程实践
type: summary
status: draft
created: 2026-04-07
updated: 2026-04-07
sources:
  - raw/你不知道的 Agent：原理、架构与工程实践.md
links:
  - https://tw93.fun/2026-03-21/agent.html
tags:
  - agent
  - architecture
  - engineering
---

# 摘要 — 你不知道的 Agent：原理、架构与工程实践

## 来源元数据

| 字段        | 值                              |
|--------------|----------------------------------|
| 来源类型     | blog                             |
| 作者         | Tw93                             |
| 年份         | 2026                             |
| 发表于       | tw93.fun                         |
| Raw 文件     | `raw/你不知道的 Agent：原理、架构与工程实践.md` |

## 主要观点

Agent 的工程效果主要由 Harness（测试验证约束基础设施）、上下文工程和工具设计决定，而非模型本身的能力。控制流、上下文分层、ACI 工具设计原则、记忆系统和评测体系是影响 Agent 稳定性的关键要素。

## 关键细节

- **Agent Loop 核心**：感知 → 决策 → 行动 → 反馈四阶段循环，核心实现不到 20 行代码
- **Workflow vs Agent 区别**：控制权在代码预设（Workflow）还是 LLM 动态决策（Agent），核心区别在于决策链是否可预测
- **五种控制模式**：Prompt Chaining、Routing、Parallelization、Orchestrator-Workers、Evaluator-Optimizer
- **Harness 四要素**：验收基线、执行边界、反馈信号、回退手段
- **上下文分层**：常驻层、按需加载层、运行时注入层、记忆层、系统层
- **Prompt Caching**：前缀匹配缓存，稳定的大系统提示比频繁变动的小提示成本更低（90% 折扣）
- **Skills 按需加载**：描述符常驻，完整内容按需注入，反例可提升路由准确率从 53% 到 85%
- **ACI 工具设计**：工具应对应 Agent 目标而非 API 操作，错误应结构化并包含修正建议
- **四种记忆**：工作记忆（上下文窗口）、程序性记忆（Skills）、情景记忆（JSONL 会话历史）、语义记忆（MEMORY.md）
- **Agent 评测结构**：task、trial、grader、transcript、outcome，比 Single-turn 评测复杂不止一个层级
- **两层可观测性**：人工抽样标注 + LLM 自动评估，两层必须一起用
- **OpenClaw 五层架构**：Gateway、Channel 适配器、Pi Agent、工具集、上下文+记忆

## 方法 / 进路

文章采用系统化工程视角，从 Agent Loop 基本运转方式出发，逐层剖析：
1. 控制流基础（Loop 结构、Workflow vs Agent 区别、五种模式）
2. Harness 优先原则（OpenAI Agent 优先开发实践、任务清晰度与验证自动化矩阵）
3. 上下文工程（分层策略、压缩策略、Prompt Caching、Skills 模式）
4. 工具设计演进（API 封装 → ACI → Advanced Tool Use）
5. 记忆系统（四种类型、整合触发与回退）
6. 多 Agent 组织（协作协议、幻觉放大、深度限制）
7. 评测体系（结构复杂性、评分器类型、从零搭建流程）
8. Trace 追踪（两层可观测性、事件流底座）
9. OpenClaw 实现案例（五层解耦、消息总线、系统提示叠加）

## 结果 / 证据

- **Skills 反例实验**：无反例时准确率从 73% 掉到 53%，加反例后升到 85%，响应时间降 18.1%
- **MCP 工具定义开销**：一个典型 MCP Server 约 4,000-6,000 tokens，5 个 Server 合计 25,000 tokens（12.5%）
- **Cursor MCP 优化**：工具描述同步到文件夹，A/B 测试中调用 MCP 工具的任务总 token 消耗减少 46.9%
- **Tool Search 效果**：上下文保留率 95%，Opus 4 准确率从 49% 提升到 74%
- **Programmatic Tool Calling**：token 消耗从约 150,000 降到约 2,000
- **Tool Use Examples**：工具调用准确率从 72% 提升到 90%

## 局限性

- 文章侧重工程实践，未深入讨论 Agent 理论基础（如认知架构、规划算法）
- OpenClaw 为个人实现案例，缺乏大规模生产验证数据
- 多 Agent 协作部分未讨论复杂依赖关系和死锁场景

## 链接到概念

- [[agent-loop]] — Agent 基本运转方式的核心循环结构
- [[harness]] — 测试验证约束基础设施的四要素
- [[上下文工程]] — 分层策略、压缩策略、Prompt Caching
- [[skills-按需加载]] — 渐进式披露原则的实现
- [[aci-工具设计]] — Agent-Computer Interface 设计原则
- [[agent-记忆系统]] — 四种记忆类型与整合机制
- [[agent-评测]] — 评测结构复杂性、评分器类型
- [[trace-追踪]] — 执行过程记录与两层可观测性

## 链接到主题

- [[agent-工程实践]] — Agent 架构、治理与工程实践的系统化梳理

## 值得保留的引用

> 更贵的模型带来的提升，很多时候没有想象中那么大，反而 Harness 和验证测试质量对成功率的影响更大。

> 工具问题多数不在数量不够，而在选不对、描述看不懂、返回一堆没用的、出了错 Agent 也不知道怎么改。

> 评测系统本身的问题，很多时候比 Agent 出问题更难发现，如果一直在 Agent 代码上反复调，效果未必明显。

> 看到评测分数下降，先查环境，再动 Agent。

> 模型负责推理，外部系统负责状态和边界，一旦这个分工确定下来，核心循环逻辑就很少需要频繁调整了。

> 新能力基本只通过三种方式接入：扩展工具集和 handler、调整系统提示结构、把状态外化到文件或数据库，不应该让循环体本身变成一个巨大的状态机。

> Skills 不能等 Agent 想起来再用，要每轮都先扫描描述，但扫描成本要足够低，实际加载数量也要受控。