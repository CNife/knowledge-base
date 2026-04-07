---
title: 摄入日志
type: log
status: stable
tags:
  - log
  - audit
  - workflow
sources: []
links: []
created: 2026-04-07
updated: 2026-04-07
---

# Wiki Log

摄入操作的完整时间顺序记录。

每条记录格式：`## [YYYY-MM-DD HH:MM] ingest | <标题>`

Unix 工具可解析：
```bash
grep "^## \[" wiki/log.md | tail -5  # 最近 5 条记录
```

---

## [2026-04-07 13:57] ingest | 2026 年 AI 编码的"渐进式 Spec"实战指南

**摘要路径**: [[summaries/summary-2026-ai-bian-ma-jian-jin-shi-spec-shi-zhan-zhi-nan|summary-2026-ai-bian-ma-jian-jin-shi-spec-shi-zhan-zhi-nan]]

**新增概念**:
- [[concepts/Spec-Coding|Spec-Coding]]
- [[concepts/渐进式编码|渐进式编码]]
- [[concepts/Reverse-Sync|Reverse-Sync]]
- [[concepts/编排层与执行层|编排层与执行层]]
- [[concepts/知识飞轮|知识飞轮]]

**新增主题**:
- [[topics/AI-编码实践|AI-编码实践]]

**状态**: success
