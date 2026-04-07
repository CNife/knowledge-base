---
description: 检测 raw/ 中的新文件，编译成 wiki 页面，检查，提交，推送
---

检测 raw/ 中的新文件，编译成 wiki 页面，检查，提交，推送。

用法：/digest

## 步骤

### 1. 检测新文件

运行：`uv run --script .opencode/skills/wiki-tools/scripts/ingest.py --new`

如果输出显示 0 个新文件 → 告诉用户"没有新文件需要消化。"并停止。

### 2. 启动并行子代理（最多 3 个）

如果新文件数量 N > 1，为每个文件启动子代理并行处理（上限 3 个并行）：

```typescript
// 为每个新文件启动子代理
const taskIds = [];
for (const file of newFiles.slice(0, 3)) {
  const taskId = task(
    subagent_type: "Sisyphus-Junior",
    category: "unspecified-high",
    load_skills: ["wiki-tools"],
    run_in_background: true,
    description: `消化 ${file} 文件`,
    prompt: `**TASK**: 消化 raw/${file} 文件到 wiki/

**EXPECTED OUTCOME**:
- 创建 wiki/summaries/${file} 摘要页面
- 创建或更新相关概念页面到 wiki/concepts/
- 更新相关主题页面到 wiki/topics/

**REQUIRED TOOLS**:
- read: 读取 raw 文件和现有 wiki 页面
- write: 创建新页面
- edit: 更新现有页面

**MUST DO**:
1. 读取 raw/${file} 文件内容
2. 使用 stub.py 创建摘要存根：uv run --script .opencode/skills/wiki-tools/scripts/stub.py summary "${file}"
3. 填充摘要页面所有内容（无占位符）
4. 识别新概念，使用 stub.py 创建概念页面
5. 更新相关主题页面
6. 确保所有页面符合 schemas/ 模板

**MUST NOT DO**:
- 不修改 raw/ 文件
- 不删除现有 wiki 页面
- 不提交更改（由主 Agent 统一提交）

**CONTEXT**:
- Wiki 根目录：/mnt/c/Obsidian/知识库
- Schema 目录：/mnt/c/Obsidian/知识库/schemas/
- 索引文件：/mnt/c/Obsidian/知识库/wiki/index.md

**IMPORTANT**: 完成后汇报创建了哪些页面及其路径。`
  );
  taskIds.push(taskId);
}
```

如果 N > 3，分批次处理（先处理 3 个，完成后处理下一批）。

### 3. 等待子代理完成

使用 `background_output()` 等待所有子代理完成：

```typescript
// 等待所有子代理完成
const results = [];
for (const taskId of taskIds) {
  const output = background_output(taskId: taskId, block: true);
  results.push(output);
}
```

### 4. 整合结果

#### 4a. 更新索引

将所有新页面添加到 `wiki/index.md`：
- 从子代理输出中提取新创建的页面路径
- 按类别（summaries/concepts/topics）添加到索引

#### 4b. 追加 log.md

在 `wiki/log.md` 中追加本次消化记录：

```markdown
## [YYYY-MM-DD HH:MM] ingest | <来源标题>

**Status**: ✅ Success / ❌ Partial / ❌ Failed

**Files Processed**:
- raw/<filename1> → wiki/summaries/<summary1>
- raw/<filename2> → wiki/summaries/<summary2>

**New Concepts**:
- [[Concept1]]
- [[Concept2]]

**Updated Topics**:
- [[Topic1]]
```

使用追加模式写入：`echo "内容" >> wiki/log.md`

### 5. 汇总失败列表

扫描子代理结果，如果有失败：

```markdown
## 本次会话结果

✅ 成功摄入：X 个文件
❌ 失败：Y 个文件

### 失败列表

| 文件名 | 错误类型 | 建议操作 |
|--------|----------|----------|
| raw/file1.md | <错误描述> | <建议操作> |

详细信息请查看 `wiki/log.md` 中的 FAILED 条目。
```

对于每个失败文件，在 `wiki/log.md` 中追加：

```markdown
## [YYYY-MM-DD HH:MM] FAILED | <filename>

**Error**: <错误类型或简短描述>

**Details**:
<详细错误信息>

**Next Steps**:
- 建议的修复操作
```

### 6. 检查

运行：`uv run --script .opencode/skills/wiki-tools/scripts/lint.py --strict`

继续前修复所有问题。

### 7. 提交并推送

```bash
git add wiki/ raw/
git commit -m "digest: <逗号分隔的来源标题>"
git push
```
