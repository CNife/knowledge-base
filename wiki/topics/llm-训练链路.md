---
title: LLM-训练链路
type: topic
status: stable
created: 2026-04-07
updated: 2026-04-07
sources:
  - raw/你不知道的大模型训练：原理、路径与新实践.md
links:
  - https://tw93.fun/2026-04-03/llm.html
tags:
  - llm-training
  - pipeline
---

# LLM-训练链路

## 范围

此主题涵盖大模型从原始数据到部署的完整训练流水线，包括九个阶段和两条反馈回路。属于 AI 基础设施领域，跨数据工程、分布式系统、强化学习、Agent 等子领域。

明确排除：纯推理优化（KV cache、量化等）、模型架构设计细节（attention 变体等）。

## 子问题

1. 预训练如何决定模型能力底座？
2. 数据配方如何影响能力分布？
3. 系统约束如何限制训练规模？
4. 后训练如何激活预训练能力？
5. 评测与奖励如何定义训练目标？
6. Agent 训练如何扩展优化对象？
7. 蒸馏如何迁移能力到更小模型？
8. 发布版本如何选择？

## 关键进路

### 预训练 + 规模定律

预训练是训练链路起点，通过下一个 token 预测将知识压缩进参数。规模定律（Chinchilla）提供预算分配工具，但实践中过训练配方（Llama3 8B 用 15T tokens）换取更高能力密度。详见 [[预训练]]。

### 数据工程 + 能力设计

数据工程是完整漏斗处理流程，不只是清洗数据，更是能力设计。数据配比决定模型能力分布，去重和污染控制影响结果质量。合成数据已从辅助手段变成正式训练流程。详见 [[数据工程]]。

### 系统配方 + 分布式约束

系统配方是分布式系统约束层，GPU 数量、显存、并行策略、容错等在训练开始前就决定规模上限。MoE、muP、WSD learning rate 等技术细节拉开同规模模型差距。详见 [[系统配方]]。

### 后训练 + 多阶段流水线

后训练是预训练之后的多阶段流程，包括 SFT、RLHF、DPO、RFT 等。DeepSeek-R1 四阶段流水线（冷启动 SFT → 推理 RL → 拒绝采样微调 → 对齐 RL）是清晰案例。GRPO 不需要独立价值网络，工程更简洁。详见 [[后训练]]。

### 评测与奖励 + 反馈回路

评测与奖励形成 eval → grader → reward → policy update → rollout 的反馈回路。ORM 只给最终答案打分，PRM 给中间步骤打分。Verified rewards 在可验证任务里替代人工偏好。Constitutional AI 和 Deliberative Alignment 把对齐变成训练目标内部的一部分。详见 [[评测与奖励]]。

### Agent 训练 + Harness 优化

Agent 训练优化对象从答案 → 轨迹 → harness program。Harness 是包在模型外层的控制程序，稳定性 > 模型训练。PARL 只训练 orchestrator，Meta-Harness 优化 harness code 本身。详见 [[agent-训练]]。

### 蒸馏部署 + 持续迭代

蒸馏将大模型推理能力迁移给更小 dense 模型，能力解耦是关键原因。发布版本是产品决策，不是训练曲线最右点。生产流量持续回流到训练，反馈回路缩短。详见 [[蒸馏部署]]。

## 系统 / 论文概览

| 名称 | 年份 | 关键贡献 | 链接 |
|------|------|----------|------|
| Chinchilla | 2022 | 规模定律、训练最优配比 | arXiv:2203.15556 |
| InstructGPT | 2022 | 1.3B 对齐模型赢过 175B | arXiv:2203.02155 |
| DeepSeekMath (GRPO) | 2024 | 组相对策略优化 | arXiv:2402.03300 |
| DeepSeek-V3 | 2024 | FP8 混合精度、无 rollback | arXiv:2412.19437 |
| Llama 3 | 2024 | 过训练配方、15T tokens | arXiv:2407.21783 |
| Constitutional AI | 2022 | AI feedback 替代人工偏好 | arXiv:2212.08073 |
| DeepSeek-R1 | 2025 | 四阶段后训练流水线 | arXiv:2501.12948 |
| Meta-Harness | 2026 | Harness code 优化 | yoonholee.com/meta-harness |
| Kimi K2.5 | 2026 | PARL 并行 Agent RL | kimi.com/blog/kimi-k2-5 |
| Cursor Composer 2 | 2026 | Real-time RL | cursor.com/blog/composer-2-technical-report |

## 重要参考

- Hoffmann et al. (2022) — "Training Compute-Optimal Large Language Models" — [[summary-你不知道的大模型训练原理路径与新实践]] — 规模定律基础
- Ouyang et al. (2022) — "Training language models to follow instructions with human feedback" — arXiv:2203.02155 — 后训练价值证明
- Shao et al. (2024) — "DeepSeekMath: Pushing the Limits of Mathematical Reasoning" — arXiv:2402.03300 — GRPO 算法
- DeepSeek-AI (2025) — "DeepSeek-R1: Incentivizing Reasoning Capability" — arXiv:2501.12948 — 四阶段流水线
- Tw93 (2026) — "你不知道的大模型训练：原理、路径与新实践" — [[summary-你不知道的大模型训练原理路径与新实践]] — 九阶段流水线综述

## 待解决问题

- 多模态预训练的规模定律适用性 [未验证]
- PRM 自动化的边界（哪些任务可程序验证中间步骤）[未验证]
- Harness 优化的自动化边界 [未验证]
- 蒸馏轨迹的最优规模和配比 [未验证]

## 相关主题

- [[OAuth-授权机制]] — 无直接关联
- [[LLM-辅助知识管理]] — 无直接关联