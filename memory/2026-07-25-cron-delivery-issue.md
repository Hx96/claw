# 2026-07-25 cron投递问题再次出现

## 现象
- 用户反馈"今日任务没收到"
- 7个cron任务全部 lastRunStatus=ok, delivered=true
- 但用户微信侧一条没收到
- 网关日志文件(/tmp/openclaw/openclaw-2026-07-25.log)只有867字节，仅记录用户消息，无cron投递日志

## 排查
- cron执行记录正常，内容生成正常
- 系统层delivery状态显示delivered
- 手动用message工具补发3条（AI HOT精选、AI日报、AI Builders简报）
- 等待用户确认手动发送是否收到

## 可能原因
1. 微信限流：7条消息在110分钟内集中投递
2. 微信折叠机制
3. access_token问题

## 待确认
- 用户是否收到手动补发的消息
- 如果手动能收到 → 问题是cron投递时序
- 如果手动也收不到 → 问题是微信通道层
