# zh-decision-bench

**English** | [中文](README.zh-CN.md)

[![Dataset](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Dataset-FFD21E?logoColor=black)](https://huggingface.co/datasets/CodyQin/zh-decision-bench) [![shipped in laya](https://img.shields.io/badge/eval%20set%20shipped%20in-laya%20v0.3.21-2a78d6)](https://github.com/NandhaKishorM/laya/pull/557) `load_dataset("CodyQin/zh-decision-bench")`

**A calibration benchmark for "System One" decision models on Chinese tasks** — measuring not just *whether the model picks the right answer*, but *whether the probabilities it reports can be trusted*.

Around the decision-model category Jev (TypeSafe AI, Sept 2026) opened up — non-generative, single forward pass, typed decisions with calibrated probabilities — every public evaluation so far is English-only (the *Just Ask Jev* paper explicitly lists other languages as future work). This repo fills the Chinese gap.

## Which model should I use? (zh, decision guide)

| Your task | Recommendation | Why (measured) |
|---|---|---|
| Routing / ordinal grading, want best quality | **Jev API** | 0.92–0.94 accuracy across routing & urgency; order-invariant (flip 0–1.7%) |
| **Binary judgment** (moderation, escalate) | **Jev API** — do **not** use LLM logit probing | Jev scam detection 0.933 / ECE 0.084; Qwen logit probe collapses on the same task (0.533 / ECE 0.42) |
| Local open decision model, Chinese-first | **NeoHorse-Jev-4B** (Apache 2.0) | Statistical tie with Jev atop voice routing (0.950 vs 0.960), **wins CS routing (0.912) and escalate (0.618) outright**; robust (flip 2.9–4.0%); weak on urgency (0.471), scam behind Jev (0.810 vs 0.952) |
| Local & free, routing-shaped tasks | **Qwen3.5-2B + logit probe** | 0.92–0.94 on routing, 0% order flips, 2.2% zh-TW flips — but avoid for binary judgments |
| Ultra-low-latency local (<30ms) | **Laya multilingual 322M + our temperature table** | 24ms/question; must fix option order (28% flip if not) and refit temperature first |
| Users write Traditional Chinese | Jev or Qwen | 1.7% / 2.2% decision flips vs Laya's 12.8% |

Full data & CIs below; raw predictions for all 2,335 model-questions in `results/raw/`.

## Key findings (v0.2, expanded and human-adjudicated)

1. **The flagship validates the category — and the zh-trained open 4B genuinely competes.** Jev (jev-latest, direct API) leads voice routing (0.960/ECE 0.035, n=323), urgency (0.676) and scam detection (**0.952/ECE 0.073**, n=21), with best-in-class order invariance (0–1.9% flips) and script robustness (zh-TW flip 1.7%, zero accuracy drop). NeoHorse-Jev-4B statistically ties Jev on voice routing (0.950 vs 0.960, CIs overlap) and **wins two business groups outright** — CS routing (0.912) and escalate (0.618) — the open 4B model beats the flagship on its home-language business tasks.
2. **LLM logit probing is strong on choice, catastrophic on binary.** Qwen3.5-2B matches Jev on routing (0.944/0.920) and is equally robust — but on binary judgments it collapses (scam 0.533/ECE 0.42; escalation ECE 0.49–0.57, refit temperature 20.1). The failure mode of "reading confidence off a generative model" is precisely the binary case.
3. **The open field is stratified.** NeoHorse-Jev-4B (zh-trained, Chinese company, first zh measurement here — its own card reports none) matches or beats Jev on routing (voice 0.950 vs 0.941, CS 0.960 vs 0.920) with good robustness (order flip 3.9–4.0%, zh-TW flip 3.4%), but fails urgency grading (0.520) and trails Jev on binary judgment (scam 0.733 vs 0.933). Laya 322M trails further on accuracy and robustness (order flip 28%) but wins on latency (24ms local, free).
4. **"100+ languages" is a layered claim in Chinese.** Everyday voice commands: Laya multilingual reaches 0.883/ECE 0.061 (near its own post-refit English figure 0.081). Business scenarios drop to 0.52–0.67 with ECE 0.23–0.31.
5. **Calibration needs are model×scenario specific — and small-n refits can mislead.** At n=323 voice routing, Qwen (T≈1.03) and NeoHorse (1.14) are near-calibrated out of the box, Laya-english is under-confident (0.44), Laya-multilingual mildly over (1.45), and Jev needs no refit at all (its shipped calibration already holds in Chinese — our v0.1 "everyone over-confident" reading was partly a small-sample artifact; we are revising it as data grows). Business scenarios are different: Laya's `noul:2` raw fit (10.2) exceeds its shipped clamp — zh binary-judgment over-confidence outruns the package's correction range.
6. **Simplified vs Traditional Chinese is not one task**: native zh-TW parallel utterances flip 12.8% of Laya's decisions (Jev 1.7%, Qwen 2.2%).

## Dataset (v0.2: 378 items / 467 questions)

| Part | Items | Source & license |
|---|---|---|
| Voice-command routing (6-way) | 323 (v0.2; 60/domain where the quality-filtered dev pool allows) | MASSIVE zh-CN dev split (Amazon, **CC BY 4.0**); only rows where every human judgment confirms the intent label; fixed sampling seed |
| E-commerce customer service (route/urgency/escalate) | 34 | Synthetic (LLM-drafted, human-adjudicated) |
| Content moderation (scam-or-illicit-promotion / escalate) | 21 | Same; includes keyword-trap items (e.g. a scam-awareness post that is *about* scams but is not one) |

**Annotation disclosure:** MASSIVE items carry the original labels remapped to this repo's option definitions; synthetic items were LLM-drafted and adjudicated item-by-item by the repo owner — the [review log is public](data/review_log.md) (7 adjudications, including one question-definition revision). All gold labels and all raw model predictions ship with the repo.

> The eval set also ships in [Laya](https://github.com/NandhaKishorM/laya)'s `research/evals/` as of **v0.3.21** ([PR #557](https://github.com/NandhaKishorM/laya/pull/557)).

Covers all three question primitives: `choice`, `score` (ordinal), `noul` (binary).

## Models

| Model | Form | Status |
|---|---|---|
| Jev (jev-latest) | TypeSafe direct API | ✅ fully evaluated (467 questions; channel check: direct vs gateway 100% decision agreement, TV 0.003) |
| Laya multilingual 322M | local, Apache 2.0 | ✅ evaluated |
| Laya english 421M | local, Apache 2.0 | ✅ evaluated (control) |
| Qwen3.5-2B | local bf16, logit-probe baseline | ✅ evaluated |
| NeoHorse-Jev-4B | local, Apache 2.0 (TokenRhythm/基元律动) | ✅ evaluated — its first zh measurement (the model card reports none) |

Fairness note: parameter counts span 322M–4B (Laya < Qwen 2B < NeoHorse 4B); Jev is a paid hosted API. The comparison is between *routes* (closed flagship / open decision models / LLM probe), not matched budgets.

## Metrics & method

Metric suite follows [Just Ask Jev (arXiv:2609.29429)](https://arxiv.org/abs/2609.29429): Accuracy, ECE (15-bin top-label), Brier, NLL, AUROC (macro), base-rate gap, selective prediction (coverage–accuracy). All reported values carry bootstrap 95% CIs (1000 resamples). Small groups (n<20) have high ECE variance; headline conclusions rest on NLL and cross-group consistency.

## Results at a glance (accuracy / ECE)

| Scenario · question | Jev API | NeoHorse 4B | Laya multi 322M | Laya en 421M | Qwen3.5-2B |
|---|---|---|---|---|---|
| Voice routing (n=323) | **0.960 / 0.035** | 0.950 / 0.031 | 0.870 / 0.056 | 0.749 / 0.276 | 0.938 / 0.020 |
| CS routing (n=34) | 0.882 / 0.107 | **0.912 / 0.097** | 0.618 / 0.311 | 0.529 / 0.185 | 0.882 / 0.093 |
| CS urgency (n=34) | **0.676 / 0.135** | 0.471 / 0.212 | 0.647 / 0.088 | 0.529 / 0.195 | 0.529 / 0.236 |
| Scam/illicit promotion (n=21) | **0.952 / 0.073** | 0.810 / 0.174 | 0.714 / 0.286 | 0.619 / 0.343 | 0.524 / 0.390 |
| Escalate (both scenarios, n=55) | 0.600 / **0.164** | **0.618** / 0.239 | 0.564 / 0.230 | 0.600 / 0.225 | 0.473 / 0.410 |
| Option-order flip rate (CS / voice) | 2.9% / **1.9%** | 2.9% / 4.0% | 20.6% / 10.8% | — | 2.9% / 8.0% |
| zh-TW flip rate (voice) | **1.7%** | 3.4% | 12.8% | — | 2.2% |
| Refit temperature (voice routing, n=323) | 3.03* | 1.14 | 1.45 | 0.44 | 1.03 |

\* Jev's shipped calibration is already good on zh voice routing — its refit does not improve ECE/NLL on the test half (the fitted T=3.03 reflects fit-half noise). The temperatures that matter in practice are the business-scenario ones above.

Full tables with CIs, Brier/NLL/AUROC and selective prediction: [reports/metrics.md](reports/metrics.md)

Figures: [reliability diagram](reports/figs/reliability_laya_multi_en.png) · [model comparison](reports/figs/model_comparison_en.png) · [selective prediction](reports/figs/coverage_accuracy_en.png) · [failure cases](reports/failures.md)

Temperature refit values per official `temp_bucket` convention: [data/temperatures_*.json](data/) — apply before trusting any raw confidence in production.

## Reproduce

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install torch --index-url https://download.pytorch.org/whl/cu128   # GPU; drop index-url for CPU
pip install -r requirements.txt
# laya-en & qwen weights: download from HF into models/ (gitignored), or let the adapter fetch them
python src/convert_massive.py            # needs data/raw/massive_zh-CN.jsonl from the official S3 bundle
python src/run_eval.py --model laya-multi --data data/massive_items.jsonl data/synthetic_items.jsonl
python src/run_eval.py --model jev --data data/massive_items.jsonl data/synthetic_items.jsonl   # needs .env key
python src/report.py results/raw/<run>.jsonl
python src/refit.py results/raw/<run>.jsonl      # E2 temperature refit
python src/permute.py --model jev --data data/massive_items.jsonl data/synthetic_items.jsonl  # E3
python src/zh_tw.py --model jev                   # E4 simplified/traditional (needs data/raw/massive_zh-TW.jsonl)
python src/plots.py
```

Reproducibility: the first line of every run file is a `_meta` record (model path / torch / CUDA / laya versions / data files / timestamp); all 2,335 raw predictions ship in `results/raw/`.

## Limitations (stated plainly)

- v0.1 business-scenario groups have n=15–25 — wide CIs; v0.2 will expand
- MASSIVE Chinese is professionally localized (not natively collected); colloquial coverage is compensated by the synthetic layer
- Single human adjudicator with LLM-assisted drafting; the [review log](data/review_log.md) is public
- Escalate-type questions are hard for every model (0.40–0.58 accuracy) — partly task ambiguity, noted honestly
- ECE is bin-sensitive at small n; headline conclusions rest on NLL and cross-group consistency

## License

- Code: Apache-2.0 ([LICENSE](LICENSE))
- Dataset: CC BY 4.0 ([LICENSE-DATA](LICENSE-DATA)); MASSIVE-derived portions attribute Amazon MASSIVE; synthetic portions carry no third-party rights

## Acknowledgements

- [Just Ask Jev](https://arxiv.org/abs/2609.29429) (metric framework)
- [MASSIVE](https://github.com/alexa/massive) (Amazon, CC BY 4.0)
- [Laya](https://huggingface.co/convaiinnovations/laya) (Convai Innovations, Apache 2.0)
