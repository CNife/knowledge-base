# Digest 工作流优化 — 符合 LLM Wiki 理念

## TL;DR

> **核心目标**: 优化 `/digest` 命令，使其立即启动子代理并行处理文件，提升效率约 5 倍，符合 LLM Wiki "LLM 负责所有 bookkeeping"的理念。
> 
> **交付物**: 
> - 更新的 `/digest` 命令定义（.opencode/commands/digest.md）
> - 新建的 `wiki/log.md` 文件（摄入时间顺序记录）
> - 子代理 prompt 模板和输出 schema 定义
> - 错误处理和文件锁定策略
> 
> **预估工作量**: Medium（涉及命令流程重构 + 新组件添加）
> **并行执行**: YES - 4 waves（分析 → 实现 → 测试 → 集成）
> **关键路径**: 分析现有流程 → 更新 digest.md → 创建 log.md → 定义子代理契约 → TDD 测试 → 集成验证

---

## Context

### 原始请求

用户要求分析 session `ses_29a7` 的工作流优化点，遵循 LLM Wiki 理念。

### 讨论总结

**关键发现**:
- **效率对比**：第一阶段（直接处理）30 分钟处理 1 个文件；第二阶段（子代理并行）6 分钟处理 2 个文件，效率提升约 5 倍
- **根本问题**：`/digest` 命令没有明确使用子代理的指令；缺少 `log.md` 文件；主 Agent 在第一阶段角色混淆
- **LLM Wiki 不符合点**：缺少时间顺序摄入记录；流程没有体现"LLM 负责所有 bookkeeping"的理念

**用户确认**:
- `log.md` 位置：`wiki/log.md`（作为 wiki 的一部分）
- `log.md` 格式：详细格式（包含摘要路径、概念列表、主题列表）
- `log.md` 追加：自动追加（无需用户确认，符合 LLM Wiki 理念）
- 并行限制：最多 3 个子代理并行
- 失败处理：记录失败并继续（不自动重试）
- lint 运行：手动运行（digest 后独立步骤）

### Metis 审查

**识别的 Gaps（已解决）**:
- 子代理 prompt schema 未定义 → 定义明确模板和输出 JSON schema
- 文件锁定策略缺失 → 使用原子追加机制（每次 digest 追加一个 block）
- 错误处理未定义 → 定义失败文件记录策略（记录到 log.md 并继续）
- 并发限制未验证 → 设置上限 3 个子代理（用户确认）
- log.md 追加策略 → 自动追加（用户确认）
- lint 自动运行 → 手动运行（用户确认）

**Guardrails（已锁定）**:
- 不修改现有 wiki/ 页面（只追加 log.md 和创建新摘要）
- 不改变 raw/ 文件（只读）
- 不添加新依赖（仅使用现有 wiki-tools）
- 保持向后兼容（digest 命令签名不变）
- 符合 LLM Wiki 理念：LLM 负责所有 bookkeeping

---

## Work Objectives

### 核心目标

优化 `/digest` 工作流，使其：
1. 立即启动子代理并行处理每个文件（最多 3 个并行）
2. 子代理完成后返回结构化 JSON 报告
3. 主 Agent 整合结果并自动追加到 `wiki/log.md`
4. 失败文件记录到 log.md 并继续处理其他文件
5. 符合 LLM Wiki 的"LLM 负责所有 bookkeeping"理念

### 具体交付物

- `.opencode/commands/digest.md`（更新：并行子代理流程）
- `wiki/log.md`（新建：摄入时间顺序记录）
- `.opencode/commands/digest-prompt-template.md`（新建：子代理 prompt 模板）
- `.opencode/commands/digest-output-schema.json`（新建：子代理输出 schema）
- 测试验证：2 个文件在 <10 分钟完成（vs 当前 6 分钟）

### 完成定义

- [ ] `/digest` 命令触发子代理并行处理（最多 3 个）
- [ ] 每个子代理完成完整摄入流程并返回 JSON 报告
- [ ] `wiki/log.md` 创建并自动追加摄入记录
- [ ] 失败文件记录到 log.md 并继续其他文件
- [ ] 效率验证：2 个文件 <10 分钟完成

### Must Have

- 立即启动子代理（不等待）
- 子代理返回结构化 JSON 报告
- log.md 自动追加（无需用户确认）
- 失败文件记录并继续
- 并行上限 3 个

### Must NOT Have（Guardrails）

- 不修改现有 wiki/ 页面（只追加 log.md）
- 不改变 raw/ 文件（只读）
- 不添加新依赖
- 不自动重试失败文件
- 不自动运行 lint（手动）
- 不超过 3 个并行子代理

---

## Verification Strategy（MANDATORY）

> **零人工干预** - 所有验证由 agent 执行。无例外。

### 测试决策

- **基础设施存在**: YES（wiki-tools scripts）
- **自动化测试**: YES（TDD）
- **框架**: uv 单脚本模式（现有基础设施）
- **TDD 流程**: RED（定义 schema + 测试用例）→ GREEN（实现功能）→ REFACTOR（优化）

### QA 策略

每个任务必须包含 agent-executed QA scenarios（见 TODO 模板）。
证据保存到 `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`。

- **命令流程验证**: Bash - 运行 digest 命令，验证子代理启动
- **JSON 输出验证**: Bash - 解析子代理输出，验证 schema 合规
- **log.md 验证**: Read - 检查 log.md 格式和内容
- **效率验证**: Bash - 测量处理时间，对比 baseline

---

## Execution Strategy

### 并行执行波次

> 最大化吞吐量，通过将独立任务分组到并行波次。
> 每波次在下一波次开始前完成。
> 目标：每波次 3-6 个任务。少于 3 个（除最后一波）= 未充分拆分。

```
Wave 1（立即开始 - 分析 + 设计）:
├── Task 1: 分析现有 digest 流程和 wiki-tools scripts [deep]
├── Task 2: 设计子代理 prompt 模板和输出 schema [deep]
├── Task 3: 设计 log.md 格式和追加策略 [quick]
└── Task 4: 设计错误处理和失败记录策略 [quick]

Wave 2（Wave 1 后 - 实现）:
├── Task 5: 更新 .opencode/commands/digest.md（并行子代理流程） [quick]
├── Task 6: 创建 wiki/log.md（初始结构） [quick]
├── Task 7: 创建 digest-prompt-template.md（子代理指令） [quick]
├── Task 8: 创建 digest-output-schema.json（输出规范） [quick]
└── Task 9: 更新 wiki-tools SKILL.md（记录新流程） [quick]

Wave 3（Wave 2 后 - TDD 测试）:
├── Task 10: 创建 digest_test.py（测试子代理启动） [deep]
├── Task 11: 创建 log_test.py（测试 log.md 格式） [deep]
├── Task 12: 创建 schema_validation_test.py（测试 JSON 输出） [deep]
└── Task 13: 运行所有测试 → PASS [quick]

Wave 4（Wave 3 后 - 集成验证）:
├── Task 14: 集成测试：完整 digest 流程（2 个文件） [deep]
├── Task 15: 效率验证：时间对比 baseline [quick]
├── Task 16: LLM Wiki 合规性检查 [deep]
└── Task 17: 文档更新：README 和 AGENTS.md [quick]

Wave FINAL（所有任务后 - 4 个并行审查，然后用户确认）:
├── Task F1: 计划合规性审计（oracle）
├── Task F2: 代码质量审查（unspecified-high）
├── Task F3: 实际 QA 测试（unspecified-high）
└── Task F4: 范围一致性检查（deep）
-> 呈现结果 -> 获取用户明确确认

关键路径: Task 1 → Task 2 → Task 5 → Task 10 → Task 14 → Task F1-F4 → 用户确认
并行加速: 约 60% 快于串行
最大并发: 4（Wave 1 & 2）
```

### 依赖矩阵（简化）

