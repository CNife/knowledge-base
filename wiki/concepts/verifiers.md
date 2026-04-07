---
title: Verifiers
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
  - verification-surface
---

# Verifiers

## 定义

Verifiers 是 Claude Code 的验证闭环机制，让输出可验、可回滚、可审计。"Claude 说完成了"其实没啥用，你得能知道它做没做对、出了问题能退回来、过程还能查，这才算数。没有 Verifier 就没有工程上的 Agent。

## 为什么重要

Verifiers 是 Claude Code 六层架构中的验证层，解决"如何判断任务完成且结果可信"的问题。假如一个任务你说不清楚「什么叫做完」，那大概率也不适合直接扔给 Claude 自主完成，验证标准本身都没有，Claude 再聪明也跑不出正确答案。与 [[claude-md]]、[[skills]]、[[hooks]] 配合使用。

## 工作原理

Verifiers 分为多个层级：

### Verifier 的层级

- **最低层**：命令退出码、lint、typecheck、unit test
- **中间层**：集成测试、截图对比、contract test、smoke test
- **更高层**：生产日志验证、监控指标、人工审查清单

### 在 Prompt、Skill 和 CLAUDE.md 中显式定义验证

```markdown
## Verification

For backend changes:
- Run `make test` and `make lint`
- For API changes, update contract tests under `tests/contracts/`

For UI changes:
- Capture before/after screenshots if visual

Definition of done:
- All tests pass
- Lint passes
- No TODO left behind unless explicitly tracked
```

### 验证闭环的三个要素

1. **可验**：能判断做没做对
2. **可回滚**：出了问题能退回来
3. **可审计**：过程还能查

## 关键属性 / 权衡

- **层级划分**：最低层（命令退出码、lint、typecheck、unit test）、中间层（集成测试、截图对比、contract test、smoke test）、更高层（生产日志验证、监控指标、人工审查清单）
- **定义位置**：在 Prompt、Skill 和 CLAUDE.md 中显式定义验证标准
- **验收标准**：哪些命令跑完算完成，失败了先查什么，截图和日志看到什么才算过
- **任务适用性**：如果说不清楚「什么叫做完」，就不适合直接扔给 Claude 自主完成

## 相关概念

- 建立于：[[claude-md]] — CLAUDE.md 定义验证标准，Verifiers 执行验证
- 建立于：[[skills]] — Skills 定义验证步骤，Verifiers 执行验证
- 与...配合：[[hooks]] — Hooks 可作为 Verifiers 的强制执行层
- 用于：[[plan-mode]] — Plan Mode 确认方案后，Verifiers 执行验证

## 来源依据

- [[summary-你不知道的-claude-code架构治理与工程实践]] — 主要来源
- raw/你不知道的 Claude Code：架构、治理与工程实践.md — 第 9 节"验证闭环：没有 Verifier 就没有工程上的 Agent"

## 待解决问题

- 如何设计 Verifiers 的回滚机制？[未验证]
- 如何设计 Verifiers 的审计日志？[未验证]
- 不同类型任务的 Verifiers 设计有何差异？[未验证]