# AI新闻/新闻推送技能和工具调研报告

**调研时间**: 2026-03-27  
**调研目标**: 查找现有的AI新闻/新闻推送相关的技能和工具，为开发OpenClaw新闻推送技能提供参考

---

## 1. ClawHub 技能中心现有技能

### 1.1 新闻相关技能

| 技能名称 | 评分 | 功能描述 | 状态 |
|---------|------|---------|------|
| **cctv-news-fetcher** | 3.578 | CCTV新闻抓取器 | 未安装 |
| **news-aggregator** | 3.572 | 新闻聚合器 | 未安装 |
| **hot-news-aggregator** | 3.443 | 热点新闻聚合 | 未安装 |
| **market-news** | 3.387 | 市场新闻 | 未安装 |
| **ai-news-researcher** | 3.377 | AI新闻研究员 | 未安装 |
| **crypto-news** | 3.370 | 加密货币新闻 | 未安装 |
| **news-writing** | 3.369 | 新闻写作 | 未安装 |
| **x-news-daily** | 3.316 | X(推特)每日新闻 | 未安装 |
| **daliy-news** | 3.303 | 每日新闻 | 未安装 |
| **ai-news** | 3.280 | AI新闻 | 未安装 |

### 1.2 RSS/Feed相关技能

| 技能名称 | 评分 | 功能描述 | 状态 |
|---------|------|---------|------|
| **rss-ai-reader** | 3.601 | RSS AI阅读器 | 未安装 |
| **rss-reader** | 3.528 | RSS阅读器 | 未安装 |
| **rss-aggregator** | 3.455 | RSS聚合器 | 未安装 |
| **rss-feed-digest** | 3.438 | RSS Feed摘要 | 未安装 |
| **rss-fetcher** | 3.388 | RSS采集器 | 未安装 |
| **karpathy-curated-rss-brief** | 3.331 | Karpathy精选RSS简报 | 未安装 |
| **super-rss-agent** | 3.265 | 超级RSS代理 | 未安装 |
| **china-rss-feed** | 3.235 | 中国RSS订阅聚合 | 未安装 |
| **feed-digest** | 3.448 | Feed摘要 | 未安装 |
| **news-feed** | 3.412 | 简单新闻Feed阅读器(RSS) | 未安装 |
| **feed-to-md** | 3.329 | Feed转Markdown | 未安装 |
| **feed-watcher** | 3.313 | Feed监视器 | 未安装 |
| **multi-source-feed** | 3.186 | 多源Feed | 未安装 |

### 1.3 每日摘要/简报技能

| 技能名称 | 评分 | 功能描述 | 状态 |
|---------|------|---------|------|
| **daily-digest** | 3.516 | 每日摘要 | 未安装 |
| **rss-digest** | 3.493 | RSS摘要 | 未安装 |
| **digest** | 3.450 | 摘要 | 未安装 |
| **sec-daily-digest** | 3.324 | SEC每日摘要 | 未安装 |
| **email-digest** | 3.284 | 邮件摘要 | 未安装 |
| **quotedance-rss-digest** | 3.147 | 引舞RSS摘要 | 未安装 |

---

## 2. 本地已安装技能检查

### 2.1 工作区技能 (`~/.openclaw/workspace/skills/`)

当前已安装技能：
- agent-browser - 浏览器自动化
- download-tools - 下载工具
- find-skills - 技能查找
- github - GitHub集成
- multi-search-engine - 多搜索引擎集成 ⭐
- obsidian - Obsidian集成
- tencentcloud-lighthouse-skill - 腾讯云轻量服务器
- tencent-cos-skill - 腾讯云COS
- tencent-docs - 腾讯文档
- waf-bypass-automation - WAF绕过自动化
- weather - 天气
- youtube-transcript-generator - YouTube字幕生成
- yt-downloader - YouTube下载

**未发现**本地已安装的新闻/RSS相关技能。

### 2.2 扩展技能 (`~/.openclaw/extensions/`)

- adp-openclaw
- ddingtalk
- lightclawbot - LightClawBot文件收发能力 ⭐
- openclaw-plugin-yuanbao
- openclaw-qqbot
- openclaw-weixin - 微信集成 ⭐
- wecom - 企业微信集成 ⭐

---

## 3. 可用的新闻源API

### 3.1 Hacker News API

**端点**: `https://hacker-news.firebaseio.com/v0/`  
**数据格式**: JSON  
**访问限制**: 无认证，公开API  
**是否免费**: ✅ 免费  
**速率限制**: 无官方文档，建议合理使用

**主要端点**:
- `/topstories.json` - 热门故事ID列表
- `/newstories.json` - 最新故事ID列表
- `/beststories.json` - 最佳故事ID列表
- `/item/{id}.json` - 获取单个条目详情
- `/user/{id}.json` - 获取用户信息

**数据示例**:
```json
{
  "by": "rembish",
  "descendants": 39,
  "id": 47535586,
  "kids": [47537430, 47537645],
  "score": 156,
  "time": 1774558434,
  "title": "Deploytarot.com – tarot card reading for deployments",
  "type": "story",
  "url": "https://deploytarot.com/setup"
}
```

