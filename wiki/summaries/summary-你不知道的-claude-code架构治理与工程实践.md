---
title: 摘要 — 你不知道的 Claude Code：架构、治理与工程实践
type: summary
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
  - context-management
---

# 摘要 — 你不知道的 Claude Code：架构、治理与工程实践

## 来源元数据

| 字段        | 值                              |
|--------------|----------------------------------|
| 来源类型     | blog                             |
| 作者         | Tw93                             |
| 年份         | 2026                             |
| 发表于       | https://tw93.fun/2026-03-12/claude.html |
| Raw 文件     | `raw/你不知道的 Claude Code：架构、治理与工程实践.md` |

## 主要观点

Claude Code 应拆成六层架构理解：CLAUDE.md/rules/memory（长期上下文）、Tools/MCP（动作能力）、Skills（按需加载方法论）、Hooks（强制执行）、Subagents（隔离上下文）、Verifiers（验证闭环）。上下文管理是最重要的系统约束，200K 上下文并非全部可用，固定开销（MCP 工具定义等）占 15-20K tokens。Prompt Caching 是 Claude Code 内部架构的核心，按前缀匹配工作。验证闭环是工程上 Agent 的必要条件——没有 Verifier 就没有可靠的自主运作。

## 关键细节

- **上下文成本构成**：200K 总上下文 = 固定开销 15-20K（系统指令 ~2K、Skill 描述符 ~1-5K、MCP 工具定义 ~10-20K、LSP 状态 ~2-5K）+ 半固定 5-10K（CLAUDE.md ~2-5K、Memory ~1-2K）+ 动态可用 160-180K
- **MCP 工具定义开销**：每个 MCP Server 包含 20-30 个工具，每个约 200 tokens，合计 4,000-6,000 tokens。接 5 个 Server，固定开销约 25,000 tokens（12.5%）
- **Anthropic 官方 CLAUDE.md**：约 2.5K tokens，可作为参考基准
- **Prompt 缓存机制**：按前缀匹配工作，从请求开头到每个 `cache_control` 断点之前的内容被缓存。顺序：System Prompt → Tool Definitions → Chat History → 当前用户输入
- **Compaction 执行流程**：fork 调用 + 命中缓存（1/10 价格）+ 摘要替换（~20k tokens）
- **五个诊断层面**：Context surface、Action surface、Control surface、Isolation surface、Verification surface
- **Skills 三种类型**：检查清单型（质量门禁）、工作流型（标准化操作）、领域专家型（封装决策框架）
- **Subagents 内置类型**：Explore（只读扫库，默认 Haiku）、Plan（规划调研）、General-purpose（通用）

## 方法 / 进路

### 六层架构框架

| 层 | 职责 |
| --- | --- |
| `CLAUDE.md` / rules / memory | 长期上下文，告诉 Claude "是什么" |
| `Tools` / `MCP` | 动作能力，告诉 Claude "能做什么" |
| `Skills` | 按需加载的方法论，告诉 Claude "怎么做" |
| `Hooks` | 强制执行某些行为，不依赖 Claude 自己判断 |
| `Subagents` | 隔离上下文的工作者，负责受控自治 |
| `Verifiers` | 验证闭环，让输出可验、可回滚、可审计 |

### 上下文分层策略

```
始终常驻    → CLAUDE.md：项目契约 / 构建命令 / 禁止事项
按路径加载  → rules：语言 / 目录 / 文件类型特定规则
按需加载    → Skills：工作流 / 领域知识
隔离加载    → Subagents：大量探索 / 并行研究
不进上下文  → Hooks：确定性脚本 / 审计 / 阻断
```

### Skills 设计原则

- 描述要让模型知道"何时该用我"，而非"我是干什么的"
- 有完整步骤、输入、输出和停止条件
- 正文只放导航和核心约束，大资料拆到 supporting files
- 有副作用的 Skill 显式设置 `disable-model-invocation: true`

### Hooks + Skills + CLAUDE.md 三层叠加

- `CLAUDE.md`：声明"提交前必须通过测试和 lint"
- `Skill`：告诉 Claude 在什么顺序下运行测试、如何看失败、如何修复
- `Hook`：对关键路径执行硬性校验，必要时阻断

### Subagents 配置约束

- `tools` / `disallowedTools`：限定能用什么工具
- `model`：探索任务用 Haiku/Sonnet，重要审查用 Opus
- `maxTurns`：防止跑飞
- `isolation: worktree`：需要动文件时隔离文件系统

## 结果 / 证据

- **作者实践经验**：半年深度使用，每月 40 刀 2 个账号
- **开源项目验证**：Kaku（Rust + Lua 混合语言项目）实践验证混合语言 Hooks 配置
- **Claude Code 团队内部演进案例**：
  - AskUserQuestion 工具演进：从加参数 → markdown 格式 → 独立工具
  - Todo 工具演进：从强制提醒 → 模型变强后成为枷锁
  - 搜索工具演进：从 RAG → Grep → 渐进式披露
- **RTK（Rust Token Killer）实践**：Tool Output 噪声过滤，`cargo test` 从几千行输出压缩到单行摘要
- **配置健康检查工具**：开源 Skill 项目 `tw93/waza`，一键检查 Claude Code 配置状态

## 局限性

- 文章基于个人实践经验，非系统性研究
- 部分建议可能随 Claude Code 版本更新而变化（如 Todo 工具演进案例）
- 未覆盖所有 Claude Code 功能（如 `/simplify`、`/rewind`、`/btw` 等命令仅简要提及）
- 部分数字为估算值（如 MCP 工具定义 token 数），实际值可能因具体工具而异

## 链接到概念

- [[claude-md]] — 项目级持久契约，每次会话都必须成立的命令、边界、禁止项
- [[hooks]] — 强制执行规则的拦截层，在生命周期事件前后执行规则
- [[subagents]] — 隔离上下文的工作单元，并行研究、限制工具与权限
- [[prompt-caching]] — Claude Code 内部架构的核心，按前缀匹配工作
- [[plan-mode]] — 探索和执行拆开的工作模式，探索阶段不动文件
- [[skills]] — 按需加载的知识与工作流，描述符常驻上下文，完整内容按需加载
- [[context-management]] — 上下文工程，最重要的系统约束
- [[verifiers]] — 验证闭环，让输出可验、可回滚、可审计

## 链接到主题

- [[agent-工程实践]] — AI Agent 工程化实践的最佳实践与方法论

## 值得保留的引用

> 卡住的地方几乎从来不是模型不够聪明，更多时候是给了它错误的上下文，或者写出来了但根本没法判断对不对，也没法撤回。

> 给 Claude 新动作能力用 Tool/MCP，给它一套工作方法用 Skill，需要隔离执行环境用 Subagent，要强制约束和审计用 Hook，跨项目分发用 Plugin。

> 既然你就是要 Claude 停下来问一句，那就直接给它一个专门的工具。加个 flag 或者约定一段输出格式，很多时候它一顺手就略过去了。

> 假如一个任务你说不清楚「什么叫做完」，那大概率也不适合直接扔给 Claude 自主完成，验证标准本身都没有，Claude 再聪明也跑不出正确答案。

> CLAUDE.md 在我看来更像是你和 Claude 之间的协作契约，不是团队文档，也不是知识库，里面只放那些每次会话都得成立的事。