---
title: Reverse Sync
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

# Reverse Sync

## 定义

发现 Bug 或执行偏差时，先修文档（Spec），再修代码。核心原则：Spec 和代码冲突时，错的一定是代码，但修正顺序是先修 Spec 再修代码。

## 为什么重要

Reverse Sync 是最容易被忽略但最重要的环节。保持文档和代码的一致性，才能让整个 Spec Coding 框架持续有效。

如果没有 Reverse Sync：
- Spec 和代码逐渐脱节
- Spec 失去参考价值
- 后续需求无法基于 Spec 进行
- 知识飞轮断裂

## 工作原理

### 触发条件

- 执行中发现 Spec 与实际代码不符
- Review 发现实现偏差
- 用户发现 Spec 遗漏或理解偏差
- Bug 修复需要调整设计

### 执行流程

```mermaid
graph LR
    A[发现偏差] --> B[确认事实]
    B --> C[更新 Spec]
    C --> D[更新 Tasks]
    D --> E[更新 Log]
    E --> F[修正代码]
    F --> G[验证修正]
```

### 文档同步铁律

每次 /fix 必须同步更新：
- spec.md — 设计文档
- tasks.md — 任务拆分
- log.md — 执行日志

## 关键属性 / 权衡

- **一致性保障**：Spec 和代码始终保持一致
- **可追溯性**：每次修正都有文档记录
- **知识沉淀**：偏差原因记录在 log.md，可沉淀到 knowledge/
- **成本**：修正前需要先更新文档，增加前期投入
- **收益**：长期维护成本降低，Spec 持续有效

## 相关概念

- 建立于：[[Spec-Coding]] — Reverse Sync 是 Spec Coding 的核心机制
- 用于：[[AI-编码实践]] — AI 编码方法论的核心实践
- 关联：[[知识飞轮]] — Reverse Sync 是知识飞轮的输入

## 来源依据

- [[summary-2026-ai-bian-ma-jian-jin-shi-spec-shi-zhan-zhi-nan]] — 主要来源，逸驹（2026）
- raw/2026 年 AI 编码的"渐进式 Spec"实战指南.md — 第 2.1 节、第 4.4 节

## 待解决问题

- 自动化程度：能否让 AI 自动识别需要 Reverse Sync 的场景？[未验证]
- 判断标准：什么样的偏差值得 Reverse Sync？[未验证]