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
