# -*- coding: utf-8 -*-
"""
发布 zh-decision-bench 到 Hugging Face Datasets（v0.1）。
结构：双 config（voice_routing / business_scenarios），JSONL，
dataset card 含 YAML 元数据、字段文档、许可与来源仓库互链。
"""
import json
import os
import sys
from pathlib import Path

from huggingface_hub import HfApi

REPO_ID = "CodyQin/zh-decision-bench"
ROOT = Path(__file__).parent.parent

CARD = """---
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

# zh-decision-bench (v0.1)

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

## License

CC BY 4.0. MASSIVE-derived rows attribute [Amazon MASSIVE](https://github.com/alexa/massive) (CC BY 4.0); synthetic rows are original.
"""


def main():
    token = None
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.startswith("HF_TOKEN="):
                token = line.split("=", 1)[1].strip()
    api = HfApi(token=token or os.environ.get("HF_TOKEN"))
    api.create_repo(repo_id=REPO_ID, repo_type="dataset", private=False, exist_ok=True)

    # 拆分两个 config 的数据文件
    massive = [json.loads(l) for l in open(ROOT / "data/massive_items.jsonl", encoding="utf-8") if l.strip()]
    synth = [json.loads(l) for l in open(ROOT / "data/synthetic_items.jsonl", encoding="utf-8") if l.strip()]
    tmp = ROOT / "results/hf_publish"
    tmp.mkdir(parents=True, exist_ok=True)
    (tmp / "voice_routing.jsonl").write_text(
        "\n".join(json.dumps(x, ensure_ascii=False) for x in massive) + "\n", encoding="utf-8")
    (tmp / "business_scenarios.jsonl").write_text(
        "\n".join(json.dumps(x, ensure_ascii=False) for x in synth) + "\n", encoding="utf-8")
    (tmp / "README.md").write_text(CARD, encoding="utf-8")

    for fn in ("README.md", "voice_routing.jsonl", "business_scenarios.jsonl"):
        api.upload_file(repo_id=REPO_ID, repo_type="dataset", path_in_repo=fn,
                        path_or_fileobj=str(tmp / fn))
        print(f"已上传 {fn}")
    print(f"完成: https://huggingface.co/datasets/{REPO_ID}")


if __name__ == "__main__":
    main()
