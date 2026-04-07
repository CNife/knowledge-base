---
title: ACI 工具设计
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
  - tools
  - interface-design
---

# ACI 工具设计

## 定义

ACI（Agent-Computer Interface）是给 Agent 设计工具的原则，工具应对应 Agent 的目标而非底层 API 操作。不能只看"工具能不能调用"，还要看"调用错了之后能不能自己修回来"。

## 为什么重要

上下文决定模型能看到什么，工具决定模型能做什么。工具定义的质量比数量更关键。仅 5 个 MCP 服务器就可能带来约 55,000 tokens 的工具定义开销。工具问题多数不在数量不够，而在选不对、描述看不懂、返回一堆没用的、出了错 Agent 也不知道怎么改。

## 工作原理

工具设计三阶段演进：

**第一代：API 封装**
- 每个 API Endpoint 对应一个工具
- 粒度过细，Agent 需要协调多个工具才能完成一个目标

**第二代：ACI**
- 工具对应 Agent 的目标，而不是底层 API 操作
- 不要只给 `update(id, content)`，而是 `update_yuque_post(post_id, title, content_markdown)`
- 一次把目标动作说完整

**第三代：Advanced Tool Use**
1. **Tool Search**：动态工具发现，上下文保留率 95%，Opus 4 准确率从 49% 提升到 74%
2. **Programmatic Tool Calling**：模型用代码编排多个工具调用，中间结果在执行环境中流转，token 消耗从约 150,000 降到约 2,000
3. **Tool Use Examples**：每个工具附带 1-5 个真实调用示例，准确率从 72% 提升到 90%

好工具 vs 差工具：

| 维度     | 好工具                                      | 差工具                                |
|---------|-------------------------------------------|--------------------------------------|
| 粒度     | 对应 Agent 要完成的目标                     | 对应 API 能做的操作                   |
| 示例     | `update_yuque_post`                       | `get_post + update_content + update_title` |
| 返回     | 与下一步决策直接相关的字段                   | 完整原始数据                          |
| 错误     | 结构化，含修正建议                          | 通用字符串 `"Error"`                 |
| 描述     | 说明何时用、何时不用                        | 只写功能说明                          |

ACI 三原则：
1. **参数精确约束**：用 Zod 等工具把定义和实现绑在一起，参数描述直接约束格式
2. **错误结构化**：包含错误码和修正建议
3. **定义实现不分离**：避免定义在 JSON schema、实现散落在各处

## 关键属性 / 权衡

- **工具定义开销**：5 个 MCP Server 约 55,000 tokens（27.5%）
- **Tool Search 效果**：上下文保留率 95%，准确率从 49% 提升到 74%
- **Programmatic Tool Calling**：token 消耗从约 150,000 降到约 2,000
- **Tool Use Examples**：准确率从 72% 提升到 90%

## 相关概念

- 建立于：[[上下文工程]] — 工具定义是上下文的一部分
- 与...协作：[[agent-loop]] — 工具调用是循环的核心环节
- 用于：[[agent-评测]] — 工具调用是评测的重要维度

## 来源依据

- [[summary-你不知道的-agent原理架构与工程实践]] — 主要来源
- raw/你不知道的 Agent：原理、架构与工程实践.md — 第 4 节"工具设计决定 Agent 能做什么"

## 待解决问题

- 工具数量上限（多少工具开始显著影响模型选择准确率）
- 动态工具发现 vs 静态工具列表的权衡
- 工具描述的自然语言 vs 形式化规范 [未验证]