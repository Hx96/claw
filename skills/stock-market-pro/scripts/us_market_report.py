#!/usr/bin/env python3
"""
美股大盘日报 — 调用 yf.py (uv隔离环境) 获取数据，组装微信日报
避免 yfinance 在系统 Python 中的 segfault 问题
"""
import subprocess
import sys
import re
import time
from datetime import datetime

YF_SCRIPT = "/root/.openclaw/workspace/skills/stock-market-pro/scripts/yf.py"

def run_yf(args):
    """Run yf.py via uv and capture stdout."""
    cmd = ["/usr/local/bin/uv", "run", "--script", YF_SCRIPT] + args
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        time.sleep(1)  # Rate limit friendly
        return r.stdout.strip()
    except Exception as e:
        return f"ERROR: {e}"

def parse_price(text):
    """Parse price from yf.py price output."""
    if not text or "ERROR" in text:
        return None
    lines = text.split('\n')
    price = None
    change = None
    change_pct = None
    for line in lines:
        if '│' not in line:
            continue
        parts = [p.strip() for p in line.split('│')]
        if len(parts) < 3:
            continue
        key = parts[1]
        val = parts[2]
        if 'Current Price' in key:
            m = re.search(r'([\d,]+\.?\d*)', val)
            if m:
                price = float(m.group(1).replace(',', ''))
        if 'Change' in key and '%' in val:
            m = re.search(r'([+-]?\d+\.?\d*)\s*\(([+-]?\d+\.?\d*)%\)', val)
            if m:
                change = float(m.group(1))
                change_pct = float(m.group(2))
    return {'price': price, 'change': change, 'change_pct': change_pct} if price else None

def parse_history(text):
    """Parse ASCII history for trend - extract closing numbers."""
    if not text:
        return ""
    # ASCII chart contains non-numeric lines; extract pure price sequences
    lines = text.split('\n')
    closes = []
    for line in lines:
        # Skip lines that look like chart borders or labels
        if any(c in line for c in ['┃', '━', '┏', '┗', '┡', '└', '│', '┌']):
            continue
        # Find numbers that look like prices (100+ to filter out small noise)
        nums = re.findall(r'\b(\d{3,}[\d,.]*)\b', line)
        for n in nums:
            try:
                v = float(n.replace(',', ''))
                if 100 < v < 100000:
                    closes.append(round(v, 2))
            except:
                pass
    if len(closes) < 5:
        return ""
    # Use last 20 closes
    closes = closes[-20:]
    avg5 = sum(closes[-5:]) / 5
    avg_all = sum(closes) / len(closes)
    if avg5 > avg_all * 1.01:
        ma = "多头排列"
    elif avg5 < avg_all * 0.99:
        ma = "空头排列"
    else:
        ma = "均线纠缠"
    recent = (closes[-1] - closes[0]) / closes[0] * 100 if closes[0] > 0 else 0
    hi, lo = max(closes), min(closes)
    pos = (closes[-1] - lo) / (hi - lo) * 100 if (hi - lo) > 0 else 50
    return f"{ma}，5日{recent:+.1f}%，区间{pos:.0f}%"

def fmt_change(val):
    if val is None:
        return "--"
    if val > 0:
        return f"🔺+{val:.2f}"
    elif val < 0:
        return f"🔻{val:.2f}"
    return f"➡️{val:.2f}"

def fmt_pct(val):
    if val is None:
        return "--"
    if val > 0:
        return f"+{val:.2f}%"
    elif val < 0:
        return f"{val:.2f}%"
    return "0.00%"

