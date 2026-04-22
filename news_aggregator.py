#!/usr/bin/env python3
"""
改进的新闻聚合脚本 - 手动主题识别
"""

from datetime import datetime

# 各信息源的热点数据
sources_data = {
    'Hacker News': [
        "AI agent on $7/month VPS with IRC transport",
        "New York City hospitals drop Palantir",
        "Moving from GitHub to Codeberg",
        "LiteLLM malware attack response",
        "Anthropic Subprocessor Changes",
        "HyperAgents: Self-referential self-improving agents",
        "Apple Discontinues Mac Pro",
        "Judge blocks Pentagon Anthropic restrictions",
        "Running Tesla Model 3's computer",
        "RAG system implementation",
        "OpenTelemetry profiles alpha",
        "Using FireWire on Raspberry Pi",
    ],
    'GitHub Trending': [
        "last30days-skill (Claude-related)",
        "oh-my-claudecode",
        "dexter",
        "RuView",
        "bytedance/deer-flow",
        "insanely-fast-whisper",
        "agentscope-ai/agentscope",
        "twentyhq/twenty",
    ],
    'Lobsters': [
        "vim-classic: Vim 8.x maintenance",
        "Shell Tricks That Make Life Easier",
        "Mojo's not (yet) Python",
        "Fedora moving to Forgejo",
        "Electric Motorcycles Security",
        "Using FireWire on Raspberry Pi",
        "Engineers promoted for simple code",
        "Large-scale deanonymization with LLMs",
        "$500 GPU outperforms Claude Sonnet",
        "GitHub Copilot data usage policy updates",
    ],
    'TechCrunch': [
        "Open source funding problem solutions",
        "AI agents startup trend",
        "Apple Mac Pro discontinuation",
    ],
    'The Verge AI': [
        "Apple discontinues Mac Pro (Intel era end)",
        "$500 GPU beats Claude Sonnet benchmarks",
        "Anthropic Pentagon supply chain issues",
        "Open source AI vs proprietary gap closing",
    ],
    'MIT Tech Review': [
        "Open source AI challenging Big Tech",
        "Smaller efficient AI models race",
        "GitHub to Codeberg migration importance",
    ],
    'Arxiv CS.AI': [
        "HyperAgents self-improving architectures",
        "Large-scale LLM deanonymization",
        "RAG systems from zero to production",
    ],
    'Product Hunt': [
        "Claude Code AI assistant",
        "Fast Whisper speech recognition",
        "AgentScope multi-agent framework",
    ],
    'Hacker Noon': [
        "GitHub to Codeberg migration guide",
        "AI agents on VPS automation",
        "OpenTelemetry alpha release",
    ],
}

