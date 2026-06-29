#!/usr/bin/env python3
"""
美股大盘日报 (US Market Daily Report)
获取美股三大指数、VIX、美债收益率、关键商品数据，生成文本摘要。
专为微信推送设计：纯文本，简洁高信息密度。
"""

import sys
import os
import json
import signal
from datetime import datetime, timedelta

# Disable multitasking/spawn that causes segfaults
os.environ['YFINANCE_NO_MULTIPROCESSING'] = '1'

def safe_float(val):
    try:
        if val is None:
            return 0.0
        if isinstance(val, str) and val.strip() in ('', '-', '--', 'nan', 'None'):
            return 0.0
        return float(val)
    except (ValueError, TypeError):
        return 0.0

def fetch_quote(symbol):
    """Fetch a single ticker quote using download."""
    try:
        import yfinance as yf
        hist = yf.download(symbol, period="5d", progress=False, threads=False)
        if hist is None or hist.empty:
            return None
        latest = hist.iloc[-1]
        if len(hist) >= 2:
            prev = hist.iloc[-2]
            prev_close = safe_float(prev['Close'])
        else:
            prev_close = safe_float(latest.get('Open', 0))
        
        current = safe_float(latest['Close'])
        change = current - prev_close
        change_pct = (change / prev_close * 100) if prev_close > 0 else 0.0
        
        return {
            'symbol': symbol,
            'price': round(current, 2),
            'change': round(change, 2),
            'change_pct': round(change_pct, 2),
        }
    except Exception as e:
        print(f"  ! {symbol}: {e}", file=sys.stderr)
        return None

def fetch_history(symbol, days=30):
    """Fetch recent closing prices for trend analysis."""
    try:
        import yfinance as yf
        hist = yf.download(symbol, period=f"{days}d", progress=False, threads=False)
        if hist is None or hist.empty:
            return []
        closes = hist['Close'].tolist()
        return [round(safe_float(c), 2) for c in closes]
    except Exception:
        return []

def analyze_trend(closes):
    """Simple trend analysis from closing prices."""
    if len(closes) < 5:
        return "数据不足"
    
    recent_5 = closes[-5:]
    recent_20 = closes[-20:] if len(closes) >= 20 else closes
    
    avg_5 = sum(recent_5) / len(recent_5)
    avg_20 = sum(recent_20) / len(recent_20)
    
    # 5日 vs 20日均线
    if avg_5 > avg_20 * 1.01:
        ma_signal = "多头排列（5日>20日）"
    elif avg_5 < avg_20 * 0.99:
        ma_signal = "空头排列（5日<20日）"
    else:
        ma_signal = "均线纠缠"
    
    # 近期波动
    if len(recent_5) >= 2:
        recent_change = (recent_5[-1] - recent_5[0]) / recent_5[0] * 100 if recent_5[0] > 0 else 0
    else:
        recent_change = 0
    
    # 区间
    high = max(closes)
    low = min(closes)
    current = closes[-1]
    pos_in_range = (current - low) / (high - low) * 100 if (high - low) > 0 else 50
    
    return f"{ma_signal}，5日变动{recent_change:+.1f}%，区间位置{pos_in_range:.0f}%"

def fmt_change(val):
    """Format change with arrow."""
    if val > 0:
        return f"🔺+{val:.2f}"
    elif val < 0:
        return f"🔻{val:.2f}"
    else:
        return f"➡️{val:.2f}"

def fmt_pct(val):
    """Format percentage."""
    if val > 0:
        return f"+{val:.2f}%"
    elif val < 0:
        return f"{val:.2f}%"
    else:
        return "0.00%"