def main():
    now = datetime.now()
    
    tickers = [
        ('^GSPC', '标普500'),
        ('^IXIC', '纳指'),
        ('^DJI', '道琼斯'),
        ('^VIX', 'VIX恐慌指数'),
        ('^TNX', '10年美债收益率'),
        ('GC=F', '黄金'),
        ('CL=F', 'WTI原油'),
    ]
    
    print(f"美股大盘日报 — {now.strftime('%Y-%m-%d %H:%M')} CST", file=sys.stderr)
    print("获取数据中...", file=sys.stderr)
    
    data = {}
    trends = {}
    for symbol, name in tickers:
        print(f"  {name}...", file=sys.stderr)
        out = run_yf(["price", symbol])
        parsed = parse_price(out)
        if parsed:
            parsed['name'] = name
            data[symbol] = parsed
        
        # Get trend for indices (not VIX/yields)
        if symbol in ('^GSPC', '^IXIC', '^DJI'):
            hist_out = run_yf(["history", symbol, "1mo"])
            t = parse_history(hist_out)
            if t:
                trends[symbol] = t
    
    if not data:
        print("❌ 数据获取失败")
        return
    
    # Build report
    lines = []
    lines.append("📈 美股大盘日报")
    lines.append(f"📊 {now.strftime('%m月%d日')} CST\n")
    
    # 三大指数
    lines.append("━━━ 三大指数 ━━━")
    for symbol, name in [('^GSPC', '标普500'), ('^IXIC', '纳指'), ('^DJI', '道琼斯')]:
        d = data.get(symbol)
        if d and d.get('price'):
            lines.append(f"{d['name']} {d['price']:,.2f}")
            chg = fmt_change(d.get('change'))
            pct = fmt_pct(d.get('change_pct'))
            lines.append(f"  {chg} ({pct})")
            t = trends.get(symbol, "")
            if t:
                lines.append(f"  趋势: {t}")
            lines.append("")
    
    # VIX
    vix = data.get('^VIX')
    if vix and vix.get('price'):
        level = "低波动" if vix['price'] < 15 else ("正常" if vix['price'] < 20 else ("偏高" if vix['price'] < 30 else "恐慌"))
        lines.append("━━━ 波动率 ━━━")
        lines.append(f"VIX {vix['price']:.2f} ({level})")
        lines.append(f"  {fmt_change(vix.get('change'))} ({fmt_pct(vix.get('change_pct'))})\n")
    
    # 美债
    tnx = data.get('^TNX')
    if tnx and tnx.get('price'):
        lines.append("━━━ 美债 ━━━")
        lines.append(f"10年期: {tnx['price']:.2f}%")
        lines.append(f"  {fmt_change(tnx.get('change'))} ({fmt_pct(tnx.get('change_pct'))})\n")
    
    # 商品
    lines.append("━━━ 关键商品 ━━━")
    for symbol, name in [('GC=F', '黄金'), ('CL=F', 'WTI原油')]:
        d = data.get(symbol)
        if d and d.get('price'):
            lines.append(f"{d['name']}: {d['price']:,.2f}")
            lines.append(f"  {fmt_change(d.get('change'))} ({fmt_pct(d.get('change_pct'))})")
    lines.append("")
    
    # 综合判断
    lines.append("━━━ 市场判断 ━━━")
    signals = []
    sp = data.get('^GSPC')
    vix_d = data.get('^VIX')
    tnx_d = data.get('^TNX')
    
    if sp:
        if sp.get('change_pct', 0) > 0.5:
            signals.append("美股走强")
        elif sp.get('change_pct', 0) < -0.5:
            signals.append("美股承压")
        else:
            signals.append("美股窄幅震荡")
    
    if vix_d and vix_d.get('price'):
        if vix_d['price'] > 25:
            signals.append("恐慌情绪高")
        elif vix_d['price'] < 13:
            signals.append("过度乐观")
    
    if tnx_d:
        if tnx_d.get('change_pct', 0) > 2:
            signals.append("美债收益率上行(压制估值)")
        elif tnx_d.get('change_pct', 0) < -2:
            signals.append("美债收益率下行(利好成长)")
    
    lines.append(" · ".join(signals))
    lines.append("")
    lines.append("数据来源: Yahoo Finance | 仅供参考")
    
    report = "\n".join(lines)
    print(report)

if __name__ == '__main__':
    main()
