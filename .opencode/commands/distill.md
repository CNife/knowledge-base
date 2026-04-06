---
description: 扫描 wiki 结构空缺并填充。提交前需用户确认
---

扫描 wiki 结构空缺并填充。提交前需用户确认。

用法：/distill [主题]

## 步骤

1. 运行 `python .opencode/skills/wiki-tools/scripts/lint.py` 暴露问题。

2. 阅读受影响的页面。

3. **在执行前向用户展示**你计划写入或更改的内容。

4. 获得批准后，填充空缺：
   - 断链 → 使用 `python .opencode/skills/wiki-tools/scripts/stub.py <类型> <名称>` 创建页面，然后填充内容
   - `stable` 页面中的 `[未验证]` → 检查 `raw/` 来源，解决或标记"有争议"
   - 孤立页面 → 从适当页面或 `wiki/index.md` 添加链接

5. 再次运行 `python .opencode/skills/wiki-tools/scripts/lint.py` 确认无问题。

6. 提交：
```bash
git add wiki/
git commit -m "distill: <填充内容>"
git push
```