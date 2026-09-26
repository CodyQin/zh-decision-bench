# -*- coding: utf-8 -*-
"""
把本仓库数据集转成 Laya 官方 laya-evals harness 格式（research/evals/），
用于向 NandhaKishorM/laya 提交社区评测数据集 PR。

字段映射：gold -> expected；choice 用标签、score 用等级序号、noul 用 true/false；
附 language 与 tags（domain / 来源 / 难度）。
"""
import json
from pathlib import Path

HEADER = """# zh-decision-bench: 中文（zh-CN）社区评测集，来自 https://github.com/CodyQin/zh-decision-bench
# 219 items / 284 questions. MASSIVE-derived items (179): Amazon MASSIVE zh-CN, CC BY 4.0.
# Synthetic items (40): CC BY 4.0, LLM-drafted, human-adjudicated (review log in source repo).
# Task framing: 6-domain voice-command routing + e-commerce CS (route/urgency/escalate)
# + content moderation (scam-or-illicit-promotion/escalate). laya 0.3.20, 2026-09-25.
"""


def convert_item(it):
    expected = {}
    for qname, qspec in it["questions"].items():
        g = it["gold"][qname]
        if qspec["type"] == "choice":
            expected[qname] = g
        elif qspec["type"] == "score":
            expected[qname] = list(qspec["criteria"]).index(g)
        else:  # noul
            expected[qname] = bool(g)
    src_tag = "massive" if it["id"].startswith("mass_") else "synthetic"
    return {
        "state": it["state"],
        "questions": it["questions"],
        "expected": expected,
        "language": "zh-CN",
        "tags": [it["domain"], src_tag, it.get("difficulty", "mid"),
                 "id:" + it["id"]],
    }


def main():
    out_lines = [HEADER.rstrip()]
    n = 0
    for f in ("data/massive_items.jsonl", "data/synthetic_items.jsonl"):
        for line in open(f, encoding="utf-8"):
            if line.strip():
                out_lines.append(json.dumps(
                    convert_item(json.loads(line)), ensure_ascii=False))
                n += 1
    dst = Path("results/zh_decision_bench.laya-evals.jsonl")
    dst.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    print(f"转换 {n} 条 -> {dst}")


if __name__ == "__main__":
    main()
