# Claude Code Skill 渐进式加载 — 研究发现

## 1. 渐进式加载的核心机制

### 1.1 两阶段加载架构

**阶段一：Discovery（发现）— 只加载 frontmatter 摘要**

源码位置：`src/skills/loadSkillsDir.ts:97-104`

```typescript
// Estimates token count for a skill based on frontmatter only
// (name, description, whenToUse) since full content is only loaded on invocation.
export function estimateSkillFrontmatterTokens(skill: Command): number {
  const frontmatterText = [skill.name, skill.description, skill.whenToUse]
    .filter(Boolean)
    .join(' ')
  return roughTokenCountEstimation(frontmatterText)
}
```

**阶段二：Invocation（调用）— 加载完整 markdown 内容**

源码位置：`src/tools/SkillTool/SkillTool.ts:622-645` (inline) 和 `122-286` (forked)

skill 摘要通过两种方式注入到 LLM 对话中：
1. **skill_listing attachment**：每轮 turn 的 attachment，列出 skill 的 name + description + whenToUse（有预算限制，1% context window）
2. **skill_discovery attachment**（实验性）：基于用户输入的智能匹配

### 1.2 摘要注入的预算控制

源码位置：`src/tools/SkillTool/prompt.ts`

- 上下文预算 = context window tokens × 4 chars/token × 1% = 默认 8000 字符
- 每个 skill 的 description + whenToUse 最大 250 字符
- bundled skills 永远保留完整描述，非 bundled 的可能被截断为 names-only
- 源码注释明确说："The listing is for discovery only — the Skill tool loads full content on invoke, so verbose whenToUse strings waste turn-1 cache_creation tokens without improving match rate."

### 1.3 完整内容加载的两种模式

**Inline 模式**（默认）：skill markdown 展开到当前对话上下文
- `processPromptSlashCommand()` 将 skill 内容包装为 user message 注入
- 插入 `<command-name>/<skillName></command-name>` tag 标识已加载
- SkillTool prompt 明确指示模型：看到此 tag 时不要再重复调用 SkillTool

**Fork 模式**：skill 在独立子 agent 中执行
- frontmatter 中 `context: fork` 声明
- 子 agent 有独立的 token 预算和工具集
- 执行完毕后返回结果摘要，不污染主对话上下文

### 1.4 SkillTool 的防重复调用机制

源码位置：`src/tools/SkillTool/prompt.ts:194`

```
If you see a <command-name> tag in the current conversation turn, 
the skill has ALREADY been loaded - follow the instructions directly 
instead of calling this tool again
```

这行指令是嵌套分析的关键。

---

## 2. 场景分析

### 场景一：Skill 嵌套（Skill A 的 markdown 内容中指示调用 Skill B）

**定义**：Skill A 的 SKILL.md 内容中，通过文字指令让模型调用 Skill B。例如 Skill A 写了"执行前先调用 /review-pr"。

**渐进式加载是否有效：✅ 有效**

**执行流程**：
1. 模型看到 skill_listing 中的 Skill A 摘要
2. 模型调用 SkillTool("A") → 加载 Skill A 完整内容
3. Skill A 内容作为 user message 注入对话，附带 `<command-name>/A</command-name>` tag
4. **关键点**：Skill B 的完整内容此时**并未加载**，只有摘要
5. 模型读到 Skill A 中"先调用 /review-pr"的指令
6. 模型在**同一个 turn 的后续 tool call** 中调用 SkillTool("review-pr")
7. Skill B 的完整内容被加载

**代码证据**：
- SkillTool prompt 中的防重复指令只检查 `<command-name>` tag，Skill B 没有此 tag
- SkillTool.ts:673-688 的遥测记录 `invocation_trigger: 'nested-skill'` 和 `query_depth`，明确识别嵌套 skill 调用
- 模型有完整的 SkillTool 工具可用，可以再次调用

