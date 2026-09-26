# -*- coding: utf-8 -*-
"""
E4 简繁一致性：MASSIVE 是平行语料——同一 id 在 zh-CN 和 zh-TW 里是
同一句话的简体版和原生繁体版（台湾本土化措辞，不是机器转换）。

把抽样的 179 条换成繁体原文重跑（criteria 保持简体，模拟"用户用繁体
提问、系统标签为简体"的真实部署形态），对比决策与概率的稳定性。

用法：python src/zh_tw.py --model laya-multi
"""
import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="laya-multi")
    ap.add_argument("--items", default="data/massive_items.jsonl")
    ap.add_argument("--tw", default="data/raw/massive_zh-TW.jsonl")
    args = ap.parse_args()

    # id -> 繁体 utt
    tw_utt = {}
    for line in open(args.tw, encoding="utf-8"):
        if line.strip():
            d = json.loads(line)
            tw_utt[d["id"]] = d["utt"].strip()

    items = [json.loads(l) for l in open(args.items, encoding="utf-8") if l.strip()]
    converted, missed = [], 0
    for it in items:
        m = re.search(r"massive_id=(\d+)", it.get("notes", ""))
        if not m or m.group(1) not in tw_utt:
            missed += 1
            continue
        converted.append({**it, "state": tw_utt[m.group(1)]})
    print(f"对上 {len(converted)} 条繁体平行句（未对上 {missed} 条）")

    # 找同一模型的简体原始 run 作为对照
    run_files = sorted(Path("results/raw").glob(f"{args.model}_*.jsonl"))
    if not run_files:
        raise SystemExit("找不到原始简体 run，先跑 run_eval.py")
    base_run = run_files[-1]
    base = {}
    for line in open(base_run, encoding="utf-8"):
        d = json.loads(line)
        if "_meta" not in d:
            base[d["item_id"]] = d
    print(f"对照 run: {base_run.name}")

    if args.model == "laya-multi":
        from laya_adapter import LayaAdapter
        adapter = LayaAdapter(subfolder="multilingual")
    elif args.model == "qwen":
        from qwen_adapter import QwenAdapter
        adapter = QwenAdapter()
    else:
        from laya_adapter import LayaAdapter
        adapter = LayaAdapter(subfolder=None)

    flips, tvs, agree_correct = [], [], []
    for it in converted:
        preds = adapter.predict_item(it)
        for qname, qspec in it["questions"].items():
            p_tw = dict(zip(preds[qname]["labels"], preds[qname]["probs"]))
            b = base.get(it["id"])
            if not b or b["question"] != qname:
                continue
            canon = b["labels"]
            v_tw = np.array([p_tw.get(c, 0.0) for c in canon])
            v_cn = np.array(b["probs"])
            flips.append(int(v_tw.argmax() != v_cn.argmax()))
            tvs.append(0.5 * np.abs(v_tw - v_cn).sum())
            agree_correct.append(int(v_tw.argmax() == b["gold_idx"]))

    print(f"\n简→繁 决策翻转率: {np.mean(flips):.1%}")
    print(f"概率 TV 距离均值: {np.mean(tvs):.3f}")
    print(f"繁体输入下准确率: {np.mean(agree_correct):.1%}（简体原run见 metrics 报告）")


if __name__ == "__main__":
    main()
