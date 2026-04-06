---
title: LLM 辅助知识管理
type: topic
status: draft
created: 2026-04-07
updated: 2026-04-07
sources:
  - raw/llm-wiki-2026-04-06.md
links:
  - https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
tags:
  - knowledge-management
  - llm
  - workflow
  - ai-agent
---

# LLM 辅助知识管理

## 范围

LLM 辅助知识管理涵盖使用大语言模型构建、维护增量式持久化知识库的模式与实践。属于 AI Agent 与知识工作自动化领域。

本主题解释 LLM Wiki 模式如何通过"编译"原始材料为结构化知识，替代传统 RAG 的"每次查询重新发现"模式，实现知识的累积与复用。不涉及具体向量数据库或嵌入模型的实现细节。

## 子问题

1. 三层架构设计：Raw sources → Wiki → Schema
2. 增量式摄入流程：新源文件的提取与整合
3. 查询与答案回填：从 wiki 合成答案并扩展知识库
4. 知识库健康检查：矛盾检测、过期声明、孤立页面
5. 适用场景：个人知识管理、研究文献整理、团队文档沉淀

## 关键进路

### 进路 1：知识库编译模式

核心思想是将原始材料（论文、文章、数据）"编译"为结构化的 Markdown wiki 页面，而非每次查询时从原始文档检索。编译一次，持久化使用。LLM 承担维护负担：更新交叉引用、保持摘要最新、标记矛盾。类比：Obsidian 是 IDE，LLM 是程序员，wiki 是代码库。

### 进路 2：增量式摄入（Ingest）

新源文件进入 raw/ 目录时，LLM 自动提取关键信息，创建或更新对应的摘要页面（wiki/summaries/），并整合到现有概念和主题页面。无需人工干预分类和标签，由 LLM 根据内容自动建立链接。

### 进路 3：有据查询（Query with Evidence）

查询时从 wiki/ 而非 raw/ 检索，确保答案基于已编译的结构化知识。使用证据包工具（evidence.py）构建引用链，每个声明可追溯至来源。优质答案可回填为新概念页面，形成知识增长飞轮。

### 进路 4：定期 Lint 检查

运行 lint 脚本定期检查知识库健康：断链、孤立页面、缺失 frontmatter、矛盾声明、过期信息。自动修复或标记待人工审核的问题。保持图谱整洁，避免知识腐化。

## 系统 / 论文概览

| 名称 | 年份 | 关键贡献 | 链接 |
|------|------|----------|------|
| Karpathy LLM Wiki | 2024 | 提出 LLM Wiki 模式，对比传统 RAG | [[summary-llm-wiki-2026-04-06.md]] |
| Obsidian + LLM 工作流 | 2024-2026 | 社区实践：用 Obsidian 作为知识库载体 | [未验证] |
| AGENTS.md 规范 | 2026 | 定义 AI 助手与知识库交互的契约 | 本仓库 AGENTS.md |

## 重要参考

- Karpathy（2024）— "LLM Wiki: A pattern for incremental, persistent knowledge bases" — [[summary-llm-wiki-2026-04-06.md]] — 提出三层架构与三种操作模式
- 知识库工具集技能 — wiki-tools — 实现 digest、ingest、lint、evidence 等自动化脚本
- AGENTS.md — 本仓库的 AI 助手协作规范，定义摄入状态与 wiki 修改边界

## 待解决问题

- 大规模 wiki（>1000 页面）的搜索与导航性能优化 [未验证]
- 多模态内容（图片、表格、公式）的自动提取与链接 [未验证]
- 团队协作场景下的冲突解决与版本控制策略 [未验证]
- LLM 幻觉导致错误知识进入 wiki 的检测与回滚机制 [未验证]

## 相关主题

[[OAuth-授权机制]]