**限制**：
- 依赖模型的"遵循指令"能力 — 如果 Skill A 没有明确指示调用 Skill B，模型可能不会主动调用
- 每次嵌套调用消耗一轮 tool call 的延迟
- 嵌套深度没有硬性限制，但受 token 预算约束

### 场景二：Agent 声明 `skills:` 依赖（Skill 引用）

**定义**：Agent（不是 Skill）的 frontmatter 中声明 `skills: [skill-A, skill-B]`。

**渐进式加载是否有效：❌ 无效 — 全量预加载**

**执行流程**：
源码位置：`src/tools/AgentTool/runAgent.ts:578-645`

```typescript
const skillsToPreload = agentDefinition.skills ?? []
// ...
const loaded = await Promise.all(
  validSkills.map(async ({ skillName, skill }) => ({
    skillName,
    skill,
    content: await skill.getPromptForCommand('', toolUseContext),
  })),
)
for (const { skillName, skill, content } of loaded) {
  initialMessages.push(
    createUserMessage({
      content: [{ type: 'text', text: metadata }, ...content],
      isMeta: true,
    }),
  )
}
```

**代码证据**：
- `getPromptForCommand('', toolUseContext)` 返回的是 skill 的**完整 markdown 内容**（含 base directory header、参数替换、shell 命令执行等）
- 所有预加载 skill 的内容被放入 agent 的 `initialMessages`
- 这些消息在 agent 启动时就全量注入，**不走渐进式加载**

**设计意图**：
- Agent 需要在启动时就有完整的领域知识，不能等 invocation 再加载
- 这是 Agent 和 Skill 的本质区别：Agent 是自主执行者，需要预加载知识；Skill 是按需工具

### 场景三：多层嵌套（A → B → C）

**定义**：Skill A 指示调用 Skill B，Skill B 再指示调用 Skill C。

**渐进式加载是否有效：✅ 有效，但有限制**

**执行流程**：
1. Skill A 完整内容加载（第一层）
2. Skill B 完整内容加载（第二层，通过 SkillTool 嵌套调用）
3. Skill C 完整内容加载（第三层）

**代码证据**：
- SkillTool 没有"调用深度限制"的代码
- 遥测记录 `query_depth` 表明系统感知嵌套层级
- 每次 SkillTool 调用都是独立的 tool use → tool result 交换

**实际限制**：
1. **Token 预算**：每层加载的完整内容都会累积在对话上下文中，不是替换而是追加
2. **模型能力**：需要模型在处理 A 的内容时正确识别需要调用 B，处理 B 时识别需要调用 C
3. **延迟**：每层嵌套是一次完整的 API 往返，3 层嵌套至少 3 轮额外延迟
4. **没有 cycle detection**：如果 A → B → A 会形成死循环（虽然模型理论上会识别重复调用）

### 场景四：Fork 模式的嵌套

**定义**：Skill A 声明 `context: fork`，在子 agent 中运行，子 agent 再调用 Skill B。

**渐进式加载是否有效：✅ 有效，且更优**

**执行流程**：
1. 主对话调用 SkillTool("A") → 启动 forked sub-agent
2. 子 agent 加载 Skill A 完整内容
3. 子 agent 内部调用 SkillTool("B") → 加载 Skill B 完整内容
4. 子 agent 返回结果摘要给主对话
5. **关键**：Skill A 和 B 的完整内容留在子 agent 上下文中，**不污染主对话**

**代码证据**：
- `executeForkedSkill` 在 finally 块中调用 `clearInvokedSkillsForAgent(agentId)` 清理子 agent 的 invoked skills 状态
- 子 agent 的 messages 收集完成后通过 `extractResultText` 提取文本摘要
- `agentMessages.length = 0` 主动释放内存

---

## 3. 补充发现

### 3.1 实验性 skill_discovery（AI 智能匹配）

`feature('EXPERIMENTAL_SKILL_SEARCH')` 守卫的功能，实现文件在泄漏源码中被 tree-shake 掉了，但从引用可以推断：

