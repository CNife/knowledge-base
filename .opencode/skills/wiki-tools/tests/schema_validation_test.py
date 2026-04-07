#!/usr/bin/env python3
"""
schema_validation_test.py — 测试 JSON schema 验证

测试 digest-output-schema.json 的有效性，以及子代理输出是否符合 schema。

输入: .opencode/commands/digest-output-schema.json
输出: pytest 测试结果
依赖: pytest, jsonschema
"""

import json
import pytest
from pathlib import Path
from jsonschema import validate, ValidationError, Draft7Validator


# Schema 文件路径
SCHEMA_PATH = (
    Path(__file__).parent.parent.parent.parent
    / "commands"
    / "digest-output-schema.json"
)


@pytest.fixture
def schema():
    """加载 JSON schema 文件"""
    with open(SCHEMA_PATH) as f:
        return json.load(f)


class TestSchemaValidity:
    """测试 schema 文件本身的有效性"""

    def test_schema_valid_json(self, schema):
        """验证 schema 文件符合 JSON Schema Draft-07 规范"""
        # 检查 schema 是否是有效的 JSON Schema Draft-07

        # 验证 schema 本身是否符合 Draft-07 meta-schema
        meta_schema = Draft7Validator.META_SCHEMA
        meta_validator = Draft7Validator(meta_schema)

        # schema 应该符合 meta-schema
        errors = list(meta_validator.iter_errors(schema))
        assert len(errors) == 0, f"Schema 不符合 Draft-07 规范: {errors}"

    def test_schema_required_fields(self, schema):
        """验证 schema 包含所有必需字段"""
        # 检查 schema 的必需字段
        assert "$schema" in schema, "Schema 缺少 $schema 字段"
        assert schema["$schema"] == "http://json-schema.org/draft-07/schema#", (
            f"$schema 值应为 Draft-07: {schema['$schema']}"
        )

        assert "title" in schema, "Schema 缺少 title 字段"
        assert "description" in schema, "Schema 缺少 description 字段"
        assert "type" in schema, "Schema 缺少 type 字段"
        assert schema["type"] == "object", f"type 应为 object: {schema['type']}"

        assert "required" in schema, "Schema 缺少 required 字段"
        required_fields = schema["required"]
        expected_required = ["file", "summary_path", "concepts", "topics", "status"]
        assert set(required_fields) == set(expected_required), (
            f"必需字段不匹配: {required_fields} vs {expected_required}"
        )

        assert "properties" in schema, "Schema 缺少 properties 字段"
        assert "additionalProperties" in schema, "Schema 缺少 additionalProperties 字段"
        assert schema["additionalProperties"] == False, (
            f"additionalProperties 应为 false: {schema['additionalProperties']}"
        )

    def test_schema_status_enum(self, schema):
        """验证 status 字段的 enum 限制"""
        status_property = schema["properties"]["status"]
        assert "enum" in status_property, "status 字段缺少 enum 限制"
        assert set(status_property["enum"]) == {"success", "failure"}, (
            f"status enum 值应为 success/failure: {status_property['enum']}"
        )


