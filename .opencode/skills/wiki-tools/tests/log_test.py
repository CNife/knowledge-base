#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pytest>=8.0.0"]
# ///
"""
log_test.py — 测试 log.md 格式和追加逻辑

测试目标：
1. log.md 格式可被 Unix 工具解析（grep "^## \\["）
2. 原子追加不覆盖已有内容
3. 每条记录包含必要字段

运行方式：
    uv run pytest tests/log_test.py -v
"""

import tempfile
import subprocess
from pathlib import Path


MOCK_LOG_CONTENT = """---
title: 摄入日志
type: log
status: stable
tags:
  - log
  - audit
  - workflow
created: 2026-04-07
updated: 2026-04-07
---

# Wiki Log

摄入操作的完整时间顺序记录。

每条记录格式：`## [YYYY-MM-DD HH:MM] ingest | <标题>`

Unix 工具可解析：
```bash
grep "^## \\[" wiki/log.md | tail -5  # 最近 5 条记录
```

---

## [2026-04-07 10:15] ingest | OAuth 2.0 的一个简单解释

**摘要路径**: [[summary-oauth-20-的一个简单解释]]

**新增概念**:
- [[OAuth-2.0]]
- [[令牌]]

**新增主题**:
- [[OAuth-授权机制]]

**状态**: success

## [2026-04-07 14:20] ingest | LLM Wiki 模式

**摘要路径**: [[summary-llm-wiki]]

**新增概念**:
- [[知识库编译]]
- [[增量式摄入]]

**新增主题**:
- [[LLM-辅助知识管理]]

**状态**: success
"""


def test_log_format_parseable():
    """验证 grep "^## \\[" 可匹配记录标题"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(MOCK_LOG_CONTENT)
        f.flush()
        temp_path = Path(f.name)

    result = subprocess.run(
        ["grep", "^## \\[", str(temp_path)],
        capture_output=True,
        text=True,
    )

    temp_path.unlink()

    assert result.returncode == 0, "grep 应该找到匹配的记录"
    lines = result.stdout.strip().split("\n")
    assert len(lines) == 2, f"应该找到 2 条记录，实际找到 {len(lines)} 条"

    for line in lines:
        assert line.startswith("## ["), "每条记录应以 '## [' 开头"
        assert "] ingest |" in line, "每条记录应包含 '] ingest |'"


def test_log_append_atomic():
    """验证追加不覆盖已有内容"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(MOCK_LOG_CONTENT)
        f.flush()
        temp_path = Path(f.name)

    original_content = temp_path.read_text()
    original_lines = len(original_content.split("\n"))

    new_entry = """
## [2026-04-07 16:00] lint | 结构检查

**状态**: success

**备注**: 无断链、无孤立页面
"""

    with open(temp_path, "a") as f:
        f.write(new_entry)

    new_content = temp_path.read_text()
    new_lines = len(new_content.split("\n"))

    temp_path.unlink()

    assert original_content in new_content, "追加不应覆盖已有内容"
    assert new_lines > original_lines, "追加后行数应增加"

    assert "OAuth 2.0 的一个简单解释" in new_content, "原有记录应保留"
    assert "LLM Wiki 模式" in new_content, "原有记录应保留"
    assert "结构检查" in new_content, "新记录应存在"


def test_log_entry_format():
    """验证每条记录包含必要字段"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(MOCK_LOG_CONTENT)
        f.flush()
        temp_path = Path(f.name)

    content = temp_path.read_text()

    temp_path.unlink()

    entries = []
    lines = content.split("\n")
    current_entry = []

    for line in lines:
        if line.startswith("## [") and current_entry:
            entries.append("\n".join(current_entry))
            current_entry = [line]
        elif line.startswith("## ["):
            current_entry = [line]
        elif current_entry:
            current_entry.append(line)

    if current_entry:
        entries.append("\n".join(current_entry))

    for entry in entries:
        if "ingest |" in entry:
            assert "**摘要路径**:" in entry, "ingest 记录应包含摘要路径"

            assert "**状态**:" in entry, "每条记录应包含状态字段"

            status_line = [l for l in entry.split("\n") if "**状态**:" in l][0]
            status_value = status_line.split("**状态**:")[1].strip()
            assert status_value in ["success", "partial", "failed"], (
                f"状态值应为 success/partial/failed，实际为 {status_value}"
            )

            assert "[2026-" in entry, "时间戳应包含年份"
            import re

            timestamp_match = re.search(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\]", entry)
            assert timestamp_match, "时间戳格式应为 [YYYY-MM-DD HH:MM]"


def test_log_grep_operations():
    """验证不同操作类型可被 grep 区分"""
    log_with_multiple_ops = (
        MOCK_LOG_CONTENT
        + """
## [2026-04-07 15:30] lint | 结构检查

**状态**: success

**备注**: 无断链、无孤立页面

## [2026-04-07 16:00] query | Agent 架构

**状态**: success

**命中页面**:
- [[agent-loop]]
"""
    )

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(log_with_multiple_ops)
        f.flush()
        temp_path = Path(f.name)

    ingest_result = subprocess.run(
        ["grep", "^## \\[.*\\] ingest", str(temp_path)],
        capture_output=True,
        text=True,
    )
    lint_result = subprocess.run(
        ["grep", "^## \\[.*\\] lint", str(temp_path)],
        capture_output=True,
        text=True,
    )
    query_result = subprocess.run(
        ["grep", "^## \\[.*\\] query", str(temp_path)],
        capture_output=True,
        text=True,
    )

    temp_path.unlink()

    assert len(ingest_result.stdout.strip().split("\n")) == 2, "应找到 2 条 ingest 记录"
    assert len(lint_result.stdout.strip().split("\n")) == 1, "应找到 1 条 lint 记录"
    assert len(query_result.stdout.strip().split("\n")) == 1, "应找到 1 条 query 记录"


def test_log_count_entries():
    """验证 grep -c 可统计记录数"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(MOCK_LOG_CONTENT)
        f.flush()
        temp_path = Path(f.name)

    result = subprocess.run(
        ["grep", "-c", "^## \\[", str(temp_path)],
        capture_output=True,
        text=True,
    )

    temp_path.unlink()

    assert result.returncode == 0, "grep -c 应成功执行"
    count = int(result.stdout.strip())
    assert count == 2, f"应统计到 2 条记录，实际统计到 {count} 条"


def test_log_tail_recent():
    """验证 tail 可获取最近记录"""
    log_with_many_entries = MOCK_LOG_CONTENT
    for i in range(3, 8):
        log_with_many_entries += f"""
## [2026-04-07 {10 + i}:00] ingest | 测试文件 {i}

**摘要路径**: [[summary-test-{i}]]

**状态**: success
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(log_with_many_entries)
        f.flush()
        temp_path = Path(f.name)

    result = subprocess.run(
        ["grep", "^## \\[", str(temp_path)],
        capture_output=True,
        text=True,
    )
    grep_output = result.stdout.strip().split("\n")

    tail_result = subprocess.run(
        ["tail", "-5"],
        input="\n".join(grep_output),
        capture_output=True,
        text=True,
    )

    temp_path.unlink()

    recent_lines = tail_result.stdout.strip().split("\n")
    assert len(recent_lines) == 5, (
        f"应获取 5 条最近记录，实际获取 {len(recent_lines)} 条"
    )

    for i in range(4, 8):
        assert f"测试文件 {i}" in tail_result.stdout, f"应包含测试文件 {i}"