- **1-4**: - - 5-9, 1
- **5-9**: 1-4 - 10-13, 2
- **10-13**: 5-9 - 14-17, 3
- **14-17**: 10-13 - F1-F4, 4
- **F1-F4**: 14-17 - 用户确认, FINAL

> 这是简化版。生成的计划必须包含所有任务的完整矩阵。

### Agent 分配总结

- **1**: **4** - T1-T2 → `deep`, T3-T4 → `quick`
- **2**: **5** - T5-T9 → `quick`
- **3**: **4** - T10-T12 → `deep`, T13 → `quick`
- **4**: **4** - T14, T16 → `deep`, T15, T17 → `quick`
- **FINAL**: **4** - F1 → `oracle`, F2 → `unspecified-high`, F3 → `unspecified-high`, F4 → `deep`

---

## TODOs

> 实现 + 测试 = 一个任务。永不分离。
> 每个任务必须包含：推荐 Agent Profile + 并行信息 + QA Scenarios。
> **没有 QA Scenarios 的任务是不完整的。无例外。**

- [x] 1. 分析现有 digest 流程和 wiki-tools scripts

  **What to do**:
  - 读取 `.opencode/commands/digest.md` 现有定义
  - 读取 `.opencode/skills/wiki-tools/scripts/digest.py` 和相关脚本
  - 分析 session `ses_29a7` 的实际执行流程（已读取 session-ses_29a7.md）
  - 识别瓶颈：第一阶段（直接处理）vs 第二阶段（子代理并行）
  - 总结现有流程的缺陷：串行处理、缺少子代理指令、缺少 log.md

  **Must NOT do**:
  - 不修改任何文件（只分析）
  - 不运行实际 digest 命令（只读取定义）

  **Recommended Agent Profile**:
  - **Category**: `deep` - 需要深入分析现有代码和 session 历史
  - **Skills**: `wiki-tools` - 需要理解 wiki-tools scripts 的设计
  - **Skills Evaluated but Omitted**: `git-master` - 不需要 git 操作（只分析）

  **Parallelization**:
  - **Can Run In Parallel**: YES（与 Task 2 并行）
  - **Parallel Group**: Wave 1（with Task 2）
  - **Blocks**: Task 5（依赖分析结果）
  - **Blocked By**: None（可立即开始）

  **References**:
  - `.opencode/commands/digest.md:1-49` - 现有 digest 命令定义
  - `.opencode/skills/wiki-tools/scripts/digest.py` - 完整摄入流程脚本
  - `session-ses_29a7.md:2403-4340` - 第一阶段和第二阶段的执行对比

  **WHY Each Reference Matters**:
  - digest.md: 了解当前命令定义，识别缺少子代理指令的问题
  - digest.py: 了解现有脚本实现，判断是否需要修改
  - session-ses_29a7.md: 了解实际执行的时间消耗对比（30 分钟 vs 6 分钟）

  **Acceptance Criteria**:
  - [ ] 分析报告写入 `.sisyphus/drafts/digest-flow-analysis.md`
  - [ ] 报告包含：现有流程缺陷、时间对比、瓶颈识别
  - [ ] 报告包含：建议的优化方向（子代理并行）

  **QA Scenarios**:

  ```
  Scenario: 分析现有 digest 命令定义
    Tool: Read
    Preconditions: 文件存在
    Steps:
      1. Read .opencode/commands/digest.md
      2. Assert: 文件包含"检测新文件"步骤
      3. Assert: 文件不包含"task(subagent_type"（缺少子代理指令）
    Expected Result: 分析报告记录现有流程缺陷
    Failure Indicators: 报告缺少缺陷识别
    Evidence: .sisyphus/evidence/task-1-digest-analysis.md

  Scenario: 分析 session 执行时间对比
    Tool: Read
    Preconditions: session 文件存在
    Steps:
      1. Read session-ses_29a7.md（lines 2403-4340）
      2. Assert: 第一阶段时间约 30 分钟（lines 2403-4173）
      3. Assert: 第二阶段时间约 6 分钟（lines 4179-4340）
      4. Assert: 效率提升约 5 倍
    Expected Result: 分析报告记录时间对比和效率差异
    Failure Indicators: 报告缺少时间数据
    Evidence: .sisyphus/evidence/task-1-time-comparison.md
  ```

  **Evidence to Capture**:
  - [ ] digest-analysis.md: 现有流程缺陷分析
  - [ ] time-comparison.md: 时间对比数据

  **Commit**: NO（分析阶段不提交）

- [x] 2. 设计子代理 prompt 模板和输出 schema

  **What to do**:
  - 基于 LLM Wiki 理念，设计子代理完整摄入流程的 prompt 模板
  - 设计子代理输出的 JSON schema（结构化报告）
  - Prompt 模板必须包含：read raw → write summary → create concepts → fill concepts → return JSON
  - JSON schema 必须包含：file、summary_path、concepts[]、topics[]、status、errors
  - 参考 session ses_29a7 中子代理实际使用的 prompt（lines 4203-4245）

  **Must NOT do**:
  - 不创建具体文件（只设计）
  - 不定义过长的 prompt（避免占用过多 context）

  **Recommended Agent Profile**:
  - **Category**: `deep` - 需要深入理解 LLM Wiki 理念和子代理设计
  - **Skills**: `wiki-tools` - 需要理解摄入流程的细节
  - **Skills Evaluated but Omitted**: `optimize-agents-md` - 不需要优化 AGENTS.md（只设计子代理 prompt）

  **Parallelization**:
  - **Can Run In Parallel**: YES（与 Task 1 并行）
  - **Parallel Group**: Wave 1（with Task 1）
  - **Blocks**: Task 7（依赖 prompt 模板）和 Task 8（依赖 schema）
  - **Blocked By**: None（可立即开始）

  **References**:
  - `raw/llm-wiki-2026-04-06.md:46-60` - LLM Wiki 的 Operations 部分（Ingest 流程）
  - `session-ses_29a7.md:4203-4245` - 实际子代理 prompt 示例（bg_4c7d0d84 和 bg_f81850b7）

  **WHY Each Reference Matters**:
  - llm-wiki-2026-04-06.md: 了解 LLM Wiki 的摄入流程定义，确保设计符合理念
  - session-ses_29a7.md: 参考实际子代理 prompt 的结构和内容

  **Acceptance Criteria**:
  - [ ] Prompt 模板设计写入 `.sisyphus/drafts/digest-prompt-design.md`
  - [ ] JSON schema 设计写入 `.sisyphus/drafts/digest-schema-design.md`
  - [ ] Prompt 模板包含：TASK、EXPECTED OUTCOME、REQUIRED TOOLS、MUST DO、MUST NOT DO、CONTEXT
  - [ ] JSON schema 包含：file、summary_path、concepts[]、topics[]、status、errors 字段

  **QA Scenarios**:

  ```
  Scenario: 验证 prompt 模板符合 LLM Wiki 理念
    Tool: Read
    Preconditions: prompt 设计文档存在
    Steps:
      1. Read .sisyphus/drafts/digest-prompt-design.md
      2. Assert: 模板包含"read raw → write summary → create concepts"
      3. Assert: 模板包含"MUST DO"和"MUST NOT DO"约束
      4. Assert: 模板包含"CONTEXT"部分（提供 raw 文件路径、schemas 路径）
    Expected Result: prompt 模板符合 LLM Wiki 的摄入流程定义
    Failure Indicators: 模板缺少关键部分
    Evidence: .sisyphus/evidence/task-2-prompt-validation.md

  Scenario: 验证 JSON schema 结构完整
    Tool: Read
    Preconditions: schema 设计文档存在
    Steps:
      1. Read .sisyphus/drafts/digest-schema-design.md
      2. Assert: schema 包含 file、summary_path、concepts[]、topics[] 字段
      3. Assert: schema 包含 status 字段（success/failure）
      4. Assert: schema 包含 errors 字段（失败时记录错误）
    Expected Result: JSON schema 足以供主 Agent 整合结果
    Failure Indicators: schema 缺少关键字段
    Evidence: .sisyphus/evidence/task-2-schema-validation.md
  ```

  **Evidence to Capture**:
  - [ ] prompt-validation.md: prompt 模板验证结果
  - [ ] schema-validation.md: JSON schema 验证结果

  **Commit**: NO（设计阶段不提交）

