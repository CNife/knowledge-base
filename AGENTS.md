# AGENTS.md — 知识库

本文件由所有 AI 编码助手（Claude Code、OpenAI Codex、Gemini CLI 等）读取。

---

## 使命

将原始 AI 研究材料转化为结构化、持续演进的 Markdown 知识库。
领域：**高性能计算（HPC）**、**AI 基础设施**、**AI Agent**。

```
raw/  →  /digest  →  wiki/  →  /query (内联)
                       ↑              ↓ 用户确认
                    /distill      /analyze → output/
```

---

## 目录语义

```
raw/          源材料。仅追加。永不编辑现有文件。Git 跟踪。
  assets/     图片资源。Git LFS 存储。
wiki/         编译后的知识页面。按规则演进。Git 跟踪。
  concepts/   原子知识单元
  topics/     更广泛的主题概述
  summaries/  每源摘要 — 摄入状态存于此
  log.md      摄入流程日志 — 自动追加（无需用户确认）
output/       临时暂存。Git 忽略。永不提交。
.opencode/    OpenCode 配置
  commands/   斜杠命令
  skills/     Agent 技能
schemas/      Markdown 模板。稳定契约。
```

---

## 技能 — 实现前先查看

所有 Python 脚本均为 **uv 单脚本模式**，使用 `uv run --script <script>` 运行。

```bash
ls .opencode/skills/wiki-tools/scripts/
uv run --script .opencode/skills/wiki-tools/scripts/<name>.py --help
```

| 技能 | 用途 |
|------|------|
| `digest.py` | 完整摄入流程：重命名新 raw 文件 + 创建摘要存根 |
| `download_images.py` | 下载 raw/*.md 中图片到 raw/assets/，更新链接为本地路径 |
| `evidence.py` | 从 wiki/ + raw/ 来源构建有依据的证据包 |
| `backfill_provenance.py` | 修复 wiki 中过时的 raw 引用和缺失的摘要链接 |
| `ingest.py` | 查找尚未被 wiki/summaries/ 引用的 raw/ 文件 |
| `rename.py` | 根据 frontmatter 标题对 raw/ 文件名进行 slug 化 — 更新 wiki 引用 |
| `search.py` | 跨 wiki/ 关键词搜索 — 仅输出到 stdout |
| `lint.py` | 结构检查：断链、孤立页面、缺失 frontmatter |
| `stub.py` | 从 schema 模板创建空白 wiki 页面 |
| `reorganize.py` | 检测 + 修复 Obsidian 图谱问题（断链、孤立、重复） |

添加技能：创建 `.opencode/skills/wiki-tools/scripts/<name>.py`（uv 单脚本模式），更新 SKILL.md。

---

## Output 与 Wiki — 严格边界

| 用户意图 | 目标 |
|----------|------|
| 用户要求生成 / 研究 / 报告 X | `output/` |
| 新 raw 来源被摄入 | `wiki/` 仅通过 `/digest` |
| 填充 lint 检测到的空缺 | `wiki/` 仅通过 `/distill` |
| 查询回答 | 仅对话 |

**`wiki/` 仅通过结构化流程修改（`/digest`、`/distill`、`/reorganize`）。**
**永不因用户请求生成内容而写入 `wiki/`。**

## 有据生成策略

- 查询、分析和任何生成的文本必须仅基于 `wiki/` 内容。
- 回答或分析前运行 `uv run --script .opencode/skills/wiki-tools/scripts/evidence.py "<问题>" --json`。
- 每个实质性声明必须引用一个或多个证据 ID，如 `[S1]`。
- 如果 wiki 对问题的覆盖不足，明确说明并停止，而非用模型先验填充。
- `wiki/summaries/` 是主要证据层。`wiki/concepts/` 和 `wiki/topics/` 是综合层，应保持可追溯至摘要/raw/url 来源。

---

## 摄入状态

当任何 `wiki/summaries/` 页面在其 `sources:` 中列出某 raw 文件时，该文件即为**已编译**。
无侧车文件。无注册表。状态隐式存在于 wiki 中。

---

## Digest 流程

`/digest` 命令检测 `raw/` 中的新文件，编译成 wiki 页面，检查，提交，推送。

**流程**：
1. 检测新文件：`uv run --script .opencode/skills/wiki-tools/scripts/ingest.py --new`
2. 启动并行子代理（最多 3 个并行）处理每个新文件
3. 等待子代理完成并返回 JSON 报告
4. 整合结果：更新 `wiki/index.md` + 追加 `wiki/log.md`
5. 运行 lint 检查：`uv run --script .opencode/skills/wiki-tools/scripts/lint.py --strict`
6. 提交并推送

**效率**：约 5 倍提升（对比串行处理）

**log.md 自动追加**：每次 digest 操作完成后自动追加记录到 `wiki/log.md`，无需用户确认。

---

## 允许

- `raw/`：仅追加文件；**`/digest` 期间允许重命名**（基于 frontmatter 标题自动 slug 化）
- `wiki/`：按 schemas 创建/更新页面 — **任何分析后需用户确认**
- `output/`：自由写入，永不提交
- 添加新技能；未经检查依赖项时永不删除
- 添加新页面时始终更新 `wiki/index.md`

## 禁止

- 删除 wiki 页面 — 使用 `status: deprecated`
- 编造事实 — 使用 `[未验证]`
- 在 `raw/` 添加侧车/元数据文件
- 因用户请求报告、分析或生成内容而写入 `wiki/`
- 提交 `output/`

---

## Wiki 页面规则

1. 每个页面符合 `schemas/` 中对应的 schema
2. 必需 frontmatter：`title`、`type`、`status`、`sources`、`links`
3. 内部链接：`[[页面名称]]` 语法
4. 无孤立 — 每个新页面至少被一个其他页面或 `wiki/index.md` 链接
5. `status`：`draft` | `stable` | `deprecated`

---

## 来源追溯

- `sources:` 列出编译本页的 raw 文件或 URL
- `links:` 列出原始 Web URL（Obsidian Clipper）
- 不确定声明：`[未验证]` — 必须在 `status: stable` 前解决

---

## Git 约定

```bash
# digest 后
git add wiki/ raw/
git commit -m "digest: <标题>"
git push

# 填充 wiki 空缺后
git add wiki/
git commit -m "distill: <填充内容>"
git push

# 添加技能后
git add .opencode/
git commit -m "skill: 添加 <名称>"
git push
```

每次推送前运行 `uv run --script .opencode/skills/wiki-tools/scripts/lint.py`。有 lint 错误不推送。
不要将 wiki 变更与技能变更打包在同一提交。

---

## 图片处理流程

raw/ 文件中的远程图片链接需要下载到本地：

```bash
# 1. 预览将要下载的图片
uv run --script .opencode/skills/wiki-tools/scripts/download_images.py

# 2. 执行下载（图片存入 raw/assets/，链接更新为本地路径）
uv run --script .opencode/skills/wiki-tools/scripts/download_images.py --apply

# 3. 提交图片（Git LFS 自动处理）
git add raw/assets/ raw/*.md .gitattributes
git commit -m "下载图片并更新链接"
git push
```

图片文件名格式：`{md文件名}-{index}.{扩展名}`，如 `github-oauth-1.jpg`。
图片由 Git LFS 自动追踪（见 `.gitattributes` 配置）。