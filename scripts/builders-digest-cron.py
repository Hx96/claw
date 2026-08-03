#!/usr/bin/env python3
"""
AI Builders 每日简报 — Python 编排脚本

流程：
1. 运行 prepare-digest.js 拿原始数据
2. 调 openclaw agent（自身AI对话能力）筛选+格式化
3. 输出结果到 stdout，cron announce 自动投递

确定性编排，不依赖AI是否"乖乖执行prompt里的message调用"。
"""

import json
import subprocess
import sys
import os
import time
from datetime import datetime, timezone

# ========== 配置 ==========

DIGEST_SCRIPT = "/root/.openclaw/workspace/skills/follow-builders/scripts/prepare-digest.js"

# 超时
AGENT_TIMEOUT = 90   # 秒，openclaw agent 超时
NODE_TIMEOUT = 30    # 秒，prepare-digest.js 超时

# ========== 工具函数 ==========

def log(msg):
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def run_digest_script():
    """运行 prepare-digest.js，返回解析后的JSON"""
    log("Running prepare-digest.js ...")
    try:
        result = subprocess.run(
            ["node", DIGEST_SCRIPT],
            capture_output=True, text=True,
            timeout=NODE_TIMEOUT
        )
        if result.returncode != 0:
            log(f"ERROR: digest script failed: {result.stderr[:500]}")
            return None
        data = json.loads(result.stdout)
        log(f"Digest data OK: {data.get('stats', {})}")
        return data
    except subprocess.TimeoutExpired:
        log("ERROR: digest script timed out")
        return None
    except json.JSONDecodeError as e:
        log(f"ERROR: digest JSON parse failed: {e}")
        return None
    except Exception as e:
        log(f"ERROR: digest script exception: {e}")
        return None


def build_ai_prompt(digest_data):
    """从 digest 数据构建给AI的 prompt"""
    # 提取 tweets
    x_items = digest_data.get("x", [])
    podcasts = digest_data.get("podcasts", [])

    # 构建 content 文本
    content_parts = []
    for builder in x_items:
        name = builder.get("name", "Unknown")
        handle = builder.get("handle", "")
        for tweet in builder.get("tweets", []):
            likes = tweet.get("likes", 0)
            text = tweet.get("text", "")
            url = tweet.get("url", "")
            content_parts.append(
                f"Builder: {name} (@{handle})\n"
                f"Likes: {likes}\n"
                f"Tweet: {text}\n"
                f"URL: {url}\n"
            )

    for pod in podcasts:
        title = pod.get("title", "")
        name = pod.get("name", "")
        url = pod.get("url", "")
        content_parts.append(
            f"Podcast: {title} by {name}\nURL: {url}\n"
        )

    content = "\n---\n".join(content_parts) if content_parts else "No content available"

    prompt = f"""你是 AI 行业资讯编辑。以下是今日 AI Builders 动态数据，请筛选 4-6 条最有价值的内容。

每条格式（中英对照）：
**姓名 身份** (❤️点赞数)
English: > 最关键1句，最长110字符
中文：1句中文概括，不超过32字
🔗 链接

规则：
- 每条必须有URL，不编造
- 技术术语保留英文
- 总长度1500字以内
- 按点赞数排序，优先高互动内容
- 最后加一行总结今日亮点

数据：
{content}

直接输出简报全文。"""

    return prompt


def call_claude_agent(prompt):
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
            cmd,
            capture_output=True, text=True,
            timeout=AGENT_TIMEOUT + 30,  # 额外30s缓冲
        )
        elapsed = time.time() - start

        if result.returncode != 0:
            # 提取有用错误信息
            stderr_tail = result.stderr[-500:] if result.stderr else ""
            stdout_tail = result.stdout[-500:] if result.stdout else ""
            log(f"ERROR: openclaw agent exited {result.returncode}")
            log(f"  stderr: {stderr_tail}")
            log(f"  stdout: {stdout_tail}")
            return None

        data = json.loads(result.stdout)
        result_meta = data.get("result", {})
        payloads = result_meta.get("payloads", [])
        if not payloads:
            log("ERROR: no payloads in agent response")
            return None

        text = payloads[0].get("text", "")
        meta = result_meta.get("meta", {})
        agent_meta = meta.get("agentMeta", {})
        model = agent_meta.get("model", "?")
        usage = agent_meta.get("usage", {})
        log(f"Agent done in {elapsed:.1f}s, model={model}, tokens={usage}")

        if not text.strip():
            log("ERROR: agent returned empty text")
            return None

        return text.strip()

    except subprocess.TimeoutExpired:
        log(f"ERROR: openclaw agent timed out after {AGENT_TIMEOUT+30}s")
        return None
    except json.JSONDecodeError as e:
        log(f"ERROR: agent JSON parse failed: {e}")
        log(f"  stdout tail: {result.stdout[-300:]}")
        return None
    except Exception as e:
        log(f"ERROR: openclaw agent exception: {e}")
        return None


# ========== 主流程 ==========

def main():
    log("=== AI Builders Daily Digest — Python orchestrator ===")

    # 1. 拉数据
    digest_data = run_digest_script()
    if not digest_data:
        # 输出到 stderr，stdout 输出错误消息让 announce 投递
        print("⚠️ AI Builders 简报失败：数据拉取异常", file=sys.stderr)
        print("⚠️ AI Builders 简报失败：数据拉取异常")
        sys.exit(1)

    # 2. 构建prompt
    prompt = build_ai_prompt(digest_data)

    # 3. 调 openclaw agent 生成简报（借用自身AI对话能力）
    digest_text = call_claude_agent(prompt)
    if not digest_text:
        print("⚠️ AI Builders 简报失败：AI生成异常", file=sys.stderr)
        print("⚠️ AI Builders 简报失败：AI生成异常")
        sys.exit(1)

    # 4. Python tokenless 投递（不依赖 JS announce 层）
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from deliver import deliver_text
    ok = deliver_text(digest_text)
    if ok:
        log("=== Done (delivered via tokenless) ===")
        sys.exit(0)
    else:
        log("=== FAILED (tokenless delivery failed) ===")
        sys.exit(1)


if __name__ == "__main__":
    main()
