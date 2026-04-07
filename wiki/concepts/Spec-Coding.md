---
title: Spec Coding
type: concept
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

# Spec Coding

## 定义

在让 AI 写代码之前，先用结构化文档（Spec）把"要做什么、怎么做、有什么约束"说清楚，然后 AI 围绕这份文档编码。Spec 是人和 AI 之间的沟通协议，而非自动化流水线的输入。

## 为什么重要

直接和 AI 聊天写代码（Vibe Coding）面临四个工程问题：
1. **上下文丢失**：对话轮次增加后，早期决策被压缩掉，AI 可能"忘记"之前的约定
2. **无法追溯**：改了什么、为什么改、改了多少轮——没有记录，无法复盘
3. **偏差累积**：每轮对话都可能引入理解偏差，累积后代码和原始需求南辕北辙
4. **协作困难**：多人协作时，每个人对"要做什么"的理解不一致

Spec Coding 通过结构化文档解决这些问题，同时遵循经济原则：Code is Cheap, Context is Expensive——把需求、约束、代码现状写进 Spec 作为高质量输入，AI 不用反复试错，对话轮次从 20 轮降到 3-5 轮，总成本反而更低。

## 工作原理

### 三条铁律

1. **No Spec, No Code** — 没有文档，不准写代码
2. **Spec is Truth** — 文档和代码冲突时，错的一定是代码
3. **Reverse Sync** — 发现 Bug，先修文档，再修代码

### Spec 内容结构

```markdown
# 需求名称
## 1. 背景与目标
## 2. 代码现状（Research Findings）
## 3. 功能点
## 4. 业务规则
## 5. 数据变更
## 6. 接口变更
## 7. 影响范围
## 8. 风险与关注点
## 9. 待澄清
## 10. 技术决策
## 11. 执行日志
## 12. 审查结论
## 13. 确认记录（HARD-GATE）
```

### 工作流

Propose → Apply → Review → Archive

- **Propose**：人主导，AI 辅助。Research 代码现状，逐个提问，分段生成文档，HARD-GATE 确认
- **Apply**：AI 主导，人审查。逐 task 执行，零偏差原则，Verification 铁律
- **Review**：两阶段 Sub Agent 审查。Spec Compliance + Code Quality
- **Archive**：知识沉淀。逐条展示 log.md 知识发现，确认后沉淀到 knowledge/

## 关键属性 / 权衡

- **适用场景**：中等及以上复杂度的需求（≥5 人日）
- **不适用场景**：简单需求（改个字段、修个 bug）——使用 [[渐进式编码]] 框架
- **成本**：前期投入（写 Spec）增加，但总成本（对话轮次）降低
- **收益**：可追溯、可复盘、协作一致、偏差可控
- **风险**：Spec 本身需要维护，Spec 和代码的一致性需要持续关注

## 相关概念

- 建立于：[[Agent-Loop]] — Spec Coding 是 Agent 工作流的约束层
- 与...对比：Vibe Coding — 直接和 AI 聊天写代码，无结构化文档
- 用于：[[AI-编码实践]] — AI 编码方法论的核心实践
- 关联：[[Reverse-Sync]] — 保持 Spec 和代码一致性的机制
- 关联：[[渐进式编码]] — Spec Coding 的渐进式落地方式

## 来源依据

- [[summary-2026-ai-bian-ma-jian-jin-shi-spec-shi-zhan-zhi-nan]] — 主要来源，逸驹（2026）
- raw/2026 年 AI 编码的"渐进式 Spec"实战指南.md — 第 2.1 节

## 待解决问题

- Spec 的粒度标准：什么样的需求值得写 Spec？[未验证]
- Spec 的维护成本：如何降低 Spec 的维护负担？[未验证]
- Spec 的自动化生成：能否让 AI 自动生成 Spec？[未验证]