- [x] 3. 设计 log.md 格式和追加策略

  **What to do**:
  - 设计 `wiki/log.md` 的结构：frontmatter + 时间顺序记录
  - 每条记录格式：`## [YYYY-MM-DD HH:MM] ingest | <标题>`
  - 每条记录内容：摘要路径、概念列表、主题列表、状态、错误（如有）
  - 设计原子追加策略：每次 digest 完成后追加一个 block，不覆盖已有内容
  - 确保 log.md 可以被 unix 工具解析（grep "^## \[" | tail -5）

  **Must NOT do**:
  - 不设计过于复杂的格式（避免可视化、统计等）
  - 不创建具体 log.md 文件（只设计格式）

  **Recommended Agent Profile**:
  - **Category**: `quick` - 格式设计相对简单，不需要深入分析
  - **Skills**: `wiki-tools` - 需要了解 wiki 的组织方式
  - **Skills Evaluated but Omitted**: `writing` - 不需要复杂文档编写（只是格式设计）

  **Parallelization**:
  - **Can Run In Parallel**: YES（与 Task 1 和 Task 2 并行）
  - **Parallel Group**: Wave 1（with Task 1, Task 2）
  - **Blocks**: Task 6（依赖 log.md 格式）
  - **Blocked By**: None（可立即开始）

  **References**:
  - `raw/llm-wiki-2026-04-06.md:54-60` - LLM Wiki 的 Indexing and logging 部分
  - `wiki/index.md:1-50` - 现有 wiki index 的结构（参考格式）

  **WHY Each Reference Matters**:
  - llm-wiki-2026-04-06.md: 了解 LLM Wiki 对 log.md 的要求（时间顺序、unix 工具可解析）
  - wiki/index.md: 参考 wiki 的 frontmatter 和格式约定

  **Acceptance Criteria**:
  - [ ] log.md 格式设计写入 `.sisyphus/drafts/log-format-design.md`
  - [ ] 格式包含：frontmatter（title, type, status, tags）+ 时间顺序记录
  - [ ] 每条记录以 `## [YYYY-MM-DD HH:MM] ingest |` 前缀开头
  - [ ] 每条记录包含：摘要路径、概念列表、主题列表、状态

  **QA Scenarios**:

  ```
  Scenario: 验证 log.md 格式可被 unix 工具解析
    Tool: Bash
    Preconditions: 格式设计文档存在
    Steps:
      1. Create mock log.md with 3 test entries using designed format
      2. Run: grep "^## \[" mock-log.md | tail -5
      3. Assert: Output shows last 5 entries（或 3 entries if less）
      4. Run: grep "^## \[" mock-log.md | wc -l
      5. Assert: Output is 3（正确的条目数）
    Expected Result: log.md 格式可被 grep、tail、wc 等工具解析
    Failure Indicators: grep 无法匹配前缀
    Evidence: .sisyphus/evidence/task-3-log-parseable.md

  Scenario: 验证原子追加策略
    Tool: Bash
    Preconditions: log.md 存在且有已有内容
    Steps:
      1. Create initial log.md with 2 entries
      2. Append 1 new entry using echo >> log.md
      3. Read log.md
      4. Assert: 前 2 条 entries 未改变
      5. Assert: 新 entry 在末尾
    Expected Result: 追加操作不覆盖已有内容
    Failure Indicators: 前 2 条 entries 被改变或丢失
    Evidence: .sisyphus/evidence/task-3-append-atomic.md
  ```

  **Evidence to Capture**:
  - [ ] log-parseable.md: unix 工具解析验证结果
  - [ ] append-atomic.md: 原子追加验证结果

  **Commit**: NO（设计阶段不提交）

- [x] 4. 设计错误处理和失败记录策略

  **What to do**:
  - 定义子代理失败的处理策略：记录失败并继续其他文件（用户已确认）
  - 定义失败记录格式：在 log.md 中追加失败条目，包含错误信息
  - 定义失败条目的结构：`## [YYYY-MM-DD HH:MM] FAILED | <filename>` + error message
  - 定义主 Agent 如何汇总失败列表并报告给用户
  - 确保失败文件不阻塞后续文件的摄入

  **Must NOT do**:
  - 不设计自动重试机制（用户明确要求不重试）
  - 不设计复杂的错误恢复策略（只记录并继续）

  **Recommended Agent Profile**:
  - **Category**: `quick` - 错误处理策略相对简单
  - **Skills**: `wiki-tools` - 需要了解摄入流程的失败点
  - **Skills Evaluated but Omitted**: `ultrabrain` - 不需要复杂的错误恢复逻辑

  **Parallelization**:
  - **Can Run In Parallel**: YES（与 Task 1-3 并行）
  - **Parallel Group**: Wave 1（with Task 1-3）
  - **Blocks**: Task 5（依赖错误处理策略）
  - **Blocked By**: None（可立即开始）

  **References**:
  - `.sisyphus/drafts/session-workflow-analysis.md:Open Questions` - 用户确认的失败处理策略
  - `raw/llm-wiki-2026-04-06.md:52` - LLM Wiki 的 Lint 操作（健康检查）

  **WHY Each Reference Matters**:
  - session-workflow-analysis.md: 了解用户确认的失败处理策略（记录并继续）
  - llm-wiki-2026-04-06.md: 参考 LLM Wiki 的健康检查理念

  **Acceptance Criteria**:
  - [ ] 错误处理策略写入 `.sisyphus/drafts/error-handling-design.md`
  - [ ] 策略明确：失败文件记录到 log.md 并继续其他文件
  - [ ] 策略包含：失败条目的格式（FAILED 前缀 + error message）
  - [ ] 策略包含：主 Agent 如何汇总失败列表并报告

  **QA Scenarios**:

  ```
  Scenario: 验证失败文件不阻塞后续摄入
    Tool: Bash（模拟）
    Preconditions: 有 3 个文件，第 2 个模拟失败
    Steps:
      1. Process file 1 → success
      2. Process file 2 → simulate failure（记录到 log.md）
      3. Process file 3 → success（验证未被阻塞）
      4. Assert: log.md 包含 2 个成功条目 + 1 个失败条目
    Expected Result: 失败文件不影响后续文件的处理
    Failure Indicators: file 3 未被处理或 log.md 缺少失败记录
    Evidence: .sisyphus/evidence/task-4-failure-nonblocking.md

  Scenario: 验证失败条目格式正确
    Tool: Read
    Preconditions: log.md 包含失败条目
    Steps:
      1. Read log.md
      2. Assert: 失败条目以 "## [timestamp] FAILED |" 开头
      3. Assert: 失败条目包含错误信息（如 "Sub-agent timeout"）
    Expected Result: 失败条目格式清晰，便于用户识别
    Failure Indicators: 失败条目格式不清晰或缺少错误信息
    Evidence: .sisyphus/evidence/task-4-failure-format.md
  ```

  **Evidence to Capture**:
  - [ ] failure-nonblocking.md: 失败不阻塞验证结果
  - [ ] failure-format.md: 失败格式验证结果

  **Commit**: NO（设计阶段不提交）