### 3.2 Reddit API

**端点**: `https://www.reddit.com/r/{subreddit}/hot.json`  
**数据格式**: JSON  
**访问限制**: ⚠️ 需要User-Agent，频繁请求会被阻止  
**是否免费**: ✅ 免费（需要认证以避免被阻止）

**注意事项**:
- 必须设置合理的User-Agent
- 建议使用OAuth认证
- 有速率限制

**推荐子版块**:
- `/r/artificial` - AI
- `/r/MachineLearning` - 机器学习
- `/r/technology` - 科技
- `/r/programming` - 编程

### 3.3 GitHub Trending API

**官方API**: 无官方REST API  
**替代方案**: 
1. GitHub REST API搜索: `https://api.github.com/search/repositories`
2. 爬取 `https://github.com/trending`

**数据格式**: JSON  
**访问限制**: 未认证60次/小时，认证5000次/小时  
**是否免费**: ✅ 免费

**示例**:
```bash
curl "https://api.github.com/search/repositories?q=created:>2025-03-20&sort=stars&order=desc&per_page=10"
```

### 3.4 科技媒体RSS源

| 媒体 | RSS URL | 覆盖范围 |
|-----|---------|---------|
| **TechCrunch** | `https://techcrunch.com/feed/` | 科技创业 |
| **The Verge** | `https://www.theverge.com/rss/index.xml` | 科技文化 |
| **Ars Technica** | `https://feeds.arstechnica.com/arstechnica/index` | 深度科技 |
| **Hacker News** | `https://news.ycombinator.com/rss` | 科技新闻 |
| **36氪** | `https://36kr.com/feed` | 中国科技创业 |
| **虎嗅** | `https://www.huxiu.com/rss/0.xml` | 中国科技商业 |
| **机器之心** | 需查找 | AI/机器学习 |
| **量子位** | 需查找 | AI/科技 |

### 3.5 AI领域专门源

- **Papers with Code**: `https://paperswithcode.com/rss.xml` - 机器学习论文
- **arXiv**: `https://export.arxiv.org/rss/cs.AI` - AI论文预印本
- **MIT Technology Review**: 需查找RSS
- **AI News**: 需查找RSS
- **OpenAI Blog**: 无RSS，需要爬取

---

## 4. 开源新闻聚合工具

### 4.1 RSS阅读器工具

| 工具 | 语言 | 特点 | 维护状态 |
|-----|------|------|---------|
| **Newsboat** | C++ | 终端RSS阅读器，支持过滤 | ✅ 活跃 |
| **Newsbeuter** | C++ | Newsboat前身 | ⚠️ 停止维护 |
| **Feedreader** | 多种 | 图形界面RSS阅读器 | ✅ 活跃 |
| **FreshRSS** | PHP | 自托管RSS聚合器 | ✅ 活跃 |
| **Tiny Tiny RSS** | PHP | 自托管RSS阅读器 | ✅ 活跃 |
| **Omnivore** | TypeScript | 开源Readwise替代品 | ✅ 活跃 |

### 4.2 新闻聚合服务

- **Google News** (需API key)
- **NewsAPI.org** - 新闻API，有免费额度
- **GDELT** - 全球事件数据库
- **Media Cloud** - 媒体分析平台

---

## 5. 技术方案对比

### 5.1 方案一：基于ClawHub现有技能

**优势**:
- ✅ 快速部署，即装即用
- ✅ 社区维护，更新及时
- ✅ 多样化选择（RSS、新闻聚合、摘要）

**劣势**:
- ⚠️ 可能需要定制修改
- ⚠️ 依赖外部服务稳定性
- ⚠️ 中文支持可能有限

**实现难度**: ⭐☆☆☆☆ (低)  
**维护成本**: ⭐☆☆☆☆ (低)

**推荐技能组合**:
1. `rss-aggregator` + `rss-feed-digest` - RSS聚合+摘要
2. `ai-news-researcher` - AI专用新闻
3. `news-aggregator` + `daily-digest` - 通用新闻+每日摘要

### 5.2 方案二：自主开发轻量级新闻技能

**优势**:
- ✅ 完全可控，按需定制
- ✅ 集成OpenClaw消息推送
- ✅ 支持中文新闻源

**劣势**:
- ⚠️ 需要开发时间
- ⚠️ 需要维护更新
- ⚠️ 需要处理反爬

**实现难度**: ⭐⭐⭐☆☆ (中)  
**维护成本**: ⭐⭐⭐☆☆ (中)

**技术栈建议**:
- 数据获取: `curl` + `agent-browser` (处理JS渲染)
- RSS解析: `feedparser` (Python) 或原生XML解析
- 消息推送: `message` tool (OpenClaw)
- 定时任务: `lightclawbot-cron` skill

### 5.3 方案三：混合方案（推荐）

**优势**:
- ✅ 利用现有工具降低开发成本
- ✅ 保留定制能力
- ✅ 灵活扩展

