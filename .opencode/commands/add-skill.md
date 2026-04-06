---
description: 向技能目录添加新技能
---

向技能目录添加新技能。

用法：/add-skill <技能名称> <描述>

步骤：
1. 查看 SKILL.md 确认技能尚不存在
2. 创建 `.opencode/skills/wiki-tools/scripts/<技能名称>.py` 使用模板
   - 如果任务定义明确，编写完整、可运行的脚本（非存根）
   - 包含带 --help 的 argparse
   - 包含模块级文档字符串：用途、输入、输出、依赖
3. 更新 SKILL.md 中的技能表
4. 确认脚本可运行：python .opencode/skills/wiki-tools/scripts/<技能名称>.py --help