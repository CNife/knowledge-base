---
description: 检测 raw/ 中的新文件，编译成 wiki 页面，检查，提交，推送
---

检测 raw/ 中的新文件，编译成 wiki 页面，检查，提交，推送。

用法：/digest

## 步骤

### 1. 检测新文件

运行：`python .opencode/skills/wiki-tools/scripts/ingest.py --new`

如果输出显示 0 个新文件 → 告诉用户"没有新文件需要消化。"并停止。

### 2. 对于每个新文件：

a. **读取文件** `raw/<filename>`。

b. **创建摘要页面** 到 `wiki/summaries/`，使用 `schemas/摘要.md`。
   - 使用 `python .opencode/skills/wiki-tools/scripts/stub.py summary "<filename>"` 创建文件。
   - 填充所有部分。无占位符。
   - 设置 `sources: raw/<filename>` 和 `links:` 为文件中的原始 URL（如有）。
   - 使用 `[[页面名称]]` 链接相关概念和主题。

c. **创建或更新概念页面** 处理引入的新概念。
   - 使用 `python .opencode/skills/wiki-tools/scripts/stub.py concept "<名称>"` 创建新页面。
   - 如果概念已存在于 wiki/，则更新它。
   - 标记不确定声明 `[未验证]`。

d. **更新现有主题页面** 如果此来源对已知领域有补充。

### 3. 更新索引

将所有新页面添加到 `wiki/index.md`。

### 4. 检查

运行：`python .opencode/skills/wiki-tools/scripts/lint.py`
继续前修复所有问题。

### 5. 提交并推送

```bash
git add wiki/ raw/
git commit -m "digest: <逗号分隔的来源标题>"
git push
```