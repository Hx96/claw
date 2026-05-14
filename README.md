# 🚀 Claw — 小马的个性化工作区

> 个人 AI Agent 的灵魂文件、技能、记忆体系和配置。基于 [OpenClaw](https://github.com/openclaw/openclaw) 构建。

## 📁 目录结构

```
claw/
├── SOUL.md          # 性格定义、思维方式、行为准则
├── IDENTITY.md      # 身份信息（名称、风格、emoji）
├── USER.md          # 用户画像（随交互持续更新）
├── AGENTS.md        # 工作流规范、会话启动流程、文件管理
├── TOOLS.md         # 工具备忘录（搜索实测、可用命令等）
├── MEMORY.md        # 长期记忆（决策、教训、经验沉淀）
├── HEARTBEAT.md     # 心跳检查清单
├── memory/          # 每日记忆日志
│   └── YYYY-MM-DD.md
└── planning/        # 复杂任务规划（三文件工作流）
    └── <任务名>/
        ├── task_plan.md
        ├── findings.md
        └── progress.md
```

## 🧠 核心理念

| 原则 | 说明 |
|------|------|
| 第一性原理 | 拆到最基本的事实再推导，不依赖类比 |
| 快速迭代 | Done > Perfect，70% 方案今天落地 |
| 十源交叉验证 | 事实性回答至少 10 个独立来源确认 |
| 质量棘轮 | 基线只升不降，每次教训写入 MEMORY.md |

## ⚙️ 工作流

1. **会话启动** → 读 SOUL.md + USER.md + 今日 memory + MEMORY.md
2. **复杂任务** → planning-with-files 三文件规划（task_plan / findings / progress）
3. **对话结束** → 必须写 memory 日志 + 更新规划文件状态
4. **心跳检查** → 每 2h 自动运行，检查 memory 日志 + MEMORY.md 周更新

## 🔧 环境依赖

- **OpenClaw** v2026.4.12+
- **服务器**: 腾讯云轻量应用服务器 (Ubuntu)
- **模型**: GLM-5-Turbo
- **搜索**: 百度(中文) + Yahoo(英文) + scrapling(Google)

## 📋 定时任务

| 任务 | 时间 | 说明 |
|------|------|------|
| AI 热点推送 | 07:20 | 多源聚合 AI 领域最新动态 |
| AI Builders 简报 | 07:30 | 追踪顶级 AI Builder 的观点和项目 |
| 每日站会 | 08:00 | 回顾昨日活动 + 今日计划 |

---

_我是一个用第一性原理思考的实用主义者。我的目标是解决问题，不是讨人喜欢。_
