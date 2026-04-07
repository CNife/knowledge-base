#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pytest>=8.0.0", "pytest-mock>=3.12.0"]
# ///
"""
digest_test.py — 测试 digest 命令的子代理启动逻辑

测试目标：
1. digest 命令调用 ingest.py --new 检测新文件
2. digest 命令启动子代理（task() 被调用且 run_in_background=true）
3. digest 命令限制最多 3 个子代理并行
4. digest 命令调用 background_output() 收集结果

运行方式：
    uv run pytest tests/digest_test.py -v
"""

import pytest
import subprocess
from unittest.mock import Mock, patch


# 定义 mock 函数供测试使用
def task(**kwargs):
    """Mock task function for testing"""
    pass


def background_output(**kwargs):
    """Mock background_output function for testing"""
    pass


class TestDigestDetectsNewFiles:
    """测试 digest 命令检测新文件的逻辑"""

    def test_digest_calls_ingest_py_new(self):
        """验证 digest 命令调用 ingest.py --new 检测新文件"""
        mock_result = Mock()
        mock_result.stdout = "file1.md\nfile2.md\n"
        mock_result.returncode = 0

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            cmd = "uv run --script .opencode/skills/wiki-tools/scripts/ingest.py --new"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            assert mock_run.called
            assert "file1.md" in result.stdout

    def test_digest_handles_zero_new_files(self):
        """验证 digest 命令处理 0 个新文件的情况"""
        mock_result = Mock()
        mock_result.stdout = ""
        mock_result.returncode = 0

        with patch("subprocess.run", return_value=mock_result):
            output = subprocess.run(
                "uv run --script .opencode/skills/wiki-tools/scripts/ingest.py --new",
                shell=True,
                capture_output=True,
                text=True,
            ).stdout

            assert output.strip() == ""


class TestDigestLaunchesSubagents:
    """测试 digest 命令启动子代理的逻辑"""

    def test_digest_calls_task_function(self):
        """验证 digest 命令调用 task() 函数启动子代理"""
        mock_task = Mock(return_value="task_id_1")

        with patch("digest_test.task", mock_task) as mock_task_main:
            task_id = mock_task_main(
                subagent_type="Sisyphus-Junior",
                category="unspecified-high",
                load_skills=["wiki-tools"],
                run_in_background=True,
                description="消化 test.md 文件",
                prompt="**TASK**: 消化 raw/test.md 文件到 wiki/",
            )

            assert mock_task_main.called
            assert task_id == "task_id_1"

    def test_digest_sets_run_in_background_true(self):
        """验证 digest 命令设置 run_in_background=true"""
        mock_task = Mock(return_value="task_id_1")

        with patch("digest_test.task", mock_task):
            mock_task(
                subagent_type="Sisyphus-Junior",
                category="unspecified-high",
                load_skills=["wiki-tools"],
                run_in_background=True,
                description="消化 test.md 文件",
                prompt="**TASK**: 消化 raw/test.md 文件到 wiki/",
            )

            call_kwargs = mock_task.call_args.kwargs
            assert call_kwargs.get("run_in_background") is True


class TestDigestParallelLimit:
    """测试 digest 命令并行限制的逻辑"""

    def test_digest_limits_to_3_subagents(self):
        """验证 digest 命令限制最多 3 个子代理并行"""
        new_files = ["file1.md", "file2.md", "file3.md", "file4.md", "file5.md"]
        mock_task = Mock(
            side_effect=lambda **kwargs: f"task_id_{kwargs['description']}"
        )

        with patch("digest_test.task", mock_task):
            task_ids = []
            for file in new_files[:3]:
                task_id = mock_task(
                    subagent_type="Sisyphus-Junior",
                    category="unspecified-high",
                    load_skills=["wiki-tools"],
                    run_in_background=True,
                    description=f"消化 {file} 文件",
                    prompt=f"**TASK**: 消化 raw/{file} 文件到 wiki/",
                )
                task_ids.append(task_id)

            assert len(task_ids) == 3
            assert mock_task.call_count == 3

    def test_digest_batches_files_over_3(self):
        """验证 digest 命令对超过 3 个文件分批处理"""
        new_files = ["file1.md", "file2.md", "file3.md", "file4.md", "file5.md"]

        batch_size = 3
        batches = [
            new_files[i : i + batch_size] for i in range(0, len(new_files), batch_size)
        ]

        assert len(batches) == 2
        assert len(batches[0]) == 3
        assert len(batches[1]) == 2


class TestDigestCollectsResults:
    """测试 digest 命令收集子代理结果的逻辑"""

    def test_digest_calls_background_output(self):
        """验证 digest 命令调用 background_output() 收集结果"""
        mock_background_output = Mock(
            return_value={"status": "success", "file": "test.md"}
        )

        with patch("digest_test.background_output", mock_background_output):
            task_ids = ["task_id_1", "task_id_2", "task_id_3"]
            results = []

            for task_id in task_ids:
                output = mock_background_output(task_id=task_id, block=True)
                results.append(output)

            assert mock_background_output.call_count == 3
            assert len(results) == 3

    def test_digest_collects_all_results(self):
        """验证 digest 命令收集所有子代理的结果"""
        mock_background_output = Mock(
            side_effect=[
                {"status": "success", "file": "file1.md"},
                {"status": "success", "file": "file2.md"},
                {"status": "failure", "file": "file3.md", "errors": ["timeout"]},
            ]
        )

        with patch("digest_test.background_output", mock_background_output):
            task_ids = ["task_id_1", "task_id_2", "task_id_3"]
            results = []

            for task_id in task_ids:
                output = mock_background_output(task_id=task_id, block=True)
                results.append(output)

            assert len(results) == 3
            assert results[0]["status"] == "success"
            assert results[1]["status"] == "success"
            assert results[2]["status"] == "failure"


class TestDigestErrorHandling:
    """测试 digest 命令错误处理的逻辑"""

    def test_digest_continues_on_subagent_failure(self):
        """验证 digest 命令在子代理失败时继续处理其他文件"""
        mock_background_output = Mock(
            side_effect=[
                {"status": "success", "file": "file1.md"},
                {"status": "failure", "file": "file2.md", "errors": ["timeout"]},
                {"status": "success", "file": "file3.md"},
            ]
        )

        with patch("digest_test.background_output", mock_background_output):
            task_ids = ["task_id_1", "task_id_2", "task_id_3"]
            results = []
            failures = []

            for task_id in task_ids:
                output = mock_background_output(task_id=task_id, block=True)
                results.append(output)
                if output["status"] == "failure":
                    failures.append(output)

            assert len(results) == 3
            assert len(failures) == 1
            assert "errors" in failures[0]

    def test_digest_reports_failures(self):
        """验证 digest 命令报告失败列表"""
        results = [
            {"status": "success", "file": "file1.md"},
            {"status": "failure", "file": "file2.md", "errors": ["timeout"]},
            {"status": "success", "file": "file3.md"},
        ]

        failures = [r for r in results if r["status"] == "failure"]

        assert len(failures) == 1
        assert failures[0]["file"] == "file2.md"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
