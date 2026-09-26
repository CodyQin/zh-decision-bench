# -*- coding: utf-8 -*-
"""
指标报告：读取 results/raw/<run>.jsonl，按 (模型, 场景, 问题) 分组计算
Accuracy / Brier / NLL / ECE / AUROC / base-rate gap / 选择性预测，
全部带 Bootstrap 95% 置信区间。输出 markdown + csv。

用法：python src/report.py results/raw/laya-multi_xxx.jsonl [...]
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from metrics import (accuracy, base_rate_gap, auroc_macro, brier, bootstrap_ci,
                     coverage_accuracy, ece, nll)


def load_records(paths):
    recs = []
    for p in paths:
        for line in open(p, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            if "_meta" in d:
                continue
            recs.append(d)
    return recs


def group_metrics(recs):
    same_structure = len({tuple(r["labels"]) for r in recs}) == 1
    m = {"n": len(recs),
         "lat_p50": float(np.median([r["latency_ms"] for r in recs]))}
    if same_structure:
        probs = np.array([r["probs"] for r in recs])
        labels = np.array([r["gold_idx"] for r in recs])
        conf = probs.max(axis=1)
        correct = (probs.argmax(axis=1) == labels).astype(float)
        m.update({
            "acc": accuracy(probs, labels),
            "acc_ci": bootstrap_ci(accuracy, probs, labels),
            "ece": ece(probs, labels),
            "ece_ci": bootstrap_ci(ece, probs, labels),
            "brier": brier(probs, labels),
            "nll": nll(probs, labels),
            "base_gap": base_rate_gap(probs, labels),
            "mean_conf": float(conf.mean()),
            "auroc": float("nan"),
        })
        try:
            m["auroc"] = auroc_macro(probs, labels)
        except Exception:
            pass
    else:
        # 跨题型汇总：只用 top-label 口径（只需最大概率与对错，与选项数无关）
        conf = np.array([max(r["probs"]) for r in recs])
        correct = np.array([int(np.argmax(r["probs"]) == r["gold_idx"]) for r in recs],
                           dtype=float)
        def _ece_flat(c, k):
            bins = np.linspace(0, 1, 16)
            v, tot = 0.0, len(c)
            for lo, hi in zip(bins[:-1], bins[1:]):
                msk = (c > lo) & (c <= hi)
                if msk.sum():
                    v += msk.sum() / tot * abs(c[msk].mean() - k[msk].mean())
            return v
        def _acc_flat(c, k):
            return float(k.mean())
        m.update({
            "acc": _acc_flat(conf, correct),
            "acc_ci": bootstrap_ci(_acc_flat, conf, correct),
            "ece": _ece_flat(conf, correct),
            "ece_ci": bootstrap_ci(_ece_flat, conf, correct),
            "brier": float("nan"),
            "nll": float("nan"),
            "base_gap": float(abs(conf.mean() - correct.mean())),
            "mean_conf": float(conf.mean()),
            "auroc": float("nan"),
        })
    m["cov_acc_50"] = coverage_accuracy(conf, correct, [0.5])[0.5]
    return m


def fmt(v):
    if isinstance(v, float):
        return f"{v:.3f}"
    return str(v)


def main():
    paths = sys.argv[1:]
    if not paths:
        raise SystemExit("用法: python src/report.py results/raw/xxx.jsonl ...")
    recs = load_records(paths)
    runs = sorted({r["run_id"] for r in recs})
    print(f"载入 {len(recs)} 条预测（runs: {runs}）")

    groups = defaultdict(list)
    for r in recs:
        groups[(r["model"], r["domain"], r["question"])].append(r)
        groups[(r["model"], "ALL", r["question"])].append(r)
        groups[(r["model"], "ALL", "ALL")].append(r)

    lines = ["# 评测结果", ""]
    rows_csv = ["model,domain,question,n,acc,acc_lo,acc_hi,ece,ece_lo,ece_hi,brier,nll,base_gap,mean_conf,auroc,cov_acc_50,lat_p50_ms"]
    for (model, domain, q), rs in sorted(groups.items()):
        m = group_metrics(rs)
        key = f"{model} | {domain} | {q}"
        print(f"{key:60s} n={m['n']:4d} acc={m['acc']:.3f} ece={m['ece']:.3f} "
              f"brier={m['brier']:.3f} nll={m['nll']:.3f} gap={m['base_gap']:.3f}")
        lines.append(f"## {key}（n={m['n']}）")
        lines.append("")
        lines.append("| 指标 | 值 | 95% CI |")
        lines.append("|---|---|---|")
        for label, key_name in [("Accuracy", "acc"), ("ECE(15bin)", "ece"),
                                ("Brier", "brier"), ("NLL", "nll"),
                                ("AUROC(macro)", "auroc"), ("Base-rate gap", "base_gap")]:
            ci = m.get(key_name + "_ci")
            ci_s = f"[{fmt(ci[0])}, {fmt(ci[1])}]" if ci else "-"
            lines.append(f"| {label} | {fmt(m[key_name])} | {ci_s} |")
        lines.append(f"| 平均置信度 | {fmt(m['mean_conf'])} | - |")
        lines.append(f"| 选择性预测 acc@50% | {fmt(m['cov_acc_50'])} | - |")
        lines.append(f"| 延迟中位数 | {fmt(m['lat_p50'])}ms | - |")
        lines.append("")
        rows_csv.append(",".join(map(str, [
            model, domain, q, m["n"], round(m["acc"], 4),
            round(m["acc_ci"][0], 4), round(m["acc_ci"][1], 4),
            round(m["ece"], 4), round(m["ece_ci"][0], 4), round(m["ece_ci"][1], 4),
            round(m["brier"], 4), round(m["nll"], 4), round(m["base_gap"], 4),
            round(m["mean_conf"], 4), round(m["auroc"], 4), round(m["cov_acc_50"], 4),
            round(m["lat_p50"], 1)])))

    out_md = Path("reports/metrics.md")
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(lines), encoding="utf-8")
    out_csv = Path("results/tables/metrics.csv")
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out_csv.write_text("\n".join(rows_csv), encoding="utf-8")
    print(f"\n已写入 {out_md} 和 {out_csv}")


if __name__ == "__main__":
    main()
