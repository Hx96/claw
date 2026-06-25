# MEMORY.md - 小马的长期记忆

_上次更新: 2026-06-22_

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

## Heartbeat配置

- **已启用**: 2026-04-29
- every: 2h, target: none, lightContext + isolatedSession
- activeHours: 07:00-23:00 Asia/Shanghai
- 用途：memory日志兜底检查、MEMORY.md周更新
- 之前HEARTBEAT.md写了规则但没配heartbeat字段，等于空文

## 定时任务清单

| 任务名 | 时间 | 状态 |
|--------|------|------|
| 每日AI热点推送 | 07:20 * * * * | ✅ 正常 |
| AI Builders 每日简报 | 07:30 * * * * | ✅ 正常 |
| 每日站会汇报 | 08:00 * * * * | ✅ 正常 |
| 每日推送检查 | 08:10 * * * * | ✅ 正常 |

⚠️ cron run日志每次执行覆盖同一文件，无法回溯历史执行状态


## 已安装的关键技能

- planning-with-files (Manus风格文件规划系统，三文件工作流) — 2026-04-27安装并集成
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

### 2026-05-08
- Heartbeat首次正常触发memory日志检查
- 发现MEMORY.md距上次更新已9天（超7天阈值），执行周更新
- 会话活动：微信对话 + 3个cron任务正常执行（07:20/07:30/08:00）

### 2026-05-09 ~ 05-16
- **05-09**: 常规日，cron正常运行
- **05-11**: 微信用户咨询精神分析话题（经常叹气的心理学解释），综合精神分析理论+现代研究回复
- **05-12**: 分析 GitHub 仓库 lijigang/ljg-skills 全部20个skill，生成分类可视化HTML+PNG发送微信。分类：认知原子(7)/输出铸造(2)/复合工作流(4)/深度分析(5)/系统运维(2)，改造优先级评估完成
- **05-13**: 常规活动
- **05-14**: AI热点推送正常执行，8源110+文章筛选出10条AI热点。当日热点：林俊阳(原阿里通义CTO)新公司$20亿估值、具身智能World Action Model、Token叠加训练效率突破、React被认为过重Python+HTMX主导2026
- **05-15~16**: Heartbeat正常检查，MEMORY.md周更新执行

### 2026-05-18 ~ 05-21
- **05-18**: 苏格拉底式交互写入SOUL.md（六层提问框架+何时给答案规则）；Addy Osmani X Article长文分析("Don't Outsource the Learning"，1376字，AI时代开发者认知退化)
- **05-19**: 每日站会汇报cron正常生成日报；planning-with-files系统运行验证正常；系统整体状态良好
- **05-21**: AI热点推送cron正常执行，8源110+文章，筛选8条。热点：OpenAI离散几何突破(585分)、GitHub VSCode扩展安全漏洞(402分)、Qwen3.7-Max Agent发布(582分)、Google I/O 2026 MCP更新

### 2026-05-27 ~ 05-30
- **05-27**: 所有cron推送正常运行（07:20/07:30/08:00），投递成功率100%。每日推送检查任务(08:10)出现超时错误，需排查timeout参数
- **05-28**: Claude Opus 4.8发布、Anthropic完成$65亿H轮融资。每日推送检查(08:10)再次超时，consecutiveErrors=1
- **05-30**: AI热点推送正常执行，热点：Open Envelope AI Agent团队架构规范、Step 3.7 Flash Agent、Rokid AI眼镜日本众筹纪录、Claude Mythos漏洞挖掘

### 2026-06-01
- AI热点推送执行，8源110+文章筛选8条AI新闻
- 关键热点：Anthropic IPO（商业化里程碑）、豆包付费上线（国内大模型商业化）、Micro-LED+AI眼镜融资、Florida起诉OpenAI
- 推送报告：`/outputs/2026-06-01/final/每日AI热点推送_2026-06-01.md`
- 下次优化方向：并发执行opencli、增加垂直领域信息源、优化相关性筛选算法

### 2026-06-24
- **personal-fit-coach 技能初始化完成**：用户说"fit"即触发此技能
  - Profile: 178cm/30y/M，距骨软骨损伤（核心约束）
  - Goal: 87→75kg，3个月，蛋白质130-150g/天，1700-1900kcal/天
  - 存储路径: `~/.openclaw/workspace/fit-coach/`（统一Git推送，不再用private目录）
  - SKILL.md已修改存储路径，数据已恢复并推送 `git@github.com:Hx96/claw.git`
  - 体重记录: 05-27(87.0)→06-24(87.7)，27天数据
  - 4周周记已完成

### 2026-06-08
- AI Builders每日简报任务超时失败（consecutiveErrors=1）
- 决策：memory日志必须当日记录不拖延，补写日志信息密度极低
- 发现memory日志6月5日、6月6日缺失，需基于cron执行记录补全

### 2026-06-16
- 所有4个cron任务正常运行（07:20/07:30/08:00/08:10），成功率100%
- AI热点：SpaceX $60亿收购Cursor（AI编程领域巨头整合）、本地AI模型体验改善、荷兰GPT-NL模型、Gartner警示40% AI代理面临淘汰、Fluxmail AI邮件助手
- AI Builders简报：Swyx goblingate、Google Gemini测试招募、Codex浏览器功能、Mistral轻量法语模型、2026无服务器与服务器融合
- 下次优化方向：并发执行opencli、增加垂直领域信息源、优化相关性筛选算法

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
10. **planning-with-files集成** — 安装技能(v2.26.1)，集成到AGENTS.md：Session启动检查、复杂任务自动规划、对话结束双重检查(planning+memory)
11. **heartbeat必须配置** — HEARTBEAT.md写了规则但openclaw.json没heartbeat字段，等于空文。配置和运行机制必须同时存在
12. **技能数据存储用workspace目录** — personal-fit-coach最初用private目录，导致不在Git追踪范围内无法同步。改到 `workspace/fit-coach/` 统一管理

## 待办/长期项目

- [x] 持续维护memory日志（**对话结束后立即写**，不拖延）— 已写入AGENTS.md强制规则
- [x] MEMORY.md定期更新（每周整理一次）— 已写入HEARTBEAT.md周一检查
- [x] HEARTBEAT中增加memory日志检查 — 已配置，每次心跳自动检查当天日志
- [x] 安装planning-with-files技能并集成到工作流 — 三文件规划系统+双重检查机制
- [x] OpenClaw安全检查投递问题已彻底解决（2026-04-11），后取消该任务
- [x] 磁盘清理（84%→53%，04-17清理6G：pnpm store、npm cache、apt cache、journal日志）
- [ ] WAF绕过技能法律使用边界待明确
- [ ] ljg-skills改造可行性待用户确认优先级（高：rank/paper/think/card）
- [x] 新闻聚合技能需要更多数据源验证（04-17：9个源已验证，日常推送稳定运行）
