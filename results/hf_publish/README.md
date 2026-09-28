---
language:
  - zh
language_bcp47:
  - zh-CN
license: cc-by-4.0
task_categories:
  - text-classification
  - feature-extraction
tags:
  - benchmark
  - calibration
  - decision-models
  - system-one
  - chinese
  - jev
  - evaluation
size_categories:
  - n<1k
configs:
  - config_name: voice_routing
    data_files:
      - split: validation
        path: voice_routing.jsonl
  - config_name: business_scenarios
    data_files:
      - split: validation
        path: business_scenarios.jsonl
---

# zh-decision-bench (v0.2)

**First Chinese-language calibration benchmark for Jev-class "System One" decision models** — accuracy *and* probability calibration on Chinese tasks.

Full methodology, five-model results (Jev, NeoHorse-Jev-4B, Laya x2, Qwen3.5-2B), raw predictions and the human adjudication log live in the [source repository](https://github.com/CodyQin/zh-decision-bench). The eval set also ships in [Laya](https://github.com/NandhaKishorM/laya)'s `research/evals/` as of v0.3.21.

## Configs

| config | items | questions | source |
|---|---|---|---|
| `voice_routing` | 179 | 179 (choice, 6-way) | MASSIVE zh-CN dev (Amazon, CC BY 4.0), quality-filtered, fixed seed |
| `business_scenarios` | 40 | 105 (choice/score/noul) | Synthetic: LLM-drafted, human-adjudicated ([review log](https://github.com/CodyQin/zh-decision-bench/blob/master/data/review_log.md)) |

## Fields

- `state` — the text to decide on (utterance / ticket / message)
- `questions` — question dict keyed by question id; each has `type` (`choice` | `score` | `noul`), `instructions`, `criteria` (options: label->description; score: ordered level list; noul: true/false descriptions)
- `gold` — ground truth keyed by question id (label / level / boolean)
- `domain`, `source`, `difficulty`, `tags`, `notes` — provenance and slicing

## Usage

```python
from datasets import load_dataset
ds = load_dataset("CodyQin/zh-decision-bench", "voice_routing")
```

## Changelog

- **v0.2 (2026-09-28)**: voice_routing 179 -> 323 (same task, official labels); business_scenarios 40 -> 55 (human-adjudicated); five-model matrix incl. NeoHorse-Jev-4B; revised the v0.1 over-confidence reading at larger n.
- **v0.1 (2026-09-27)**: initial release.

## License

CC BY 4.0. MASSIVE-derived rows attribute [Amazon MASSIVE](https://github.com/alexa/massive) (CC BY 4.0); synthetic rows are original.
