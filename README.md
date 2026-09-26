# zh-decision-bench

**中文场景下的"System One"决策模型校准评测**：不只测**选得对不对**，还测**报出的概率可不可信**。

围绕 Jev（TypeSafe AI，2026-09 发布）引出的"决策模型"类别——非生成式、单次前向、输出带校准概率的类型化决策——目前公开评测均为英文（Just Ask Jev 论文明确把"其他语言"列为 future work）。本仓库填中文这个空位。

## 核心发现（v0.1，人工审定后终值）

1. **通用 LLM 与专用决策模型的胜负是分任务方向的**：Qwen3.5-2B（logit 探针）在"多选一/分级"题上全面领先（语音路由 94.4% vs 88.3%，客服路由 92.0% vs 64.0%，紧急度 64% vs 56%），且更稳（选项顺序翻转率 0% vs 28%，简繁翻转 2.2% vs 12.8%）；但在"是否判断"题上反而崩掉（转人工准确率仅 40%、ECE 0.49–0.57、重标温度高达 20.1）——Laya 在这两组相对占优。**"决策模型路线"的价值主张在中文场景需要按任务重新划界。**
2. **"支持 100+ 语言"的中文答案是分层的**：日常语音指令 Laya 多语言版 322M 达 88.3%/ECE 0.061（接近其官方英文重标后水平 0.081）；业务场景掉到 52–67% 且 ECE 恶化到 0.23–0.31。
3. **过度自信是系统性的、且是场景属性**：Laya 多语言版四个业务桶重标温度全部 >1（1.33–5.70）；英文版双向（0.41–5.53）；Qwen 分裂（0.81–20.09）。过度/不足自信随"模型×场景"组合变化，不是模型的固定属性。
4. **选项顺序敏感性**：Laya 客服场景 28% 的题仅打乱选项顺序答案即翻转（语音场景 10.6%）；Qwen 同题 0%。上生产前必须固定顺序或做聚合。
5. **简繁不是同一个任务**：同一句话换原生繁体（MASSIVE 平行语料），Laya 准确率 88.3%→82.1%、决策翻转 12.8%（Qwen：2.2%）。
6. **多语言版的价值可量化**：英文 421M 版在同样中文语音任务上 75.4%/ECE 0.281——多语言版 +13 个百分点、校准好 4.6 倍。

## 数据集（v0.1：219 条 / 284 问）

| 部分 | 条数 | 来源与许可 |
|---|---|---|
| 语音指令路由（6 选） | 179 | MASSIVE zh-CN dev 集（Amazon，**CC BY 4.0**），仅保留人工质检 intent 全合格条目，抽样种子固定 |
| 电商客服（路由/紧急度/转人工） | 25 | 自创合成（AI 起草、人工审定） |
| 内容风控（诈骗或违规引流/转人工） | 15 | 同上，含关键词陷阱题（如"谈论诈骗的提醒帖"本身不是诈骗） |

**标注流程（如实披露）**：MASSIVE 部分沿用原始标注并按本仓库选项定义重映射；合成部分由 LLM 起草、项目所有者逐条人工审定——[审核日志公开](data/review_log.md)（7 条意见全部落实，含一次问题定义修订）。全部 gold 与模型原始预测一并发布。

三种题型覆盖：`choice`（选项路由）、`score`（有序分级）、`noul`（是否判断）。

## 模型

| 模型 | 形态 | 状态 |
|---|---|---|
| Laya multilingual 322M | 本地，Apache 2.0 | ✅ 已测 |
| Laya english 421M | 本地，Apache 2.0 | ✅ 已测（对照组） |
| Qwen3.5-2B | 本地 bf16，logit 探针基线 | ✅ 已测 |
| Jev API | 闭源 | ⏸ 未测：TypeSafe 直连注册暂停（2026-09-22 起），重开后补测；OpenRouter 网关适配器已备好（`src/jev_adapter.py`） |

公平性注记：Qwen 为 2B 对 Laya 322M/421M，参数量约 6 倍、单问延迟约 3 倍——比较的是"路线"（生成式 LLM vs 专用决策模型）而非同量级。

