---
title: Agent 评测
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
  - evaluation
  - testing
---

# Agent 评测

## 定义

Agent 评测是验证 Agent 行为正确性的系统化方法，比 Single-turn 评测复杂不止一个层级。结构包括 task、trial、grader、transcript、outcome、evaluation harness、agent harness 和 evaluation suite。

## 为什么重要

很多团队把评测往后放，结果改了 Prompt 不知道是否变好，换了模型不知道是否退化。评测系统本身的问题比 Agent 出问题更难发现。如果两个领域专家拿同一案例独立判断结论不一致，验收标准就还没写清楚。

## 工作原理

Agent 评测结构：
- **task**：任务定义
- **trial**：单次运行
- **grader**：评分器
- **transcript**：完整执行记录
- **outcome**：环境最终结果

Single-turn vs Agent 评测对比：
- Single-turn：Prompt → LLM → Response → 打分
- Agent：Tools + Environment + Task → Agent 多步调用工具并更新环境状态 → 验证环境实际结果

两类评分器：

| 类型       | 典型做法                              | 确定性 | 适用场景               |
|-----------|--------------------------------------|-------|----------------------|
| 代码评分器 | 字符串匹配、单元测试 pass/fail、结构比对  | 最高   | 有明确正确答案的任务     |
| 模型评分器 | 按评分标准打分、两个答案对比选优、多模型投票 | 中     | 语义质量、风格、推理过程 |
| 人工评分器 | 专家抽样审查、标注队列校准              | 可靠但慢 | 建立基准、校准自动 judge |

评测指标：
- **Pass@k**：k 次至少一次正确，适合探索能力上限
- **Pass^k**：k 次全部正确，适合上线回归

## 关键属性 / 权衡

- **调查数据**：Offline evaluation 54.5%，Online evaluation 44.8%，Not evaluating yet 22.8%
- **常用指标**：Internal human review 59.8%，LLM-as-judge 53.3%，Traditional ML/DS metrics 16.9%
- **环境隔离**：每次运行从干净状态开始，测试之间不共享缓存

## 相关概念

- 建立于：[[harness]] — 评测是 Harness 的核心部分
- 用于：[[agent-loop]] — 评测验证循环结果
- 数据来源：[[trace-追踪]] — Transcript 是评测数据

## 来源依据

- [[summary-你不知道的-agent原理架构与工程实践]] — 主要来源
- raw/你不知道的 Agent：原理、架构与工程实践.md — 第 8 节"Agent 评测如何做"

## 待解决问题

- 评分器漂移校准（LLM judge 如何保持稳定）
- 环境噪声 vs 模型退化区分
- Agent 评测的自动化程度上限 [未验证]