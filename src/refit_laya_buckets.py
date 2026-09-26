# -*- coding: utf-8 -*-
"""
按 Laya 官方口径重算温度：桶 = (题型, 选项数档位)，格式与 laya.common.temp_bucket
一致（"choice:3-5" / "noul:2" / ...），并遵守官方 TEMP_MIN=0.5 / TEMP_MAX=5.0 钳制。
产出可直接写进 PR 的 data/temperatures_laya_buckets.json。
"""
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from metrics import apply_temperature, ece, fit_temperature, nll

TEMP_MIN, TEMP_MAX = 0.5, 5.0


def bucket_of(qtype, k):
    size = "2" if k <= 2 else "3-5" if k <= 5 else "6-10" if k <= 10 else "11+"
    return f"{qtype}:{size}"


def main():
    runs = sorted(Path("results/raw").glob("laya-multi_*.jsonl"))
    path = runs[-1]
    recs = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    recs = [r for r in recs if "_meta" not in r]
    print(f"使用 run: {path.name}（{len(recs)} 问）")

    groups = defaultdict(lambda: defaultdict(list))
    for r in recs:
        b = bucket_of(r["qtype"], len(r["labels"]))
        h = int(hashlib.md5(r["item_id"].encode()).hexdigest(), 16)
        groups[b]["fit" if h % 2 == 0 else "test"].append(r)

    out = {"_meta": {"convention": "laya.common.temp_bucket (question_type, option-count band)",
                     "clamp": [TEMP_MIN, TEMP_MAX], "run": path.name,
                     "model": "laya-multilingual-322M", "data": "zh-decision-bench v0.1"}}
    print(f"{'桶':14s} {'fit/test':>9s} {'T原始':>7s} {'T钳制':>7s} {'ECE前':>7s} {'ECE后':>7s} {'NLL前':>7s} {'NLL后':>7s}")
    for b in sorted(groups):
        fit_r, test_r = groups[b]["fit"], groups[b]["test"]
        if len(fit_r) < 8 or len(test_r) < 8:
            print(f"{b:14s} {len(fit_r):>4d}/{len(test_r):<4d} 样本不足跳过")
            continue
        lp_f = np.log(np.clip(np.array([r["probs"] for r in fit_r]), 1e-9, 1))
        y_f = np.array([r["gold_idx"] for r in fit_r])
        T_raw, _ = fit_temperature(lp_f, y_f)
        T = min(max(T_raw, TEMP_MIN), TEMP_MAX)
        lp_t = np.log(np.clip(np.array([r["probs"] for r in test_r]), 1e-9, 1))
        y_t = np.array([r["gold_idx"] for r in test_r])
        p0 = np.exp(lp_t); p0 /= p0.sum(axis=1, keepdims=True)
        p1 = apply_temperature(lp_t, T)
        e0, e1 = ece(p0, y_t), ece(p1, y_t)
        n0, n1 = nll(p0, y_t), nll(p1, y_t)
        print(f"{b:14s} {len(fit_r):>4d}/{len(test_r):<4d} {T_raw:7.2f} {T:7.2f} {e0:7.3f} {e1:7.3f} {n0:7.3f} {n1:7.3f}")
        out[b] = {"T": round(T, 3), "T_raw": round(T_raw, 3),
                  "clamped": T != T_raw, "n_fit": len(fit_r), "n_test": len(test_r),
                  "ece_before": round(e0, 4), "ece_after": round(e1, 4),
                  "nll_before": round(n0, 4), "nll_after": round(n1, 4)}

    dst = Path("data/temperatures_laya_buckets.json")
    dst.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n已写入 {dst}")


if __name__ == "__main__":
    main()
