# -*- coding: utf-8 -*-
"""
评测主程序：对数据集逐条调用模型，把每个 (题目, 问题) 的概率向量
写入 results/raw/<run_id>.jsonl，一行一条，供后续指标计算。

用法：
  python src/run_eval.py --model laya-multi --data data/massive_items.jsonl data/synthetic_items.jsonl
"""
import argparse
import importlib
import json
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def gold_index(labels, gold_val, qname):
    """把 gold 值映射为 labels 下标。"""
    if isinstance(gold_val, bool):
        return 0 if gold_val else 1  # noul: labels = ["true","false"]
    return labels.index(gold_val)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True,
                    help="laya-multi / laya-en / qwen / jev")
    ap.add_argument("--data", nargs="+", required=True)
    ap.add_argument("--limit", type=int, default=0, help="只跑前N条（调试用）")
    args = ap.parse_args()

    run_id = f"{args.model}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out_path = Path("results/raw") / f"{run_id}.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # 加载适配器
    if args.model.startswith("laya"):
        from laya_adapter import LayaAdapter
        sub = "multilingual" if args.model == "laya-multi" else None
        adapter = LayaAdapter(subfolder=sub)
        model_desc = "convaiinnovations/laya " + (sub or "root(english)")
    elif args.model == "qwen":
        from qwen_adapter import QwenAdapter
        adapter = QwenAdapter()
        model_desc = adapter.model_id + " bf16"
    elif args.model == "jev":
        from jev_adapter import JevAdapter
        adapter = JevAdapter(probe=True)
        model_desc = "TypeSafe Jev API (jev-1.13.0)"
    else:
        raise SystemExit(f"未知模型 {args.model}")

    # 环境元信息（可复现性）
    import torch, laya
    meta = {"_meta": {"run_id": run_id, "model": args.model, "model_desc": model_desc,
                      "torch": torch.__version__, "cuda": torch.cuda.is_available(),
                      "laya": getattr(laya, "__version__", "?"),
                      "data": args.data, "started": datetime.now().isoformat(),
                      "limit": args.limit}}
    print(json.dumps(meta, ensure_ascii=False))

    n_items = n_q = 0
    t_start = time.time()
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(meta, ensure_ascii=False) + "\n")
        for data_file in args.data:
            items = [json.loads(l) for l in open(data_file, encoding="utf-8") if l.strip()]
            if args.limit:
                items = items[:args.limit]
            for item in items:
                preds = adapter.predict_item(item)
                for qname, qspec in item["questions"].items():
                    p = preds[qname]
                    gold_val = item["gold"][qname]
                    try:
                        gi = gold_index(p["labels"], gold_val, qname)
                    except ValueError:
                        print(f"!! gold 不在 labels 中，跳过 {item['id']}/{qname}")
                        continue
                    rec = {"run_id": run_id, "model": args.model, "item_id": item["id"],
                           "domain": item["domain"], "question": qname,
                           "qtype": qspec["type"], "labels": p["labels"],
                           "probs": p["probs"], "gold_idx": gi,
                           "confidence": p.get("confidence"),
                           "answer_confidence": p.get("answer_confidence"),
                           "latency_ms": round(preds["_latency_ms"], 1)}
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    n_q += 1
                n_items += 1
                if n_items % 25 == 0:
                    f.flush()
                    print(f"  已完成 {n_items} 条 / {n_q} 问 / 用时 {time.time()-t_start:.0f}s")
    print(f"完成：{n_items} 条题目 {n_q} 个问题 -> {out_path}（总用时 {time.time()-t_start:.0f}s）")


if __name__ == "__main__":
    main()
