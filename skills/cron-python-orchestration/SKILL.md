---
name: cron-python-orchestration
description: 定时任务Python编排模式。当涉及"定时任务"、"cron编排"、"Python编排"、"确定性投递"、"cron投递失败"、"定时推送"、"cron任务"等关键词时触发。解决隔离会话中AI调message工具不可靠的问题，用Python脚本做确定性编排。
---

# 定时任务 Python 编排模式

> **核心问题：** cron隔离会话里让AI手动调message工具不可靠——AI可能不执行、参数错误、或消息被微信折叠/吞掉。反复踩坑10+次（04月~07月）。
>
> **最终方案：** Python脚本做确定性编排（拉数据+调AI生成+输出结果），投递交给cron系统层announce。

---

## 架构对比

### ❌ 旧方案（不可靠）

```
cron触发 → AI隔离会话
  → AI执行数据拉取
  → AI格式化内容
  → AI手动调message工具发送  ← 这一步不可靠！
→ 微信
```

**失败原因：**
- AI在隔离会话中不一定执行prompt里的message调用
- 即使返回messageId，消息可能被微信折叠/吞掉
- `delivery.mode=none` + 手动message = 无系统层保障

### ✅ 新方案（Python编排 + announce投递）

```
cron触发(agentTurn) → AI隔离会话
  → AI用exec执行: python3 /path/to/script.py
  → Python脚本内部:
     ① subprocess拉数据（确定性）
     ② subprocess调 openclaw agent --agent main 生成内容（借用自身AI能力）
     ③ 解析JSON结果，print到stdout
  → AI原样输出脚本结果
→ cron delivery.mode=announce 系统层投递 → 微信
```

**可靠性保障：**
- Python脚本做编排，不依赖AI是否"乖乖执行message调用"
- 投递由cron系统层announce负责，AI只生成内容
- `bestEffort=false` + `failureAlert.after=1` 确保失败即告警

---

## 关键配置

### cron任务模板

```bash
openclaw cron add \
  --name "任务名" \
  --cron "0 8 * * *" \
  --tz "Asia/Shanghai" \
  --exact \
  --session isolated \
  --wake now \
  --light-context \
  --timeout-seconds 180 \
  --message "执行 Python 脚本生成内容，然后直接输出脚本结果：

\`\`\`
python3 /path/to/script.py
\`\`\`

脚本会自动完成数据拉取和内容生成。你只需要：
1. 用 exec 工具执行上面的命令
2. 读取 stdout 输出
3. 直接原样输出脚本打印的正文（不要添加任何额外内容）

不要调用 message 工具，不要执行 git 操作，不要添加额外评论。" \
  --announce \
  --channel openclaw-weixin \
  --to "{user_wechat_id}" \
  --account "{account_id}" \
  --no-best-effort-deliver \
  --failure-alert \
  --failure-alert-after 1 \
  --failure-alert-channel openclaw-weixin \
  --failure-alert-to "{user_wechat_id}" \
  --failure-alert-account-id "{account_id}"
```

### ⚠️ 不可省略的字段

| 字段 | 值 | 原因 |
|------|-----|------|
| `delivery.mode` | `announce` | 系统层投递，唯一可靠方式 |
| `delivery.bestEffort` | `false` | 投递失败=任务失败，不留暗坑 |
| `failureAlert.after` | `1` | 失败立即告警 |
| `payload.lightContext` | `true` | 轻量上下文，减少token消耗 |
| prompt中**不能**有`message(action="send"...)`指令 | — | AI在隔离会话调message不可靠 |

---

## Python编排脚本模板

