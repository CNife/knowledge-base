---
title: Plan Mode
type: concept
status: stable
created: 2026-04-07
updated: 2026-04-07
sources:
  - raw/你不知道的 Claude Code：架构、治理与工程实践.md
links:
  - https://tw93.fun/2026-03-12/claude.html
tags:
  - claude-code
  - agent-engineering
  - workflow
---

# Plan Mode

## 定义

Plan Mode 是 Claude Code 的工作模式，将探索和执行拆开：探索阶段以只读操作为主，不动文件；确认方案后再执行。其核心是把执行成本在计划确认之后才发生。

## 为什么重要

Plan Mode 解决"急着出代码"的问题。对于复杂重构、迁移、跨模块改动，这样做比直接执行有用多了，在错误假设上越跑越偏的情况会少很多。与 [[prompt-caching]] 相关：Plan Mode 不切换工具集，避免破坏缓存。实际实现是 `EnterPlanMode` 作为模型可以自己调用的工具，检测到复杂问题时自主进入。

## 工作原理

Plan Mode 将探索和执行拆开：

### 探索阶段

- 以只读操作为主
- Claude 可以先澄清目标和边界
- 再提交具体方案
- 执行成本在计划确认之后才发生

### 进入方式

- 按两下 `Shift+Tab` 进入 Plan Mode
- 或 Claude 检测到复杂问题时自主调用 `EnterPlanMode` 工具

### 进阶玩法

开一个 Claude 写计划，再开一个 Codex 以"高级工程师"身份审这个计划，让 AI 审 AI，效果很好。

### 与缓存的关系

直觉上 Plan Mode 应该切换成只读工具集，但这会破坏缓存。实际实现：`EnterPlanMode` 是模型可以自己调用的工具，工具集不变，缓存不受影响。

## 关键属性 / 权衡

- **执行时机**：探索阶段不动文件，确认方案后再执行
- **成本控制**：执行成本在计划确认之后才发生
- **缓存保护**：不切换工具集，避免破坏缓存
- **AI 审 AI**：开一个 Claude 写计划，再开一个 Codex 审计划
- **适用场景**：复杂重构、迁移、跨模块改动

## 相关概念

- 建立于：[[prompt-caching]] — Plan Mode 不切换工具集，避免破坏缓存
- 与...配合：[[subagents]] — Plan Mode 可使用 Subagent 进行隔离探索
- 与...配合：[[verifiers]] — Plan Mode 确认方案后，Verifiers 执行验证
- 用于：[[context-management]] — Plan Mode 避免在错误假设上浪费上下文

## 来源依据

- [[summary-你不知道的-claude-code架构治理与工程实践]] — 主要来源
- raw/你不知道的 Claude Code：架构、治理与工程实践.md — 第 4 节"Plan Mode 的工程价值"

## 待解决问题

- Plan Mode 与普通模式的切换时机如何判断？[未验证]
- 如何设计 Plan Mode 的计划模板？[未验证]
- Plan Mode 的计划如何与 [[claude-md]] 结合？[未验证]