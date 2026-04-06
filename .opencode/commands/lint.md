---
description: 运行 wiki 检查器并修复问题
---

运行 wiki 检查器并修复问题。

用法：/lint

## 步骤

1. 运行 `python .opencode/skills/wiki-tools/scripts/lint.py`

2. 对发现的每类问题：
   - **断链** → 提议使用 `python .opencode/skills/wiki-tools/scripts/stub.py` 创建存根页面
   - **孤立页面** → 提议添加到 `wiki/index.md`
   - **缺失 frontmatter** → 添加必需字段
   - **stable 页面中的 [未验证]** → 尝试从 `raw/` 来源解决

3. 重新运行 `python .opencode/skills/wiki-tools/scripts/lint.py` 确认无问题。