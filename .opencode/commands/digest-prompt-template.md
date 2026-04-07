# 子代理 Prompt 模板 — Digest 摄入流程

用于启动子代理完成 raw 文件的完整摄入流程。

---

## Prompt 模板

```markdown
## 1. TASK

消化 raw 文件 `{filename}`，完成完整摄入流程：
1. 读取 raw 文件内容
2. 填充摘要页面（按 schema）
3. 创建概念页面（如有新概念）
4. 填充概念页面内容
5. 返回结构化 JSON 报告

## 2. EXPECTED OUTCOME

返回 JSON 报告，包含：
- file: 处理的 raw 文件名
- summary_path: 摘要页面路径（如 wiki/summaries/summary-xxx.md）
- concepts[]: 创建或更新的概念页面列表
- topics[]: 创建或更新的主题页面列表
- status: "success" 或 "failure"
- errors[]: 错误信息（失败时）

## 3. REQUIRED TOOLS

- Read: 读取 raw 文件和 schema 文件
- Write: 创建摘要、概念、主题页面
- Edit: 填充页面内容

## 4. MUST DO

1. 读取 raw 文件：`raw/{filename}`
2. 读取摘要 schema：`schemas/摘要.md`
3. 填充摘要页面：
   - 设置 sources: `raw/{filename}`
   - 设置 links: 原始 URL（如有）
   - 填充所有必需部分（主要观点、关键细节、方法、结果、局限性）
   - 链接到相关概念和主题
4. 创建概念页面（如有新概念）：
   - 使用 `schemas/概念.md` 作为模板
   - 设置 sources 和 links
   - 填充定义、为什么重要、工作原理
5. 填充概念页面内容：
   - 添加来源依据
   - 链接到相关概念
6. 返回 JSON 报告（见 EXPECTED OUTCOME）

## 5. MUST NOT DO

1. 不编辑 wiki/index.md（主 Agent 负责）
2. 不运行 lint.py（主 Agent 负责）
3. 不运行 git 命令（主 Agent 负责）
4. 不修改现有 wiki 页面（只创建新页面）
5. 不删除任何文件
6. 不返回非 JSON 格式的输出

## 6. CONTEXT

- Raw 文件路径：`raw/{filename}`
- 摘要存根路径：`wiki/summaries/{summary_stub}`
- 概念 schema: `schemas/概念.md`
- 主题 schema: `schemas/主题.md`
- 摘要 schema: `schemas/摘要.md`
- Wiki 根目录：`wiki/`
- 概念目录：`wiki/concepts/`
- 主题目录：`wiki/topics/`

文章核心内容预览（前 500 字）：
{raw_content_preview}
```

---

## 占位符说明

| 占位符 | 来源 | 说明 |
|--------|------|------|
| `{filename}` | digest.py | raw 文件名（已重命名） |
| `{summary_stub}` | digest.py | 摘要存根文件名 |
| `{raw_content_preview}` | 主 Agent | raw 文件前 500 字预览 |

---

## 使用示例

```bash
# 主 Agent 启动子代理时替换占位符
task(
  subagent_type="Sisyphus-Junior",
  run_in_background=true,
  description="消化 raw 文件",
  prompt=prompt_template.replace("{filename}", filename)
                        .replace("{summary_stub}", summary_stub)
                        .replace("{raw_content_preview}", preview)
)
```

---

## 设计要点

1. **简洁性**: Prompt 约 500-800 字，避免占用过多 context
2. **结构化**: 六个部分清晰分离（TASK、EXPECTED OUTCOME、REQUIRED TOOLS、MUST DO、MUST NOT DO、CONTEXT）
3. **职责分离**: 子代理负责摄入，主 Agent 负责整合
4. **占位符设计**: 运行时替换，避免硬编码
