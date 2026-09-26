# -*- coding: utf-8 -*-
"""
失败案例集：提取"高置信但答错"的案例（最危险的错误）和
E3 中顺序一变就翻的案例。输出 markdown 到 reports/failures.md。
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np


def main():
    run = sys.argv[1] if len(sys.argv) > 1 else "laya-multi"
    runs = sorted(Path("results/raw").glob(f"{run}_*.jsonl"))
    if not runs:
        raise SystemExit("找不到 run")
    recs = [json.loads(l) for l in open(runs[-1], encoding="utf-8") if l.strip()]
    recs = [r for r in recs if "_meta" not in r]

    # item_id -> state（从数据文件反查）
    states = {}
    for f in Path("data").glob("*_items.jsonl"):
        for line in open(f, encoding="utf-8"):
            if line.strip():
                d = json.loads(line)
                states[d["id"]] = d["state"]

    wrong = [r for r in recs if int(np.argmax(r["probs"])) != r["gold_idx"]]
    conf_wrong = sorted(wrong, key=lambda r: -max(r["probs"]))[:15]

    lines = [f"# 失败案例集（{run}，高置信但答错的 Top 15）", "",
             "这些是部署中最危险的错误：模型很确定，但确定错了。", ""]
    for i, r in enumerate(conf_wrong, 1):
        pred = r["labels"][int(np.argmax(r["probs"]))]
        gold = r["labels"][r["gold_idx"]]
        p = max(r["probs"])
        top3 = sorted(zip(r["labels"], r["probs"]), key=lambda x: -x[1])[:3]
        top3_s = "，".join(f"{l} {p:.2f}" for l, p in top3)
        lines.append(f"{i}. **[{r['item_id']}｜{r['domain']}/{r['question']}]** 置信度 {p:.2f}")
        lines.append(f"   - 原文：{states.get(r['item_id'], '(未找到)')}")
        lines.append(f"   - 预测：{pred}　|　正确：{gold}　|　前三：{top3_s}")
        lines.append("")

    if Path("results/tables/permute.csv").exists():
        prows = [l.split(",") for l in open("results/tables/permute.csv", encoding="utf-8").read().splitlines()[1:]]
        flips = [r for r in prows if r[3] == "1"]
        lines += [f"## 顺序敏感案例（E3 翻转，共 {len(flips)} 条，列前 10）", ""]
        for r in flips[:10]:
            iid = r[0]
            lines.append(f"- **[{iid}｜{r[1]}/{r[2]}]** 换顺序后答案改变，最大概率极差 {float(r[4]):.2f}")
        lines.append("")

    out = Path("reports/failures.md")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"已生成 {out}（高置信错误 {len(conf_wrong)} 条展示，总错误 {len(wrong)}/{len(recs)}）")


if __name__ == "__main__":
    main()
