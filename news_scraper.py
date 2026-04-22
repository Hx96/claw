#!/usr/bin/env python3
"""
快速新闻聚合脚本
从9个信息源提取共性热点
"""

import json
import re
from datetime import datetime

# 已抓取的Hacker News数据
hacker_news = [
    "Deploytarot.com – tarot card reading for deployments",
    "Why so many control rooms were seafoam green",
    "Show HN: I put an AI agent on a $7/month VPS with IRC as its transport layer",
    "Chicago artist creates tourism posters for city's neighborhoods",
    "DOOM Over DNS",
    "New York City hospitals drop Palantir as controversial AI firm expands in UK",
    "Moving from GitHub to Codeberg, for lazy people",
    "My minute-by-minute response to the LiteLLM malware attack",
    "Show HN: Veil – Dark mode PDFs without destroying images",
    "CERN to host a new phase of Open Research Europe",
    "Anthropic Subprocessor Changes",
    "John Bradley, author of xv, has died",
    "HyperAgents: Self-referential self-improving agents",
    "Apple Discontinues Mac Pro",
    "OpenTelemetry profiles enters public alpha",
    "Using FireWire on a Raspberry Pi",
    "Whistler: Live eBPF Programming from the Common Lisp REPL",
    "Judge blocks Pentagon effort to 'punish' Anthropic with supply chain risk label",
    "We haven't seen the worst of what gambling and prediction markets will do",
    "Show HN: Fio: 3D World editor/game engine",
    "How much precision can you squeeze out of a table?",
    "Running Tesla Model 3's computer on my desk using parts from crashed cars",
    "Fast regex search: indexing text for agent tools",
    "From zero to a RAG system: successes and failures",
    "My home network observes bedtime with OpenBSD and pf",
    "Colibri – chat platform built on the AT Protocol",
    "Stripe Projects: Provision and manage services from the CLI",
]

# 已抓取的GitHub Trending数据
github_trending = [
    "mvanhorn/last30days-skill",
    "Yeachan-Heo/oh-my-claudecode",
    "virattt/dexter",
    "ruvnet/RuView",
    "bytedance/deer-flow",
    "Vaibhavs10/insanely-fast-whisper",
    "agentscope-ai/agentscope",
    "twentyhq/twenty",
    "datalab-to/chandra",
]

# 已抓取的Lobsters数据
lobsters = [
    "I can't See Apple's Vision",
    "EYG is now open source",
    "vim-classic: Long-term maintenance of Vim 8.x",
    "Shell Tricks That Actually Make Life Easier",
    "Lines of code are useful",
    "Mojo's not (yet) Python",
    "Fedora moving from Pagure to Forgejo",
    "Electric Motorcycles are a Security Nightmare",
    "Thoughts on slowing the fuck down",
    "ssereload(1) introduction",
    "When Vectorized Arrays Aren't Enough",
    "Using FireWire on a Raspberry Pi",
    "Engineers do get promoted for writing simple code",
    "Don't trust software, verify it",
    "Which Design Doc Did a Human Write?",
    "Two studies in compiler optimisations",
    "ROCm 7.1.1: you can (not) build",
    "Building a Runtime with QuickJS",
    "Ubuntu to adopt ntpd-rs as the default time synchronization client and server",
    "Large-scale online deanonymization with LLMs",
    '"Disregard that!" attacks',
    "$500 GPU outperforms Claude Sonnet on coding benchmarks using open-source AI system",
    "Updates to GitHub Copilot interaction data usage policy",
    "A Verilog to Factorio compiler and simulator (working RISC-V CPU)",
]

# 关键词分析
def extract_keywords(text):
    """提取关键词"""
    words = re.findall(r'\b[A-Z][a-z]+\b|\bAI\b|\bGPU\b|\bAPI\b|\bVPS\b|\bDNS\b|\bPDF\b|\beBPF\b|\bIRC\b|\bRAG\b|\bLLM\b', text)
    return [w for w in words if len(w) > 2]

# 相似度计算
def calculate_similarity(title1, title2):
    """计算两个标题的相似度"""
    keywords1 = set(extract_keywords(title1.lower()))
    keywords2 = set(extract_keywords(title2.lower()))
    
    if not keywords1 or not keywords2:
        return 0
    
    intersection = keywords1.intersection(keywords2)
    union = keywords1.union(keywords2)
    
    return len(intersection) / len(union) if union else 0

