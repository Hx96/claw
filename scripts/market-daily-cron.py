#!/usr/bin/env python3
"""
每日大盘日报 — Python 编排脚本

流程：
1. 调 us_market_report_v3.py 获取美股数据
2. 调 cn_market_report.py 获取 A 股数据（JSON）
3. web_fetch multpl.com 获取估值数据（PE/CAPE/股息率/PB）
4. 读格雷厄姆 SKILL.md 作为风格 prompt
5. 调 openclaw agent 生成全球大盘日报
6. stdout 输出 → cron announce 自动投递
"""

import json
import subprocess
import sys
import os
import time
from datetime import datetime, timezone, timedelta

CST = timezone(timedelta(hours=8))
AGENT_TIMEOUT = 120
SCRIPTS_DIR = "/root/.openclaw/workspace/skills/stock-market-pro/scripts"
GRAHAM_SKILL = "/root/.openclaw/workspace/.claude/skills/benjamin-graham-perspective/SKILL.md"

# ========== 工具函数 ==========

def log(msg):
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", file=sys.stderr, flush=True)


def run_script(cmd, timeout=30):
    """运行子脚本，返回 stdout"""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
        if result.returncode != 0:
            log(f"script failed: {' '.join(cmd)} → rc={result.returncode}")
            log(f"  stderr: {result.stderr[-300:]}")
            return None
        return result.stdout
    except subprocess.TimeoutExpired:
        log(f"script timed out: {' '.join(cmd)}")
        return None
    except Exception as e:
        log(f"script exception: {e}")
        return None


def fetch_url(url, timeout=15):
    """用 web_fetch 拉取网页（通过 openclaw agent 工具不行，这里用 curl）"""
    try:
        result = subprocess.run(
            ["curl", "-sL", "--max-time", str(timeout), url],
            capture_output=True, text=True, timeout=timeout + 5
        )
        if result.returncode != 0:
            return None
        # 简单提取数字
        return result.stdout
    except:
        return None


def extract_number(html, pattern):
    """从 HTML 中提取第一个匹配的数字"""
    import re
    m = re.search(pattern, html)
    if m:
        try:
            return float(m.group(1))
        except:
            pass
    return None


# ========== 数据获取 ==========

def fetch_us_market():
    """美股数据：直接调 us_market_report_v3.py"""
    log("Fetching US market data ...")
    out = run_script(
        ["python3", f"{SCRIPTS_DIR}/us_market_report_v3.py"],
        timeout=30
    )
    return out  # 返回格式化文本


def fetch_cn_market():
    """A 股数据：调 cn_market_report.py，返回 JSON"""
    log("Fetching CN market data ...")
    out = run_script(
        ["python3", f"{SCRIPTS_DIR}/cn_market_report.py"],
        timeout=45
    )
    if not out:
        return None
    try:
        return json.loads(out)
    except json.JSONDecodeError as e:
        log(f"CN market JSON parse failed: {e}")
        return None


def fetch_valuation():
    """从 multpl.com 提取估值数据"""
    log("Fetching valuation data ...")
    val = {}

    # PE (TTM)
    html = fetch_url("https://www.multpl.com/s-p-500-pe-ratio")
    if html:
        val["pe_ttm"] = extract_number(html, r'"currentValue">([\d.]+)')
        val["pe_avg"] = extract_number(html, r'"historicalAvg">([\d.]+)')

    # CAPE (Shiller PE)
    html = fetch_url("https://www.multpl.com/shiller-pe")
    if html:
        val["cape"] = extract_number(html, r'"currentValue">([\d.]+)')

    # 股息率
    html = fetch_url("https://www.multpl.com/s-p-500-dividend-yield")
    if html:
        val["div_yield"] = extract_number(html, r'"currentValue">([\d.]+)')

    # PB
    html = fetch_url("https://www.multpl.com/s-p-500-price-to-book")
    if html:
        val["pb"] = extract_number(html, r'"currentValue">([\d.]+)')

    # 过滤 None
    val = {k: v for k, v in val.items() if v is not None}
    if not val:
        log("WARNING: no valuation data extracted")
    else:
        log(f"Valuation: {val}")

    return val


# ========== AI 生成 ==========

