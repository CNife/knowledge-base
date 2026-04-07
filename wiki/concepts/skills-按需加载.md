---
title: Skills 按需加载
type: concept
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
  - skills
  - progressive-disclosure
---

# Skills 按需加载

## 定义

Skills 按需加载是上下文工程的核心模式：系统提示只保留描述符索引，完整知识按需加载。描述符要足够短（避免常驻上下文持续涨 token），也要足够像路由条件而非功能介绍。

## 为什么重要

Skills 实现渐进式披露（progressive disclosure）：模型先获得索引和导航，再按需拉取细节。Skills 反例实验显示，无反例时准确率从 73% 掉到 53%，加反例后升到 85%，响应时间降 18.1%。反例不是可选项，是 Skill 描述能否起作用的关键。

## 工作原理

描述符结构：
```yaml
---
name: deploy
description: Use when deploying to production or rolling back.  # 约 9 tokens
---
```

高效 vs 低效描述符对比：
```yaml
# 低效（约 45 tokens）
description: |
  This skill handles the complete deployment process to production.
  It covers environment checks, rollback procedures, and post-deploy
  verification. Use this before deploying any code to production.

# 高效（约 9 tokens）
description: Use when deploying to production or rolling back.
```

描述符写法要求：
1. **何时用**：Use when / Don't use when
2. **反例**：至少说明什么时候不要用
3. **产出物**：执行后产生什么

调用规则：
1. 每次回复前先扫描 `available_skills`
2. 有明确匹配时再读取对应 SKILL.md
3. 多个匹配时优先选最具体的那个
4. 没有匹配就不读取
5. 一次只加载一个

## 关键属性 / 权衡

- **路由准确率**：无反例 53%，有反例 85%
- **响应时间**：有反例降 18.1%
- **描述符成本**：低效约 45 tokens，高效约 9 tokens
- **调用频率策略**：
  - 高频（>1 次/会话）→ 保持 auto-invoke，优化描述符
  - 低频（<1 次/会话）→ disable-auto-invoke，手动触发
  - 极低频（<1 次/月）→ 移除 Skill，改为 AGENTS.md 文档

## 相关概念

- 建立于：[[上下文工程]] — Skills 是按需加载的具体实现
- 与...协作：[[agent-记忆系统]] — MEMORY.md 与 Skills 协作
- 用于：[[agent-loop]] — 每轮扫描 Skills 描述符

## 来源依据

- [[summary-你不知道的-agent原理架构与工程实践]] — 主要来源
- [[summary-你不知道的-claude-code架构治理与工程实践]] — 主要来源
- raw/你不知道的 Agent：原理、架构与工程实践.md — 第 3 节"为什么 Skills 要按需加载"
- raw/你不知道的 Claude Code：架构、治理与工程实践.md — 第 4 节"Skills 设计"

## 待解决问题

- 最佳描述符长度（当前约 9 tokens 高效，但可能过于简略）
- 多个 Skills 同时匹配时的优先级算法
- Skills 与 MCP 的边界（何时用 Skill，何时用 MCP）[未验证]