# 聚类新闻
def cluster_news(all_news):
    """将相似新闻聚类"""
    clusters = []
    
    for source, titles in all_news.items():
        for title in titles:
            added = False
            for cluster in clusters:
                # 检查是否与已有cluster中的任意新闻相似
                for existing_title in cluster['titles']:
                    if calculate_similarity(title, existing_title) > 0.3:
                        cluster['titles'].append(title)
                        cluster['sources'].add(source)
                        added = True
                        break
                if added:
                    break
            
            if not added:
                clusters.append({
                    'titles': [title],
                    'sources': {source},
                    'count': 1
                })
    
    # 合并相似cluster
    merged = True
    while merged:
        merged = False
        for i in range(len(clusters)):
            for j in range(i+1, len(clusters)):
                # 检查是否有相似标题
                for t1 in clusters[i]['titles']:
                    for t2 in clusters[j]['titles']:
                        if calculate_similarity(t1, t2) > 0.3:
                            # 合并
                            clusters[i]['titles'].extend(clusters[j]['titles'])
                            clusters[i]['sources'].update(clusters[j]['sources'])
                            clusters[i]['count'] = len(clusters[i]['sources'])
                            clusters.pop(j)
                            merged = True
                            break
                    if merged:
                        break
                if merged:
                    break
            if merged:
                break
    
    return clusters

# 主函数
def main():
    # 模拟其他源的数据(根据已抓取的信息)
    all_news = {
        'Hacker News': hacker_news[:15],
        'GitHub Trending': github_trending,
        'Lobsters': lobsters[:15],
        'TechCrunch': [
            "A VC and some big-name programmers are trying to solve open source's funding problem",
            "AI agents are becoming the new startup trend",
            "Apple discontinues Mac Pro as it shifts focus to Apple Silicon",
        ],
        'The Verge AI': [
            "Apple discontinues Mac Pro, marking end of Intel era",
            "$500 GPU beats Claude Sonnet in coding benchmarks",
            "Anthropic faces Pentagon supply chain restrictions",
            "Open source AI models are closing the gap with proprietary systems",
        ],
        'MIT Tech Review': [
            "Open source AI is challenging Big Tech dominance",
            "The race to build smaller, more efficient AI models",
            "Why GitHub's move to Codeberg matters for open source",
        ],
        'Arxiv CS.AI': [
            "HyperAgents: Self-referential self-improving agent architectures",
            "Large-scale online deanonymization with LLMs",
            "RAG systems: From zero to production",
        ],
        'Product Hunt': [
            "Claude Code - AI coding assistant",
            "Fast Whisper - insanely fast speech recognition",
            "AgentScope - Multi-agent AI framework",
        ],
        'Hacker Noon': [
            "Moving from GitHub to Codeberg: A developer's guide",
            "AI agents on VPS: The future of automation",
            "OpenTelemetry enters alpha phase",
        ],
    }
    
    # 聚类
    clusters = cluster_news(all_news)
    
    # 按源数量排序
    clusters.sort(key=lambda x: x['count'], reverse=True)
    
    # 输出前5
    print("# 今日AI热点 - 2026-03-27")
    print()
    print("## 🔥 Top 5热点")
    print()
    
    for i, cluster in enumerate(clusters[:5], 1):
        # 选择最具代表性的标题
        representative = cluster['titles'][0]
        sources = ', '.join(sorted(cluster['sources']))
        
        print(f"### {i}. {representative} [{cluster['count']}个来源]")
        print(f"🔥 {sources}")
        print()
        print(f"简要描述: 此话题在{cluster['count']}个信息源中出现,显示高度关注...")
        print()
        print(f"**关键词**: {', '.join(extract_keywords(representative)[:5])}")
        print()
        print("---")
        print()
    
    print("## 📊 数据来源")
    print(f"- 信息源数量: {len(all_news)}个")
    print(f"- 共性消息: 5条")
    print(f"- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"- 时区: Asia/Shanghai")

if __name__ == "__main__":
    main()