def format_cn_market_text(cn_data):
    """把 A 股 JSON 数据格式化成文本"""
    if not cn_data:
        return "A 股数据获取失败"

    lines = []

    # 宽基指数
    indices = cn_data.get("indices", [])
    if indices:
        lines.append("=== A股宽基指数 ===")
        for idx in indices:
            name = idx.get("name", "")
            price = idx.get("price", 0)
            pct = idx.get("change_pct", 0)
            sign = "+" if pct > 0 else ""
            lines.append(f"  {name}: {price:,.2f} ({sign}{pct:.2f}%)")
        lines.append("")

    # 港股
    hk = cn_data.get("hk_indices", [])
    if hk:
        lines.append("=== 港股指数 ===")
        for h in hk[:3]:
            name = h.get("name", "")
            price = h.get("price", 0)
            pct = h.get("change_pct", 0)
            sign = "+" if pct > 0 else ""
            lines.append(f"  {name}: {price:,.2f} ({sign}{pct:.2f}%)")
        lines.append("")

    # 行业板块
    sectors = cn_data.get("sectors", {})
    top5 = sectors.get("top5", [])
    bottom5 = sectors.get("bottom5", [])
    if top5:
        lines.append("=== 行业涨幅 Top5 ===")
        for s in top5[:3]:
            name = s.get("name", "")
            pct = s.get("change_pct", 0)
            leader = s.get("leader", "")
            lines.append(f"  {name} {pct:+.2f}% (领涨: {leader})")
        lines.append("")
    if bottom5:
        lines.append("=== 行业跌幅 Top5 ===")
        for s in bottom5[:3]:
            name = s.get("name", "")
            pct = s.get("change_pct", 0)
            lines.append(f"  {name} {pct:+.2f}%")
        lines.append("")

    # 新闻
    news = cn_data.get("news", [])
    if news:
        lines.append("=== 财经要闻（前15条）===")
        for n in news[:15]:
            title = n.get("title", "")
            lines.append(f"  · {title}")
        lines.append("")

    return "\n".join(lines)


def build_prompt(us_text, cn_text, valuation, graham_skill):
    """构建给 AI 的格雷厄姆式日报 prompt"""
    today = datetime.now(CST).strftime("%Y-%m-%d")
    weekdays = ["一", "二", "三", "四", "五", "六", "日"]
    weekday = weekdays[datetime.now(CST).weekday()]

    val_text = ""
    if valuation:
        parts = []
        if "pe_ttm" in valuation:
            parts.append(f"PE(TTM)={valuation['pe_ttm']}")
        if "cape" in valuation:
            parts.append(f"CAPE(Shiller)={valuation['cape']}")
        if "div_yield" in valuation:
            parts.append(f"股息率={valuation['div_yield']}%")
        if "pb" in valuation:
            parts.append(f"PB={valuation['pb']}")
        val_text = " | ".join(parts)
    else:
        val_text = "估值数据获取失败"

    prompt = f"""你是本杰明·格雷厄姆，《聪明的投资者》作者。以下是你内化的思维框架：

{graham_skill[:3000]}

---

## 今日市场数据（{today} 周{weekday}）

### 估值指标
{val_text}

### 美股数据
{us_text}

### A股数据
{cn_text}

---

请以格雷厄姆的视角和语气，生成每日全球大盘日报。

格式：

📊 每日全球大盘日报 | {today} 周{weekday}

【美股市场】
1. 市场温度计（PE/CAPE/股息率 vs 债券收益率，给出高估/合理/低估判定）
2. 美股指数概览（道琼斯/标普/纳指/VIX/美债/黄金）
3. 资产配置建议（25%-75%股债规则）
4. 格雷厄姆式提醒（一句干冷反讽）

【A股市场】
1. A股宽基指数（上证/深证/创业板/科创50/沪深300/中证500/中证1000/上证50）
2. 港股指数（恒生/恒生科技）
3. 行业板块热力（涨幅Top3 + 跌幅Top3，附领涨股）
4. 影响盘面的关键消息（筛选5-8条，分利好/利空）
5. 格雷厄姆视角点评

## 要求
- 美股用格雷厄姆语气：定义先行、数据驱动、干冷学术反讽
- A股适配中国市场特色但保持格雷厄姆框架
- 聚焦宽基指数，不分析个股
- 全文1200字以内
- 直接输出报告全文，不加任何前言、自我介绍或解释性语句
- 不要输出"我以格雷厄姆的视角"之类的开场白，直接输出"📊 每日全球大盘日报"""

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
    log("=== 每日大盘日报 — Python orchestrator ===")

    # 1. 并行/顺序拉数据
    us_text = fetch_us_market()
    if not us_text:
        us_text = "美股数据获取失败"

    cn_data = fetch_cn_market()
    cn_text = format_cn_market_text(cn_data)

    valuation = fetch_valuation()

    # 2. 读格雷厄姆 skill
    graham_skill = ""
    try:
        with open(GRAHAM_SKILL, "r") as f:
            graham_skill = f.read()
    except Exception as e:
        log(f"WARNING: cannot read graham skill: {e}")

    # 3. 构建 prompt
    prompt = build_prompt(us_text, cn_text, valuation, graham_skill)

    # 4. 调 AI 生成
    report = call_agent(prompt)
    if not report:
        # 降级：直接输出原始数据
        print("⚠️ 大盘日报 AI 生成异常，原始数据如下：")
        print(f"\n{us_text}\n")
        print(cn_text)
        sys.exit(1)

    # 5. Python tokenless 投递（不依赖 JS announce 层）
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
