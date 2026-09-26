# zh-decision-bench

**中文场景下的"System One"决策模型校准评测**：不只测**选得对不对**，还测**报出的概率可不可信**。

围绕 Jev（TypeSafe AI，2026-09 发布）引出的"决策模型"类别——非生成式、单次前向、输出带校准概率的类型化决策——目前所有公开评测都是英文的（Just Ask Jev 论文明确把"其他语言"列为 future work）。本仓库填中文这个空位。

## 核心发现（v0.1，数字随标注审定滚动更新）

1. **"支持 100+ 语言"的中文答案是分层的**：日常语音指令路由 Laya 多语言版 322M 达到 88.3% 准确率、ECE 0.061；但换到业务场景（电商客服路由 64%、紧急度分级 48%、内容风控 57–73%），且 ECE 恶化到 0.2–0.3——严重过度自信。
2. **过度自信是系统性的**：温度重标实验（响应模型卡 "refit temperature on your own data" 的号召）中，多语言版在全部四个业务桶拟合出的温度均 >1（1.35–5.70）；而英文版在同数据上呈双向（0.41–5.53）——过度/不足自信是**场景属性**，不是模型固有属性。
3. **选项顺序敏感性高**：电商客服场景 28% 的题目仅打乱选项呈现顺序，模型的选择就翻转（语音场景 12.3%）。上生产系统前必须固定顺序或做聚合。
4. **简繁不是同一个任务**：同一句话换成原生繁体（MASSIVE 平行语料，非机器转换），准确率 88.3%→82.1%，决策翻转率 12.8%。
5. **多语言版的价值可量化**：英文 421M 版在同样的中文语音任务上 75.4%/ECE 0.281——多语言版 +13 个百分点、校准好 4.6 倍。

## 数据集（v0.1：219 条 / 284 问）

| 部分 | 条数 | 来源与许可 |
|---|---|---|
| 语音指令路由（6 选） | 179 | MASSIVE zh-CN dev 集（Amazon，**CC BY 4.0**），仅保留人工质检 intent 全合格的条目，抽样种子固定 |
| 电商客服（路由/紧急度/转人工） | 25 | 自创合成（AI 起草、人工审定，含边界案例） |
| 内容风控（诈骗识别/转人工） | 15 | 同上，含关键词陷阱题（如"谈论诈骗的提醒帖"本身不是诈骗） |

**标注流程（如实披露）**：MASSIVE 部分沿用原始标注并按本仓库选项定义重映射；合成部分由 LLM 起草、人工逐条审定（审核记录见 releases）。全部 gold 与原始预测一并发布。

三种题型覆盖：`choice`（选项路由）、`score`（有序分级）、`noul`（是否判断）。

## 模型

| 模型 | 形态 | 状态 |
|---|---|---|
| Laya multilingual 322M | 本地，Apache 2.0 | ✅ 已测 |
| Laya english 421M | 本地，Apache 2.0 | ✅ 已测（对照组） |
| Qwen3.5-2B | 本地，logit 探针基线 | 🚧 进行中 |
| Jev API | 闭源 | ⏸ 待接入 |

## 指标与方法

指标体系参照 [Just Ask Jev (arXiv:2609.29429)](https://arxiv.org/abs/2609.29429)：Accuracy、ECE（15-bin top-label）、Brier、NLL、AUROC(macro)、base-rate gap、选择性预测（coverage-accuracy）。全部报告值带 Bootstrap 95% 置信区间（1000 次重采样）。小样本组（n<20）的 ECE 波动大，结论以跨组一致性为准。

## 结果速览

（v0.1，laya-multilingual，详细表见 [reports/metrics.md](reports/metrics.md)）

| 场景 | n | Acc | ECE | 平均置信度 |
|---|---|---|---|---|
| 语音指令路由 | 179 | 0.883 | 0.061 | — |
| 电商客服·路由 | 25 | 0.640 | 0.271 | 高于准确率（过度自信） |
| 电商客服·紧急度 | 25 | 0.480 | 0.104 | — |
| 内容风控·诈骗 | 15 | 0.733 | 0.293 | — |
| 转人工（两场景） | 40 | 0.575 | 0.205 | — |

图表：[可靠性图](reports/figs/reliability_laya_multi.png) · [模型对比](reports/figs/model_comparison.png) · [选择性预测](reports/figs/coverage_accuracy.png) · [失败案例集](reports/failures.md)

## 复现

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install torch --index-url https://download.pytorch.org/whl/cu128   # GPU；CPU 去掉 index-url
pip install -r requirements.txt
# 数据：MASSIVE 原始文件见 data/raw（从官方 S3 下载，gitignore）
python src/convert_massive.py
python src/run_eval.py --model laya-multi --data data/massive_items.jsonl data/synthetic_items.jsonl
python src/report.py results/raw/<run>.jsonl
python src/refit.py results/raw/<run>.jsonl      # E2 温度重标
python src/permute.py --model laya-multi --data data/massive_items.jsonl data/synthetic_items.jsonl  # E3
python src/zh_tw.py --model laya-multi           # E4 简繁
python src/plots.py
```

环境锁定：每个 run 的原始预测首行含 `_meta`（torch/CUDA/laya 版本、数据文件、时间戳）。全部原始预测在 `results/raw/`。

## 局限（如实）

- v0.1 合成场景每组 n=15–25，置信区间宽；v0.2 计划扩充
- MASSIVE 中文为专业本地化语料（非原生采集），口语原生度由合成层补足
- 单人审定 + LLM 辅助复核；标注过程全部公开
- ECE 在小样本下方差大（bin 数敏感）；主结论以 NLL 与跨组一致性支撑

## 许可

- 代码：Apache-2.0
- 数据集：CC BY 4.0（MASSIVE 派生部分署名 Amazon MASSIVE；合成部分无第三方权利）

## 致谢

- [Just Ask Jev](https://arxiv.org/abs/2609.29429)（指标体系）
- [MASSIVE](https://github.com/alexa/massive)（Amazon，CC BY 4.0）
- [Laya](https://huggingface.co/convaiinnovations/laya)（Convai Innovations，Apache 2.0）
