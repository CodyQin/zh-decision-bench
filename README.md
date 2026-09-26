# zh-decision-bench

**English** | [中文](README.zh-CN.md)

**A calibration benchmark for "System One" decision models on Chinese tasks** — measuring not just *whether the model picks the right answer*, but *whether the probabilities it reports can be trusted*.

Around the decision-model category Jev (TypeSafe AI, Sept 2026) opened up — non-generative, single forward pass, typed decisions with calibrated probabilities — every public evaluation so far is English-only (the *Just Ask Jev* paper explicitly lists other languages as future work). This repo fills the Chinese gap.

## Key findings (v0.1, post human review)

1. **The LLM-vs-decision-model contest splits by task type.** Qwen3.5-2B (logit probing) leads decisively on choice/ordinal tasks (voice routing 94.4% vs 88.3%; customer-service routing 92.0% vs 64.0%; urgency 64% vs 56%) and is far more robust (option-order flip rate 0% vs 28%; traditional-Chinese flip 2.2% vs 12.8%) — but collapses on binary judgments (escalation accuracy 40%, ECE 0.49–0.57, refit temperature 20.1), where the dedicated decision model holds the relative edge. **The value proposition of the decision-model route needs to be re-scoped by task, not accepted or rejected wholesale.**
2. **"100+ languages" is a layered claim in Chinese.** Everyday voice commands: Laya multilingual 322M reaches 88.3% / ECE 0.061 (close to its own post-refit English figure of 0.081). Business scenarios: 52–67% with ECE degrading to 0.23–0.31.
3. **Over-confidence is systematic — and scenario-dependent.** Refit temperatures for Laya multilingual are uniformly >1 (1.33–5.70); the English checkpoint is bidirectional (0.41–5.53); Qwen is split (0.81–20.09). Over/under-confidence varies by model×scenario combination, not by model alone.
4. **Option-order sensitivity.** 28% of customer-service items flip their answer when options are merely reordered (voice: 10.6%); Qwen flips 0% on the same items. Fix the order or aggregate before production use.
5. **Simplified vs Traditional Chinese is not one task.** Same utterances in native Traditional Chinese (MASSIVE parallel corpus): Laya 88.3%→82.1%, 12.8% decision flips (Qwen: 2.2%).
6. **The multilingual checkpoint's value is quantifiable**: the English 421M checkpoint scores 75.4% / ECE 0.281 on the same Chinese voice tasks — multilingual buys +13 points and 4.6× better calibration.

## Dataset (v0.1: 219 items / 284 questions)

| Part | Items | Source & license |
|---|---|---|
| Voice-command routing (6-way) | 179 | MASSIVE zh-CN dev split (Amazon, **CC BY 4.0**); only rows where every human judgment confirms the intent label; fixed sampling seed |
| E-commerce customer service (route/urgency/escalate) | 25 | Synthetic (LLM-drafted, human-adjudicated) |
| Content moderation (scam-or-illicit-promotion / escalate) | 15 | Same; includes keyword-trap items (e.g. a scam-awareness post that is *about* scams but is not one) |

**Annotation disclosure:** MASSIVE items carry the original labels remapped to this repo's option definitions; synthetic items were LLM-drafted and adjudicated item-by-item by the repo owner — the [review log is public](data/review_log.md) (7 adjudications, including one question-definition revision). All gold labels and all raw model predictions ship with the repo.

Covers all three question primitives: `choice`, `score` (ordinal), `noul` (binary).

## Models

| Model | Form | Status |
|---|---|---|
| Laya multilingual 322M | local, Apache 2.0 | ✅ evaluated |
| Laya english 421M | local, Apache 2.0 | ✅ evaluated (control) |
| Qwen3.5-2B | local bf16, logit-probe baseline | ✅ evaluated |
| Jev API | closed | ⏸ not evaluated: TypeSafe direct signups paused since 2026-09-22; adapter ready (`src/jev_adapter.py`) for when it reopens |

Fairness note: Qwen is 2B vs Laya's 322M/421M — ~6× parameters, ~3× per-question latency. The comparison is between *routes* (generative LLM vs dedicated decision model), not matched budgets.

