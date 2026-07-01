#!/usr/bin/env python3
"""
美股大盘日报 v2 — 使用 TradingView Scanner API (无限制/无需API Key)
替代被Yahoo Finance限流的yfinance方案
"""
import json
import subprocess
import sys
from datetime import datetime, timezone, timedelta

SCANNER_URL = "https://scanner.tradingview.com"

def fetch_tv(tickers, market="america"):
    """Fetch data from TradingView scanner API."""
    payload = json.dumps({
        "symbols": {"tickers": tickers},
        "columns": ["close", "change", "change_abs", "high", "low"]
    })
    
    result = subprocess.run(
        ["curl", "-sL", f"{SCANNER_URL}/{market}/scan",
         "-H", "Content-Type: application/json",
         "-d", payload,
         "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"],
        capture_output=True, text=True, timeout=15
    )
    
    try:
        data = json.loads(result.stdout)
        out = {}
        for item in data.get("data", []):
            s = item["s"]
            vals = item.get("d", [None]*5)
            out[s] = {
                "close": vals[0],
                "change_pct": vals[1],
                "change_abs": vals[2],
                "high": vals[3],
                "low": vals[4],
            }
        return out
    except Exception as e:
        print(f"TV scan error ({market}): {e}", file=sys.stderr)
        return {}

def fmt_pct(val):
    if val is None:
        return "--"
    return f"+{val:.2f}%" if val > 0 else f"{val:.2f}%"

def fmt_chg(val):
    if val is None:
        return "--"
    return f"🔺+{val:.2f}" if val > 0 else f"🔻{val:.2f}"

def main():
    # America market: ETFs
    us_data = fetch_tv(["AMEX:SPY", "NASDAQ:QQQ", "AMEX:GLD", "ARCA:USO"])
    
    # Global market: indices, VIX, bonds
    global_data = fetch_tv([
        "NASDAQ:IXIC",   # Nasdaq Composite
        "TVC:VIX",       # VIX
        "TVC:US10Y",     # 10Y Treasury Yield
        "TVC:GOLD",      # Gold spot
    ], market="global")
    
    now = datetime.now(timezone(timedelta(hours=8)))  # CST
    
    weekday = now.weekday()
    hour = now.hour
    is_weekend = weekday >= 5
    
    if is_weekend:
        session = "休市"
    elif 21 <= hour or hour < 5:
        session = "盘前/盘中"
    elif 5 <= hour < 8:
        session = "盘后"
    else:
        session = "休市"
    
    lines = []
    lines.append("📈 美股大盘日报")
    lines.append(f"📊 {now.strftime('%m月%d日')} CST | {session}\n")
    
    # === 三大指数 ===
    lines.append("━━━ 三大指数 ━━━")
    
    index_map = [
        ("AMEX:SPY", "标普500 (SPY)"),
        ("NASDAQ:QQQ", "纳指100 (QQQ)"),
    ]
    
    for ticker, name in index_map:
        d = us_data.get(ticker)
        if d and d.get("close"):
            lines.append(f"{name}")
            lines.append(f"  {d['close']:,.2f} {fmt_chg(d.get('change_abs'))} ({fmt_pct(d.get('change_pct'))})")
            if d.get("high") and d.get("low"):
                lines.append(f"  日内: {d['low']:,.2f} - {d['high']:,.2f}")
            lines.append("")
        else:
            lines.append(f"{name}: 数据获取失败\n")
    
    # Nasdaq Composite
    ndq = global_data.get("NASDAQ:IXIC")
    if ndq and ndq.get("close"):
        lines.append(f"纳指综合 (IXIC)")
        lines.append(f"  {ndq['close']:,.2f} {fmt_chg(ndq.get('change_abs'))} ({fmt_pct(ndq.get('change_pct'))})\n")
    
    # === VIX ===
    vix = global_data.get("TVC:VIX")
    if vix and vix.get("close"):
        level = "低波动" if vix["close"] < 15 else ("正常" if vix["close"] < 20 else ("偏高" if vix["close"] < 30 else "恐慌"))
        lines.append("━━━ 波动率 ━━━")
        lines.append(f"VIX {vix['close']:.2f} ({level})")
        lines.append(f"  {fmt_chg(vix.get('change_abs'))} ({fmt_pct(vix.get('change_pct'))})\n")
    
    # === 美债 ===
    tnx = global_data.get("TVC:US10Y")
    if tnx and tnx.get("close") is not None:
        lines.append("━━━ 美债 ━━━")
        lines.append(f"10年期收益率: {tnx['close']:.3f}%")
        lines.append(f"  {fmt_chg(tnx.get('change_abs'))} ({fmt_pct(tnx.get('change_pct'))})\n")
    
    # === 商品 ===
    lines.append("━━━ 关键商品 ━━━")
    
    gold = global_data.get("TVC:GOLD")
    if not gold or not gold.get("close"):
        gold = us_data.get("AMEX:GLD")
        gold_name = "黄金ETF (GLD)"
    else:
        gold_name = "黄金"
    if gold and gold.get("close"):
        lines.append(f"{gold_name}: {gold['close']:,.2f}")
        lines.append(f"  {fmt_chg(gold.get('change_abs'))} ({fmt_pct(gold.get('change_pct'))})")
    
    oil = us_data.get("ARCA:USO")
    if oil and oil.get("close"):
        lines.append(f"原油ETF (USO): {oil['close']:,.2f}")
        lines.append(f"  {fmt_chg(oil.get('change_abs'))} ({fmt_pct(oil.get('change_pct'))})")
    lines.append("")
    
    # === 市场判断 ===
    lines.append("━━━ 市场判断 ━━━")
    signals = []
    
    spy = us_data.get("AMEX:SPY")
    if spy:
        pct = spy.get("change_pct") or 0
        if pct > 0.5:
            signals.append("美股走强")
        elif pct < -0.5:
            signals.append("美股承压")
        else:
            signals.append("美股窄幅震荡")
    
    if vix and vix.get("close"):
        if vix["close"] > 25:
            signals.append("恐慌情绪高")
        elif vix["close"] < 13:
            signals.append("过度乐观")
    
    if tnx and tnx.get("change_pct") is not None:
        if tnx["change_pct"] > 2:
            signals.append("美债收益率上行(压制估值)")
        elif tnx["change_pct"] < -2:
            signals.append("美债收益率下行(利好成长)")
    
    if not signals:
        signals.append("数据不足")
    
    lines.append(" · ".join(signals))
    lines.append("")
    lines.append("数据来源: TradingView | 仅供参考")
    
    print("\n".join(lines))

if __name__ == "__main__":
    main()