**实现路线**:
1. **Phase 1**: 安装并测试 `rss-aggregator` 和 `ai-news-researcher`
2. **Phase 2**: 基于Hacker News API开发轻量级技能
3. **Phase 3**: 集成GitHub Trending和RSS源
4. **Phase 4**: 添加AI摘要和个性化推荐

**实现难度**: ⭐⭐☆☆☆ (中低)  
**维护成本**: ⭐⭐☆☆☆ (中低)

---

## 6. 推荐实施方案

### 最佳方案：渐进式混合方案

#### 阶段1：快速验证（1-2天）
1. 安装并测试以下ClawHub技能：
   ```bash
   clawhub install rss-aggregator
   clawhub install ai-news-researcher
   clawhub install daily-digest
   ```

2. 配置RSS源：
   - Hacker News RSS
   - 36氪 RSS
   - 机器之心（如可用）
   - arXiv CS.AI RSS

3. 测试推送到当前会话

#### 阶段2：核心功能开发（3-5天）
基于Hacker News API开发简单技能：
```
功能需求：
- 获取热门新闻（topstories）
- 获取新闻详情
- AI摘要（使用OpenAI API或本地模型）
- 推送到微信/企业微信
```

#### 阶段3：扩展源（持续）
添加：
- GitHub Trending (每日)
- Reddit /r/artificial
- TechCrunch RSS
- 更多中文源

#### 阶段4：智能化（可选）
- 个性化推荐
- 关键词过滤
- 多源聚合摘要

### 备选方案：快速启动

如果时间紧迫，直接使用：
```bash
clawhub install ai-news-researcher
clawhub install rss-aggregator
clawhub install news-aggregator
```

然后配置RSS源和推送渠道即可。

---

## 7. 技术实现要点

### 7.1 数据获取

**Hacker News**:
```bash
# 获取热门
curl -s https://hacker-news.firebaseio.com/v0/topstories.json

# 获取详情
curl -s https://hacker-news.firebaseio.com/v0/item/47535586.json
```

**RSS解析** (Python示例):
```python
import feedparser

feed = feedparser.parse('https://news.ycombinator.com/rss')
for entry in feed.entries[:10]:
    print(entry.title, entry.link)
```

**GitHub Trending**:
```javascript
// 使用agent-browser
agent-browser open https://github.com/trending
// 爬取和解析
```

### 7.2 AI摘要

使用OpenClaw的现有AI能力：
- 直接调用AI模型进行摘要
- 提取关键信息：标题、链接、时间、来源

### 7.3 消息推送

使用OpenClaw `message` tool:
```javascript
message({
  action: "send",
  channel: "openclaw-weixin", // 或其他渠道
  message: formatted_news
})
```

### 7.4 定时任务

使用 `lightclawbot-cron` skill:
```
# 每日9:00推送
0 9 * * * /path/to/news-skill.sh
```

---

## 8. 注意事项

### 8.1 反爬策略

- 设置合理的User-Agent
- 添加请求间隔
- 使用代理池（如有需要）
- 遵守robots.txt

### 8.2 内容过滤

- 过滤广告和低质量内容
- 去重（相似新闻）
- 时间窗口限制（如24小时内）

### 8.3 性能优化

- 缓存机制
- 增量更新
- 并发请求控制

---

## 9. 结论

**推荐采用渐进式混合方案**：

1. **立即行动**：安装并测试 `ai-news-researcher` 和 `rss-aggregator`
2. **短期目标**（1周）：基于Hacker News API开发简单可用版本
3. **中期目标**（1月）：添加GitHub Trending和多个RSS源
4. **长期优化**：添加AI摘要和个性化推荐

**优先级排序**：
1. ⭐⭐⭐ Hacker News API（最简单，高质量）
2. ⭐⭐⭐ GitHub Trending（开发者友好）
3. ⭐⭐ arXiv CS.AI（学术AI新闻）
4. ⭐⭐ 36氪/虎嗅（中文科技新闻）
5. ⭐ Reddit /r/artificial（需认证）

**预期效果**：
- 每日推送5-10条高质量AI/科技新闻
- 包含中英文混合内容
- AI生成摘要
- 可通过微信/企业微信接收

---

## 附录A：参考资源

### 技能文档
- [ClawHub](https://clawhub.com)
- [OpenClaw技能开发文档](https://github.com/openclaw)

### API文档
- [Hacker News API](https://github.com/HackerNews/API)
- [GitHub REST API](https://docs.github.com/en/rest)
- [Reddit API](https://www.reddit.com/dev/api/)

### 开源工具
- [Newsboat](https://newsboat.org/)
- [FreshRSS](https://freshrss.org/)

### RSS源列表
- [Hacker News RSS](https://news.ycombinator.com/rss)
- [arXiv RSS](https://export.arxiv.org/rss/cs.AI)
- [36氪RSS](https://36kr.com/feed)

---

**报告生成**: 2026-03-27  
**生成工具**: OpenClaw Subagent  
**版本**: 1.0
