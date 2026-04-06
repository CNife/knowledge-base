---
title: "摘要 — LLM Wiki 知识库构建模式"
type: summary
status: draft
created: 2026-04-06
updated: 2026-04-06
sources:
  - raw/llm-wiki-2026-04-06.md
links:
  - https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
tags:
  - knowledge-management
  - llm
  - workflow
---

## 摘要 — LLM Wiki 知识库构建模式

## 来源元数据

| 字段        | 值                              |
|--------------|----------------------------------|
| 来源类型     | note |
| 作者         | Karpathy                          |
| 年份         | 2024                            |
| 发表于       | GitHub Gist             |
| Raw 文件     | `raw/llm-wiki-2026-04-06.md` |

## 主要观点

LLM 可以增量式构建和维护持久化的 wiki 知识库，替代传统 RAG 的"每次查询重新发现知识"模式，实现知识的编译与累积。

## 关键细节

三层架构：
- **Raw sources** — 不可变的源文档（文章、论文、数据文件）
- **Wiki** — LLM 生成的结构化 markdown 文件（摘要、实体页、概念页）
- **Schema** — 配置文档（CLAUDE.md/AGENTS.md），定义 wiki 结构和操作流程

三种操作：
- **Ingest** — 新源文件进入时，LLM 提取关键信息，整合到现有 wiki
- **Query** — 从 wiki 合成答案，好的答案可回填为新页面
- **Lint** — 定期检查矛盾、过期声明、孤立页面、缺失链接

## 方法 / 进路

与传统 RAG 的区别：
- RAG：每次查询从原始文档检索片段 → 合成答案 → 无积累
- LLM Wiki：编译一次 → 持久化 → 查询时直接使用已编译知识

关键洞见：**维护的负担由 LLM 承担**（更新交叉引用、保持摘要最新、标记矛盾），而非人类。

## 结果 / 证据

适用场景：
- 个人：目标追踪、健康、心理学
- 研究：论文、报告 → 逐步构建综合 wiki
- 阅读：每章存档，构建角色、主题页面
- 团队：Slack、会议记录 → 内部 wiki

## 局限性

- 模式描述偏抽象，具体实现需与 LLM 协作定制
- 大规模 wiki 需要搜索工具（如 qmd）
- LLM 无法一次性读取带图片的 markdown，需分步处理

## 链接到概念

- [[知识库编译]] — LLM Wiki 的核心操作模式
- [[增量式摄入]] — 新源文件的处理流程
- [[Wiki-Lint]] — 知识库健康检查机制

## 链接到主题

- [[LLM-辅助知识管理]] — LLM 在知识工作中的应用模式

## 值得保留的引用

> The wiki is a persistent, compounding artifact. The cross-references are already there. The contradictions have already been flagged.

> Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase.

> The tedious part of maintaining a knowledge base is not the reading or the thinking — it's the bookkeeping.