## 指标与方法

指标体系参照 [Just Ask Jev (arXiv:2609.29429)](https://arxiv.org/abs/2609.29429)：Accuracy、ECE（15-bin top-label）、Brier、NLL、AUROC(macro)、base-rate gap、选择性预测（coverage-accuracy）。全部报告值带 Bootstrap 95% 置信区间（1000 次重采样）。小样本组（n<20）ECE 方差大，结论以 NLL 与跨组一致性支撑。

## 结果速览（准确率 / ECE）

| 场景·问题 | Laya 多语言 322M | Laya 英文 421M | Qwen3.5-2B |
|---|---|---|---|
| 语音指令路由（n=179） | 0.883 / 0.061 | 0.754 / 0.281 | **0.944 / 0.032** |
| 电商客服·路由（n=25） | 0.640 / 0.293 | 0.520 / 0.184 | **0.920 / 0.058** |
| 电商客服·紧急度（n=25） | 0.560 / 0.091 | 0.520 / 0.207 | **0.640 / 0.243** |
| 内容风控·诈骗引流（n=15） | **0.667** / 0.311 | **0.667** / 0.321 | 0.533 / 0.421 |
| 转人工·两场景（n=40） | **0.550** / 0.230 | 0.575 / 0.269 | 0.400 / 0.486 |
| 顺序翻转率（客服/语音） | 28.0% / 10.6% | — | **0.0% / 7.3%** |
| 简繁翻转率（语音） | 12.8% | — | **2.2%** |
| 重标温度范围 | 1.33–5.70 | 0.41–5.53 | 0.81–20.09 |

详细表（含置信区间、Brier/NLL/AUROC/选择性预测）：[reports/metrics.md](reports/metrics.md)

图表：[可靠性图](reports/figs/reliability_laya_multi.png) · [模型对比](reports/figs/model_comparison.png) · [选择性预测](reports/figs/coverage_accuracy.png) · [失败案例集](reports/failures.md)

## 复现

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install torch --index-url https://download.pytorch.org/whl/cu128   # GPU；CPU 去掉 index-url
pip install -r requirements.txt
# laya 英文权重与 Qwen 权重从 HF 下载放 models/（见 .gitignore），或由适配器自动拉取
python src/convert_massive.py            # 需要 data/raw/massive_zh-CN.jsonl（官方 S3 包）
python src/run_eval.py --model laya-multi --data data/massive_items.jsonl data/synthetic_items.jsonl
python src/report.py results/raw/<run>.jsonl
python src/refit.py results/raw/<run>.jsonl      # E2 温度重标
python src/permute.py --model laya-multi --data data/massive_items.jsonl data/synthetic_items.jsonl  # E3
python src/zh_tw.py --model laya-multi           # E4 简繁（需 data/raw/massive_zh-TW.jsonl）
python src/plots.py
```

可复现性：每个 run 的原始预测首行含 `_meta`（模型路径/torch/CUDA/laya 版本/数据文件/时间戳）；852 条原始预测全部随仓库发布（`results/raw/`）。

## 局限（如实）

- v0.1 合成场景每组 n=15–25，置信区间宽；v0.2 计划扩充
- MASSIVE 中文为专业本地化语料（非原生采集），口语原生度由合成层补足
- 单人审定 + LLM 辅助复核；[审核日志](data/review_log.md)公开
- Jev 未实测（注册暂停）；重开后补测，适配器已就绪
- ECE 在小样本下方差大（bin 数敏感）；主结论以 NLL 与跨组一致性支撑

## 许可

- 代码：Apache-2.0
- 数据集：CC BY 4.0（MASSIVE 派生部分署名 Amazon MASSIVE；合成部分无第三方权利）

## 致谢

- [Just Ask Jev](https://arxiv.org/abs/2609.29429)（指标体系）
- [MASSIVE](https://github.com/alexa/massive)（Amazon，CC BY 4.0）
- [Laya](https://huggingface.co/convaiinnovations/laya)（Convai Innovations，Apache 2.0）
