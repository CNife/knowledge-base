---
description: 将新来源文件摄入知识流程
---

将新来源文件摄入知识流程。

用法：/ingest <文件路径>  或  /ingest（查看所有 raw/ 文件状态）

步骤：
1. 如无参数：运行 `python .opencode/skills/wiki-tools/scripts/ingest.py` 并显示状态表
2. 如给定文件路径：
   a. 如文件不在 raw/ 中，复制或移动到那里（询问用户选择）
   b. 运行 `python .opencode/skills/wiki-tools/scripts/ingest.py --new` 检查是否为新
   c. 询问用户："是否现在填写摘要？"
   d. 如是：阅读 raw 文件并使用 `schemas/摘要.md` 写入完整的 wiki/summaries/ 页面