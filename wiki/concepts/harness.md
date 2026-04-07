---
title: Harness
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
  - testing
  - verification
---

# Harness

## 定义

Harness 是围绕 Agent 构建的测试、验证与约束基础设施，包括验收基线、执行边界、反馈信号和回退手段四个部分。它决定 Agent 能否稳定完成任务，而非模型本身的能力上限。

## 为什么重要

Harness 比模型更关键。任务清晰度和验证自动化程度决定 Agent 的适用区域：右上角（目标明确、结果可自动验证）最适合 Agent 发挥；左下角（两者都缺）Agent 基本起不到作用。更贵的模型带来的提升很多时候没有想象中那么大，反而 Harness 和验证测试质量对成功率的影响更大。

## 工作原理

Harness 四要素：
1. **验收基线**：明确什么算完成（测试 pass、lint clean、特定输出格式）
2. **执行边界**：权限限制、沙箱隔离、受保护文件列表
3. **反馈信号**：命令退出码、lint 结果、单元测试、截图对比
4. **回退手段**：git revert、checkpoint、rollback 脚本

任务清晰度 × 验证自动化矩阵：

| 任务清晰度 | 验证自动化 | Agent 适用性 |
|-----------|-----------|------------|
| 明确      | 高        | 最适合（右上角） |
| 明确      | 低        | 吞吐量天花板是人的审查速度（左上角） |
| 模糊      | 高        | 高效地往错误方向跑（右下角） |
| 模糊      | 低        | Agent 基本无效（左下角） |

## 关键属性 / 权衡

- **验收基线清晰度**：如果两个领域专家拿同一案例独立判断结论不一致，验收标准就还没写清楚
- **环境隔离**：每次运行从干净状态开始，测试之间不共享缓存、临时文件或数据库状态
- **正例 + 反例覆盖**：只测"应该做 X"会让评分器往一个方向优化，必须加入"不应该做 X"的情况
- **回退成本**：git revert 成本低，checkpoint 成本中等，数据库 rollback 成本高
- **验证层级**：命令退出码 → lint/typecheck → unit test → integration test → production logs

## 相关概念

- 约束于：[[agent-loop]] — Harness 不进循环，在外部控制
- 用于：[[agent-评测]] — Harness 是评测基础设施的一部分
- 与...协作：[[上下文工程]] — 验证结果可写入上下文（如 test pass/fail）
- 实现：[[trace-追踪]] — Trace 是 Harness 验证的数据来源

## 来源依据

- [[summary-你不知道的-agent原理架构与工程实践]] — 主要来源
- raw/你不知道的 Agent：原理、架构与工程实践.md — 第 2 节"为什么 Harness 比模型更关键"

## 待解决问题

- 如何量化 Harness 对成功率的影响（控制变量实验）
- 不同任务类型的最小 Harness 集合（简单任务 vs 复杂任务）
- Harness 本身的 bug 如何发现（评分器漂移、环境噪声）