- [x] 5. 更新 .opencode/commands/digest.md（并行子代理流程）

  **What to do**:
  - 重写 digest.md，加入并行子代理流程
  - 第 1 步：检测新文件（保留）
  - 第 2 步：为每个新文件启动子代理（最多 3 个并行）
    - 使用 task() 函数
    - category: "unspecified-high"
    - load_skills: ["wiki-tools"]
    - run_in_background: true
    - prompt: 引用 digest-prompt-template.md
  - 第 3 步：等待子代理完成（background_output）
  - 第 4 步：整合结果（更新 index.md + 追加 log.md）
  - 第 5 步：提交并推送

  **Must NOT do**:
  - 不修改现有的 digest.py（保持脚本不变）
  - 不删除现有的步骤（只重排和添加）

  **Recommended Agent Profile**:
  - **Category**: `quick` - 文件更新相对简单，只需重写命令定义
  - **Skills**: `wiki-tools` - 需要理解 digest 流程
  - **Skills Evaluated but Omitted**: `optimize-agents-md` - 不需要优化 AGENTS.md（只更新命令）

  **Parallelization**:
  - **Can Run In Parallel**: NO（依赖 Task 1 的分析结果和 Task 4 的错误处理策略）
  - **Parallel Group**: Wave 2（Sequential）
  - **Blocks**: Task 10（依赖更新的 digest.md）
  - **Blocked By**: Task 1, Task 4

  **References**:
  - `.sisyphus/drafts/digest-flow-analysis.md` - 现有流程缺陷分析（Task 1 输出）
  - `.sisyphus/drafts/error-handling-design.md` - 错误处理策略（Task 4 输出）
  - `.opencode/commands/digest.md:1-49` - 现有 digest 命令定义

  **WHY Each Reference Matters**:
  - digest-flow-analysis.md: 了解现有流程缺陷，确保新流程解决这些问题
  - error-handling-design.md: 了解错误处理策略，确保集成到命令中
  - digest.md: 参考现有结构，保持向后兼容

  **Acceptance Criteria**:
  - [ ] digest.md 包含"为每个新文件启动子代理"步骤
  - [ ] digest.md 包含 task() 函数调用示例
  - [ ] digest.md 包含 background_output() 调用示例
  - [ ] digest.md 包含"追加 log.md"步骤
  - [ ] digest.md 包含"汇总失败列表"步骤

  **QA Scenarios**:

  ```
  Scenario: 验证 digest.md 包含子代理指令
    Tool: Bash
    Preconditions: digest.md 已更新
    Steps:
      1. grep "task(subagent_type" .opencode/commands/digest.md
      2. Assert: 找到至少 1 处匹配
      3. grep "run_in_background: true" .opencode/commands/digest.md
      4. Assert: 找到至少 1 处匹配
    Expected Result: digest.md 包含明确的子代理启动指令
    Failure Indicators: grep 未找到匹配
    Evidence: .sisyphus/evidence/task-5-digest-subagent.md

  Scenario: 验证 digest.md 包含并行限制
    Tool: Bash
    Preconditions: digest.md 已更新
    Steps:
      1. grep -i "最多 3 个" .opencode/commands/digest.md
      2. Assert: 找到匹配（明确并行限制）
    Expected Result: digest.md 明确限制最多 3 个并行子代理
    Failure Indicators: 未找到并行限制说明
    Evidence: .sisyphus/evidence/task-5-digest-parallel-limit.md
  ```

  **Evidence to Capture**:
  - [ ] digest-subagent.md: 子代理指令验证结果
  - [ ] digest-parallel-limit.md: 并行限制验证结果

  **Commit**: YES（Wave 2 一次性提交）
  - Message: `digest: 优化工作流 - 并行子代理 + log.md`
  - Files: .opencode/commands/digest.md（与 Task 6-9 一起提交）
  - Pre-commit: 无（命令定义文件，无需测试）

