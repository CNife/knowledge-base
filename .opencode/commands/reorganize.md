---
description: 检测并修复 Obsidian 图谱健康问题：断链、孤立、可能重复
---

检测并修复 Obsidian 图谱健康问题：断链、孤立、可能重复。

用法：/reorganize

## 步骤

1. 运行：`python .opencode/skills/wiki-tools/scripts/reorganize.py`
   - 显示所有断开的 `[[链接]]` 及模糊匹配的修复候选
   - 显示孤立页面（未被任何地方链接）
   - 显示可能的重复页面（名称高度相似）

2. 与用户一起审查报告。

3. 对**明确的断链**（单一明确候选）：
   运行：`python .opencode/skills/wiki-tools/scripts/reorganize.py --fix`
   这将自动应用单候选修复。

4. 对**模糊的断链**（多个候选或无匹配）：
   询问用户哪个目标是正确的。
   然后手动编辑页面修复链接。
   或：如果目标页面根本不存在，询问是否应创建存根：
   `python .opencode/skills/wiki-tools/scripts/stub.py concept "<名称>"`

5. 对**孤立页面**：
   阅读孤立页面，确定哪些现有页面应该链接到它，
   在那里添加 `[[链接]]`。始终也更新 `wiki/index.md`。

6. 对**可能重复**：
   阅读两个页面。询问用户：合并为一个，还是添加交叉链接？
   如果合并：保留更丰富的页面，另一个用 `status: deprecated`
   和"已被 [[页面名称]] 取代"行。

7. 运行：`python .opencode/skills/wiki-tools/scripts/lint.py` 确认无问题。

8. 提交：
   ```bash
   git add wiki/
   git commit -m "reorganize: 修复断链和图谱空缺"
   git push
   ```