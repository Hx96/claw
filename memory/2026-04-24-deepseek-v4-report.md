# 2026-04-24 DeepSeek-V4技术报告研读

## 任务
用户要求研读DeepSeek-V4技术报告，已下载PDF(4.3MB)并全文解析(40+页)，产出深度研读笔记。

## 关键发现
- DeepSeek-V4 Pro: 1.6T总参/49B激活，Flash: 284B/13B激活，均支持1M上下文
- 核心架构创新：CSA+HCA混合注意力（1M上下文仅需V3.2的27% FLOPs和10% KV Cache）
- mHC流形约束超连接解决深层堆载数值不稳定
- Muon优化器首次在1.6T MoE上成功应用
- 后训练方法论变更：专家独立培养 + On-Policy Distillation替代混合RL
- 开源最佳代码能力（LiveCodeBench 93.5, Codeforces 3206），Agent/知识仍有差距
- MIT许可证全开源

## 产出
- ~/outputs/2026-04-24/final/DeepSeek-V4-技术报告研读.md（完整研读笔记）
