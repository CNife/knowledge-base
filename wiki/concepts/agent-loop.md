---
title: Agent Loop
type: concept
status: draft
created: 2026-04-07
updated: 2026-04-07
sources:
  - raw/你不知道的 Agent：原理、架构与工程实践.md
links:
  - https://tw93.fun/2026-03-21/agent.html
tags:
  - agent
  - control-flow
---

# Agent Loop

## 定义

Agent Loop 是 AI Agent 的核心运转机制，通过"感知 → 决策 → 行动 → 反馈"四个阶段的持续循环，直到模型返回纯文本为止。模型负责推理，外部系统负责状态和边界，分工确定后核心循环逻辑稳定不变。

## 为什么重要

Agent Loop 是所有 Agent 实现的基础结构。大多数 Agent 失效不是模型不够强，而是循环体变成了巨大的状态机，或者上下文被污染。稳定的循环设计让新能力通过工具集扩展、系统提示调整或状态外化接入，而不需要修改循环本身。

## 工作原理

```typescript
const messages: MessageParam[] = [{ role: "user", content: userInput }];

while (true) {
  const response = await client.messages.create({
    model: "claude-opus-4-6",
    max_tokens: 8096,
    tools: toolDefinitions,
    messages,
  });

  if (response.stop_reason === "tool_use") {
    const toolResults = await Promise.all(
      response.content
        .filter((b) => b.type === "tool_use")
        .map(async (b) => ({
          type: "tool_result" as const,
          tool_use_id: b.id,
          content: await executeTool(b.name, b.input),
        }))
    );
    messages.push({ role: "assistant", content: response.content });
    messages.push({ role: "user", content: toolResults });
  } else {
    return response.content.find((b) => b.type === "text")?.text ?? "";
  }
}
```

四阶段循环：
1. **感知**：收集上下文（CLAUDE.md、Skills、Memory、用户输入）
2. **决策**：LLM 推理，决定下一步行动或返回文本
3. **行动**：调用工具（执行命令、读取文件、访问 API）
4. **反馈**：工具结果返回，追加到 messages，继续循环

## 关键属性 / 权衡

- **循环稳定性**：从最小实现到支持子 Agent、上下文压缩、Skills 加载，主循环基本不变
- **能力接入方式**：三种方式 — 扩展工具集、调整系统提示结构、状态外化到文件或数据库
- **状态管理**：模型只负责推理，不持有状态；状态在 messages[]（短期）和文件/数据库（长期）
- **终止条件**：`stop_reason === "tool_use"` 继续循环，否则返回文本结束
- **并发控制**：同一 session 内消息串行，不同 session 可并发

## 相关概念

- 建立于：[[上下文工程]] — 控制模型能看到什么
- 与...协作：[[aci-工具设计]] — 控制模型能做什么
- 用于：[[agent-评测]] — 评测需要完整 Trace
- 约束于：[[harness]] — 验证与回退机制

## 来源依据

- [[summary-你不知道的-agent原理架构与工程实践]] — 主要来源
- raw/你不知道的 Agent：原理、架构与工程实践.md — 第 1 节"Agent Loop 的基本运转方式"

## 待解决问题

- 循环深度限制（防止无限递归）
- 长会话的上下文压缩策略（何时触发、保留什么）
- 多 Agent 协作时子 Agent 循环如何与主 Agent 循环协调 [未验证]