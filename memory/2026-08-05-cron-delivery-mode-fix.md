# 2026-08-05 cron投递模式批量修复

## 问题
用户反馈今日推送没收到。排查发现：
- AI HOT日报(06:50) 内容生成成功但 deliveryStatus=not-delivered
- 大盘日报(07:00) 投递报错 ret=-2 prepare failed (context_token过期)
- 其余任务还没到执行时间

## 根因
检查 `/root/.openclaw/cron/jobs.json` 发现7个cron任务中6个 `delivery.mode=none`，只有大盘日报是 `announce`。

mode=none 意味着系统不做投递，完全靠AI在隔离会话调message工具或deliver.py脚本——这条路径从04月到07月反复证明不可靠（MEMORY.md教训#1）。

大盘日报虽然mode=announce，但遇到了context_token 24h过期(ret=-2)，sendWithFallback降级可能在announce路径没生效。

## 修复
1. 6个mode=none的任务全部改成 announce + bestEffort=false + failureAlert.after=1
2. 手动补发今日AI HOT日报和大盘日报（分2段发送）

## 后续观察
- 明天(08-06)各任务是否正常通过announce投递
- 大盘日报的context_token过期问题是否在announce路径有降级逻辑——如果没有，下周可能再次失败
- 需要确认：deliver.py脚本是否还需要保留在prompt中（announce模式下应该不需要了，但保留作为fallback不会有害）