class TestOutputValidation:
    """测试子代理输出是否符合 schema"""

    def test_output_matches_schema_success(self, schema):
        """验证成功的子代理输出符合 schema"""
        # 成功案例（来自设计文档）
        valid_output = {
            "file": "oauth-authorization-code-2026-04-06.md",
            "summary_path": "summaries/summary-oauth-authorization-code.md",
            "concepts": [
                {
                    "name": "授权码授权",
                    "path": "concepts/授权码授权.md",
                    "created": True,
                },
                {
                    "name": "OAuth-2.0",
                    "path": "concepts/OAuth-2.0.md",
                    "created": False,
                },
            ],
            "topics": [
                {
                    "name": "OAuth-授权机制",
                    "path": "topics/OAuth-授权机制.md",
                    "created": True,
                }
            ],
            "status": "success",
            "errors": [],
        }

        # 验证应该通过
        validate(valid_output, schema)

    def test_output_matches_schema_failure(self, schema):
        """验证失败的子代理输出符合 schema"""
        # 失败案例（来自设计文档）
        failure_output = {
            "file": "invalid-file-2026-04-06.md",
            "summary_path": "",
            "concepts": [],
            "topics": [],
            "status": "failure",
            "errors": [
                "Failed to read raw file: File not found",
                "Cannot proceed without raw content",
            ],
        }

        # 验证应该通过
        validate(failure_output, schema)

    def test_output_missing_required_field(self, schema):
        """验证缺少必需字段的输出会失败"""
        # 缺少必需字段
        invalid_output = {
            "file": "test.md",
            "status": "success",
            # 缺少 summary_path, concepts, topics
        }

        # 验证应该失败
        with pytest.raises(ValidationError) as exc_info:
            validate(invalid_output, schema)

        # 检查错误信息
        assert (
            "required" in str(exc_info.value).lower()
            or "missing" in str(exc_info.value).lower()
        )

    def test_output_invalid_status_value(self, schema):
        """验证无效的 status 值会失败"""
        # status 值不在 enum 中
        invalid_output = {
            "file": "test.md",
            "summary_path": "summaries/summary-test.md",
            "concepts": [],
            "topics": [],
            "status": "pending",  # 无效值
        }

        # 验证应该失败
        with pytest.raises(ValidationError) as exc_info:
            validate(invalid_output, schema)

        # 检查错误信息
        assert "enum" in str(exc_info.value).lower()

    def test_output_additional_properties(self, schema):
        """验证额外字段会失败（additionalProperties: false）"""
        # 包含额外字段
        invalid_output = {
            "file": "test.md",
            "summary_path": "summaries/summary-test.md",
            "concepts": [],
            "topics": [],
            "status": "success",
            "extra_field": "should not be allowed",  # 额外字段
        }

        # 验证应该失败
        with pytest.raises(ValidationError) as exc_info:
            validate(invalid_output, schema)

        # 检查错误信息
        assert (
            "additional" in str(exc_info.value).lower()
            or "extra" in str(exc_info.value).lower()
        )

    def test_output_concept_missing_required(self, schema):
        """验证概念对象缺少必需字段会失败"""
        # 概念对象缺少必需字段
        invalid_output = {
            "file": "test.md",
            "summary_path": "summaries/summary-test.md",
            "concepts": [
                {
                    "name": "Test Concept"
                    # 缺少 path 字段
                }
            ],
            "topics": [],
            "status": "success",
        }

        # 验证应该失败
        with pytest.raises(ValidationError) as exc_info:
            validate(invalid_output, schema)

        # 检查错误信息
        assert (
            "required" in str(exc_info.value).lower()
            or "missing" in str(exc_info.value).lower()
        )

    def test_output_minimal_valid(self, schema):
        """验证最小有效输出（不含可选字段）"""
        # 最小有效输出（不含 errors 字段）
        minimal_output = {
            "file": "test.md",
            "summary_path": "summaries/summary-test.md",
            "concepts": [],
            "topics": [],
            "status": "success",
        }

        # 验证应该通过
        validate(minimal_output, schema)


class TestSchemaExamples:
    """测试 schema 中的 examples 是否有效"""

    def test_schema_examples_valid(self, schema):
        """验证 schema 中的 examples 字段值有效"""
        # 检查 file 字段的 examples
        file_examples = schema["properties"]["file"].get("examples", [])
        assert len(file_examples) > 0, "file 字段缺少 examples"

        # 检查 summary_path 字段的 examples
        summary_examples = schema["properties"]["summary_path"].get("examples", [])
        assert len(summary_examples) > 0, "summary_path 字段缺少 examples"

        # 检查 status 字段的 examples
        status_examples = schema["properties"]["status"].get("examples", [])
        assert len(status_examples) > 0, "status 字段缺少 examples"
        assert status_examples[0] in schema["properties"]["status"]["enum"], (
            f"status example 不在 enum 中: {status_examples[0]}"
        )