```python
#!/usr/bin/env python3
"""
任务名 — Python 编排脚本

流程：
1. 拉取数据（确定性）
2. 调 openclaw agent 生成内容（借用自身AI对话能力，不用外部API）
3. 输出结果到 stdout，cron announce 自动投递
"""

import json
import subprocess
import sys
import time
from datetime import datetime, timezone


# ========== 配置 ==========
DATA_SCRIPT = "/path/to/data-fetch.js"  # 数据拉取脚本
AGENT_TIMEOUT = 90    # openclaw agent 超时秒数
NODE_TIMEOUT = 30     # 数据拉取超时秒数


# ========== 工具函数 ==========

def log(msg):
    """日志输出到 stderr，不污染 stdout"""
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", file=sys.stderr, flush=True)


def fetch_data():
    """运行数据拉取脚本，返回解析后的JSON"""
    log("Fetching data ...")
    try:
        result = subprocess.run(
            ["node", DATA_SCRIPT],
            capture_output=True, text=True,
            timeout=NODE_TIMEOUT
        )
        if result.returncode != 0:
            log(f"ERROR: data script failed: {result.stderr[:500]}")
            return None
        data = json.loads(result.stdout)
        log(f"Data OK")
        return data
    except Exception as e:
        log(f"ERROR: {e}")
        return None


def build_prompt(data):
    """从数据构建给AI的prompt"""
    # 根据具体任务实现
    return f"根据以下数据生成内容：\n{json.dumps(data, ensure_ascii=False)}"


def call_agent(prompt):
    """调用 openclaw agent（自身AI对话能力），返回生成的文本"""
    log("Calling openclaw agent ...")
    cmd = [
        "openclaw", "agent",
        "--agent", "main",
        "--message", prompt,
        "--json",
        "--timeout", str(AGENT_TIMEOUT),
    ]
    try:
        start = time.time()
        result = subprocess.run(
            cmd, capture_output=True, text=True,
            timeout=AGENT_TIMEOUT + 30,
        )
        elapsed = time.time() - start
        if result.returncode != 0:
            stderr_tail = result.stderr[-500:] if result.stderr else ""
            log(f"ERROR: agent exited {result.returncode}")
            log(f"  stderr: {stderr_tail}")
            return None
        resp = json.loads(result.stdout)
        payloads = resp.get("result", {}).get("payloads", [])
        if not payloads:
            log("ERROR: no payloads in response")
            return None
        text = payloads[0].get("text", "").strip()
        log(f"Agent done in {elapsed:.1f}s")
        return text if text else None
    except Exception as e:
        log(f"ERROR: {e}")
        return None


# ========== 主流程 ==========

def main():
    log("=== Task Start ===")

    # 1. 拉数据
    data = fetch_data()
    if not data:
        print("⚠️ 任务失败：数据拉取异常")
        sys.exit(1)

    # 2. 构建prompt
    prompt = build_prompt(data)

    # 3. 调AI生成内容
    content = call_agent(prompt)
    if not content:
        print("⚠️ 任务失败：AI生成异常")
        sys.exit(1)

    # 4. 输出到stdout（cron announce自动投递）
    print(content)
    log("=== Done ===")
    sys.exit(0)


if __name__ == "__main__":
    main()
```

---

## 实战案例：AI Builders 每日简报

### 脚本位置
`/root/.openclaw/workspace/scripts/builders-digest-cron.py`

### cron配置（关键字段）
```json
{
  "name": "AI Builders 每日简报",
  "schedule": {"kind": "cron", "expr": "0 8 * * *"},
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "执行 python3 /root/.openclaw/workspace/scripts/builders-digest-cron.py，原样输出结果。不要调message工具。",
    "timeoutSeconds": 120,
    "lightContext": true
  },
  "delivery": {
    "mode": "announce",
    "channel": "openclaw-weixin",
    "to": "o9cq80_r2wmTBUtFu0AJ6T-jxK68@im.wechat",
    "accountId": "999559c28b26-im-bot",
    "bestEffort": false
  },
  "failureAlert": {"after": 1, "channel": "openclaw-weixin", ...}
}
```

### 执行时序（实测）
```
T+0s    cron触发，AI隔离会话启动
T+1s    AI执行 exec("python3 builders-digest-cron.py")
T+2s    Python: subprocess运行 node prepare-digest.js
T+5s    Python: 数据拉取完成
T+5s    Python: subprocess调 openclaw agent --agent main
T+68s   Python: agent返回简报文本
T+69s   Python: print简报到stdout
T+70s   AI: 读取stdout，原样输出
T+79s   cron: announce投递到微信
T+80s   ✅ 用户收到消息
```

---

## cron投递方案选型历史（血泪教训）

| 日期 | 方案 | 结果 |
|------|------|------|
| 04-11 | `delivery.mode=announce` | ✅ 首次验证通过 |
| 06-30 | `delivery.mode=none` + AI分段调message | ⚠️ 短期有效，后期失败 |
| 07-21 | `delivery.mode=announce` | ✅ 再次验证通过 |
| 07-27 | `delivery.mode=none` + message带to参数 | ❌ delivered=true但用户收不到 |
| 07-28 | `delivery.mode=announce` + Python编排 | ✅ **最终方案** |

**结论：announce是唯一可靠路径。不再尝试任何手动message方案。**

---

## 常见问题排查

### cron任务显示 ok 但用户没收到

1. 检查 `delivery.mode` 是否为 `announce`（不是none/off）
2. 检查 `delivery.bestEffort` 是否为 `false`
3. 检查 `delivery.to` 和 `delivery.accountId` 是否正确
4. 检查 prompt 中是否有手动message指令（有则删除）
5. 用 `openclaw cron run --id {id}` 手动触发验证

### openclaw CLI 被插件阻塞

```
[plugins] qqbot missing register/activate export
```

解决方案：在 openclaw.json 中禁用问题插件
```python
d['plugins']['entries']['qqbot']['enabled'] = False
```

### openclaw agent 命令

```bash
# 从CLI跑一轮AI对话（拿JSON结果）
openclaw agent --agent main --message "..." --json --timeout 90

# 返回格式
# resp.result.payloads[0].text = AI生成的文本
# resp.result.meta.agentMeta.model = 使用的模型
# resp.result.meta.agentMeta.usage = token用量
```

---

## 适用场景

- ✅ 需要拉取数据 + AI格式化的定时推送（新闻、简报、日报）
- ✅ 投递可靠性要求高的场景
- ✅ 不想依赖外部API，只用openclaw自身能力
- ❌ 不适用于纯提醒类任务（直接用cron agentTurn + announce即可）
- ❌ 不适用于需要多轮对话的场景（agent是单轮）
