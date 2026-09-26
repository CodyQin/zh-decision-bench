# -*- coding: utf-8 -*-
"""
E3 选项顺序敏感性：同样的题目、同样的选项，只打乱选项呈现顺序，
模型的选择和概率会不会变？工业可用性的试金石。

只测 choice 题。每题跑原始顺序 + 4 个随机置换（种子固定可复现），
指标：翻转率（argmax 是否变）、最大概率的极差、概率向量的 TV 距离。

用法：python src/permute.py --model laya-multi --data data/massive_items.jsonl data/synthetic_items.jsonl
"""
import argparse
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="laya-multi")
    ap.add_argument("--data", nargs="+", required=True)
    ap.add_argument("--n-perm", type=int, default=4)
    args = ap.parse_args()

    if args.model == "laya-multi":
        from laya_adapter import LayaAdapter
        adapter = LayaAdapter(subfolder="multilingual")
    elif args.model == "laya-en":
        from laya_adapter import LayaAdapter
        adapter = LayaAdapter(subfolder=None)
    else:
        raise SystemExit("目前支持 laya-multi / laya-en")

    items = []
    for f in args.data:
        items += [json.loads(l) for l in open(f, encoding="utf-8") if l.strip()]
    # 只保留含 choice 问题的题
    items = [it for it in items
             if any(q["type"] == "choice" for q in it["questions"].values())]
    print(f"共 {len(items)} 条含 choice 的题目，每条跑 {args.n_perm + 1} 种顺序")

    stats = defaultdict(list)
    rows = ["item_id,domain,question,flipped,max_prob_range,tv_mean"]
    for it in items:
        for qname, qspec in it["questions"].items():
            if qspec["type"] != "choice":
                continue
            canon = list(qspec["criteria"].keys())
            rng = random.Random(hash(it["id"]) & 0xFFFF)
            orders = [canon]
            for _ in range(args.n_perm):
                o = canon[:]
                rng.shuffle(o)
                orders.append(o)
            runs = []
            for o in orders:
                qs = {qname: {**qspec, "criteria": {k: qspec["criteria"][k] for k in o}}}
                preds = adapter.predict_item({**it, "questions": qs})
                p = dict(zip(preds[qname]["labels"], preds[qname]["probs"]))
                runs.append([p.get(c, 0.0) for c in canon])
            P = np.array(runs)  # (n_orders, K) 已对齐回原始标签顺序
            argmaxes = P.argmax(axis=1)
            flipped = int(len(set(argmaxes.tolist())) > 1)
            tv = np.mean([0.5 * np.abs(P[i] - P[j]).sum()
                          for i in range(len(P)) for j in range(i + 1, len(P))])
            row = {"flipped": flipped,
                   "max_prob_range": float(P.max(axis=1).max() - P.max(axis=1).min()),
                   "tv_mean": float(tv)}
            stats[(it["domain"], qname)].append(row)
            rows.append(f"{it['id']},{it['domain']},{qname},{flipped},"
                        f"{row['max_prob_range']:.4f},{row['tv_mean']:.4f}")

    print(f"\n{'组':44s} {'n':>4s} {'翻转率':>7s} {'概率极差':>8s} {'TV距离':>8s}")
    for (dom, q), rs in sorted(stats.items()):
        flip = np.mean([r["flipped"] for r in rs])
        rng_ = np.mean([r["max_prob_range"] for r in rs])
        tv = np.mean([r["tv_mean"] for r in rs])
        print(f"{dom+'/'+q:44s} {len(rs):4d} {flip:7.1%} {rng_:8.3f} {tv:8.3f}")

    out = Path("results/tables/permute.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(rows), encoding="utf-8")
    print(f"\n明细已写入 {out}")


if __name__ == "__main__":
    main()
