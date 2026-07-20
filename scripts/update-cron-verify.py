#!/usr/bin/env python3
"""批量更新 cron 任务：追加投递验证逻辑 + delivery.mode=off"""
import subprocess, json, sys

VERIFY_SUFFIX = """

## 投递验证（必须执行，不可跳过）
内容生成完毕后，按以下步骤投递并验证：

1. 用 message 工具发送内容（action=send, channel=openclaw-weixin），如内容超过500字则分2段发送
2. 发送后执行：sleep 5 && grep "text sent OK" /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log | tail -5
3. 如果日志中有刚发送时间附近的 "text sent OK" → 投递成功，输出 ✅ 已验证投递
4. 如果没有 "text sent OK" → 等60秒后用 message 工具重试发送
5. 最多重试3次（第1次 + 2次重试）
6. 3次都失败 → 输出 ❌ 投递失败，请检查

注意：不要依赖系统的 delivery 机制，自己用 message 工具发。不要输出"系统自动投递"。"""

# 跳过不需要消息验证的任务
SKIP_NAMES = {"每日站会Git同步", "每日推送检查"}

def get_jobs():
    result = subprocess.run(["openclaw", "cron", "list", "--json"], 
                          capture_output=True, text=True)
    return json.loads(result.stdout).get("jobs", [])

def update_job(job):
    jid = job["id"]
    name = job["name"]
    msg = job.get("payload", {}).get("message", "")
    
    if name in SKIP_NAMES:
        print(f"⏭️  跳过: {name}")
        return
    
    if "投递验证" in msg:
        print(f"✅ 已有验证逻辑: {name}")
        return
    
    new_msg = msg + VERIFY_SUFFIX
    
    # 用 openclaw cron edit 更新 message 和 delivery
    cmd = [
        "openclaw", "cron", "edit", jid,
        "--message", new_msg,
        "--no-deliver",  # delivery.mode = off
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    
    if result.returncode == 0:
        print(f"✅ 更新成功: {name}")
    else:
        print(f"❌ 更新失败: {name}")
        print(f"   stderr: {result.stderr[:200]}")

def main():
    jobs = get_jobs()
    print(f"共 {len(jobs)} 个任务\n")
    
    for job in jobs:
        try:
            update_job(job)
        except Exception as e:
            print(f"❌ 异常: {job['name']}: {e}")
    
    print("\n=== 验证结果 ===")
    jobs2 = get_jobs()
    for job in jobs2:
        name = job["name"]
        mode = job.get("delivery", {}).get("mode", "N/A")
        msg = job.get("payload", {}).get("message", "")
        has_verify = "投递验证" in msg
        print(f"  {name}: delivery.mode={mode}, has_verify={has_verify}")

if __name__ == "__main__":
    main()
