---
title: AI 编码实践
type: topic
status: draft
created: 2026-04-07
updated: 2026-04-07
sources:
  - raw/2026 年 AI 编码的"渐进式 Spec"实战指南.md
links:
  - https://mp.weixin.qq.com/s?__biz=MzIzOTU0NTQ0MA==&mid=2247559315&idx=1&sn=5c1f9df548e912354b5b5e25ec4bcbb5
tags:
  - ai-coding
  - methodology
---

# AI 编码实践

## 范围

此主题涵盖 AI 辅助编码的方法论、工具选型与工程实践。属于 AI Agent 领域。

明确排除：
- 纯粹的代码生成工具（无 Agent 能力）
- 低代码/无代码平台
- 传统 IDE 的代码补全功能

## 子问题

1. **方法论设计**：如何设计 AI 编码的工作流程和约束机制？
2. **工具选型**：如何选择合适的 AI 编码工具？
3. **架构设计**：如何设计 AI 编码系统的架构？
4. **知识管理**：如何管理和沉淀领域知识？
5. **质量保障**：如何保障 AI 编码的质量？
6. **协作模式**：人和 AI 如何协作？

## 关键进路

### 进路 1：Spec Coding

在让 AI 写代码之前，先用结构化文档（Spec）把"要做什么、怎么做、有什么约束"说清楚，然后 AI 围绕这份文档编码。

核心机制：
- [[Spec-Coding]] — Spec Coding 的定义和原理
- [[Reverse-Sync]] — 保持 Spec 和代码一致性的机制
- [[渐进式编码]] — Spec Coding 的渐进式落地方式

### 进路 2：编排层 + 执行层

两层 AI 架构：编排层 AI（强模型）负责理解需求、生成 Spec、审查结果；执行层 AI（编码工具）负责读写代码、执行命令、运行测试。

核心机制：
- [[编排层与执行层]] — 两层架构的定义和原理
- [[上下文工程]] — 编排层负责上下文管理

### 进路 3：知识飞轮

需求实践 → 踩坑 → 沉淀 knowledge / 更新 prompt / 修改模板 → AI 更准 → 更好的实践。

核心机制：
- [[知识飞轮]] — 知识飞轮的定义和原理

## 系统 / 论文概览

| 名称 | 年份 | 关键贡献 | 链接 |
|------|------|----------|------|
| code_copilot 框架 | 2026 | 渐进式 Spec Coding 框架，编排层+执行层架构 | [[summary-2026-ai-bian-ma-jian-jin-shi-spec-shi-zhan-zhi-nan]] |
| Claude Code | 2025 | Anthropic 官方终端 AI 编码 Agent | https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview |
| opencode | 2025 | 开源终端 AI 编码 Agent，模型自由选择 | https://opencode.ai/docs/ |
| Cursor | 2025 | IDE 内交互式 AI 搭档 | https://cursor.sh/ |
| Superpowers | 2025 | agentic skills 框架（HARD-GATE、两阶段 review） | https://github.com/obra/superpowers |

## 重要参考

- 逸驹（2026）— "2026 年 AI 编码的'渐进式 Spec'实战指南" — [[summary-2026-ai-bian-ma-jian-jin-shi-spec-shi-zhan-zhi-nan]] — 渐进式 Spec Coding 框架的完整实践
- Simon Willison（2026）— "Writing about Agentic Engineering Patterns" — https://simonwillison.net/2026/Feb/23/agentic-engineering-patterns/ — Agent 工程模式
- Simon Willison（2026）— "Writing code is cheap now" — https://simonwillison.net/guides/agentic-engineering-patterns/code-is-cheap/ — Code is Cheap 原则
- Frederick Brooks（1975）— 《人月神话》— 软件复杂度理论

## 待解决问题

- **复杂度分级标准**：如何量化定义需求复杂度？[未验证]
- **知识质量保障**：如何确保沉淀的知识是高质量的？[未验证]
- **跨团队一致性**：不同团队如何统一 AI 编码方法论？[未验证]
- **自动化程度**：能否让 AI 自动判断需求复杂度和选择流程？[未验证]

## 相关主题

- [[Agent-工程实践]] — Agent 架构、治理与工程实践的系统化梳理
- [[LLM-辅助知识管理]] — LLM Wiki 模式与增量式知识管理