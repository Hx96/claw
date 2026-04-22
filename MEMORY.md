# MEMORY.md - 小马的长期记忆

_上次更新: 2026-04-22_

## 用户画像

- 通过企业微信（openclaw-weixin）沟通
- 微信 ID: o9cq80_r2wmTBUtFu0AJ6T-jxK68@im.wechat
- 时区: Asia/Shanghai
- 风格偏好: 直接、高效、不要废话
- 对AI工具和Agent技术高度关注

## 环境信息

- **服务器**: 腾讯云轻量应用服务器 (VM-0-10-ubuntu)
- **OpenClaw**: v2026.4.12 (2026.4.2 → 2026.4.8 → 2026.4.12)
- **opencli**: v1.6.1（70+站点，无浏览器环境12个可用）
- **Node.js**: v22.22.1 (NVM管理)
- **模型**: glmcode/GLM-5-Turbo
- **微信账号ID**: b16fc7cc8099-im-bot（accountId: 999559c28b26-im-bot）
- **搜索引擎**: 百度(中文) + Yahoo(英文)，Google被腾讯云IP封锁，已通过scrapling绕过

## 定时任务清单

| 任务名 | 时间 | 状态 |
|--------|------|------|
| 每日AI热点推送 | 07:20 * * * * | ✅ 正常 |
| AI Builders 每日简报 | 07:30 * * * * | ✅ 正常 |
| 每日站会汇报 | 08:00 * * * * | ✅ 正常 |
| 每日推送检查 | 08:10 * * * * | ✅ 正常 |

⚠️ cron run日志每次执行覆盖同一文件，无法回溯历史执行状态


## 已安装的关键技能

- agent-browser (无头浏览器，绕Google验证用scrapling)
- multi-search-engine (17引擎)
- follow-builders (AI Builders Digest)
- waf-bypass-automation (下载保护内容)
- news-scout (AI+投资新闻)
- free-google-search-with-browser (scrapling绕过Google)
- x-tweet-fetcher (抓推文，无API key)
- opencli (12个免浏览器命令：hackernews/arxiv/stackoverflow/wikipedia/v2ex等)

## 重要事件时间线

### 2026-03-25
- 首次活跃日，大量调研任务
- 糖酒会调研、数据开发Agent调研、AI Agent开发调研
- ClawHub技能排行调研，安装multi-search-engine
- 技术社区养虾调研（真养虾不是隐喻）
- 确立多源交叉验证原则

### 2026-03-26
- 麦肯锡方法PPT下载任务（多个PPT源，WAF绕过）
- 创建OpenClaw每日安全检查定时任务(08:00)
- 完成麦肯锡知识体系大纲

### 2026-03-27
- 安全检查任务调整到22:00
- 每日AI热点推送创建(07:20)，9个信息源验证
- AI新闻技能调研（ClawHub 30+个相关技能）
- 技能流行度排行（tech-news-digest > ai-news-researcher > news-aggregator）
- 假设驱动问题解决法文档
- 最后一条memory日志

### 2026-03-28 ~ 2026-04-10
- 无memory日志记录（04-05~04-10空白）
- cron任务持续运行（AI热点推送、AI Builders简报、安全检查）
- 期间AI热点：Gemma 4发布、Qwen3.6-Plus、Cursor 3、Claude Code发现23年Linux漏洞
- 04-07：openclaw.json被clobbered，微信配置丢失重建
- 04-11：新增插件（ddingtalk、wecom、yuanbao、qqbot）

### 2026-04-13
- 排查AI Builders简报投递问题（用户反馈07:30没收到）
- 发现cron日志显示delivered但微信端消息可能被折叠
- 手动补发简报到微信
- 抓取3条记忆相关推文详情（Garry Tan、Aditya Agarwal）推送
- **决策：确认每天写memory日志的习惯**

### 2026-04-17
- 磁盘清理：84%→53%，释放约6G（pnpm/npm/apt/journal/tmp）
- 手动重新触发AI热点+AI Builders简报
- 用户提问：解放战争时期货币政策（整理1937-1949货币崩溃数据）

### 2026-04-18
- opencli v1.6.1搜索能力实测，结果沉淀到TOOLS.md
- 结论：无浏览器环境12个命令可用，覆盖论文/代码/社区/新闻/词典/百科

### 2026-04-14~04-21
- 04-14/15/16/21有会话活动，但未写memory日志（日志断档老问题）
- 04-19/20无活动记录
- 04-22补全04-14~04-21空白日志

### 2026-04-04
- 创建每日站会汇报定时任务(08:00)
- 发现并修复：站会任务缺accountId导致投递失败
- 发现并修复：站会prompt中memory文件路径格式不对（日志是日期前缀+主题格式）
- 优化站会任务：三个数据源（memory日志 > cron执行记录 > MEMORY.md）
- SOUL.md增加：所有配置和操作必须实测验证
- 创建MEMORY.md，补全记忆体系

### 2026-04-11
- 网关卡顿→重启恢复，发现今早4个推送任务全部因Gateway draining失败
- **全面修复cron投递配置**（第一性原理驱动，不重启网关）
- 修复内容：
  - 5个任务 `delivery.mode` 从 `off` → `announce`
  - 5个任务补充 `delivery.channel`/`delivery.to`/`delivery.accountId`
  - 移除prompt中手动调message工具的指令（隔离会话中会导致 `requires target` 错误）
  - 投递逻辑完全交给系统层 delivery 配置，AI只负责生成内容
- 磁盘使用率：84%（04-11）→ 53%（04-17，已清理6G）

## 教训与经验

1. **cron投递：系统层delivery vs 手动message** — 隔离会话没有对话上下文，手动调message会缺target报错。正确做法：`delivery.mode=announce` + 正确的channel/to/accountId，让系统自动投递，AI只输出内容
2. **cron任务创建后必须验证投递** — 不加accountId的微信任务会静默失败
3. **修复问题以不重启为第一目标** — 配置文件修改后cron下次执行会重新读取，不需要重启网关
4. **第一性原理思考** — 不要头痛医头，先拆解到根本原因再行动
5. **memory日志文件名是 `YYYY-MM-DD-主题.md`** — 不是纯日期.md（虽然也有纯日期的）
6. **Google在腾讯云IP被封锁** — 用scrapling+patchright绕过，需xvfb-run
7. **站会数据源要多样化** — 不能只靠memory日志，cron执行记录也是有效数据源
8. **cron run日志是覆盖写入** — 每次执行覆盖同一jsonl文件，无法回溯历史。只有最近一次执行的记录
9. **memory日志要当天写** — 拖到补写时已丢失上下文，补写的日志信息密度极低（04-14~04-21就是教训）

## 待办/长期项目

- [ ] 持续维护memory日志（**对话结束后立即写**，不拖延）
- [ ] MEMORY.md定期更新（每周整理一次）
- [ ] 考虑在HEARTBEAT中增加memory日志检查：当天无日志则提醒自己写
- [x] OpenClaw安全检查投递问题已彻底解决（2026-04-11），后取消该任务
- [x] 磁盘清理（84%→53%，04-17清理6G：pnpm store、npm cache、apt cache、journal日志）
- [ ] WAF绕过技能法律使用边界待明确
- [x] 新闻聚合技能需要更多数据源验证（04-17：9个源已验证，日常推送稳定运行）
