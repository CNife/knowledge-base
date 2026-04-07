---
title: Skills
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

# Skills

## 定义

Skills 是 Claude Code 的按需加载知识与工作流，描述符常驻上下文，完整内容按需加载。它不是模板库，而是给 Claude 一个方法包，告诉 Claude "怎么做"。

## 为什么重要

Skills 是 Claude Code 六层架构中的方法论层，解决"如何执行"的问题。与 [[claude-md]] 对比：CLAUDE.md 是始终常驻的契约，Skills 是按需加载的工作流。Skills 描述符常驻上下文，每个启用的 Skill 都在偷上下文空间，因此描述符应写短点。与 [[context-management]] 密切相关，是上下文分层策略中"按需加载"的部分。

## 工作原理

Skills 采用"渐进式披露"（progressive disclosure）设计：

### 按需加载机制

- `SKILL.md` 负责定义任务语义、边界和执行骨架
- supporting files 负责提供领域细节
- 脚本负责确定性收集上下文或证据

### 目录结构

```
.claude/skills/
└── incident-triage/
    ├── SKILL.md
    ├── runbook.md
    ├── examples.md
    └── scripts/
        └── collect-context.sh
```

### 三种典型类型

**类型一：检查清单型（质量门禁）**
发布前跑一遍，确保不漏项：
```yaml
---
name: release-check
description: Use before cutting a release to verify build, version, and smoke test.
---

## Pre-flight (All must pass)
- [ ] `cargo build --release` passes
- [ ] `cargo clippy -- -D warnings` clean
- [ ] Version bumped in Cargo.toml
- [ ] CHANGELOG updated
- [ ] `kaku doctor` passes on clean env

## Output
Pass / Fail per item. Any Fail must be fixed before release.
```

**类型二：工作流型（标准化操作）**
配置迁移高风险，显式调用 + 内置回滚步骤：
```yaml
---
name: config-migration
description: Migrate config schema. Run only when explicitly requested.
disable-model-invocation: true
---

## Steps
1. Backup: `cp ~/.config/kaku/config.toml ~/.config/kaku/config.toml.bak`
2. Dry run: `kaku config migrate --dry-run`
3. Apply: remove `--dry-run` after confirming output
4. Verify: `kaku doctor` all pass

## Rollback
`cp ~/.config/kaku/config.toml.bak ~/.config/kaku/config.toml`
```

**类型三：领域专家型（封装决策框架）**
运行时出问题时让 Claude 按固定路径收集证据：
```yaml
---
name: runtime-diagnosis
description: Use when kaku crashes, hangs, or behaves unexpectedly at runtime.
---

## Evidence Collection
1. Run `kaku doctor` and capture full output
2. Last 50 lines of `~/.local/share/kaku/logs/`
3. Plugin state: `kaku --list-plugins`

## Decision Matrix
| Symptom | First Check |
|---|---|
| Crash on startup | doctor output → Lua syntax error |
| Rendering glitch | GPU backend / terminal capability |
| Config not applied | Config path + schema version |

## Output Format
Root cause / Blast radius / Fix steps / Verification command
```

## 关键属性 / 权衡

- **描述符成本**：每个启用的 Skill，描述符常驻上下文，约 1-5K tokens
- **描述符优化**：低效描述符 ~45 tokens，高效描述符 ~9 tokens
- **auto-invoke 策略**：
  - 高频（>1 次/会话）→ 保持 auto-invoke，优化描述符
  - 低频（<1 次/会话）→ disable-auto-invoke，手动触发，描述符完全脱离上下文
  - 极低频（<1 次/月）→ 移除 Skill，改为 AGENTS.md 中的文档
- **副作用控制**：有副作用的 Skill 要显式设置 `disable-model-invocation: true`

## 相关概念

- 建立于：[[context-management]] — Skills 是上下文分层策略中"按需加载"的部分
- 与...对比：[[claude-md]] — CLAUDE.md 是始终常驻的契约，Skills 是按需加载的工作流
- 与...配合：[[hooks]] — Skills 告诉 Claude 如何执行，Hooks 强制执行关键路径校验
- 与...配合：[[verifiers]] — Skills 定义验证步骤，Verifiers 执行验证

## 来源依据

- [[summary-你不知道的-claude-code架构治理与工程实践]] — 主要来源
- raw/你不知道的 Claude Code：架构、治理与工程实践.md — 第 5 节"Skills 设计：不是模板库，是用的时候才加载的工作流"

## 待解决问题

- 如何设计 Skill 的描述符，让模型稳定触发？[未验证]
- Skill 与 Plugin 的关系是什么？[未验证]
- 如何评估 Skill 的使用频率和效果？[未验证]