- [x] 6. 创建 wiki/log.md（初始结构）

  **What to do**:
  - 创建 `wiki/log.md` 文件
  - 添加 frontmatter：
    ```yaml
    ---
    title: Wiki Log
    type: log
    status: active
    tags: [meta, intake-history]
    ---
    ```
  - 添加头部说明：
    ```markdown
    # Wiki Log

    摄入操作的完整时间顺序记录。

    每条记录格式：`## [YYYY-MM-DD HH:MM] ingest | <标题>`

    Unix 工具可解析：
    ```bash
    grep "^## \[" wiki/log.md | tail -5  # 最近 5 条记录
    ```

    ---
    ```
  - 不添加初始记录（等待第一次 digest 执行）

  **Must NOT do**:
  - 不添加初始摄入记录（记录应在实际 digest 执行时生成）
  - 不设计过于复杂的 frontmatter

  **Recommended Agent Profile**:
  - **Category**: `quick` - 创建简单文件，无需深入分析
  - **Skills**: `wiki-tools` - 需要了解 wiki 文件约定
  - **Skills Evaluated but Omitted**: `writing` - 不需要复杂文档编写

  **Parallelization**:
  - **Can Run In Parallel**: YES（与 Task 5 并行）
  - **Parallel Group**: Wave 2（with Task 5）
  - **Blocks**: Task 10（依赖 log.md 存在）
  - **Blocked By**: Task 3（依赖 log.md 格式设计）

  **References**:
  - `.sisyphus/drafts/log-format-design.md` - log.md 格式设计（Task 3 输出）
  - `wiki/index.md:1-20` - 参考 wiki 文件的 frontmatter 格式

  **WHY Each Reference Matters**:
  - log-format-design.md: 了解 log.md 的格式设计
  - wiki/index.md: 参考 wiki 文件的标准格式

  **Acceptance Criteria**:
  - [ ] wiki/log.md 文件已创建
  - [ ] frontmatter 包含 title, type, status, tags 字段
  - [ ] 头部说明包含格式说明和 unix 工具解析示例
  - [ ] 文件内容符合 log-format-design.md 的设计

  **QA Scenarios**:

  ```
  Scenario: 验证 log.md 文件存在且格式正确
    Tool: Bash
    Preconditions: log.md 已创建
    Steps:
      1. ls wiki/log.md
      2. Assert: 文件存在
      3. head -10 wiki/log.md
      4. Assert: 输出包含 frontmatter（---）
      5. Assert: 输出包含 "title: Wiki Log"
    Expected Result: log.md 文件存在且格式正确
    Failure Indicators: 文件不存在或格式错误
    Evidence: .sisyphus/evidence/task-6-log-created.md

  Scenario: 验证 log.md 可被 unix 工具解析
    Tool: Bash
    Preconditions: log.md 已创建
    Steps:
      1. grep "^## \[" wiki/log.md
      2. Assert: 输出为空（初始状态无记录）或显示已有记录
      3. grep "^## \[" wiki/log.md | tail -5
      4. Assert: 命令执行成功（无错误）
    Expected Result: log.md 可被 grep 解析
    Failure Indicators: grep 报错或无法匹配
    Evidence: .sisyphus/evidence/task-6-log-parseable.md
  ```

  **Evidence to Capture**:
  - [ ] log-created.md: log.md 创建验证结果
  - [ ] log-parseable.md: log.md 解析验证结果

  **Commit**: YES（Wave 2 一次性提交）
  - Message: 与 Task 5 相同
  - Files: wiki/log.md（与 Task 5, 7-9 一起提交）
  - Pre-commit: 无

- [x] 7. 创建 digest-prompt-template.md（子代理指令）

  **What to do**:
  - 创建 `.opencode/commands/digest-prompt-template.md`
  - 写入子代理 prompt 模板（基于 Task 2 的设计）
  - 模板包含：
    - TASK 部分：消化 raw 文件，填充摘要，创建概念
    - EXPECTED OUTCOME 部分：摘要页面路径、概念列表
    - REQUIRED TOOLS 部分：read, write, edit
    - MUST DO 部分：读取 raw、按 schema 填充、设置 sources/links
    - MUST NOT DO 部分：不编辑 index.md、不运行 lint/git
    - CONTEXT 部分：raw 文件路径、schemas 路径、文章核心内容
  - 使用占位符：`{filename}`、`{summary_stub}`、`{raw_content_preview}`

  **Must NOT do**:
  - 不硬编码具体文件名（使用占位符）
  - 不写过长内容（避免占用过多 context）

  **Recommended Agent Profile**:
  - **Category**: `quick` - 创建模板文件，相对简单
  - **Skills**: `wiki-tools` - 需要理解摄入流程
  - **Skills Evaluated but Omitted**: `writing` - 不需要复杂文档编写

  **Parallelization**:
  - **Can Run In Parallel**: YES（与 Task 5-6 并行）
  - **Parallel Group**: Wave 2（with Task 5-6）
  - **Blocks**: None（模板文件，不被其他任务依赖）
  - **Blocked By**: Task 2（依赖 prompt 模板设计）

  **References**:
  - `.sisyphus/drafts/digest-prompt-design.md` - prompt 模板设计（Task 2 输出）
  - `session-ses_29a7.md:4203-4245` - 实际子代理 prompt 示例

  **WHY Each Reference Matters**:
  - digest-prompt-design.md: 了解 prompt 模板的设计
  - session-ses_29a7.md: 参考实际使用的 prompt 结构

  **Acceptance Criteria**:
  - [ ] digest-prompt-template.md 文件已创建
  - [ ] 文件包含 TASK、EXPECTED OUTCOME、REQUIRED TOOLS 部分
  - [ ] 文件包含 MUST DO、MUST NOT DO 部分
  - [ ] 文件使用占位符：{filename}、{summary_stub}

  **QA Scenarios**:

  ```
  Scenario: 验证 prompt 模板包含关键部分
    Tool: Bash
    Preconditions: digest-prompt-template.md 已创建
    Steps:
      1. grep "**TASK**" .opencode/commands/digest-prompt-template.md
      2. Assert: 找到匹配
      3. grep "**EXPECTED OUTCOME**" .opencode/commands/digest-prompt-template.md
      4. Assert: 找到匹配
      5. grep "**MUST DO**" .opencode/commands/digest-prompt-template.md
      6. Assert: 找到匹配
    Expected Result: prompt 模板包含所有关键部分
    Failure Indicators: 某部分缺失
    Evidence: .sisyphus/evidence/task-7-prompt-parts.md

  Scenario: 验证 prompt 模板使用占位符
    Tool: Bash
    Preconditions: digest-prompt-template.md 已创建
    Steps:
      1. grep "{filename}" .opencode/commands/digest-prompt-template.md
      2. Assert: 找到匹配（占位符存在）
      3. grep "{summary_stub}" .opencode/commands/digest-prompt-template.md
      4. Assert: 找到匹配
    Expected Result: prompt 模板使用占位符，可在运行时替换
    Failure Indicators: 占位符缺失或硬编码具体值
    Evidence: .sisyphus/evidence/task-7-prompt-placeholders.md
  ```

  **Evidence to Capture**:
  - [ ] prompt-parts.md: prompt 部分验证结果
  - [ ] prompt-placeholders.md: 占位符验证结果

  **Commit**: YES（Wave 2 一次性提交）
  - Message: 与 Task 5 相同
  - Files: .opencode/commands/digest-prompt-template.md（与 Task 5-6, 8-9 一起提交）
  - Pre-commit: 无

- [x] 8. 创建 digest-output-schema.json（输出规范）

  **What to do**:
  - 创建 `.opencode/commands/digest-output-schema.json`
  - 定义子代理输出 JSON schema：
    ```json
    {
      "$schema": "http://json-schema.org/draft-07/schema#",
      "type": "object",
      "required": ["file", "summary_path", "concepts", "topics", "status"],
      "properties": {
        "file": {"type": "string"},
        "summary_path": {"type": "string"},
        "concepts": {"type": "array", "items": {"type": "string"}},
        "topics": {"type": "array", "items": {"type": "string"}},
        "status": {"type": "string", "enum": ["success", "failure"]},
        "errors": {"type": "array", "items": {"type": "string"}}
      }
    }
    ```
  - 确保 schema 足以供主 Agent 整合结果

  **Must NOT do**:
  - 不定义过于复杂的 schema（保持简洁）
  - 不添加可选字段（只定义必需字段）

  **Recommended Agent Profile**:
  - **Category**: `quick` - 创建 JSON schema 文件，相对简单
  - **Skills**: `wiki-tools` - 需要理解摄入流程的输出结构
  - **Skills Evaluated but Omitted**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES（与 Task 5-7 并行）
  - **Parallel Group**: Wave 2（with Task 5-7）
  - **Blocks**: Task 10（依赖 schema 验证）
  - **Blocked By**: Task 2（依赖 schema 设计）

  **References**:
  - `.sisyphus/drafts/digest-schema-design.md` - JSON schema 设计（Task 2 输出）

  **WHY Each Reference Matters**:
  - digest-schema-design.md: 了解 JSON schema 的设计

  **Acceptance Criteria**:
  - [ ] digest-output-schema.json 文件已创建
  - [ ] schema 包含 file、summary_path、concepts、topics、status 字段
  - [ ] schema 包含 errors 字段（可选）
  - [ ] schema 符合 JSON Schema Draft-07 规范

  **QA Scenarios**:

  ```
  Scenario: 验证 JSON schema 符合规范
    Tool: Bash
    Preconditions: digest-output-schema.json 已创建
    Steps:
      1. cat .opencode/commands/digest-output-schema.json
      2. Assert: 输出包含 "$schema": "http://json-schema.org/draft-07/schema#"
      3. Assert: 输出包含 "required": ["file", "summary_path", ...]
    Expected Result: JSON schema 符合 Draft-07 规范
    Failure Indicators: schema 格式错误或缺少必需字段
    Evidence: .sisyphus/evidence/task-8-schema-valid.md

  Scenario: 验证 schema 包含所有关键字段
    Tool: Bash
    Preconditions: digest-output-schema.json 已创建
    Steps:
      1. python3 -c "import json; schema = json.load(open('.opencode/commands/digest-output-schema.json')); print(schema['required'])"
      2. Assert: 输出包含 "file", "summary_path", "concepts", "topics", "status"
    Expected Result: schema 包含所有关键字段
    Failure Indicators: 某字段缺失
    Evidence: .sisyphus/evidence/task-8-schema-fields.md
  ```

  **Evidence to Capture**:
  - [ ] schema-valid.md: schema 规范验证结果
  - [ ] schema-fields.md: schema 字段验证结果

  **Commit**: YES（Wave 2 一次性提交）
  - Message: 与 Task 5 相同
  - Files: .opencode/commands/digest-output-schema.json（与 Task 5-7, 9 一起提交）
  - Pre-commit: 无

- [x] 9. 更新 wiki-tools SKILL.md（记录新流程）

  **What to do**:
  - 更新 `.opencode/skills/wiki-tools/SKILL.md`
  - 在"使用示例"部分添加新的 digest 流程说明：
    ```markdown
    ### 消化新来源（并行子代理）

    /digest 命令现在使用并行子代理处理文件：

    1. 检测 raw/ 中的新文件
    2. 为每个新文件启动子代理（最多 3 个并行）
    3. 等待子代理完成并返回 JSON 报告
    4. 整合结果：更新 wiki/index.md + 追加 wiki/log.md
    5. 提交并推送

    效率提升：约 5 倍（对比串行处理）
    ```
  - 在工具列表中添加 log.md 说明

  **Must NOT do**:
  - 不删除现有内容（只添加新说明）
  - 不修改现有的工具命令

  **Recommended Agent Profile**:
  - **Category**: `quick` - 文档更新，相对简单
  - **Skills**: `wiki-tools` - 需要了解 wiki-tools 的组织
  - **Skills Evaluated but Omitted**: `writing` - 不需要复杂文档编写

  **Parallelization**:
  - **Can Run In Parallel**: YES（与 Task 5-8 并行）
  - **Parallel Group**: Wave 2（with Task 5-8）
  - **Blocks**: None（文档更新，不被其他任务依赖）
  - **Blocked By**: Task 5（依赖 digest.md 更新）

  **References**:
  - `.opencode/skills/wiki-tools/SKILL.md:1-109` - 现有 SKILL.md 内容
  - `.opencode/commands/digest.md` - 新的 digest 流程（Task 5 输出）

  **WHY Each Reference Matters**:
  - SKILL.md: 了解现有文档结构，保持一致性
  - digest.md: 参考新的 digest 流程说明

  **Acceptance Criteria**:
  - [ ] SKILL.md 已更新
  - [ ] 文档包含新的 digest 流程说明
  - [ ] 文档提到效率提升（约 5 倍）
  - [ ] 文档提到并行子代理和 log.md

  **QA Scenarios**:

  ```
  Scenario: 验证 SKILL.md 包含新流程说明
    Tool: Bash
    Preconditions: SKILL.md 已更新
    Steps:
      1. grep "并行子代理" .opencode/skills/wiki-tools/SKILL.md
      2. Assert: 找到匹配
      3. grep "效率提升" .opencode/skills/wiki-tools/SKILL.md
      4. Assert: 找到匹配
    Expected Result: SKILL.md 包含新的 digest 流程说明
    Failure Indicators: 未找到相关说明
    Evidence: .sisyphus/evidence/task-9-skill-updated.md

  Scenario: 验证 SKILL.md 提到 log.md
    Tool: Bash
    Preconditions: SKILL.md 已更新
    Steps:
      1. grep -i "log.md" .opencode/skills/wiki-tools/SKILL.md
      2. Assert: 找到匹配
    Expected Result: SKILL.md 提到 log.md 的作用
    Failure Indicators: 未找到 log.md 说明
    Evidence: .sisyphus/evidence/task-9-skill-log.md
  ```

  **Evidence to Capture**:
  - [ ] skill-updated.md: SKILL.md 更新验证结果
  - [ ] skill-log.md: log.md 说明验证结果

  **Commit**: YES（Wave 2 一次性提交）
  - Message: 与 Task 5 相同
  - Files: .opencode/skills/wiki-tools/SKILL.md（与 Task 5-8 一起提交）
  - Pre-commit: 无

- [x] 10. 创建 digest_test.py（测试子代理启动）

  **What to do**:
  - 创建 `.opencode/skills/wiki-tools/tests/digest_test.py`
  - 测试用例：
    1. `test_digest_detects_new_files()` - 验证 ingest.py --new 被调用
    2. `test_digest_launches_subagents()` - 验证 task() 被调用且 run_in_background=true
    3. `test_digest_parallel_limit()` - 验证最多 3 个子代理并行
    4. `test_digest_collects_results()` - 验证 background_output() 被调用
  - 使用 mock 模拟子代理返回值

  **Must NOT do**:
  - 不运行实际的 digest 命令（只测试逻辑）
  - 不创建实际的 wiki 文件（只 mock）

  **Recommended Agent Profile**:
  - **Category**: `deep` - TDD 测试需要深入理解流程
  - **Skills**: `wiki-tools` - 需要理解 digest 流程
  - **Skills Evaluated but Omitted**: None

  **Parallelization**:
  - **Can Run In Parallel**: NO（依赖 Wave 2 完成）
  - **Parallel Group**: Wave 3（Sequential）
  - **Blocks**: Task 13（依赖测试文件）
  - **Blocked By**: Task 5（依赖 digest.md）

  **References**:
  - `.opencode/commands/digest.md` - 新的 digest 流程（Task 5 输出）
  - `.opencode/skills/wiki-tools/scripts/digest.py` - 现有 digest 脚本

  **Acceptance Criteria**:
  - [ ] digest_test.py 文件已创建
  - [ ] 包含至少 3 个测试用例
  - [ ] 所有测试用例可运行（uv run pytest）

  **QA Scenarios**:
  ```
  Scenario: 验证测试文件存在且可运行
    Tool: Bash
    Steps:
      1. ls .opencode/skills/wiki-tools/tests/digest_test.py
      2. cd .opencode/skills/wiki-tools && uv run pytest tests/digest_test.py -v
      3. Assert: 测试运行成功（可能失败，因为功能未实现）
    Expected Result: 测试文件存在且语法正确
    Evidence: .sisyphus/evidence/task-10-test-created.md
  ```

  **Commit**: YES（Wave 3 一次性提交）
  - Message: `test: digest 工作流测试套件`
  - Files: .opencode/skills/wiki-tools/tests/digest_test.py（与 Task 11-12 一起提交）
  - Pre-commit: `uv run pytest tests/ -v`

- [x] 11. 创建 log_test.py（测试 log.md 格式）

  **What to do**:
  - 创建 `.opencode/skills/wiki-tools/tests/log_test.py`
  - 测试用例：
    1. `test_log_format_parseable()` - 验证 grep "^## \[" 可匹配
    2. `test_log_append_atomic()` - 验证追加不覆盖已有内容
    3. `test_log_entry_format()` - 验证每条记录包含必要字段
  - 使用临时文件测试

  **Must NOT do**:
  - 不修改实际的 wiki/log.md（使用临时文件）
  - 不测试可视化功能（log.md 是纯文本）

  **Recommended Agent Profile**:
  - **Category**: `deep` - TDD 测试需要深入理解格式
  - **Skills**: `wiki-tools` - 需要理解 log.md 结构
  - **Skills Evaluated but Omitted**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES（与 Task 10 并行）
  - **Parallel Group**: Wave 3（with Task 10）
  - **Blocks**: Task 13（依赖测试文件）
  - **Blocked By**: Task 6（依赖 log.md 创建）

  **References**:
  - `wiki/log.md` - 新创建的 log.md 文件（Task 6 输出）
  - `.sisyphus/drafts/log-format-design.md` - log.md 格式设计（Task 3 输出）

  **Acceptance Criteria**:
  - [ ] log_test.py 文件已创建
  - [ ] 包含至少 3 个测试用例
  - [ ] 所有测试用例可运行

  **QA Scenarios**:
  ```
  Scenario: 验证 log 测试文件存在
    Tool: Bash
    Steps:
      1. ls .opencode/skills/wiki-tools/tests/log_test.py
      2. cd .opencode/skills/wiki-tools && uv run pytest tests/log_test.py -v
    Expected Result: 测试文件存在且可运行
    Evidence: .sisyphus/evidence/task-11-log-test-created.md
  ```

  **Commit**: YES（Wave 3 一次性提交）
  - Message: 与 Task 10 相同
  - Files: .opencode/skills/wiki-tools/tests/log_test.py（与 Task 10, 12 一起提交）
  - Pre-commit: `uv run pytest tests/ -v`

- [x] 12. 创建 schema_validation_test.py（测试 JSON 输出）

  **What to do**:
  - 创建 `.opencode/skills/wiki-tools/tests/schema_validation_test.py`
  - 测试用例：
    1. `test_schema_valid_json()` - 验证 schema 文件符合 JSON Schema Draft-07
    2. `test_schema_required_fields()` - 验证 schema 包含所有必需字段
    3. `test_output_matches_schema()` - 验证模拟的子代理输出符合 schema
  - 使用 jsonschema 库验证

  **Must NOT do**:
  - 不测试实际的子代理输出（使用 mock 数据）
  - 不修改 schema 文件（只验证）

  **Recommended Agent Profile**:
  - **Category**: `deep` - TDD 测试需要深入理解 JSON Schema
  - **Skills**: `wiki-tools` - 需要理解输出结构
  - **Skills Evaluated but Omitted**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES（与 Task 10-11 并行）
  - **Parallel Group**: Wave 3（with Task 10-11）
  - **Blocks**: Task 13（依赖测试文件）
  - **Blocked By**: Task 8（依赖 schema 文件）

  **References**:
  - `.opencode/commands/digest-output-schema.json` - JSON schema 文件（Task 8 输出）
  - `.sisyphus/drafts/digest-schema-design.md` - schema 设计（Task 2 输出）

  **Acceptance Criteria**:
  - [ ] schema_validation_test.py 文件已创建
  - [ ] 包含至少 3 个测试用例
  - [ ] 所有测试用例可运行

  **QA Scenarios**:
  ```
  Scenario: 验证 schema 测试文件存在
    Tool: Bash
    Steps:
      1. ls .opencode/skills/wiki-tools/tests/schema_validation_test.py
      2. cd .opencode/skills/wiki-tools && uv run pytest tests/schema_validation_test.py -v
    Expected Result: 测试文件存在且可运行
    Evidence: .sisyphus/evidence/task-12-schema-test-created.md
  ```

  **Commit**: YES（Wave 3 一次性提交）
  - Message: 与 Task 10 相同
  - Files: .opencode/skills/wiki-tools/tests/schema_validation_test.py（与 Task 10-11 一起提交）
  - Pre-commit: `uv run pytest tests/ -v`

- [x] 13. 运行所有测试 → PASS

  **What to do**:
  - 运行 `cd .opencode/skills/wiki-tools && uv run pytest tests/ -v`
  - 确保所有测试通过（GREEN 阶段）
  - 如果测试失败：返回 Task 10-12 修复实现
  - 测试通过后：记录结果到 evidence

  **Must NOT do**:
  - 不跳过失败的测试
  - 不删除测试来让测试通过

  **Recommended Agent Profile**:
  - **Category**: `quick` - 运行测试命令，相对简单
  - **Skills**: `wiki-tools` - 需要理解测试结构
  - **Skills Evaluated but Omitted**: None

  **Parallelization**:
  - **Can Run In Parallel**: NO（依赖 Task 10-12 完成）
  - **Parallel Group**: Wave 3（Sequential）
  - **Blocks**: Task 14（依赖测试通过）
  - **Blocked By**: Task 10-12

  **References**:
  - `.opencode/skills/wiki-tools/tests/digest_test.py` - digest 测试
  - `.opencode/skills/wiki-tools/tests/log_test.py` - log 测试
  - `.opencode/skills/wiki-tools/tests/schema_validation_test.py` - schema 测试

  **Acceptance Criteria**:
  - [ ] 所有测试通过（uv run pytest tests/ -v → 0 failures）
  - [ ] 测试结果记录到 `.sisyphus/evidence/task-13-all-tests-pass.md`

  **QA Scenarios**:
  ```
  Scenario: 验证所有测试通过
    Tool: Bash
    Steps:
      1. cd .opencode/skills/wiki-tools
      2. uv run pytest tests/ -v
      3. Assert: Exit code is 0（所有测试通过）
      4. Assert: Output contains "N passed" and no "failed"
    Expected Result: 所有测试通过
    Failure Indicators: 有测试失败
    Evidence: .sisyphus/evidence/task-13-all-tests-pass.md
  ```

  **Commit**: NO（测试通过是验证，不产生新文件）

- [x] 14. 集成测试：完整 digest 流程（2 个文件）

  **What to do**:
  - 准备 2 个测试 raw 文件（mock 或使用现有 raw 文件）
  - 运行 `/digest` 命令
  - 验证：
    1. 2 个子代理被启动（并行）
    2. 2 个摘要页面被创建
    3. wiki/log.md 被追加 2 条记录
    4. wiki/index.md 被更新
    5. 总时间 <10 分钟
  - 清理测试文件

  **Must NOT do**:
  - 不修改实际的 wiki/index.md（使用临时索引或 mock）
  - 不提交测试文件

  **Recommended Agent Profile**:
  - **Category**: `deep` - 集成测试需要端到端验证
  - **Skills**: `wiki-tools` - 需要理解完整流程
  - **Skills Evaluated but Omitted**: None

  **Parallelization**:
  - **Can Run In Parallel**: NO（依赖 Wave 3 完成）
  - **Parallel Group**: Wave 4（Sequential）
  - **Blocks**: Task 15（依赖集成测试结果）
  - **Blocked By**: Task 13（依赖测试通过）

  **References**:
  - `.opencode/commands/digest.md` - digest 命令定义
  - `.opencode/commands/digest-prompt-template.md` - 子代理 prompt 模板
  - `.opencode/commands/digest-output-schema.json` - 子代理输出 schema

  **Acceptance Criteria**:
  - [ ] 2 个文件被成功摄入
  - [ ] wiki/log.md 包含 2 条新记录
  - [ ] 总时间 <10 分钟
  - [ ] 结果记录到 `.sisyphus/evidence/task-14-integration-test.md`

  **QA Scenarios**:
  ```
  Scenario: 验证完整 digest 流程
    Tool: Bash + Read
    Steps:
      1. Prepare 2 mock raw files in raw/
      2. Run /digest command
      3. Wait for completion
      4. Assert: wiki/summaries/ contains 2 new summary files
      5. Assert: wiki/log.md contains 2 new entries
      6. Assert: Total time <10 minutes (check timestamp)
    Expected Result: 完整流程成功执行
    Failure Indicators: 有步骤失败或超时
    Evidence: .sisyphus/evidence/task-14-integration-test.md
  ```

  **Commit**: NO（集成测试是验证，不产生新文件）

- [x] 15. 效率验证：时间对比 baseline

  **What to do**:
  - 对比 session ses_29a7 的 baseline（第一阶段 30 分钟处理 1 个文件）
  - 测量新的 digest 流程时间
  - 计算 efficiency gain：
    - Baseline: 30 分钟 / 1 文件 = 30 分钟/文件
    - New: <10 分钟 / 2 文件 = <5 分钟/文件
    - Efficiency gain: >5x
  - 记录结果到 evidence

  **Must NOT do**:
  - 不修改 baseline 数据（只对比）
  - 不伪造时间数据

  **Recommended Agent Profile**:
  - **Category**: `quick` - 时间对比，相对简单
  - **Skills**: `wiki-tools` - 需要理解流程
  - **Skills Evaluated but Omitted**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES（与 Task 14 并行）
  - **Parallel Group**: Wave 4（with Task 14）
  - **Blocks**: Task F3（依赖效率数据）
  - **Blocked By**: Task 14（依赖集成测试结果）

  **References**:
  - `session-ses_29a7.md:2403-4173` - Baseline（第一阶段时间）
  - `.sisyphus/evidence/task-14-integration-test.md` - 新流程时间

  **Acceptance Criteria**:
  - [ ] Efficiency gain >5x
  - [ ] 结果记录到 `.sisyphus/evidence/task-15-efficiency-gain.md`

  **QA Scenarios**:
  ```
  Scenario: 验证效率提升 >5x
    Tool: Bash
    Steps:
      1. Read baseline time from session-ses_29a7.md (30 minutes for 1 file)
      2. Read new flow time from task-14-integration-test.md (<10 minutes for 2 files)
      3. Calculate efficiency gain
      4. Assert: Efficiency gain >5x
    Expected Result: 效率提升显著
    Failure Indicators: 效率提升不足
    Evidence: .sisyphus/evidence/task-15-efficiency-gain.md
  ```

  **Commit**: NO（效率验证是分析，不产生新文件）

- [x] 16. LLM Wiki 合规性检查

  **What to do**:
  - 对照 raw/llm-wiki-2026-04-06.md 的理念检查：
    1. ✅ LLM 负责所有 bookkeeping（log.md 自动追加）
    2. ✅ 一次消化一个文件（子代理独立处理）
    3. ✅ Wiki 是持久的、复合的 artifact（log.md 记录历史）
    4. ✅ 三层架构（Raw → Wiki → Schema）
    5. ✅ 三种操作（Ingest via digest, Query via /query, Lint via lint.py）
  - 记录合规性检查结果

  **Must NOT do**:
  - 不伪造合规性结果
  - 不忽略不符合点

  **Recommended Agent Profile**:
  - **Category**: `deep` - 合规性检查需要深入理解 LLM Wiki 理念
  - **Skills**: `wiki-tools` - 需要理解 wiki 结构
  - **Skills Evaluated but Omitted**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES（与 Task 14-15 并行）
  - **Parallel Group**: Wave 4（with Task 14-15）
  - **Blocks**: Task F1（依赖合规性检查结果）
  - **Blocked By**: Task 5-9（依赖实现的流程）

  **References**:
  - `raw/llm-wiki-2026-04-06.md:18-60` - LLM Wiki 核心理念
  - `.opencode/commands/digest.md` - 新的 digest 流程
  - `wiki/log.md` - 摄入历史记录

  **Acceptance Criteria**:
  - [ ] 所有 LLM Wiki 核心理念都被满足
  - [ ] 合规性检查结果记录到 `.sisyphus/evidence/task-16-llm-wiki-compliance.md`

  **QA Scenarios**:
  ```
  Scenario: 验证 LLM Wiki 合规性
    Tool: Read
    Steps:
      1. Read raw/llm-wiki-2026-04-06.md (lines 18-60)
      2. For each core principle, verify implementation exists
      3. Assert: All principles are satisfied
    Expected Result: 100% LLM Wiki 合规
    Failure Indicators: 有不符合点
    Evidence: .sisyphus/evidence/task-16-llm-wiki-compliance.md
  ```

  **Commit**: NO（合规性检查是分析，不产生新文件）

- [x] 17. 文档更新：README 和 AGENTS.md

  **What to do**:
  - 更新 `README.md`：
    - 添加 "log.md - 摄入时间顺序记录" 说明
    - 更新 "最近更新" 部分
  - 更新 `AGENTS.md`：
    - 添加 "log.md 自动追加（无需用户确认）" 说明
    - 更新 "Digest 流程" 部分，提到并行子代理
  - 确保文档反映新的工作流

  **Must NOT do**:
  - 不删除现有文档内容（只添加和更新）
  - 不修改文档的格式约定

  **Recommended Agent Profile**:
  - **Category**: `quick` - 文档更新，相对简单
  - **Skills**: `wiki-tools` - 需要理解 wiki 结构
  - **Skills Evaluated but Omitted**: `writing` - 不需要复杂文档编写

  **Parallelization**:
  - **Can Run In Parallel**: YES（与 Task 14-16 并行）
  - **Parallel Group**: Wave 4（with Task 14-16）
  - **Blocks**: None（文档更新，不被其他任务依赖）
  - **Blocked By**: Task 5-9（依赖实现的流程）

  **References**:
  - `README.md` - 现有 README
  - `AGENTS.md` - 现有 AGENTS.md
  - `.opencode/commands/digest.md` - 新的 digest 流程

  **Acceptance Criteria**:
  - [ ] README.md 包含 log.md 说明
  - [ ] AGENTS.md 包含 digest 流程更新
  - [ ] 文档反映新的工作流

  **QA Scenarios**:
  ```
  Scenario: 验证 README 包含 log.md 说明
    Tool: Bash
    Steps:
      1. grep -i "log.md" README.md
      2. Assert: 找到匹配
    Expected Result: README 提到 log.md
    Failure Indicators: 未找到 log.md 说明
    Evidence: .sisyphus/evidence/task-17-readme-updated.md

  Scenario: 验证 AGENTS.md 包含 digest 流程更新
    Tool: Bash
    Steps:
      1. grep -i "并行子代理" AGENTS.md
      2. Assert: 找到匹配
    Expected Result: AGENTS.md 提到并行子代理
    Failure Indicators: 未找到更新
    Evidence: .sisyphus/evidence/task-17-agents-updated.md
  ```

  **Commit**: YES（最终提交）
  - Message: `docs: 更新 digest 工作流文档`
  - Files: README.md, AGENTS.md
  - Pre-commit: 无

---

## Final Verification Wave（MANDATORY — 所有实现任务后）

> 4 个审查 agent 并行运行。全部必须 APPROVE。呈现整合结果给用户并获取明确 "okay"。

- [x] F1. **计划合规性审计** — `oracle`
  读取计划全文。对每个 "Must Have": 验证实现存在（读文件、curl endpoint、运行命令）。对每个 "Must NOT Have": 搜索代码库中的禁止模式 — 如果找到则拒绝并提供 file:line。检查 evidence 文件存在于 .sisyphus/evidence/。对比交付物与计划。
  输出: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [x] F2. **代码质量审查** — `unspecified-high`
  运行 `tsc --noEmit` + linter + `bun test`。审查所有改变文件：`as any`/`@ts-ignore`、空 catch、console.log in prod、注释代码、未用 imports。检查 AI slop: 过度注释、过度抽象、通用名称（data/result/item/temp）。
  输出: `Build [PASS/FAIL] | Lint [PASS/FAIL] | Tests [N pass/N fail] | Files [N clean/N issues] | VERDICT`

- [x] F3. **实际 QA 测试** — `unspecified-high`（+ playwright skill 如果 UI）
  从干净状态开始。执行每个任务的每个 QA scenario — 跟随精确步骤、捕获证据。测试跨任务集成（功能一起工作，而非隔离）。测试边缘情况：空状态、无效输入、快速动作。保存到 `.sisyphus/evidence/final-qa/`。
  输出: `Scenarios [N/N pass] | Integration [N/N] | Edge Cases [N tested] | VERDICT`

- [x] F4. **范围一致性检查** — `deep`
  对每个任务：读 "What to do"、读实际 diff（git log/diff）。验证 1:1 — spec 中所有内容已构建（无遗漏）、spec 外无内容已构建（无 creep）。检查 "Must NOT do" 合规。检测跨任务污染：Task N 修改 Task M 的文件。标记未解释的改变。
  输出: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

- **Wave 1**: 不提交（分析阶段）
- **Wave 2**: `digest: 优化工作流 - 并行子代理 + log.md` - .opencode/commands/digest.md, wiki/log.md, .opencode/commands/digest-prompt-template.md, .opencode/commands/digest-output-schema.json, .opencode/skills/wiki-tools/SKILL.md
- **Wave 3**: `test: digest 工作流测试套件` - .opencode/skills/wiki-tools/tests/digest_test.py, log_test.py, schema_validation_test.py
- **Wave 4**: 不提交（集成验证）
- **Final**: 用户确认后一次性提交

---

## Success Criteria

### 验证命令

```bash
# 验证 digest 命令触发子代理
grep "task(subagent_type" .opencode/commands/digest.md

# 验证 log.md 存在并格式正确
ls wiki/log.md && grep "^## \[" wiki/log.md | head -5

# 验证子代理 schema 存在
ls .opencode/commands/digest-output-schema.json && cat .opencode/commands/digest-output-schema.json

# 验证测试通过
cd .opencode/skills/wiki-tools && uv run pytest tests/ -v

# 效率对比（预期：<10 分钟 vs 当前 6 分钟）
time uv run .opencode/commands/digest.md  # 实际测试需要 raw 文件
```

### 最终检查清单

- [ ] 所有 "Must Have" 存在
- [ ] 所有 "Must NOT Have" 缺失
- [ ] 所有测试通过
- [ ] log.md 自动追加工作
- [ ] 失败文件记录正确
- [ ] 并行上限 3 个生效
- [ ] 效率提升验证（<10 分钟 vs 6 分钟）
- [ ] LLM Wiki 合规（LLM 负责 bookkeeping）