---
title: Agent-训练
type: concept
status: stable
created: 2026-04-07
updated: 2026-04-07
sources:
  - raw/你不知道的大模型训练：原理、路径与新实践.md
links:
  - https://tw93.fun/2026-04-03/llm.html
tags:
  - llm-training
  - agent
  - harness
  - parl
---

# Agent-训练

## 定义

Agent 训练是优化能规划、调用工具、接收反馈、在长任务里保持连贯的系统，训练对象从模型本身扩展到 harness（包在模型外层的控制程序）和环境。优化目标从答案 → 轨迹 → harness program。

## 为什么重要

推理模型（o1、DeepSeek-R1）证明 RL 能显著提升数学、代码、逻辑任务表现，同时打开推理算力扩展的新维度。RL 训练不只教模型答题，还教模型分配推理预算。难点变成让模型在环境里持续行动，而不只是把单次思考拉长。

## 工作原理

Reasoning Model vs Agentic Model：

| 属性 | Reasoning Model | Agentic Model |
|------|-----------------|---------------|
| 优化单元 | 答案 | 轨迹 |
| 主要瓶颈 | Verifier 准确度 | Harness 质量 |
| 典型奖励 | Outcome reward | Outcome + process + context |
| 常见失败 | 走捷径推理 | 工具误用 / context drift / reward hacking |

Harness 组成：
- Prompt construction
- Memory update
- Retrieval policy
- Context editing
- Tool orchestration

PARL（Kimi K2.5）：
- 只训练 orchestrator，冻结 sub-agent
- 奖励信号：r_perf（任务成功）、r_parallel（并行分解）、r_finish（完成约束）
- 训练早期 r_parallel 权重高，后期退到 0

Meta-Harness：
- 优化 harness code 本身，而非权重
- 同一底模只改 harness 可拉出 6x 性能差距
- 在线文本分类比 ACE 高 7.7 点，context token 用量压到 1/4

## 关键属性 / 权衡

- **Harness 稳定性 > 模型训练**：工具返回值不稳定、环境不一致时，grader 先出错
- **环境质量 > 数据多样性**：稳定性、真实性、覆盖度、难度分布、反馈丰富度、抗利用性
- **训练目标变化**：在完整任务里保持可靠，不只是做对一道题
- **Environment bootstrap**：agent loop 开始前先跑 shell command 整理环境快照注入首轮 prompt

## 相关概念

- 建立于：[[后训练]] — Agent 训练是后训练的扩展
- 建立于：[[评测与奖励]] — Agent reward design 更细
- 用于：[[蒸馏部署]] — Agent 能力通过生产流量持续迭代

## 来源依据

- [[summary-你不知道的大模型训练原理路径与新实践]] — 主要来源
- Lee et al. (2026). Meta-Harness: End-to-End Optimization of Model Harnesses. yoonholee.com/meta-harness
- Kimi Team (2026). Kimi K2.5 Tech Blog: Visual Agentic Intelligence. kimi.com/blog/kimi-k2-5

## 待解决问题

- Harness 优化的自动化边界 [未验证]
- 多 sub-agent 的 credit assignment 通用方案 [未验证]