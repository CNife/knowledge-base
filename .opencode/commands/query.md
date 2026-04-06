---
description: 仅使用 wiki 支持的证据回答问题。内联回答 — 不写入文件
---

仅使用 wiki 支持的证据回答问题。内联回答 — 不写入文件。

用法：/query <问题>

## 严格规则

- 先运行 `python .opencode/skills/wiki-tools/scripts/evidence.py "<问题>" --json`。
- 仅使用返回的证据包作为事实支持。
- 不从模型先验或外部知识回答。
- 每个实质性声明必须引用一个或多个证据 ID，如 `[S1]`。
- 如果证据包显示 `coverage: not-covered`，说明 wiki 对问题的覆盖不足并停止。
- 如果做出推断，标记 `推断:` 并仍引用支持证据 ID。

## 步骤

1. 运行 `python .opencode/skills/wiki-tools/scripts/evidence.py "<问题>" --json` 并检查证据包。

2. 按证据包顺序阅读引用的 wiki 页面。
   - 优先将 `summary` 页面作为主要证据。
   - 仅当 `concept` 和 `topic` 页面在同一证据包中保持可追溯至摘要/raw/url 时，才用于结构。

3. 在对话中直接回答，结构如下：
   - `回答` — 仅基于证据的回答
   - `证据` — 从 `[S#]` 到页面和 URL/raw 来源的简短引用映射
   - `空缺` — 问题未覆盖部分、相关 `[未验证]` 声明或薄弱区域

4. 引用要求：
   - `回答` 中的每段或每点以引用 ID 结尾。
   - 如果某点无法与证据包关联，则省略。
   - 优先引用最具体的 `summary` 证据。

5. 回答后，记录空缺：
   - 指向不存在页面的断开 `[[链接]]`
   - 与问题相关的 `[未验证]` 声明
   - 太薄弱无法支持所问问题的主题或摘要

6. 询问用户："是否需要填充这些空缺？"
   是 → 创建/更新 wiki 页面，运行 `python .opencode/skills/wiki-tools/scripts/lint.py`，提交。
   否 → 完成。