- **Turn 0 发现**：`getTurnZeroSkillDiscovery(input, messages, context)` — 基于用户输入文本匹配相关 skills，阻塞式调用
- **Inter-turn 发现**：`startSkillDiscoveryPrefetch()` — 在 `query.ts:331` 并行启动，基于 write-pivot 检测（非写操作的 turn 跳过），异步预取
- **性能考量**：注释说旧的 assistant_turn 信号路径"97% of those calls found nothing in prod"，所以改成了并行 prefetch
- **skipSkillDiscovery 保护**：skill 内容本身不会触发 discovery（避免 SKILL.md 中 110KB 的文字触发搜索）
- **skill_discovery attachment**：发现结果作为 attachment 注入，UI 层渲染为 "Skills relevant to your task:"

### 3.2 Compaction 后 Skill 内容恢复

源码位置：`src/services/compact/compact.ts:1489-1660`

**已调用 skill 的恢复**：
- `createSkillAttachmentIfNeeded()` 生成 `invoked_skills` 类型的 attachment
- 按 `invokedAt` 时间降序排列，最近调用的优先保留
- 每个 skill 最大 5000 tokens，总预算 25000 tokens
- 超出预算的 skill 被丢弃
- 每个 skill 截断后追加：`[... skill content truncated for compaction; use Read on the skill path if you need the full text]`

**skill_listing 的恢复**：
- compaction 后**不会**重新注入 skill_listing（~4K tokens 的 cache_creation 开销不值得）
- 模型仍然有 SkillTool 在工具 schema 中，可以按需调用
- `resetSentSkillNames()` 不在 `postCompactCleanup` 中调用（刻意跳过）
- 动态新增的 skill 通过 `skillChangeDetector` / cacheUtils 重置处理

### 3.3 System Prompt 中的 Skill 相关内容

`getSessionSpecificGuidanceSection()` 中关于 skill 的内容只有一行：

```
/<skill-name> (e.g., /commit) is shorthand for users to invoke a user-invocable skill.
When executed, the skill gets expanded to a full prompt.
Use the Skill tool to execute them.
IMPORTANT: Only use Skill tool for skills listed in its user-invocable skills section
- do not guess or use built-in CLI commands.
```

**关键发现：system prompt 中不包含 skill 列表。** Skill 列表完全通过 attachment（skill_listing）和 SkillTool 的工具 schema 传递。这意味着 skill 列表不在 system prompt 的 cache scope 内，每次 turn 都重新生成。

---

## 4. Claude Code vs OpenClaw 的关键差异

| 维度 | Claude Code | OpenClaw |
|------|-------------|----------|
| Skill 描述注入方式 | attachment (skill_listing) + SkillTool prompt | system prompt 中的 `<available_skills>` 标签 |
| 摘要字段 | name + description + whenToUse | name + description |
| 预算控制 | 1% context window，bundled 优先 | 无显式预算控制 |
| 防重复调用 | `<command-name>` tag + prompt 指令 | `<available_skills>` 标签 + "只读一个" 指令 |
| Agent 预加载 | `skills:` frontmatter 全量注入 | N/A |
| Fork 模式 | `context: fork` 子 agent 隔离 | sessions_spawn |
| 实验性功能 | skill_discovery (AI 匹配) | 无对应功能 |

## 5. 核心结论

1. **Claude Code 的渐进式加载是真实有效的** — 启动时只注入 name+description+whenToUse 摘要，完整内容仅在 SkillTool invocation 时加载
2. **Skill 嵌套场景有效** — 模型可以在 Skill A 加载后继续调用 SkillTool 加载 Skill B，系统有专门的遥测追踪嵌套调用
3. **Agent 的 skills: 声明不走渐进式加载** — 这是设计决策：Agent 是自主执行者，需要预加载完整知识
4. **Fork 模式是处理嵌套的最佳实践** — 子 agent 隔离上下文，避免主对话 token 膨胀
5. **OpenClaw 的 `<available_skills>` 标签方式本质上也是渐进式加载** — 启动时注入描述列表，skill 文件内容只在 read 调用时加载
