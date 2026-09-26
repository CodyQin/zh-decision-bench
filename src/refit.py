# -*- coding: utf-8 -*-
"""
E2 温度重标定：响应模型卡 "Ships over-confident — refit temperature on your
own data" 的号召，在中文数据上拟合温度并量化校准改善。

方法：按 (domain, question) 分桶；item_id 哈希奇偶决定 fit/test 对半划分；
fit 半区上网格搜索 T 最小化 NLL（log-probs = log(probs)）；
test 半区报告重标前后的 ECE / NLL / Brier。

用法：python src/refit.py results/raw/laya-multi_xxx.jsonl
"""
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from metrics import apply_temperature, brier, ece, fit_temperature, nll


def split_key(item_id):
    h = int(hashlib.md5(item_id.encode()).hexdigest(), 16)
    return "fit" if h % 2 == 0 else "test"


def main():
    path = sys.argv[1]
    recs, seen = [], set()
    for l in open(path, encoding="utf-8"):
        l = l.strip()
        if not l:
            continue
        try:
            d = json.loads(l)
        except json.JSONDecodeError:
            continue
        if "_meta" in d:
            continue
        key = (d.get("item_id"), d.get("question"))
        if key in seen:
            continue
        seen.add(key)
        recs.append(d)

    groups = defaultdict(lambda: defaultdict(list))
    for r in recs:
        groups[(r["domain"], r["question"])][split_key(r["item_id"])].append(r)

    rows = ["domain,question,n_fit,n_test,T,ece_before,ece_after,nll_before,nll_after,brier_before,brier_after"]
    temps = {}
    print(f"{'组':44s} {'T':>6s} {'ECE前':>7s} {'ECE后':>7s} {'NLL前':>7s} {'NLL后':>7s}")
    for (domain, q), parts in sorted(groups.items()):
        fit_recs, test_recs = parts["fit"], parts["test"]
        if len(fit_recs) < 8 or len(test_recs) < 8:
            print(f"{domain+'/'+q:44s}  样本不足（fit={len(fit_recs)}, test={len(test_recs)}），跳过")
            continue
        lp_fit = np.log(np.clip(np.array([r["probs"] for r in fit_recs]), 1e-9, 1))
        y_fit = np.array([r["gold_idx"] for r in fit_recs])
        T, _ = fit_temperature(lp_fit, y_fit)

        lp_test = np.log(np.clip(np.array([r["probs"] for r in test_recs]), 1e-9, 1))
        y_test = np.array([r["gold_idx"] for r in test_recs])
        p_before = np.exp(lp_test); p_before /= p_before.sum(axis=1, keepdims=True)
        p_after = apply_temperature(lp_test, T)

        eb, ea = ece(p_before, y_test), ece(p_after, y_test)
        nb, na = nll(p_before, y_test), nll(p_after, y_test)
        bb, ba = brier(p_before, y_test), brier(p_after, y_test)
        print(f"{domain+'/'+q:44s} {T:6.2f} {eb:7.3f} {ea:7.3f} {nb:7.3f} {na:7.3f}")
        rows.append(f"{domain},{q},{len(fit_recs)},{len(test_recs)},{T:.3f},"
                    f"{eb:.4f},{ea:.4f},{nb:.4f},{na:.4f},{bb:.4f},{ba:.4f}")
        temps[f"{domain}/{q}"] = {"T": T, "n_fit": len(fit_recs), "n_test": len(test_recs)}

    model = recs[0]["model"] if recs else "unknown"
    out = Path(f"results/tables/temperature_refit_{model}.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(rows), encoding="utf-8")
    (Path("data") / f"temperatures_{model}.json").write_text(
        json.dumps(temps, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n已写入 {out} 和 data/temperatures_{model}.json")


if __name__ == "__main__":
    main()
