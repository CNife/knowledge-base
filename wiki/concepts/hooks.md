---
title: Hooks
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
  - control-surface
---

# Hooks

## 定义

Hooks 是 Claude Code 的强制执行规则拦截层，在生命周期事件前后执行确定性脚本，不依赖 Claude 自己判断。它将不能交给 Claude 临场发挥的事情，重新收回到确定性的流程里。

## 为什么重要

Hooks 是 Claude Code 六层架构中的控制层，解决自动化失控问题。它提供强制约束和审计能力，在 Claude 执行操作前后插入自定义逻辑。与 [[claude-md]] 和 [[skills]] 配合使用：CLAUDE.md 声明约束，Skills 告诉 Claude 如何执行，Hooks 强制执行关键路径校验。在 100 次编辑的会话中，每次节省 30-60 秒，累积节省 1-2 小时。

## 工作原理

Hooks 在生命周期事件前后触发，执行确定性脚本：

### 当前支持的 Hook 点

- `PostToolUse`：工具使用后触发
- `Notification`：任务完成后触发
- `SessionStart`：会话开始时触发

### 配置示例

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit",
        "pattern": "*.rs",
        "hooks": [
          {
            "type": "command",
            "command": "cargo check 2>&1 | head -30",
            "statusMessage": "Running cargo check..."
          }
        ]
      },
      {
        "matcher": "Edit",
        "pattern": "*.lua",
        "hooks": [
          {
            "type": "command",
            "command": "luajit -b $FILE /dev/null 2>&1 | head -10",
            "statusMessage": "Checking Lua syntax..."
          }
        ]
      }
    ],
    "Notification": [
      {
        "type": "command",
        "command": "osascript -e 'display notification \"Task completed\" with title \"Claude Code\"'"
      }
    ]
  }
}
```

### 适合 vs 不适合放到 Hooks

**适合**：
- 阻断修改受保护文件
- Edit 后自动格式化/lint/轻量校验
- SessionStart 后注入动态上下文（Git 分支、环境变量）
- 任务完成后推送通知

**不适合**：
- 需要读大量上下文的复杂语义判断
- 长时间运行的业务流程
- 需要多步推理和权衡的决策（这些该在 [[skills]] 或 [[subagents]] 里）

## 关键属性 / 权衡

- **执行时机**：生命周期事件前后，不进上下文
- **输出限制**：必须限制输出长度（`| head -30`），避免 Hook 输出反而污染上下文
- **确定性**：执行确定性脚本，不依赖模型判断
- **与 RTK 的关系**：RTK（Rust Token Killer）通过 Hook 透明重写命令输出，过滤噪声
- **成本节省**：在 100 次编辑的会话中，每次节省 30-60 秒，累积节省 1-2 小时

## 相关概念

- 建立于：[[claude-md]] — CLAUDE.md 声明约束，Hooks 强制执行
- 与...配合：[[skills]] — Skills 告诉 Claude 如何执行，Hooks 强制执行关键路径校验
- 与...对比：[[subagents]] — Subagents 用于隔离上下文的工作单元，Hooks 用于强制执行规则
- 用于：[[context-management]] — Hooks 不进上下文，避免污染

## 来源依据

- [[summary-你不知道的-claude-code架构治理与工程实践]] — 主要来源
- raw/你不知道的 Claude Code：架构、治理与工程实践.md — 第 6 节"Hooks：在 Claude 执行操作前后，强制插入你自己的逻辑"

## 待解决问题

- Hooks 与 [[prompt-caching]] 的关系？Hook 执行是否影响缓存？[未验证]
- 如何设计 Hook 的错误处理和回滚机制？[未验证]