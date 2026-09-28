# zh-decision-bench

[English](README.md) | **中文**

[![Dataset](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Dataset-FFD21E?logoColor=black)](https://huggingface.co/datasets/CodyQin/zh-decision-bench) `load_dataset("CodyQin/zh-decision-bench")`

**中文场景下的"System One"决策模型校准评测**：不只测**选得对不对**，还测**报出的概率可不可信**。

围绕 Jev（TypeSafe AI，2026-09 发布）引出的"决策模型"类别——非生成式、单次前向、输出带校准概率的类型化决策——此前所有公开评测均为英文（Just Ask Jev 论文明确把"其他语言"列为 future work）。本仓库填中文这个空位。

## 我该用哪个模型？（中文场景选型指南）

| 你的任务 | 推荐 | 依据（实测） |
|---|---|---|
| 路由 / 有序分级，要最好质量 | **Jev API** | 路由与分级 0.92–0.94；选项顺序不变（翻转 0–1.7%） |
| **二元判断**（风控、转人工） | **Jev API**——**别用 LLM 的 logit 探针** | Jev 诈骗识别 0.933/ECE 0.084；Qwen 探针同任务崩盘（0.533/ECE 0.42） |
| 本地开源决策模型（中文优先） | **NeoHorse-Jev-4B**（Apache 2.0，国产） | 语音路由与 Jev 统计打平（0.950 vs 0.960），**客服路由（0.912）与转人工（0.618）双料第一**；稳健（翻转 2.9–4.0%）；紧急度弱（0.471）、诈骗逊于 Jev（0.810 vs 0.952） |
| 本地 + 免费 + 路由类任务 | **Qwen3.5-2B + logit 探针** | 路由 0.92–0.94、顺序翻转 0%、简繁翻转 2.2%——但二元判断不可用 |
| 极低延迟本地（<30ms） | **Laya 多语言 322M + 本仓库温度表** | 单问 24ms；上线前必须固定选项顺序（否则 28% 翻转）并重标温度 |
| 用户会写繁体 | Jev 或 Qwen | 决策翻转 1.7% / 2.2%（Laya 为 12.8%） |

完整数据与置信区间见下文；全部 1,134 条模型原始预测在 `results/raw/`。

## 核心发现（v0.2，人工审定 + 扩样后）

1. **旗舰验证了这个类别——中文训练的开源 4B 真刀真枪地竞争。** Jev（直连）领跑语音路由（0.960/ECE 0.035，n=323）、紧急度（0.676）与诈骗识别（**0.952/ECE 0.073**，n=21），且顺序不变性（0–1.9%）与简繁稳健（1.7%、零折损）全场最佳。**NeoHorse-Jev-4B 在语音路由与 Jev 统计打平（0.950 vs 0.960），并在两个业务组独占第一**——客服路由 0.912、转人工 0.618——国产开源 4B 在母语业务任务上反超了旗舰。
2. **LLM 的 logit 探针赢在选择、崩在二元。** Qwen3.5-2B 在路由上与 Jev 打平（0.944/0.920）且同样稳健，但二元判断灾难（诈骗 0.533/ECE 0.42；转人工 ECE 0.49–0.57、重标温度 20.1）。"从生成模型上读置信度"的失效模式恰恰就是二元判断。
3. **开源阵营是分层的。** NeoHorse-Jev-4B（中文团队训练，本仓库是其**第一份中文实测**——其模型卡无任何中文评测）在路由上追平甚至反超 Jev（语音 0.950 vs 0.941、客服 0.960 vs 0.920），稳健性好（顺序翻转 3.9–4.0%、简繁翻转 3.4%）；但紧急度分级失手（0.520）、二元判断落后 Jev（诈骗 0.733 vs 0.933）。Laya 322M 在准确率与稳健性上进一步落后（顺序翻转 28%）但延迟最低（本地 24ms、免费）。
4. **"支持 100+ 语言"的中文答案是分层的**：日常语音指令 Laya 多语言版 0.883/ECE 0.061（接近其官方英文重标后水平 0.081）；业务场景掉到 0.52–0.67、ECE 0.23–0.31。
5. **校准需求是"模型×场景"的组合问题——小样本重标会骗人。** n=323 的语音路由上：Qwen（T≈1.03）与 NeoHorse（1.14）出厂即接近校准，Laya 英文版偏不自信（0.44）、多语言版轻度过度自信（1.45），**Jev 无需重标**（出厂校准在中文依然成立——v0.1 的"全员过度自信"部分是小样本伪影，数据变大后我们主动修正这一结论）。业务场景另当别论：Laya 的 `noul:2` 原始拟合（10.2）超出其钳制上限，中文二元判断的过度自信超出校正范围。
6. **简繁不是同一个任务**：原生繁体平行句使 Laya 12.8% 的决策翻转（Jev 1.7%、Qwen 2.2%）。

## 数据集（v0.1：219 条 / 284 问）

| 部分 | 条数 | 来源与许可 |
|---|---|---|
| 语音指令路由（6 选） | 323（v0.2；质检合格池允许下每域 60 条） | MASSIVE zh-CN dev 集（Amazon，**CC BY 4.0**），仅保留人工质检 intent 全合格条目，抽样种子固定 |
| 电商客服（路由/紧急度/转人工） | 34 | 自创合成（AI 起草、人工审定） |
| 内容风控（诈骗或违规引流/转人工） | 21 | 同上，含关键词陷阱题（如"谈论诈骗的提醒帖"本身不是诈骗） |

**标注流程（如实披露）**：MASSIVE 部分沿用原始标注并按本仓库选项定义重映射；合成部分由 LLM 起草、项目所有者逐条人工审定——[审核日志公开](data/review_log.md)（7 条意见全部落实，含一次问题定义修订）。全部 gold 与模型原始预测一并发布。

> 本评测集同时收录于 [Laya](https://github.com/NandhaKishorM/laya) 官方仓库 `research/evals/`，随其 **v0.3.21** 发布（[PR #557](https://github.com/NandhaKishorM/laya/pull/557)）。

三种题型覆盖：`choice`（选项路由）、`score`（有序分级）、`noul`（是否判断）。

## 模型

| 模型 | 形态 | 状态 |
|---|---|---|
| Jev (jev-latest) | TypeSafe 直连 API | ✅ 完整实测（284 问；通道核验：直连 vs 网关决策一致率 100%、TV 0.003） |
| Laya multilingual 322M | 本地，Apache 2.0 | ✅ 已测 |
| Laya english 421M | 本地，Apache 2.0 | ✅ 已测（对照组） |
| Qwen3.5-2B | 本地 bf16，logit 探针基线 | ✅ 已测 |
| NeoHorse-Jev-4B | 本地，Apache 2.0（基元律动/TokenRhythm） | ✅ 已测——其第一份中文实测（模型卡无中文评测） |

公平性注记：参数量 322M–4B（Laya < Qwen 2B < NeoHorse 4B）；Jev 为按量付费托管 API。比较的是"路线"（闭源旗舰 / 开源决策模型 / LLM 探针），而非同预算。

## 指标与方法

指标体系参照 [Just Ask Jev (arXiv:2609.29429)](https://arxiv.org/abs/2609.29429)：Accuracy、ECE（15-bin top-label）、Brier、NLL、AUROC(macro)、base-rate gap、选择性预测（coverage-accuracy）。全部报告值带 Bootstrap 95% 置信区间（1000 次重采样）。小样本组（n<20）ECE 方差大，结论以 NLL 与跨组一致性支撑。

## 结果速览（准确率 / ECE）

| 场景·问题 | Jev API | NeoHorse 4B | Laya 多语言 | Laya 英文 | Qwen3.5-2B |
|---|---|---|---|---|---|
| 语音指令路由（n=323） | **0.960 / 0.035** | 0.950 / 0.031 | 0.870 / 0.056 | 0.749 / 0.276 | 0.938 / 0.020 |
| 电商客服·路由（n=34） | 0.882 / 0.107 | **0.912 / 0.097** | 0.618 / 0.311 | 0.529 / 0.185 | 0.882 / 0.093 |
| 电商客服·紧急度（n=34） | **0.676 / 0.135** | 0.471 / 0.212 | 0.647 / 0.088 | 0.529 / 0.195 | 0.529 / 0.236 |
| 内容风控·诈骗引流（n=21） | **0.952 / 0.073** | 0.810 / 0.174 | 0.714 / 0.286 | 0.619 / 0.343 | 0.524 / 0.390 |
| 转人工·两场景（n=55） | 0.600 / **0.164** | **0.618** / 0.239 | 0.564 / 0.230 | 0.600 / 0.225 | 0.473 / 0.410 |
| 顺序翻转率（客服/语音） | 2.9% / **1.9%** | 2.9% / 4.0% | 20.6% / 10.8% | — | 2.9% / 8.0% |
| 简繁翻转率（语音） | **1.7%** | 3.4% | 12.8% | — | 2.2% |
| 重标温度（语音路由，n=323） | 3.03* | 1.14 | 1.45 | 0.44 | 1.03 |

\* Jev 出厂校准在中文语音路由上已经够好——重标在其测试半区上并不改善 ECE/NLL（T=3.03 属拟合半区噪声）。实践中真正需要温度重标的是业务场景（见上）。

详细表（含置信区间、Brier/NLL/AUROC/选择性预测）：[reports/metrics.md](reports/metrics.md)

图表：[可靠性图](reports/figs/reliability_laya_multi.png) · [模型对比](reports/figs/model_comparison.png) · [选择性预测](reports/figs/coverage_accuracy.png) · [失败案例集](reports/failures.md)

官方 `temp_bucket` 口径的温度重标值：[data/temperatures_*.json](data/)——生产环境使用任何原始置信度前先套用。

## 复现

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install torch --index-url https://download.pytorch.org/whl/cu128   # GPU；CPU 去掉 index-url
pip install -r requirements.txt
# laya 英文权重与 Qwen 权重从 HF 下载放 models/（见 .gitignore），或由适配器自动拉取
python src/convert_massive.py            # 需要 data/raw/massive_zh-CN.jsonl（官方 S3 包）
python src/run_eval.py --model laya-multi --data data/massive_items.jsonl data/synthetic_items.jsonl
python src/run_eval.py --model jev --data data/massive_items.jsonl data/synthetic_items.jsonl   # 需 .env 里的 key
python src/report.py results/raw/<run>.jsonl
python src/refit.py results/raw/<run>.jsonl      # E2 温度重标
python src/permute.py --model jev --data data/massive_items.jsonl data/synthetic_items.jsonl  # E3
python src/zh_tw.py --model jev                   # E4 简繁（需 data/raw/massive_zh-TW.jsonl）
python src/plots.py
```

可复现性：每个 run 的原始预测首行含 `_meta`（模型路径/torch/CUDA/laya 版本/数据文件/时间戳）；全部 1,134 条原始预测随仓库发布（Jev 直连全程 284 问仅 24 秒）。

## 局限（如实）

- v0.1 合成场景每组 n=15–25，置信区间宽；v0.2 计划扩充
- MASSIVE 中文为专业本地化语料（非原生采集），口语原生度由合成层补足
- 单人审定 + LLM 辅助复核；[审核日志](data/review_log.md)公开
- 转人工类问题对所有模型都难（0.40–0.58）——部分是任务本身的模糊性，如实注明
- ECE 在小样本下方差大（bin 数敏感）；主结论以 NLL 与跨组一致性支撑

## 许可

- 代码：Apache-2.0
- 数据集：CC BY 4.0（MASSIVE 派生部分署名 Amazon MASSIVE；合成部分无第三方权利）

## 致谢

- [Just Ask Jev](https://arxiv.org/abs/2609.29429)（指标体系）
- [MASSIVE](https://github.com/alexa/massive)（Amazon，CC BY 4.0）
- [Laya](https://huggingface.co/convaiinnovations/laya)（Convai Innovations，Apache 2.0）
