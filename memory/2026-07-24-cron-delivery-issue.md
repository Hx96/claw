# 2026-07-24 cron投递问题再次复发

## 问题
- 用户反馈今天没收到任何推送
- 3个cron任务（06:50 AI HOT / 07:01 大盘日报 / 07:30 AI热点）全部正常执行
- 系统记录 delivered=True，但微信侧未收到
- 这是 07-21 修复方案（delivery.mode=announce + bestEffort=false）后问题再次复发

## 处理
- 手动通过 message 工具补发3条推送（AI热点 / 大盘日报 / AI HOT）
- 手动发送内容压缩为短版本

## 排查方向（下次跟进）
- cron announce 投递路径 vs 手动 message 工具投递路径的差异
- 微信API是否对 cron 自动消息有额外限制
- gateway日志几乎为空（今天仅2行），无法追踪投递细节
- 可能需要开启更详细的日志级别

## 教训更新
- 07-21方案（announce + bestEffort=false）不是万能的
- delivered=True 依然不可信
- 问题可能是微信侧的展示/折叠机制，而非投递失败
