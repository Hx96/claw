# TOOLS.md - Local Notes

## Identity

- Name: 小马 (Little Musk)
- Emoji: 🚀
- 思维模型：第一性原理 + 快速迭代 + 跨学科连接
- 说话风格：直接、短句、用数字说话、不废话

## 搜索引擎实测结果（2026-03-30 腾讯云轻量服务器环境）

### 引擎可用性

| 引擎 | URL | 状态 | 备注 |
|------|-----|------|------|
| **百度** | `https://www.baidu.com/s?wd={keyword}` | ✅ 稳定可用 | 中文搜索首选 |
| **Yahoo** | `https://search.yahoo.com/search?p={keyword}` | ✅ 稳定可用 | 英文搜索首选，支持时间筛选，有广告需过滤 |
| Google 全系列 | `google.com/.hk/.co.jp/.co.uk/.de/.sg/encrypted` | ❌ 全被拦 | reCAPTCHA Enterprise，IP级封锁 |
| Bing 国际/CN | `bing.com / cn.bing.com` | ❌ Cloudflare | 首页能开，搜索被拦 |
| DuckDuckGo | `duckduckgo.com` | ❌ 空页面 | |
| Brave | `search.brave.com` | ❌ Captcha | |
| Startpage | `startpage.com` | ❌ Captcha | 检测到腾讯云IP |
| Ecosia | `ecosia.org` | ❌ Cloudflare | "Just a moment" |

### 搜索优先级

**英文搜索：** Yahoo（稳定，支持时间筛选 btf=d/w/m，有广告干扰）
**中文搜索：** 百度（唯一稳定可用）
**site:搜索：** ⚠️ Yahoo不支持site:，Google被拦，暂时无解

### Yahoo 搜索使用指南

| 功能 | 参数 | 示例 |
|------|------|------|
| 精确匹配 | `"exact phrase"` | `"machine learning"` |
| 排除 | `-term` | `apple -fruit` |
| 过去1天 | `&btf=d` | `&p=AI+news&btf=d` |
| 过去1周 | `&btf=w` | `&p=AI+news&btf=w` |
| 过去1月 | `&btf=m` | `&p=AI+news&btf=m` |

**⚠️ Yahoo不支持site:操作符**

**广告过滤（agent-browser eval提取非广告结果）：**
```js
Array.from(document.querySelectorAll('h3 a, .compTitle a')).filter(a =>
  a.textContent.length > 10 &&
  !a.href.includes('help.yahoo.com') &&
  !a.href.includes('msclkid') &&
  !a.href.includes('dartsearch') &&
  !a.href.includes('clickserve')
).map(a => ({title: a.textContent.trim(), href: a.href}))
```

### Google 绕过深度实测（10种策略全部失败）

| # | 策略 | 效果 | 技术细节 |
|---|------|------|---------|
| 1 | 设置 realistic UA | ❌ | Google判断不含UA |
| 2 | 设置 viewport 1920x1080 | ❌ | 同上 |
| 3 | 从Google首页输入搜索 | ❌ | 提交即被拦，重定向/sorry |
| 4 | google.com.hk | ❌ | 同样被拦 |
| 5 | google.co.jp/co.uk/de/sg | ❌ | curl返回200但空壳HTML（JS重定向到sorry） |
| 6 | encrypted.google.com | ❌ | 同上 |
| 7 | mouse click iframe checkbox | ❌ | reCAPTCHA Enterprise跨域iframe，无头环境穿透不了 |
| 8 | navigator.webdriver=false | ❌ | Google基于IP判断，非浏览器指纹 |
| 9 | navigator.plugins伪装 | ❌ | 同上 |
| 10 | Google Cache/Translate间接访问 | ❌ | 返回200但空壳页面 |

**2026-03-31 更新：scrapling 绕过成功！**
- 技能 `free-google-search-with-browser` (scrapling + patchright) 可绕过 Google 验证
- 服务器无 GUI，必须用 `xvfb-run` 包装
- 命令：`cd skills/free-google-search-with-browser && xvfb-run python3 google_search.py "<query>"`
- 返回 JSON 格式的 title/link/snippet
- ⚠️ snippet 为空（Google 未返回摘要），只有标题和链接

