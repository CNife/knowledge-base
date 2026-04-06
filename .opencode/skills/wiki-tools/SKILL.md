---
name: wiki-tools
description: 知识库维护工具集 — 消化、查询、检查、重组等操作
---

## 工具列表

所有脚本均为 uv 单脚本模式，使用 `uv run --script <script>` 或 `uv run python <script>` 运行。

| 工具 | 用途 | 命令 |
|------|------|------|
| `digest.py` | 完整摄入流程：重命名新 raw 文件 + 创建摘要存根 | `uv run --script .opencode/skills/wiki-tools/scripts/digest.py --apply` |
| `download_images.py` | 下载 raw/*.md 中的图片到 raw/assets/ 并更新链接 | `uv run --script .opencode/skills/wiki-tools/scripts/download_images.py --apply` |
| `evidence.py` | 从 wiki/ + raw/ 来源构建有依据的证据包 | `uv run --script .opencode/skills/wiki-tools/scripts/evidence.py "<查询>" --json` |
| `backfill_provenance.py` | 修复 wiki 中过时的 raw 引用和缺失的摘要链接 | `uv run --script .opencode/skills/wiki-tools/scripts/backfill_provenance.py --apply` |
| `ingest.py` | 查找尚未被 wiki/summaries/ 引用的 raw/ 文件 | `uv run --script .opencode/skills/wiki-tools/scripts/ingest.py --new` |
| `rename.py` | 根据 frontmatter 标题对 raw/ 文件名进行 slug 化 | `uv run --script .opencode/skills/wiki-tools/scripts/rename.py --apply` |
| `search.py` | 跨 wiki/ 关键词搜索 — 仅输出到 stdout | `uv run --script .opencode/skills/wiki-tools/scripts/search.py "<关键词>"` |
| `lint.py` | 结构检查：断链、孤立页面、缺失 frontmatter | `uv run --script .opencode/skills/wiki-tools/scripts/lint.py --strict` |
| `stub.py` | 从 schema 模板创建空白 wiki 页面 | `uv run --script .opencode/skills/wiki-tools/scripts/stub.py <类型> <名称>` |
| `reorganize.py` | 检测并修复 Obsidian 图谱问题（断链、孤立、重复） | `uv run --script .opencode/skills/wiki-tools/scripts/reorganize.py --fix` |

## 使用示例

### 消化新来源

```bash
# 预览
uv run --script .opencode/skills/wiki-tools/scripts/digest.py

# 执行
uv run --script .opencode/skills/wiki-tools/scripts/digest.py --apply
```

### 下载图片

```bash
# 预览（显示将要下载的图片）
uv run --script .opencode/skills/wiki-tools/scripts/download_images.py

# 执行下载并更新链接
uv run --script .opencode/skills/wiki-tools/scripts/download_images.py --apply

# 仅处理指定文件
uv run --script .opencode/skills/wiki-tools/scripts/download_images.py --file raw/example.md --apply
```

### 构建证据包

```bash
# 人类可读
uv run --script .opencode/skills/wiki-tools/scripts/evidence.py "flash attention"

# JSON 输出（供命令消费）
uv run --script .opencode/skills/wiki-tools/scripts/evidence.py "kv cache" --json
```

### 创建新页面

```bash
# 摘要页面
uv run --script .opencode/skills/wiki-tools/scripts/stub.py summary "paper-flashattention-2023.md"

# 概念页面
uv run --script .opencode/skills/wiki-tools/scripts/stub.py concept "flash-attention"

# 主题页面
uv run --script .opencode/skills/wiki-tools/scripts/stub.py topic "gpu-memory-optimization"
```

### 检查和修复

```bash
# 结构检查
uv run --script .opencode/skills/wiki-tools/scripts/lint.py

# 图谱重组
uv run --script .opencode/skills/wiki-tools/scripts/reorganize.py --fix
```

## 添加新技能

1. 创建 `.opencode/skills/wiki-tools/scripts/<名称>.py`
2. 包含模块文档字符串（用途 / 输入 / 输出 / 依赖）和 `--help`
3. 更新此 SKILL.md 中的表格

模板（uv 单脚本模式）：
```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []  # 或 ["httpx>=0.27.0"] 等
# ///
"""
<名称>.py — <一行描述>

输入:  ...
输出: stdout 或写入 <位置>
依赖:  <pip 包，如有（内联于 dependencies）>
"""
import argparse

def main():
    parser = argparse.ArgumentParser(description="...")
    args = parser.parse_args()

if __name__ == "__main__":
    main()
```