# 手动识别的共性主题
common_themes = [
    {
        'theme': 'AI代理与自动化 (AI Agents & Automation)',
        'sources': ['Hacker News', 'GitHub Trending', 'The Verge AI', 'Arxiv CS.AI', 'Product Hunt', 'Hacker Noon'],
        'description': 'AI代理框架、自动化工具和VPS部署成为热点。Claude Code、AgentScope等工具蓬勃发展,开发者关注AI agents的实际应用。',
        'keywords': 'AI Agents, Claude, Automation, VPS, Multi-agent Framework',
        'evidence': [
            'Hacker News: AI agent on $7 VPS',
            'GitHub: oh-my-claudecode, AgentScope',
            'Product Hunt: Claude Code',
            'Hacker Noon: AI agents on VPS',
            'Arxiv: HyperAgents'
        ]
    },
    {
        'theme': 'Apple Mac Pro 停产 (Apple Discontinues Mac Pro)',
        'sources': ['Hacker News', 'TechCrunch', 'The Verge AI'],
        'description': 'Apple正式停产Mac Pro,标志着Intel时代的彻底结束。这一决定引发了开发者社区的广泛讨论。',
        'keywords': 'Apple, Mac Pro, Discontinuation, Intel Era',
        'evidence': [
            'Hacker News: Apple Discontinues Mac Pro',
            'TechCrunch: Apple Mac Pro discontinuation',
            'The Verge: Apple discontinues Mac Pro'
        ]
    },
    {
        'theme': '开源AI追赶闭源模型 (Open Source AI Closing Gap)',
        'sources': ['The Verge AI', 'MIT Tech Review', 'Lobsters', 'GitHub Trending'],
        'description': '开源AI模型在性能和成本效益上快速追赶闭源系统。$500 GPU即可超越Claude Sonnet编码基准,显示开源生态的强劲势头。',
        'keywords': 'Open Source AI, GPU, Benchmarks, Performance',
        'evidence': [
            'Lobsters: $500 GPU outperforms Claude Sonnet',
            'The Verge: Open source AI closing gap',
            'MIT Review: Open source AI challenging Big Tech',
            'GitHub: deer-flow, fast-whisper'
        ]
    },
    {
        'theme': '代码托管平台迁移 (GitHub to Codeberg Migration)',
        'sources': ['Hacker News', 'Lobsters', 'MIT Tech Review', 'Hacker Noon'],
        'description': '开发者社区对GitHub的垄断地位表示担忧,Codberg等去中心化替代方案获得关注。Fedora等大型项目也开始迁移。',
        'keywords': 'GitHub, Codeberg, Migration, Forgejo',
        'evidence': [
            'Hacker News: Moving from GitHub to Codeberg',
            'Lobsters: Fedora moving to Forgejo',
            'MIT Review: GitHub to Codeberg importance',
            'Hacker Noon: Migration guide'
        ]
    },
    {
        'theme': 'RAG系统与LLM应用 (RAG Systems & LLM Applications)',
        'sources': ['Hacker News', 'Arxiv CS.AI', 'GitHub Trending', 'MIT Tech Review'],
        'description': '检索增强生成(RAG)系统从理论到实践的成熟,LLM在实际应用中的部署和优化成为关注焦点。',
        'keywords': 'RAG, LLM, Deployment, Optimization',
        'evidence': [
            'Hacker News: RAG system implementation',
            'Arxiv: RAG from zero to production',
            'GitHub: AgentScope, fast-whisper',
            'MIT Review: Smaller efficient AI models'
        ]
    }
]

# 生成报告
def generate_report():
    print("# 今日AI热点 - 2026-03-27")
    print()
    print("## 🔥 Top 5热点")
    print()
    
    for i, theme in enumerate(common_themes, 1):
        sources_list = ', '.join(theme['sources'])
        print(f"### {i}. {theme['theme']} [{len(theme['sources'])}个来源]")
        print(f"🔥 {sources_list}")
        print()
        print(theme['description'])
        print()
        print(f"**关键词**: {theme['keywords']}")
        print()
        
        # 添加证据
        if theme['evidence']:
            print("**证据**:")
            for evidence in theme['evidence'][:3]:
                print(f"- {evidence}")
        print()
        print("---")
        print()
    
    print("## 📊 数据来源")
    print(f"- 信息源数量: 9个")
    print(f"- 共性消息: 5条")
    print(f"- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"- 时区: Asia/Shanghai")
    print()
    print("## 🔍 分析说明")
    print("本报告基于以下9个信息源的交叉分析生成:")
    print("1. Hacker News - 技术讨论社区")
    print("2. GitHub Trending - 开源项目热度")
    print("3. Lobsters - 技术新闻聚合")
    print("4. TechCrunch Open Source - 科技媒体")
    print("5. The Verge AI - AI垂直媒体")
    print("6. MIT Technology Review - 技术评论")
    print("7. Arxiv CS.AI - 学术前沿")
    print("8. Product Hunt - 产品发布平台")
    print("9. Hacker Noon - 开发者社区")
    print()
    print("📌 **共性识别标准**: 同一话题在2个及以上信息源中出现")

if __name__ == "__main__":
    generate_report()
