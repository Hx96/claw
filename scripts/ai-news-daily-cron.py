#!/usr/bin/env python3
"""
每日 AI 热点推送 — Python 编排脚本

流程：
1. opencli 多源并行抓取（HN / 36Kr / HF trending / Product Hunt）
2. 数据汇总 + 去重
3. 调 openclaw agent 筛选 + 格式化
4. stdout 输出 → cron announce 自动投递
"""

import json
import subprocess
import sys
import os
import time
from datetime import datetime, timezone, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

CST = timezone(timedelta(hours=8))
AGENT_TIMEOUT = 90
OPENCLI_TIMEOUT = 20

# ========== 工具函数 ==========

def log(msg):
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", file=sys.stderr, flush=True)


def run_opencli(args, timeout=OPENCLI_TIMEOUT):
    """运行 opencli 命令，返回解析后的 JSON"""
    cmd = ["opencli"] + args + ["-f", "json"]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
        if result.returncode != 0:
            # opencli 经常把错误写到 stdout，尝试解析
            pass
        out = result.stdout.strip()
        # opencli 会附加 update notice，提取 JSON
        start = out.find('[')
        if start < 0:
            start = out.find('{')
        end = out.rfind(']')
        if end < 0:
            end = out.rfind('}')
        if start >= 0 and end > start:
            try:
                return json.loads(out[start:end + 1])
            except json.JSONDecodeError:
                pass
        return None
    except subprocess.TimeoutExpired:
        log(f"opencli timed out: {' '.join(args)}")
        return None
    except Exception as e:
        log(f"opencli exception: {e}")
        return None


def curl_json(url, timeout=OPENCLI_TIMEOUT):
    """GET URL，返回解析后的 JSON"""
    try:
        result = subprocess.run(
            ["curl", "-sS", "--max-time", str(timeout), url],
            capture_output=True, text=True, timeout=timeout + 5
        )
        if result.returncode != 0:
            return None
        return json.loads(result.stdout)
    except:
        return None


# ========== 数据源 ==========

def fetch_hn():
    """Hacker News 热帖"""
    log("  → HN top ...")
    data = run_opencli(["hackernews", "top", "--limit", "15"])
    if data is None:
        data = []
    items = []
    for item in data:
        items.append({
            "source": "HN",
            "title": item.get("title", ""),
            "url": item.get("url", item.get("link", "")),
            "score": item.get("score", item.get("points", 0)),
            "comments": item.get("comments", item.get("descendants", 0)),
        })
    log(f"  ← HN: {len(items)} items")
    return items


def fetch_36kr():
    """36氪热门"""
    log("  → 36kr ...")
    data = run_opencli(["36kr", "hot", "--limit", "10"])
    if data is None:
        data = []
    items = []
    for item in data:
        items.append({
            "source": "36Kr",
            "title": item.get("title", item.get("name", "")),
            "url": item.get("url", item.get("link", "")),
            "score": item.get("score", item.get("hot", 0)),
            "summary": item.get("summary", item.get("description", ""))[:200],
        })
    log(f"  ← 36Kr: {len(items)} items")
    return items


def fetch_hf_trending():
    """HuggingFace trending models"""
    log("  → HF trending ...")
    data = curl_json("https://huggingface.co/api/trending")
    if data is None:
        return []
    items = []
    # HF trending 返回可能多种格式
    trending_list = data if isinstance(data, list) else data.get("models", data.get("trending", []))
    for item in (trending_list or [])[:10]:
        name = item.get("id", item.get("name", ""))
        likes = item.get("likes", 0)
        downloads = item.get("downloads", item.get("downloadsAllTime", 0))
        items.append({
            "source": "HF",
            "title": f"🤗 {name}",
            "url": f"https://huggingface.co/{name}",
            "score": likes,
            "summary": f"Downloads: {downloads:,} | Likes: {likes}",
        })
    log(f"  ← HF: {len(items)} items")
    return items


