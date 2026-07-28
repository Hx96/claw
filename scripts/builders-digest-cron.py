#!/usr/bin/env python3
"""
AI Builders 每日简报 — Python 编排脚本

流程：
1. 运行 prepare-digest.js 拿原始数据
2. 调 GLM API（OpenAI兼容）让AI筛选+格式化
3. 轮询等待AI返回
4. 通过 openclaw message send 发到微信

确定性编排，不依赖AI是否"乖乖执行prompt里的message调用"。
"""

import json
import subprocess
import sys
import os
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone

# ========== 配置 ==========

DIGEST_SCRIPT = "/root/.openclaw/workspace/skills/follow-builders/scripts/prepare-digest.js"

# GLM API (glmcode, Anthropic兼容接口)
GLM_API_URL = "https://open.bigmodel.cn/api/anthropic/v1/messages"
GLM_API_KEY = "9751f1cd23ea43f1a913b1dd5d97623e.HvJnizl2km8er4rw"
GLM_MODEL = "glm-5.2"

# 超时
AI_TIMEOUT = 120  # 秒
NODE_TIMEOUT = 30  # 秒

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


def call_glm_api(prompt):
    """调用 GLM API (Anthropic兼容)，返回AI生成的文本"""
    log(f"Calling GLM API (model={GLM_MODEL}, Anthropic compat) ...")

    payload = {
        "model": GLM_MODEL,
        "max_tokens": 2000,
        "messages": [
            {"role": "user", "content": prompt}
        ],
    }

    headers = {
        "Content-Type": "application/json",
        "x-api-key": GLM_API_KEY,
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(GLM_API_URL, data=data, headers=headers, method="POST")

    try:
        start = time.time()
        with urllib.request.urlopen(req, timeout=AI_TIMEOUT) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        elapsed = time.time() - start
        # Anthropic 格式: content[0].text
        content_blocks = result.get("content", [])
        content = "\n".join(
            b.get("text", "") for b in content_blocks if b.get("type") == "text"
        )
        usage = result.get("usage", {})
        log(f"GLM API done in {elapsed:.1f}s, tokens={usage}")
        return content
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8")[:500]
        except:
            pass
        log(f"ERROR: GLM API HTTP {e.code}: {body}")
        return None
    except Exception as e:
        log(f"ERROR: GLM API exception: {e}")
        return None


# 注意：不通过 Python 发微信消息。
# cron 任务的 delivery.mode=announce 会自动投递 stdout 最后一行之后的纯文本内容。
# Python 脚本只需把最终简报打印到 stdout，投递交给系统。


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

    # 3. 调AI生成简报
    digest_text = call_glm_api(prompt)
    if not digest_text:
        print("⚠️ AI Builders 简报失败：AI生成异常", file=sys.stderr)
        print("⚠️ AI Builders 简报失败：AI生成异常")
        sys.exit(1)

    # 4. 输出简报到 stdout
    # cron 的 agentTurn prompt 会让AI执行本脚本，然后读取 stdout 投递
    # 这里直接输出纯简报文本
    print(digest_text)
    log("=== Done ===")
    sys.exit(0)


if __name__ == "__main__":
    main()
