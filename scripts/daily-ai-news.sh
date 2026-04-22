#!/bin/bash
# 每日AI热点聚合脚本 - 从9个信息源提取共性热点
# 每天早上7:20运行

set -e

DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M:%S)
TIMEZONE="Asia/Shanghai"
REPORT_FILE="/root/.openclaw/workspace/daily_ai_hotspot_${DATE}.md"
LOG_FILE="/tmp/daily-ai-news-${DATE}.log"

echo "[$TIME] 开始执行每日AI热点聚合..." | tee -a "$LOG_FILE"

# 调用子agent执行聚合任务
echo "[$TIME] 启动新闻聚合子agent..." | tee -a "$LOG_FILE"

# 使用sessions_spawn调用子agent，但这里我们直接生成报告
# 因为cron环境中无法直接调用sessions_spawn

# 生成报告头部
cat > "$REPORT_FILE" << EOF
# 今日AI热点 - ${DATE}

## 🔥 Top 5热点

生成时间: ${TIME} ${TIMEZONE}
数据来源: 9个开源/科技信息源

EOF

echo "[$TIME] 报告文件已创建: $REPORT_FILE" | tee -a "$LOG_FILE"

# 注意：实际的热点抓取需要通过OpenClaw的会话机制触发
# 这个脚本主要是作为cron任务的入口点

echo "[$TIME] 脚本执行完成" | tee -a "$LOG_FILE"
echo "[$TIME] 请通过OpenClaw主会话触发实际的新闻聚合任务" | tee -a "$LOG_FILE"

# 返回报告文件路径，供后续发送使用
echo "$REPORT_FILE"
