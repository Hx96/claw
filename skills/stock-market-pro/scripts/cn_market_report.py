#!/usr/bin/env python3
"""
A股大盘日报 v1 — 使用 akshare (新浪/同花顺源) 获取宽基指数、行业板块、财经新闻
数据源：
  - stock_zh_index_spot_sina: 新浪宽基指数实时行情
  - stock_board_industry_summary_ths: 同花顺行业板块
  - stock_info_global_em: 东方财富财经要闻
"""
import json
import sys
import time
import traceback
from datetime import datetime, timezone, timedelta

def safe_fetch(func, name, retries=2, delay=1.0):
    last_err = None
    for i in range(retries):
        try:
            r = func()
            if r is not None and len(r) > 0:
                return r
        except Exception as e:
            last_err = e
        time.sleep(delay)
    print(f"  ! {name} failed: {last_err}", file=sys.stderr)
    return None


def fetch_cn_indices():
    """A股宽基指数 via 新浪"""
    import akshare as ak
    df = safe_fetch(lambda: ak.stock_zh_index_spot_sina(), "cn_indices")
    if df is None:
        return []
    
    broad = {
        'sh000001': '上证指数',
        'sz399001': '深证成指', 
        'sz399006': '创业板指',
        'sh000688': '科创50',
        'sh000300': '沪深300',
        'sh000905': '中证500',
        'sh000852': '中证1000',
        'sh000016': '上证50',
    }
    
    results = []
    for _, row in df.iterrows():
        code = str(row.get('代码', ''))
        if code in broad:
            results.append({
                'code': code,
                'name': broad[code],
                'price': float(row.get('最新价', 0)),
                'change_pct': float(row.get('涨跌幅', 0)),
                'change_amt': float(row.get('涨跌额', 0)),
                'prev_close': float(row.get('昨收', 0)),
                'volume': float(row.get('成交量', 0)),
                'turnover': float(row.get('成交额', 0)),
            })
    return results


def fetch_hk_indices():
    """港股指数 via 新浪"""
    import akshare as ak
    df = safe_fetch(lambda: ak.stock_hk_index_spot_sina(), "hk_indices")
    if df is None:
        return []
    
    targets = {'HSI': '恒生指数', 'HSTECH': '恒生科技'}
    results = []
    for _, row in df.iterrows():
        name = str(row.get('名称', ''))
        if '恒生' in name or '国企' in name:
            results.append({
                'name': name,
                'price': float(row.get('最新价', 0)),
                'change_pct': float(row.get('涨跌幅', 0)),
            })
    return results[:5]


def fetch_sectors():
    """行业板块涨跌 via 同花顺"""
    import akshare as ak
    df = safe_fetch(lambda: ak.stock_board_industry_summary_ths(), "sectors")
    if df is None:
        return {'top5': [], 'bottom5': []}
    
    if '涨跌幅' in df.columns:
        # 过滤掉成交量为0的（未开盘/休市数据）
        active = df[df['涨跌幅'] != 0] if '涨跌幅' in df.columns else df
        if len(active) == 0:
            active = df
        top5 = active.nlargest(5, '涨跌幅')
        bottom5 = active.nsmallest(5, '涨跌幅')
        
        def fmt(d):
            return {
                'name': str(d.get('板块', '')),
                'change_pct': float(d.get('涨跌幅', 0)),
                'leader': str(d.get('领涨股', '')),
                'leader_change': float(d.get('领涨股-涨跌幅', 0)),
                'net_inflow': float(d.get('净流入', 0)),
            }
        return {
            'top5': [fmt(r) for _, r in top5.iterrows()],
            'bottom5': [fmt(r) for _, r in bottom5.iterrows()],
        }
    return {'top5': [], 'bottom5': []}


def fetch_news():
    """财经要闻 via 东方财富"""
    import akshare as ak
    df = safe_fetch(lambda: ak.stock_info_global_em(), "news")
    if df is None:
        return []
    
    news = []
    for _, row in df.head(25).iterrows():
        news.append({
            'title': str(row.get('标题', '')),
            'summary': str(row.get('摘要', ''))[:200],
            'time': str(row.get('发布时间', '')),
            'url': str(row.get('链接', '')),
        })
    return news


def main():
    print("=== A股大盘数据抓取 ===", file=sys.stderr)
    
    result = {
        'fetch_time': datetime.now(timezone(timedelta(hours=8))).isoformat(),
        'indices': fetch_cn_indices(),
        'hk_indices': fetch_hk_indices(),
        'sectors': fetch_sectors(),
        'news': fetch_news(),
    }
    
    # 输出到stdout（JSON）
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
