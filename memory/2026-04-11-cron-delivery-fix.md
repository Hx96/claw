# 2026-04-11 - Cron投递全面修复

## 时间范围
2026-04-11 13:00 ~ 14:36 (Asia/Shanghai)

---

## 背景

用户反馈收不到消息，网关卡顿后自动重启（13:01）。今早07:20-08:10的三个推送任务全部因Gateway draining失败。

---

## 排查过程

### 1. 诊断投递配置
- 检查 `~/.openclaw/cron/jobs.json` 中5个任务的配置
- 发现所有任务的 `delivery.mode = "off"`，`payload.channel`/`payload.to`/`payload.deliver` 全部为空
- 微信channel配置：仅1个账号 `999559c28b26-im-bot`，绑定用户 `o9cq80_r2wmTBUtFu0AJ6T-jxK68@im.wechat`

### 2. 第一轮修复：补充delivery配置
- 给5个任务设置 `delivery.mode = "announce"`
- 补充 `delivery.channel = "openclaw-weixin"`
- 补充 `delivery.to = "o9cq80_r2wmTBUtFu0AJ6T-jxK68@im.wechat"`
- 补充 `delivery.accountId = "999559c28b26-im-bot"`
- 设置 `payload.deliver = true`

### 3. 用户反馈"修复以不重启网关为目的"
- 意识到第一性原理：先分析根本原因，不要惯性思维
- cron执行时网关会重新读取jobs.json，修改配置文件不需要重启

### 4. 第二轮修复：发现message failed
- 日志：`message failed: Action send requires a target`
- 根因：prompt里教AI在隔离会话中手动调用message工具投递，但隔离会话没有对话上下文，缺少target参数
- 之前安全检查连续14次失败的根因也是这个

### 5. 第三轮修复：移除手动message指令
- 从5个任务的prompt中移除所有手动调用message工具的指令
- 替换为："不要调用message工具手动发送！直接输出内容即可，系统会自动投递。"
- 投递逻辑完全交给系统层 delivery 配置

### 6. 验证
- 推送检查任务实测：`delivered: true`，`status: ok`，用户确认收到
- AI Builders简报任务入队执行

---

## 关键决策

| 决策 | 原因 |
|------|------|
| delivery.mode=announce 而非手动message | 隔离会话无对话上下文，手动调用必然失败 |
| 不重启网关 | cron每次执行会重新读取jobs.json，热加载即可 |
| 保留delivery配置 + 移除prompt指令 | 双层保险：系统层投递为主，不让AI干预投递逻辑 |

---

## 系统状态快照

- OpenClaw v2026.4.8
- 5个cron任务全部修复
- 磁盘84%（7.6G剩余）
- 04-05~04-10 memory日志空白

---

## 沉淀到SOUL.md的行为准则

新增：**不重启优先** — 修复问题时，默认以不重启服务为第一目标。重启是最后手段，不是第一反应。

## 沉淀到MEMORY.md的经验

1. cron投递要靠系统层delivery配置，不让AI手动调message
2. 修复问题默认不重启
3. 配置改完必须实测验证投递是否到达
