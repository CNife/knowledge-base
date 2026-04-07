---
title: CLAUDE.md
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
  - context-management
---

# CLAUDE.md

## 定义

CLAUDE.md 是 Claude Code 的项目级持久契约文件，定义每次会话都必须成立的命令、边界和禁止项。它不是团队文档或知识库，而是与 Claude 之间的协作契约，只放那些每次会话都得成立的事。

## 为什么重要

CLAUDE.md 是 Claude Code 六层架构中的长期上下文层，告诉 Claude "是什么"。它解决上下文污染问题——如果写成团队知识库，每次加载都会污染上下文，关键指令被稀释。Anthropic 官方 CLAUDE.md 约 2.5K tokens，可作为参考基准。与 [[context-management]] 密切相关，是上下文分层策略中"始终常驻"的部分。

## 工作原理

CLAUDE.md 在每次会话开始时自动加载，常驻上下文。其内容应包括：

1. **Build And Test**：怎么构建、怎么测试、怎么运行（最核心）
2. **Architecture Boundaries**：关键目录结构与模块边界
3. **Coding Conventions**：代码风格和命名约束
4. **Safety Rails**：绝对不能干的事（NEVER 列表）和必须做的事（ALWAYS 列表）
5. **Verification**：验证标准
6. **Compact Instructions**：压缩时必须保留的信息

### 高质量模板结构

```markdown
# Project Contract

## Build And Test
- Install: `pnpm install`
- Dev: `pnpm dev`
- Test: `pnpm test`
- Typecheck: `pnpm typecheck`
- Lint: `pnpm lint`

## Architecture Boundaries
- HTTP handlers live in `src/http/handlers/`
- Domain logic lives in `src/domain/`
- Do not put persistence logic in handlers
- Shared types live in `src/contracts/`

## Coding Conventions
- Prefer pure functions in domain layer
- Do not introduce new global state without explicit justification
- Reuse existing error types from `src/errors/`

## Safety Rails
## NEVER
- Modify `.env`, lockfiles, or CI secrets without explicit approval
- Remove feature flags without searching all call sites
- Commit without running tests

## ALWAYS
- Show diff before committing
- Update CHANGELOG for user-facing changes

## Verification
- Backend changes: `make test` + `make lint`
- API changes: update contract tests under `tests/contracts/`
- UI changes: capture before/after screenshots

## Compact Instructions
Preserve:
1. Architecture decisions (NEVER summarize)
2. Modified files and key changes
3. Current verification status (pass/fail commands)
4. Open risks, TODOs, rollback notes
```

## 关键属性 / 权衡

- **Token 成本**：约 2-5K tokens（半固定开销），应保持短、硬、可执行
- **加载时机**：每次会话开始时自动加载，始终常驻
- **内容边界**：只放契约，不放背景资料和低频任务知识（这些放到 [[skills]]）
- **演进方式**：每次纠正 Claude 错误后，让它自己更新："Update your CLAUDE.md so you don't make that mistake again."
- **与 rules 的区别**：`.claude/rules/*` 用于路径或语言相关规则，避免所有规则都堆到根 CLAUDE.md

## 相关概念

- 建立于：[[context-management]] — CLAUDE.md 是上下文分层策略中"始终常驻"的部分
- 与...对比：[[skills]] — Skills 是按需加载的工作流，CLAUDE.md 是始终常驻的契约
- 与...配合：[[hooks]] — CLAUDE.md 声明约束，Hooks 强制执行
- 与...配合：[[verifiers]] — CLAUDE.md 定义验证标准，Verifiers 执行验证

## 来源依据

- [[summary-你不知道的-claude-code架构治理与工程实践]] — 主要来源
- raw/你不知道的 Claude Code：架构、治理与工程实践.md — 第 12 节"如何写一个好的 CLAUDE.md"

## 待解决问题

- 如何定期 review CLAUDE.md，识别过时的条目？[未验证]
- CLAUDE.md 与 `.claude/rules/*` 的最佳分工边界是什么？[未验证]