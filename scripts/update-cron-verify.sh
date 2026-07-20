#!/bin/bash
# 批量更新 cron 任务：delivery.mode=off + prompt 追加投递验证逻辑
# 验证逻辑：AI 生成内容后用 message 工具发送，然后检查日志确认

set -euo pipefail

VERIFY_PROMPT='

## 投递验证（必须执行，不可跳过）
内容生成完毕后，按以下步骤投递并验证：

1. 用 message 工具发送内容（action=send, channel=openclaw-weixin），如内容超过500字则分2段发送
2. 发送后执行：sleep 5 && grep "text sent OK" /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log | tail -5
3. 如果日志中有发送时间附近的 "text sent OK" → 投递成功，输出 ✅ 已验证投递
4. 如果没有 "text sent OK" → 等60秒后重试发送
5. 最多重试3次（第1次 + 2次重试）
6. 3次都失败 → 输出 ❌ 投递失败，请检查

注意：不要依赖系统的 delivery 机制，自己用 message 工具发。'

echo "Updating cron jobs..."

# 获取所有需要更新的任务（除了 Git 同步和推送检查）
JOBS=$(openclaw cron list --json 2>&1 | python3 -c "
import json, sys
data = json.load(sys.stdin)
for job in data.get('jobs', []):
    name = job.get('name', '')
    jid = job.get('id', '')
    # 排除 Git 同步和推送检查（这两个不需要消息投递验证）
    if 'Git' not in name and '推送检查' not in name:
        print(f'{jid}|{name}')
")

echo "$JOBS" | while IFS='|' read -r jid name; do
    echo "Updating: $name ($jid)"
    
    # 获取当前 prompt
    CURRENT=$(openclaw cron list --json 2>&1 | python3 -c "
import json, sys
data = json.load(sys.stdin)
for job in data.get('jobs', []):
    if job.get('id') == '$jid':
        msg = job.get('payload', {}).get('message', '')
        # 检查是否已有验证逻辑
        if '投递验证' in msg:
            print('SKIP')
        else:
            print('UPDATE')
        break
")
    
    if [ "$CURRENT" = "SKIP" ]; then
        echo "  → 已有验证逻辑，跳过"
        continue
    fi
    
    echo "  → 需要更新（请手动执行下方命令）"
done

echo ""
echo "=== 由于 openclaw cron edit 不支持追回 prompt，需手动更新每个任务 ==="
