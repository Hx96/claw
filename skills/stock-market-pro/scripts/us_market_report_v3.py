#!/usr/bin/env python3
"""
美股大盘日报 v3 — 使用 opencli (东方财富) + TradingView 双数据源
- 指数: opencli eastmoney index-board (真实指数价格)
- VIX/美债/黄金: TradingView Scanner API
"""
import json
import subprocess
import sys
from datetime import datetime, timezone, timedelta

def run_opencli(args):
    """Run opencli and return parsed JSON."""
    result = subprocess.run(
        ["opencli"] + args + ["-f", "json"],
        capture_output=True, text=True, timeout=15
    )
    # opencli appends update notice, extract JSON array
    out = result.stdout.strip()
    # Find the JSON array/object
    start = out.find('[')
    if start < 0:
        start = out.find('{')
    end = out.rfind(']')
    if end < 0:
        end = out.rfind('}')
    if start >= 0 and end > start:
        try:
            return json.loads(out[start:end+1])
        except:
            pass
    return []

def fetch_tv_global(tickers):
    """Fetch from TradingView global scanner."""
    payload = json.dumps({
        "symbols": {"tickers": tickers},
        "columns": ["close", "change", "change_abs"]
    })
    result = subprocess.run(
        ["curl", "-sL", "https://scanner.tradingview.com/global/scan",
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
            vals = item.get("d", [None]*3)
            out[s] = {
                "close": vals[0],
                "change_pct": vals[1],
                "change_abs": vals[2],
            }
        return out
    except:
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
    
    # === 数据获取 ===
    # 1. 三大指数 via opencli (东方财富)
    indices_raw = run_opencli(["eastmoney", "index-board", "--group", "us"])
    indices = {}
    if isinstance(indices_raw, list):
        for r in indices_raw:
            code = r.get("code", "")
            if code == "SPX" or code == "SP500":
                indices["SPX"] = r
            elif code == "NDX" or code == "IXIC":
                indices["NDX"] = r
            elif code == "DJIA" or code == "DJI":
                indices["DJI"] = r
    
    # 2. VIX / 美债 / 黄金 via TradingView
    tv_data = fetch_tv_global(["TVC:VIX", "TVC:US10Y", "TVC:GOLD"])
    
    # === 生成报告 ===
    lines = []
    lines.append("📈 美股大盘日报")
    lines.append(f"📊 {now.strftime('%m月%d日')} CST | {session}\n")
    
    # 三大指数
    lines.append("━━━ 三大指数 ━━━")
    display = [
        ("DJI", "道琼斯"),
        ("SPX", "标普500"),
        ("NDX", "纳斯达克"),
    ]
    for key, name in display:
        d = indices.get(key)
        if d:
            price = d.get("price", 0)
            pct = d.get("changePercent", 0)
            chg = d.get("change", 0)
            hi = d.get("high", 0)
            lo = d.get("low", 0)
            prev = d.get("prevClose", 0)
            lines.append(f"{name}")
            lines.append(f"  {price:,.2f} {fmt_chg(chg)} ({fmt_pct(pct)})")
            if hi and lo and hi != lo:
                lines.append(f"  日内: {lo:,.2f} - {hi:,.2f}")
            lines.append("")
        else:
            lines.append(f"{name}: 数据获取失败\n")
    
    # VIX
    vix = tv_data.get("TVC:VIX")
    if vix and vix.get("close"):
        level = "低波动" if vix["close"] < 15 else ("正常" if vix["close"] < 20 else ("偏高" if vix["close"] < 30 else "恐慌"))
        lines.append("━━━ 波动率 ━━━")
        lines.append(f"VIX {vix['close']:.2f} ({level})")
        lines.append(f"  {fmt_chg(vix.get('change_abs'))} ({fmt_pct(vix.get('change_pct'))})\n")
    
    # 美债
    tnx = tv_data.get("TVC:US10Y")
    if tnx and tnx.get("close") is not None:
        lines.append("━━━ 美债 ━━━")
        lines.append(f"10年期收益率: {tnx['close']:.3f}%")
        lines.append(f"  {fmt_chg(tnx.get('change_abs'))} ({fmt_pct(tnx.get('change_pct'))})\n")
    
    # 黄金
    gold = tv_data.get("TVC:GOLD")
    if gold and gold.get("close"):
        lines.append("━━━ 关键商品 ━━━")
        lines.append(f"黄金: {gold['close']:,.2f}")
        lines.append(f"  {fmt_chg(gold.get('change_abs'))} ({fmt_pct(gold.get('change_pct'))})\n")
    
    # 市场判断
    lines.append("━━━ 市场判断 ━━━")
    signals = []
    
    spx = indices.get("SPX")
    if spx:
        pct = spx.get("changePercent", 0) or 0
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
    lines.append("数据来源: 东方财富 + TradingView | 仅供参考")
    
    print("\n".join(lines))

if __name__ == "__main__":
    main()