## Metrics & method

Metric suite follows [Just Ask Jev (arXiv:2609.29429)](https://arxiv.org/abs/2609.29429): Accuracy, ECE (15-bin top-label), Brier, NLL, AUROC (macro), base-rate gap, selective prediction (coverage–accuracy). All reported values carry bootstrap 95% CIs (1000 resamples). Small groups (n<20) have high ECE variance; headline conclusions rest on NLL and cross-group consistency.

## Results at a glance (accuracy / ECE)

| Scenario · question | Laya multi 322M | Laya en 421M | Qwen3.5-2B |
|---|---|---|---|
| Voice routing (n=179) | 0.883 / 0.061 | 0.754 / 0.281 | **0.944 / 0.032** |
| CS routing (n=25) | 0.640 / 0.293 | 0.520 / 0.184 | **0.920 / 0.058** |
| CS urgency (n=25) | 0.560 / 0.091 | 0.520 / 0.207 | **0.640 / 0.243** |
| Scam/illicit promotion (n=15) | **0.667** / 0.311 | **0.667** / 0.321 | 0.533 / 0.421 |
| Escalate (both scenarios, n=40) | **0.550** / 0.230 | 0.575 / 0.269 | 0.400 / 0.486 |
| Option-order flip rate (CS / voice) | 28.0% / 10.6% | — | **0.0% / 7.3%** |
| zh-TW flip rate (voice) | 12.8% | — | **2.2%** |
| Refit temperature range | 1.33–5.70 | 0.41–5.53 | 0.81–20.09 |

Full tables with CIs, Brier/NLL/AUROC and selective prediction: [reports/metrics.md](reports/metrics.md)

Figures: [reliability diagram](reports/figs/reliability_laya_multi.png) · [model comparison](reports/figs/model_comparison.png) · [selective prediction](reports/figs/coverage_accuracy.png) · [failure cases](reports/failures.md)

## Reproduce

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install torch --index-url https://download.pytorch.org/whl/cu128   # GPU; drop index-url for CPU
pip install -r requirements.txt
# laya-en & qwen weights: download from HF into models/ (gitignored), or let the adapter fetch them
python src/convert_massive.py            # needs data/raw/massive_zh-CN.jsonl from the official S3 bundle
python src/run_eval.py --model laya-multi --data data/massive_items.jsonl data/synthetic_items.jsonl
python src/report.py results/raw/<run>.jsonl
python src/refit.py results/raw/<run>.jsonl      # E2 temperature refit
python src/permute.py --model laya-multi --data data/massive_items.jsonl data/synthetic_items.jsonl  # E3
python src/zh_tw.py --model laya-multi           # E4 simplified/traditional (needs data/raw/massive_zh-TW.jsonl)
python src/plots.py
```

Reproducibility: the first line of every run file is a `_meta` record (model path / torch / CUDA / laya versions / data files / timestamp); all 852 raw predictions ship in `results/raw/`.

## Limitations (stated plainly)

- v0.1 business-scenario groups have n=15–25 — wide CIs; v0.2 will expand
- MASSIVE Chinese is professionally localized (not natively collected); colloquial coverage is compensated by the synthetic layer
- Single human adjudicator with LLM-assisted drafting; the [review log](data/review_log.md) is public
- Jev not measured (signups paused); adapter ready for when it reopens
- ECE is bin-sensitive at small n; headline conclusions rest on NLL and cross-group consistency

## License

- Code: Apache-2.0 ([LICENSE](LICENSE))
- Dataset: CC BY 4.0 ([LICENSE-DATA](LICENSE-DATA)); MASSIVE-derived portions attribute Amazon MASSIVE; synthetic portions carry no third-party rights

## Acknowledgements

- [Just Ask Jev](https://arxiv.org/abs/2609.29429) (metric framework)
- [MASSIVE](https://github.com/alexa/massive) (Amazon, CC BY 4.0)
- [Laya](https://huggingface.co/convaiinnovations/laya) (Convai Innovations, Apache 2.0)
