---
title: Prompt Caching
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
  - caching
---

# Prompt Caching

## 定义

Prompt Caching 是 Claude Code 内部架构的核心机制，按前缀匹配工作，从请求开头到每个 `cache_control` 断点之前的内容被缓存。高命中率不光省钱，速率限制也会松很多，Anthropic 甚至会对命中率跑告警，太低直接宣布 SEV。

## 为什么重要

Prompt Caching 是 Claude Code 整个架构的设计基础。Claude Code 的 Prompt Layout 专门为缓存设计：静态内容（System Prompt、Tool Definitions）在前，动态内容（Chat History、当前用户输入）在后。破坏缓存会导致成本大幅增加和速率限制收紧。与 [[context-management]] 和 [[subagents]] 密切相关。

## 工作原理

Prompt 缓存按前缀匹配工作：

### Claude Code 的 Prompt 顺序

```
1. System Prompt → 静态，锁定
2. Tool Definitions → 静态，锁定
3. Chat History → 动态，在后面
4. 当前用户输入 → 最后
```

### 缓存机制

从请求开头到每个 `cache_control` 断点之前的内容都会被缓存。顺序很重要：静态内容在前，动态内容在后。

### Compaction 的实际实现

Compaction（上下文压缩）执行流程：
1. 左边：上下文快满时的状态
2. 中间：Claude Code 开一个 fork 调用，把完整对话历史喂给模型，加一句"Summarize this conversation"
3. 这一步命中缓存，只需 1/10 的价格
4. 右边：压缩完之后，原来几十轮对话被替换成一段 ~20k tokens 的摘要，System + Tools 还在，再挂上之前用到的文件引用

### MCP 工具的缓存策略

Claude Code 有数十个 MCP 工具，每次请求全量包含会很贵，但中途移除会破坏缓存。解决方案：
- 发送轻量级 stub，只有工具名，标记 `defer_loading: true`
- 模型通过 ToolSearch 工具"发现"它们
- 完整的工具 schema 只在模型选择后才加载
- 缓存前缀保持稳定

## 关键属性 / 权衡

- **缓存粒度**：按前缀匹配，从请求开头到 `cache_control` 断点
- **成本节省**：命中缓存只需 1/10 的价格
- **速率限制**：高命中率速率限制会松很多
- **模型唯一性**：Prompt 缓存是模型唯一的，切换模型会破坏缓存
- **动态信息处理**：当前时间等动态信息不应放在系统 Prompt，应放到下一条消息里（`<system-reminder>` 标签）

## 相关概念

- 建立于：[[context-management]] — Prompt Caching 是上下文管理的基础机制
- 与...配合：[[subagents]] — 会话中途切换模型会破坏缓存，应使用 Subagent 交接
- 与...配合：[[plan-mode]] — Plan Mode 不切换工具集，避免破坏缓存
- 用于：[[claude-md]] — CLAUDE.md 作为静态内容，优先被缓存

## 来源依据

- [[summary-你不知道的-claude-code架构治理与工程实践]] — 主要来源
- raw/你不知道的 Claude Code：架构、治理与工程实践.md — 第 8 节"Prompt Caching：Claude Code 内部架构的核心"

## 待解决问题

- 如何监控和优化 Prompt Caching 命中率？[未验证]
- 不同模型的缓存策略有何差异？[未验证]
- 缓存失效的具体触发条件是什么？[未验证]