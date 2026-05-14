# HEARTBEAT.md

## 1. Memory 日志检查（最高优先级）

```bash
TODAY=$(date +%Y-%m-%d)
ls ~/.openclaw/workspace/memory/${TODAY}*.md 2>/dev/null
```

- **如果没有今天的日志**：检查 `/tmp/openclaw-heartbeat-state.json` 是否有今天会话活动的记录
- 如果有活动记录但缺日志 → 用 `openclaw sessions --json` 获取最近会话信息，创建 `memory/YYYY-MM-DD.md` 补写
- 如果没有任何活动 → 不创建空日志（避免"无记录"垃圾文件）

## 2. MEMORY.md 周更新（每周一检查）

- 距上次MEMORY.md修改超过7天？→ 读最近7天memory日志，提取重要内容更新MEMORY.md
- 检查方式：`stat -c %Y ~/.openclaw/workspace/MEMORY.md`，对比当前时间戳

## 3. 注意事项

- Heartbeat运行在isolated session，没有对话历史上下文
- 只依赖HEARTBEAT.md中的指令和文件系统状态
- 不要推断之前对话内容，只基于可验证的事实操作
- 如果什么需要关注的都没有，回复 HEARTBEAT_OK