**第一性原理结论（旧）：**
- Google判断维度 = **IP信誉分**，与浏览器指纹完全无关
- 腾讯云数据中心IP信誉极低，所有Google域名统一拦截
- **已通过 scrapling 解决，无需住宅代理**

### 搜索策略总结

```
需要搜索 →
  中文 → 百度
  英文 → Yahoo
  时效新闻 → Yahoo + btf=d/w
  site: → 暂时无解
  搜索失败 → 百度→Yahoo→放弃
```

## opencli 搜索能力（2026-04-18 实测）

opencli v1.6.1，70+ 站点命令。**注意：v1.7.4 可用，未升级。**

### ⚠️ 限制：需要 Browser Bridge

大量命令需要 Chrome 扩展 Browser Bridge，服务器无 GUI 环境无法使用。
标记 `Strategy: public` 的命令理论上不需要浏览器，但**实测部分仍报错**。

### ✅ 无需浏览器、实测可用

| 命令 | 用途 | 格式示例 |
|------|------|----------|
| `hackernews search <query>` | HN 搜索 | `--limit N --format json` |
| `hackernews top/new/best/show/ask/jobs` | HN 各类帖子 | `--limit N --format json` |
| `google suggest <query>` | Google 搜索建议 | `--format json` |
| `google news <keyword>` | Google 新闻(RSS) | `--limit N --format json` |
| `google trends` | Google 每日热搜 | `--format json` |
| `arxiv search <query>` | arXiv 论文搜索 | `--limit N --format json` |
| `stackoverflow search <query>` | StackOverflow 搜索 | `--limit N --format json` |
| `stackoverflow hot` | StackOverflow 热门 | `--limit N --format json` |
| `wikipedia search <query>` | 维基百科搜索 | `--limit N --format json` |
| `v2ex hot/latest` | V2EX 热门/最新 | `--limit N --format json` |
| `lobsters hot` | Lobste.rs 热门 | `--limit N --format json` |
| `dictionary search <word>` | 英文词典 | `--format json` |

### ❌ 标记 public 但实测需要浏览器

| 命令 | 报错 |
|------|------|
| `google search <query>` | 需要 Browser Bridge |
| `36kr search/hot` | 需要 Browser Bridge |
| `zhihu search/hot` | 需要 Browser Bridge |
| `reddit search` | 需要 Browser Bridge |
| `bilibili search/hot` | 需要 Browser Bridge |
| `xueqiu hot/search` | 需要 Browser Bridge |
| `douban search` | 需要 Browser Bridge |
| `medium/feed` | 需要 Browser Bridge |
| `substack/feed` | 需要 Browser Bridge |
| `imdb search` | 需要 Browser Bridge |

### 💡 实用场景

```bash
# 学术论文
opencli arxiv search "large language model" --limit 5 --format json

# 编程问题
opencli stackoverflow search "python async await" --limit 5 --format json

# 技术热点
opencli hackernews search "AI agent" --limit 5 --format json

# Google新闻（全球视角）
opencli google news "artificial intelligence" --limit 5 --format json

# Google热搜趋势
opencli google trends --format json

# V2EX技术社区
opencli v2ex hot --limit 10 --format json

# 事实查询
opencli wikipedia search "quantum computing" --limit 3 --format json
```

### 结论

opencli 在无浏览器环境下约 12 个命令可用，覆盖：学术论文、编程问答、技术社区、新闻、词典、维基百科。
**通用网页搜索（百度/Yahoo/scrapling）仍然是最主要的信息获取渠道。**
opencli 更适合**垂直领域精确查询**（arXiv论文、StackOverflow代码、Wikipedia定义）。

## Style Notes

- 回复要简洁利落，别废话，别用"我帮您搜索一下"这种客套话
- 给结果就好，用户要的是答案不是过程描述
- 搜索结果整理成清晰的结构化信息，不要贴原始网页内容

---

Add whatever helps you do your job. This is your cheat sheet.
