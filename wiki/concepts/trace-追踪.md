---
title: Trace 追踪
type: concept
status: draft
created: 2026-04-07
updated: 2026-04-07
sources:
  - raw/你不知道的 Agent：原理、架构与工程实践.md
links:
  - https://tw93.fun/2026-03-21/agent.html
tags:
  - agent
  - observability
  - debugging
---

# Trace 追踪

## 定义

Trace 追踪是记录 Agent 完整执行过程的机制，包括完整 Prompt、多轮 messages[]、工具调用与返回、推理链、最终输出、token 消耗和延迟。没有完整 Trace，失败案例无法稳定复现。

## 为什么重要

传统 APM 只监控延迟和错误率，接口层看起来正常但真正问题在模型某一轮错误决策。只有回看完整 Trace 才能定位问题。Trace 是 [[agent-评测]] 和 [[harness]] 的数据基础。

## 工作原理

Trace 记录内容：
```
每次 Agent 运行：
├── 完整 Prompt，含系统提示
├── 多轮交互的完整 messages[]
├── 每次工具调用 + 参数 + 返回值
├── 推理链，如有 thinking 模式
├── 最终输出
└── token 消耗 + 延迟
```

两层可观测性：
1. **人工抽样标注**：基于规则采样错误案例、长对话和用户负反馈，由人工判断执行质量和失败原因，主要用来摸清失败模式
2. **LLM 自动评估**：对更大范围的 Trace 做全量覆盖，以第一层标注结果作为校准依据

事件流底座：
- Agent Loop 在 `tool_start`、`tool_end`、`turn_end` 三个节点发出事件
- 完整 Trace 同步落盘，再分发给日志系统、UI 更新、在线评测、人工审查队列
- 事件一次发布，多路消费，主循环不需要为任何下游改代码

## 关键属性 / 权衡

- **在线评测采样率**：10-20% 的 Trace 运行在线评测
- **采样规则**：负反馈触发 100% 进队列、高成本对话优先审查、模型或 Prompt 变更后头 48 小时全量审查
- **语义检索能力**：查询「哪些 Trace 里 Agent 混淆了两种工具」，不只精确字符串匹配

## 相关概念

- 数据来源：[[agent-loop]] — Loop 发出事件
- 用于：[[agent-评测]] — Transcript 是评测数据
- 实现：[[harness]] — Trace 是验证数据来源

## 来源依据

- [[summary-你不知道的-agent原理架构与工程实践]] — 主要来源
- raw/你不知道的 Agent：原理、架构与工程实践.md — 第 9 节"如何追踪 Agent 的执行过程"

## 待解决问题

- Trace 存储成本与查询效率（大规模场景）
- 敏感信息脱敏（Trace 包含完整用户输入）
- Trace 分析自动化程度 [未验证]