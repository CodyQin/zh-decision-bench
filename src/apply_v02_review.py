# -*- coding: utf-8 -*-
"""应用 v0.2 人工审定：0008 改 route；risk_0002 维持（定义对齐）；合并入正式集。"""
import json
from pathlib import Path

DRAFT = Path("data/synthetic_items_v02_draft.jsonl")
MAIN = Path("data/synthetic_items.jsonl")

PATCH = {
    "syn_cs_v02_0008": {"route": "退换售后"},
}
NOTES = {
    "syn_cs_v02_0008": "客服承诺的补偿券未兑现属售后履约问题（人工审定 2026-09-28；与v0.1 syn_cs_0008交易型优惠券问题构成边界对照）",
    "syn_risk_v02_0002": "非法放贷广告：按'诈骗或违规引流'定义判 True（人工审定时提出taxonomy异议，经v0.1定义对齐后维持）",
}

items = [json.loads(l) for l in DRAFT.read_text(encoding="utf-8").splitlines() if l.strip()]
for it in items:
    for k, v in PATCH.get(it["id"], {}).items():
        it["gold"][k] = v
    if it["id"] in NOTES:
        it["notes"] = NOTES[it["id"]]
    it["source"] = "synthetic (AI起草，人工审定)"

main = [json.loads(l) for l in MAIN.read_text(encoding="utf-8").splitlines() if l.strip()]
main_ids = {x["id"] for x in main}
merged = main + [x for x in items if x["id"] not in main_ids]
MAIN.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in merged) + "\n", encoding="utf-8")
print(f"合并完成：正式集 {len(merged)} 条（新增 {len(merged) - len(main)}）")
