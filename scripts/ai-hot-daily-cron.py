#!/usr/bin/env python3
"""
AI HOT 每日推送 — Python 编排脚本

流程：
1. curl aihot.virxact.com API 拉取精选 + 热点
2. 调 openclaw agent 格式化简报
3. stdout 输出 → cron announce 自动投递
"""

import json
import subprocess
import sys
import os
import time
from datetime import datetime, timezone, timedelta

# ========== 配置 ==========

UA = "aihot-skill/0.3.5 (+https://aihot.virxact.com/aihot-skill/)"
BASE = "https://aihot.virxact.com/api/public"
CST = timezone(timedelta(hours=8))

AGENT_TIMEOUT = 90
CURL_TIMEOUT = 20

# ========== 工具函数 ==========

def log(msg):
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", file=sys.stderr, flush=True)


def curl_json(url, timeout=CURL_TIMEOUT):
    """GET URL，返回解析后的 JSON"""
    try:
        result = subprocess.run(
            ["curl", "-sS", "--max-time", str(timeout),
             "-H", f"User-Agent: {UA}", url],
            capture_output=True, text=True, timeout=timeout + 5
        )
        if result.returncode != 0:
            log(f"curl failed: {url} → rc={result.returncode}")
            return None
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        log(f"JSON parse failed: {url} → {e}")
        return None
    except Exception as e:
        log(f"curl exception: {url} → {e}")
        return None


def fetch_aihot_data():
    """拉取 aihot 精选 + 热点数据"""
    since = (datetime.now(timezone.utc) - timedelta(hours=24))
    since_str = since.strftime("%Y-%m-%dT%H:%M:%SZ")

    log(f"Fetching items since={since_str} ...")
    items = curl_json(f"{BASE}/items?mode=selected&since={since_str}&take=50")
    topics = curl_json(f"{BASE}/hot-topics")

    return {"items": items, "topics": topics}


def build_prompt(data):
    """构建给 AI 的格式化 prompt"""
    items_raw = data.get("items") or {}
    topics_raw = data.get("topics") or {}

    # items 可能是 list 或 dict
    items_list = []
    if isinstance(items_raw, list):
        items_list = items_raw
    elif isinstance(items_raw, dict):
        items_list = items_raw.get("items", []) or items_raw.get("data", [])

    topics_list = []
    if isinstance(topics_raw, list):
        topics_list = topics_raw
    elif isinstance(topics_raw, dict):
        topics_list = topics_raw.get("topics", []) or topics_raw.get("data", [])

    # 构建 items 文本
    items_text_parts = []
    for i, item in enumerate(items_list[:30], 1):
        title = item.get("title", "")
        summary = item.get("summary", item.get("description", ""))[:150]
        url = item.get("url", item.get("link", ""))
        score = item.get("score", item.get("hotness", 0))
        source = item.get("source", "")
        items_text_parts.append(
            f"{i}. [{score}] {title}\n   {summary}\n   🔗 {url}\n   来源: {source}"
        )

    items_text = "\n".join(items_text_parts) if items_text_parts else "无精选数据"

    # 构建 topics 文本
    topics_text_parts = []
    for t in topics_list[:10]:
        name = t.get("name", t.get("title", ""))
        score = t.get("score", t.get("hotness", 0))
        desc = t.get("description", "")[:100]
        topics_text_parts.append(f"- [{score}] {name}: {desc}")

    topics_text = "\n".join(topics_text_parts) if topics_text_parts else "无热点数据"

    today = datetime.now(CST).strftime("%Y-%m-%d")
    weekdays = ["一", "二", "三", "四", "五", "六", "日"]
    weekday = weekdays[datetime.now(CST).weekday()]

    prompt = f"""你是AI资讯编辑。以下是来自 AI HOT (aihot.virxact.com) 的过去24小时数据。

## 精选文章（按热度排序）
{items_text}

## 当前热点话题
{topics_text}

请生成今日 AI 简报，格式如下：

🔥 AI HOT 日报 | {today} 周{weekday}

筛选 5-8 条最重要的 AI 资讯，每条格式：

① 标题（中文，技术术语保留英文）
1句中文摘要（不超过40字）
🔗 链接

最后附"💡 今日亮点"总结1-2句。

规则：
- 全文800字以内
- 不编造内容，只基于上面数据
- 每条必须有URL
- 按重要性排序
- 直接输出简报全文，不加额外说明"""

    return prompt


def call_agent(prompt):
    """调 openclaw agent 生成简报"""
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
            log(f"agent exited {result.returncode}: {stderr_tail}")
            return None

        data = json.loads(result.stdout)
        payloads = data.get("result", {}).get("payloads", [])
        if not payloads:
            log("no payloads in agent response")
            return None

        text = payloads[0].get("text", "").strip()
        if not text:
            log("agent returned empty text")
            return None

        meta = data.get("result", {}).get("meta", {}).get("agentMeta", {})
        log(f"Agent done in {elapsed:.1f}s, model={meta.get('model','?')}")
        return text

    except subprocess.TimeoutExpired:
        log(f"agent timed out after {AGENT_TIMEOUT+30}s")
        return None
    except Exception as e:
        log(f"agent exception: {e}")
        return None


# ========== 主流程 ==========

def main():
    log("=== AI HOT Daily — Python orchestrator ===")

    # 1. 拉数据
    data = fetch_aihot_data()
    if not data.get("items") and not data.get("topics"):
        print("⚠️ AI HOT 日报失败：API 数据拉取异常")
        sys.exit(1)

    # 2. 构建 prompt
    prompt = build_prompt(data)

    # 3. 调 AI 格式化
    report = call_agent(prompt)
    if not report:
        print("⚠️ AI HOT 日报失败：AI生成异常")
        sys.exit(1)

    # 4. stdout 输出，cron announce 自动投递
    print(report)
    log("=== Done ===")
    sys.exit(0)


if __name__ == "__main__":
    main()
