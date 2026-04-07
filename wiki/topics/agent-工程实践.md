---
title: Agent 工程实践
type: topic
status: draft
created: 2026-04-07
updated: 2026-04-07
sources:
  - raw/你不知道的 Agent：原理、架构与工程实践.md
  - raw/你不知道的 Claude Code：架构、治理与工程实践.md
links:
  - https://tw93.fun/2026-03-21/agent.html
  - https://tw93.fun/2026-03-12/claude.html
tags:
  - agent
  - engineering
  - best-practices
---

# Agent 工程实践

## 范围

此主题涵盖 AI Agent 的工程化实践，包括控制流设计、上下文管理、工具设计、记忆系统、多 Agent 组织、评测体系和可观测性。属于 AI Agent 领域，侧重工程实现而非理论研究。

排除：Agent 理论基础（认知架构、规划算法）、强化学习理论、自然语言处理基础。

## 子问题

1. Agent 控制流如何稳定运转（[[agent-loop]]）
2. 如何管理模型上下文避免污染（[[上下文工程]]）
3. 工具设计如何让 Agent 选对（[[aci-工具设计]]）
4. 记忆系统如何跨会话保持状态（[[agent-记忆系统]]）
5. 评测体系如何验证 Agent 行为（[[agent-评测]]）
6. 执行过程如何追踪和调试（[[trace-追踪]]）
7. 测试验证约束基础设施如何搭建（[[harness]]）

## 关键进路

### 进路 1：Harness 优先原则

任务清晰度和验证自动化程度决定 Agent 适用区域。目标明确、结果可自动验证的场景最适合 Agent。[[harness]] 是比模型更关键的基础设施。

### 进路 2：上下文分层管理

按信息使用频率和稳定性分层：常驻层、按需加载层、运行时注入层、记忆层、系统层。[[上下文工程]] 和 [[skills-按需加载]] 实现渐进式披露。

### 进路 3：ACI 工具设计

工具对应 Agent 目标而非 API 操作。错误结构化并包含修正建议。[[aci-工具设计]] 让 Agent 更容易一次选对，失败后也能快速修正。

### 进路 4：两层可观测性

人工抽样标注 + LLM 自动评估，两层必须一起用。[[trace-追踪]] 提供完整执行记录，[[agent-评测]] 基于 Trace 验证行为。

## 系统 / 论文概览

| 系统          | 年份    | 关键贡献                           | 链接                    |
|--------------|--------|-----------------------------------|------------------------|
| Claude Code  | 2026   | 六层架构：Context、Action、Control、Isolation、Verification | [[summary-你不知道的-claude-code架构治理与工程实践]] |
| OpenClaw     | 2026   | 五层解耦：Gateway、Channel、Pi Agent、工具集、上下文+记忆 | [[summary-你不知道的-agent原理架构与工程实践]] |

## 重要参考

- Tw93（2026）—"你不知道的 Agent：原理、架构与工程实践" — [[summary-你不知道的-agent原理架构与工程实践]] — Agent 工程化系统梳理
- Tw93（2026）—"你不知道的 Claude Code：架构、治理与工程实践" — [[summary-你不知道的-claude-code架构治理与工程实践]] — Claude Code 六层架构

## 待解决问题

- 多 Agent 协作时的状态同步与冲突解决 [未验证]
- Agent 自主度与安全性的权衡
- 长任务跨 session 继续的最佳实践

## 相关主题

- [[LLM-辅助知识管理]] — LLM Wiki 模式与知识管理