def fetch_producthunt():
    """Product Hunt 今日产品"""
    log("  → Product Hunt ...")
    data = run_opencli(["producthunt", "today", "--limit", "10"])
    if data is None:
        data = []
    items = []
    for item in data:
        items.append({
            "source": "PH",
            "title": item.get("name", item.get("title", "")),
            "url": item.get("url", item.get("website", "")),
            "score": item.get("upvotes", item.get("votes", 0)),
            "summary": item.get("tagline", item.get("description", ""))[:200],
        })
    log(f"  ← PH: {len(items)} items")
    return items


# ========== AI 生成 ==========

def build_prompt(all_items):
    """构建给 AI 的筛选 prompt"""
    today = datetime.now(CST).strftime("%Y-%m-%d")
    weekdays = ["一", "二", "三", "四", "五", "六", "日"]
    weekday = weekdays[datetime.now(CST).weekday()]

    # 按来源分组
    by_source = {}
    for item in all_items:
        src = item["source"]
        if src not in by_source:
            by_source[src] = []
        by_source[src].append(item)

    # 构建数据文本
    parts = []
    for src, items in by_source.items():
        parts.append(f"\n### {src}（{len(items)}条）")
        for i, item in enumerate(items, 1):
            title = item["title"]
            score = item.get("score", 0)
            url = item.get("url", "")
            summary = item.get("summary", "")
            line = f"{i}. [{score}] {title}"
            if summary:
                line += f"\n   {summary}"
            if url:
                line += f"\n   🔗 {url}"
            parts.append(line)

    data_text = "\n".join(parts)

    prompt = f"""你是AI日报编辑。以下是今日多个来源的原始数据（{today} 周{weekday}）：

{data_text}

请筛选 8 条最有价值的 AI 相关内容，生成日报。

格式：

📰 AI 日报 | {today} 周{weekday}

① 标题（中文，技术术语保留英文）
1-2句中文摘要
🔗 链接

---

筛选规则：
- 必须与 AI/ML/LLM/Agent/开源模型 相关
- 优先高互动（score 高）的内容
- 同一事件只保留1条，去重
- 没有AI相关内容的来源可以跳过
- 每条必须有URL，不编造

全文1000字以内。直接输出日报全文。"""

    return prompt


def call_agent(prompt):
    """调 openclaw agent 生成日报"""
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
    log("=== 每日 AI 热点 — Python orchestrator ===")

    # 1. 并行拉取多源数据
    all_items = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {
            pool.submit(fetch_hn): "HN",
            pool.submit(fetch_36kr): "36Kr",
            pool.submit(fetch_hf_trending): "HF",
            pool.submit(fetch_producthunt): "PH",
        }
        for future in as_completed(futures):
            src = futures[future]
            try:
                items = future.result()
                all_items.extend(items)
            except Exception as e:
                log(f"  {src} fetch error: {e}")

    log(f"Total items collected: {len(all_items)}")

    if not all_items:
        print("⚠️ AI 日报失败：所有数据源拉取异常")
        sys.exit(1)

    # 2. 构建 prompt
    prompt = build_prompt(all_items)

    # 3. 调 AI 筛选 + 格式化
    report = call_agent(prompt)
    if not report:
        # 降级：输出原始标题列表
        print("⚠️ AI 日报 AI 生成异常，原始数据：")
        for item in sorted(all_items, key=lambda x: x.get("score", 0), reverse=True)[:10]:
            print(f"  · [{item['source']}] {item['title']} → {item.get('url','')}")
        sys.exit(1)

    # 4. Python tokenless 投递（不依赖 JS announce 层）
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from deliver import deliver_text
    ok = deliver_text(report)
    if ok:
        log("=== Done (delivered via tokenless) ===")
        sys.exit(0)
    else:
        log("=== FAILED (tokenless delivery failed) ===")
        sys.exit(1)


if __name__ == "__main__":
    main()
