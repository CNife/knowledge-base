---
title: Subagents
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
  - isolation-surface
---

# Subagents

## 定义

Subagents 是从主对话派出去的独立 Claude 实例，有自己的上下文窗口，只用指定的工具，干完汇报结果。其最大价值不是"并行"，而是隔离——扫代码库、跑测试、做审查这类会产生大量输出的事，交给 Subagent 做，主线程只拿一个摘要。

## 为什么重要

Subagents 是 Claude Code 六层架构中的隔离层，解决长会话质量下降问题。大量探索、并行研究会产生大量输出，塞进主线程很快就把有效上下文挤没了。Subagents 提供隔离上下文和权限的工作单元，与 [[context-management]] 密切相关，是上下文分层策略中"隔离加载"的部分。

## 工作原理

Subagents 作为独立 Claude 实例运行，有自己的上下文窗口：

### Claude Code 内置 Subagents

- **Explore**：只读扫库，默认跑 Haiku 省成本
- **Plan**：规划调研
- **General-purpose**：通用

### 配置约束

必须显式约束，避免隔离没有意义：

- `tools` / `disallowedTools`：限定能用什么工具，别给和主线程一样宽的权限
- `model`：探索任务用 Haiku/Sonnet，重要审查用 Opus
- `maxTurns`：防止跑飞
- `isolation: worktree`：需要动文件时隔离文件系统

### 后台运行

长时间运行的 bash 命令可以按 `Ctrl+B` 移到后台，Claude 之后会用 BashOutput 工具查看结果，不会阻塞主线程继续工作。Subagent 同理，直接告诉它「在后台跑」就行。

## 关键属性 / 权衡

- **上下文隔离**：有自己的上下文窗口，不污染主线程
- **权限约束**：必须显式限定工具和权限，避免隔离没有意义
- **模型选择**：探索任务用 Haiku/Sonnet 省成本，重要审查用 Opus
- **输出格式**：必须固定，主线程拿到才能用
- **任务依赖**：子任务之间不应强依赖，频繁共享中间状态不适合用 Subagent

## 相关概念

- 建立于：[[context-management]] — Subagents 是上下文分层策略中"隔离加载"的部分
- 与...对比：[[hooks]] — Hooks 用于强制执行规则，Subagents 用于隔离上下文
- 与...配合：[[prompt-caching]] — 会话中途切换模型会破坏缓存，应使用 Subagent 交接
- 用于：[[plan-mode]] — Plan Mode 可使用 Subagent 进行隔离探索

## 来源依据

- [[summary-你不知道的-claude-code架构治理与工程实践]] — 主要来源
- raw/你不知道的 Claude Code：架构、治理与工程实践.md — 第 7 节"Subagents：派一个独立的 Claude 去干一件具体的事"

## 待解决问题

- Subagents 与主线程的通信协议是什么？[未验证]
- 如何设计 Subagents 的错误处理和结果回收机制？[未验证]
- 多个 Subagents 之间如何协调？[未验证]