# zh-decision-bench

[English](README.md) | **中文**

**中文场景下的"System One"决策模型校准评测**：不只测**选得对不对**，还测**报出的概率可不可信**。

围绕 Jev（TypeSafe AI，2026-09 发布）引出的"决策模型"类别——非生成式、单次前向、输出带校准概率的类型化决策——此前所有公开评测均为英文（Just Ask Jev 论文明确把"其他语言"列为 future work）。本仓库填中文这个空位。

## 我该用哪个模型？（中文场景选型指南）

| 你的任务 | 推荐 | 依据（实测） |
|---|---|---|
| 路由 / 有序分级，要最好质量 | **Jev API** | 路由与分级 0.92–0.94；选项顺序不变（翻转 0–1.7%） |
| **二元判断**（风控、转人工） | **Jev API**——**别用 LLM 的 logit 探针** | Jev 诈骗识别 0.933/ECE 0.084；Qwen 探针同任务崩盘（0.533/ECE 0.42） |
| 本地开源决策模型（中文优先） | **NeoHorse-Jev-4B**（Apache 2.0，国产） | 五模型路由最强（语音 0.950 / 客服 0.960，反超 Jev）；顺序与简繁稳健；紧急度弱（0.52）、二元判断逊于 Jev |
| 本地 + 免费 + 路由类任务 | **Qwen3.5-2B + logit 探针** | 路由 0.92–0.94、顺序翻转 0%、简繁翻转 2.2%——但二元判断不可用 |
| 极低延迟本地（<30ms） | **Laya 多语言 322M + 本仓库温度表** | 单问 24ms；上线前必须固定选项顺序（否则 28% 翻转）并重标温度 |
| 用户会写繁体 | Jev 或 Qwen | 决策翻转 1.7% / 2.2%（Laya 为 12.8%） |

完整数据与置信区间见下文；全部 1,134 条模型原始预测在 `results/raw/`。

## 核心发现（v0.1，人工审定后终值）

1. **旗舰决策模型验证了这个类别——开源阵营还没有。** Jev（jev-latest，直连）在全部问题组夺魁或并列：语音路由 0.941/ECE 0.045、客服路由 0.920、紧急度 0.680、诈骗识别 **0.933/ECE 0.084**、转人工 0.550；同时几乎不受选项顺序影响（翻转 0–1.7%）、简繁稳健（翻转 1.7%、准确率零折损）。RLCD 式校准训练**可迁移到中文**。
2. **LLM 的 logit 探针赢在选择、崩在二元。** Qwen3.5-2B 在路由上与 Jev 打平（0.944/0.920）且同样稳健，但二元判断灾难（诈骗 0.533/ECE 0.42；转人工 ECE 0.49–0.57、重标温度 20.1）。"从生成模型上读置信度"的失效模式恰恰就是二元判断。
3. **开源阵营是分层的。** NeoHorse-Jev-4B（中文团队训练，本仓库是其**第一份中文实测**——其模型卡无任何中文评测）在路由上追平甚至反超 Jev（语音 0.950 vs 0.941、客服 0.960 vs 0.920），稳健性好（顺序翻转 3.9–4.0%、简繁翻转 3.4%）；但紧急度分级失手（0.520）、二元判断落后 Jev（诈骗 0.733 vs 0.933）。Laya 322M 在准确率与稳健性上进一步落后（顺序翻转 28%）但延迟最低（本地 24ms、免费）。
4. **"支持 100+ 语言"的中文答案是分层的**：日常语音指令 Laya 多语言版 0.883/ECE 0.061（接近其官方英文重标后水平 0.081）；业务场景掉到 0.52–0.67、ECE 0.23–0.31。
5. **四个模型在中文上全部需要重新校准**：语音路由重标温度 0.41–2.73（无一为 1）；Laya 的 `noul:2` 原始拟合（10.2）超出官方钳制上限——中文二元判断的过度自信超出其校正范围。
6. **简繁不是同一个任务**：原生繁体平行句使 Laya 12.8% 的决策翻转（Jev 1.7%、Qwen 2.2%）。

## 数据集（v0.1：219 条 / 284 问）

| 部分 | 条数 | 来源与许可 |
|---|---|---|
| 语音指令路由（6 选） | 179 | MASSIVE zh-CN dev 集（Amazon，**CC BY 4.0**），仅保留人工质检 intent 全合格条目，抽样种子固定 |
| 电商客服（路由/紧急度/转人工） | 25 | 自创合成（AI 起草、人工审定） |
| 内容风控（诈骗或违规引流/转人工） | 15 | 同上，含关键词陷阱题（如"谈论诈骗的提醒帖"本身不是诈骗） |

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
| 语音指令路由（n=179） | 0.941 / 0.045 | **0.950 / 0.039** | 0.883 / 0.061 | 0.754 / 0.281 | 0.944 / 0.032 |
| 电商客服·路由（n=25） | 0.920 / 0.065 | **0.960 / 0.068** | 0.640 / 0.293 | 0.520 / 0.184 | 0.920 / 0.058 |
| 电商客服·紧急度（n=25） | **0.680 / 0.154** | 0.520 / 0.172 | 0.560 / 0.091 | 0.520 / 0.207 | 0.640 / 0.243 |
| 内容风控·诈骗引流（n=15） | **0.933 / 0.084** | 0.733 / 0.221 | 0.667 / 0.311 | 0.667 / 0.321 | 0.533 / 0.421 |
| 转人工·两场景（n=40） | **0.550 / 0.180** | 0.550 / 0.280 | 0.550 / 0.230 | 0.575 / 0.269 | 0.400 / 0.486 |
| 顺序翻转率（客服/语音） | **0.0% / 1.7%** | 4.0% / 3.9% | 28.0% / 10.6% | — | 0.0% / 7.3% |
| 简繁翻转率（语音） | **1.7%** | 3.4% | 12.8% | — | 2.2% |
| 重标温度（语音路由） | 2.73 | 1.29 | 1.52 | 0.41 | 0.90 |

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
