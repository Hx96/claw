# Claude Code Skill 渐进式加载分析 — 最终报告

## 结论

Claude Code 的 skill 渐进式加载是**真实有效的两阶段架构**：

- **Discovery 阶段**：启动时只注入每个 skill 的 `name` + `description` + `whenToUse`（摘要有预算上限，context window 的 1%，约 8000 字符）
- **Invocation 阶段**：模型通过 SkillTool 调用时才加载 skill 的完整 markdown 内容

源码注释原话：`"name, description, whenToUse since full content is only loaded on invocation"`

---

## 三种场景逐一分析

### 1. Skill 嵌套（A 的内容指示调用 B）— ✅ 有效

模型加载 Skill A 后读到"先调用 /B"的指令，在同一 turn 后续调用 SkillTool("B") 加载 B 的完整内容。系统遥测专门追踪 `invocation_trigger: 'nested-skill'` 和 `query_depth`。

**防重复机制**：SkillTool prompt 写了"如果当前 turn 有 `<command-name>` tag 说明已加载，不要再调用"。Skill B 没有此 tag，所以不会被拦截。

### 2. Agent 的 skills: 声明 — ❌ 不走渐进式，全量预加载

Agent frontmatter 的 `skills: [A, B]` 字段会在 agent 启动时调用 `skill.getPromptForCommand()` 加载**完整 markdown**，全量注入 initialMessages。

这是设计决策：Agent 是自主执行者，需要预加载完整领域知识，不能等 invocation。

### 3. 多层嵌套（A → B → C）— ✅ 有效，但有实际限制

- **无硬性深度限制**，代码中没有调用链长度检查
- **限制 1**：每层完整内容累积在上下文中（除非用 fork 模式）
- **限制 2**：每层嵌套是一次 API 往返延迟
- **限制 3**：没有 cycle detection，A → B → A 理论上可能死循环
- **最佳实践**：Skill A 用 `context: fork` 在子 agent 中运行，子 agent 再调用 B 和 C，结果摘要返回主对话，不污染主上下文

---

## OpenClaw 对比

OpenClaw 的 `<available_skills>` 标签本质上也是渐进式加载——启动时注入描述列表，skill 文件内容只在 read 调用时加载。但有几个差异：

- OpenClaw 把描述列表放在 system prompt 中（cache 效率高），Claude Code 放在每轮 turn 的 attachment 中
- Claude Code 有 budget truncation 和 bundled 优先机制，OpenClaw 没有
- Claude Code 有 fork 模式隔离嵌套上下文，OpenClaw 对应用 sessions_spawn

---

*分析基于 github.com/mehmoodosman/claude-code 泄漏源码（512K 行 TypeScript，2026-03-31 通过 npm source map 恢复）*