def main():
    now = datetime.now()
    print(f"美股大盘日报 — 数据获取于 {now.strftime('%Y-%m-%d %H:%M')} CST\n", file=sys.stderr)
    
    # 定义关注的大盘指标
    indices = [
        ('^GSPC', '标普500'),
        ('^IXIC', '纳指'),
        ('^DJI', '道琼斯'),
        ('^VIX', 'VIX恐慌指数'),
    ]
    
    yields = [
        ('^TNX', '10年期美债收益率'),
        ('^TYX', '30年期美债收益率'),
    ]
    
    commodities = [
        ('GC=F', '黄金'),
        ('CL=F', 'WTI原油'),
    ]
    
    etfs = [
        ('SPY', 'SPY（标普ETF）'),
        ('QQQ', 'QQQ（纳指ETF）'),
    ]
    
    print("获取数据中...", file=sys.stderr)
    
    # Fetch all
    all_data = {}
    for symbol, name in indices + yields + commodities + etfs:
        print(f"  {name}...", file=sys.stderr)
        q = fetch_quote(symbol)
        if q:
            q['name'] = name
            all_data[symbol] = q
    
    # Trend analysis for major indices
    trends = {}
    for symbol, name in indices:
        if symbol == '^VIX':
            continue
        print(f"  {name}趋势...", file=sys.stderr)
        closes = fetch_history(symbol, 30)
        if closes:
            trends[symbol] = analyze_trend(closes)
    
    # Build report
    lines = []
    lines.append("📈 美股大盘日报")
    lines.append(f"📊 {now.strftime('%m月%d日')} CST\n")
    
    # 三大指数
    lines.append("━━━ 三大指数 ━━━")
    for symbol, name in indices:
        if symbol == '^VIX':
            continue
        d = all_data.get(symbol)
        if d:
            lines.append(f"{d['name']} {d['price']:,.2f}")
            lines.append(f"  {fmt_change(d['change'])} ({fmt_pct(d['change_pct'])})")
            t = trends.get(symbol, "")
            if t:
                lines.append(f"  趋势: {t}")
            lines.append("")
    
    # VIX
    vix = all_data.get('^VIX')
    if vix:
        vix_level = "低波动" if vix['price'] < 15 else ("正常" if vix['price'] < 20 else ("偏高" if vix['price'] < 30 else "恐慌"))
        lines.append("━━━ 波动率 ━━━")
        lines.append(f"VIX {vix['price']:.2f} ({vix_level})")
        lines.append(f"  {fmt_change(vix['change'])} ({fmt_pct(vix['change_pct'])})\n")
    
    # 美债收益率
    lines.append("━━━ 美债收益率 ━━━")
    for symbol, name in yields:
        d = all_data.get(symbol)
        if d:
            lines.append(f"{d['name']}: {d['price']:.2f}%")
            lines.append(f"  {fmt_change(d['change'])} ({fmt_pct(d['change_pct'])})")
    lines.append("")
    
    # 商品
    lines.append("━━━ 关键商品 ━━━")
    for symbol, name in commodities:
        d = all_data.get(symbol)
        if d:
            lines.append(f"{d['name']}: {d['price']:,.2f}")
            lines.append(f"  {fmt_change(d['change'])} ({fmt_pct(d['change_pct'])})")
    lines.append("")
    
    # 综合判断
    lines.append("━━━ 市场判断 ━━━")
    sp = all_data.get('^GSPC')
    vix_d = all_data.get('^VIX')
    tnx = all_data.get('^TNX')
    
    signals = []
    if sp and sp['change_pct'] > 0.5:
        signals.append("美股走强")
    elif sp and sp['change_pct'] < -0.5:
        signals.append("美股承压")
    else:
        signals.append("美股窄幅震荡")
    
    if vix_d:
        if vix_d['price'] > 25:
            signals.append("市场恐慌情绪高")
        elif vix_d['price'] < 13:
            signals.append("市场过度乐观")
    
    if tnx:
        if tnx['change_pct'] > 2:
            signals.append("美债收益率上行（压制估值）")
        elif tnx['change_pct'] < -2:
            signals.append("美债收益率下行（利好成长）")
    
    lines.append(" · ".join(signals))
    lines.append("")
    lines.append("数据来源: Yahoo Finance | 仅供参考")
    
    report = "\n".join(lines)
    print(report)
    return report

if __name__ == '__main__':
    main()
