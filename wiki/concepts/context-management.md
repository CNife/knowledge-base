---
title: Context Management
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
  - context-surface
---

# Context Management

## 定义

Context Management（上下文工程）是 Claude Code 的最重要系统约束，管理哪些信息常驻、哪些按需加载。200K 上下文并非全部可用，固定开销占 15-20K tokens，动态可用仅 160-180K tokens。

## 为什么重要

卡住的地方通常不是上下文不够长，而是太吵了，有用的信息被大量无关内容淹没了。上下文管理解决上下文污染问题，是 Claude Code 六层架构中的 Context surface 层。与 [[claude-md]]、[[skills]]、[[subagents]]、[[hooks]] 密切相关，是整个架构的基础。

## 工作原理

上下文管理采用分层策略：

### 真实的上下文成本构成

```
200K 总上下文
├── 固定开销 (~15-20K)
│   ├── 系统指令: ~2K
│   ├── 所有启用的 Skill 描述符: ~1-5K
│   ├── MCP Server 工具定义: ~10-20K  ← 最大隐形杀手
│   └── LSP 状态: ~2-5K
│
├── 半固定 (~5-10K)
│   ├── CLAUDE.md: ~2-5K
│   └── Memory: ~1-2K
│
└── 动态可用 (~160-180K)
    ├── 对话历史
    ├── 文件内容
    └── 工具调用结果
```

### 推荐的上下文分层

```
始终常驻    → CLAUDE.md：项目契约 / 构建命令 / 禁止事项
按路径加载  → rules：语言 / 目录 / 文件类型特定规则
按需加载    → Skills：工作流 / 领域知识
隔离加载    → Subagents：大量探索 / 并行研究
不进上下文  → Hooks：确定性脚本 / 审计 / 阻断
```

### MCP 工具定义开销

每个 MCP Server 包含 20-30 个工具，每个约 200 tokens，合计 4,000-6,000 tokens。接 5 个 Server，固定开销约 25,000 tokens（12.5%）。

### Tool Output 噪声

`cargo test` 一次完整输出动辄几千行，`git log`、`find`、`grep` 在稍大的仓库里也能轻松塞满屏幕。这些输出 Claude 并不需要全看，但只要它出现在上下文里，就是实实在在的 token 消耗。

### 压缩机制的陷阱

默认压缩算法按"可重新读取"判断，早期的 Tool Output 和文件内容会被优先删掉，顺带把架构决策和约束理由也一起扔了。解决方案：在 CLAUDE.md 里写明 Compact Instructions。

## 关键属性 / 权衡

- **总上下文**：200K tokens
- **固定开销**：15-20K tokens（系统指令、Skill 描述符、MCP 工具定义、LSP 状态）
- **半固定**：5-10K tokens（CLAUDE.md、Memory）
- **动态可用**：160-180K tokens（对话历史、文件内容、工具调用结果）
- **MCP 工具定义**：每个 Server 4,000-6,000 tokens，接 5 个 Server 约 25,000 tokens（12.5%）
- **Tool Output 噪声**：`cargo test` 等命令输出动辄几千行，挤占动态可用空间

## 相关概念

- 建立于：[[claude-md]] — CLAUDE.md 是上下文分层策略中"始终常驻"的部分
- 建立于：[[skills]] — Skills 是上下文分层策略中"按需加载"的部分
- 建立于：[[subagents]] — Subagents 是上下文分层策略中"隔离加载"的部分
- 建立于：[[hooks]] — Hooks 不进上下文，避免污染
- 建立于：[[prompt-caching]] — Prompt Caching 是上下文管理的基础机制

## 来源依据

- [[summary-你不知道的-claude-code架构治理与工程实践]] — 主要来源
- raw/你不知道的 Claude Code：架构、治理与工程实践.md — 第 3 节"上下文工程：最重要的系统约束"

## 待解决问题

- 如何监控上下文使用情况？`/context` 命令的具体输出格式是什么？[未验证]
- 如何设计 Tool Output 过滤策略？RTK 的具体实现是什么？[未验证]
- 不同任务的上下文需求有何差异？[未验证]