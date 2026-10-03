# -*- coding: utf-8 -*-
"""
E6: 干扰鲁棒性（distractor robustness）。
在 state 前插入不同长度的无关中文文本，测决策翻转率与准确率衰减。
灵感来源：typic-bert 论文报告 Laya 在 7k 干扰 token 下准确率跌至 25-30%。
我们测中文场景——没人做过。

用法：
  python src/distract.py --model laya-multi --data data/massive_items.jsonl
  python src/distract.py --model jev --data data/massive_items.jsonl
"""
import argparse
import json
import random
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))


# 无关中文文本池（中性、无指令性、无情感色彩——纯粹测试注意力分散）
NEUTRAL_SENTENCES = [
    "今天天气晴朗，适合户外运动。",
    "这家餐厅的招牌菜是红烧肉，配米饭很下饭。",
    "高铁从北京南站出发大约需要四个半小时到达上海。",
    "图书馆开放时间为早八点到晚十点，周末照常。",
    "这部纪录片讲述了长江流域的生态变迁历程。",
    "小区门口新开了一家便利店，营业到凌晨两点。",
    "这幅水彩画用了大量湿画法来表现江南的雾气。",
    "这款运动鞋的鞋底采用了缓震科技，适合长跑。",
    "博物馆的青铜器展厅正在举行特展，门票半价。",
    "从地铁站到公司步行大约需要十二分钟。",
    "猫咪喜欢在午后的阳光里打盹，这是它们的天性。",
    "这栋写字楼共二十八层，物业费包含中央空调费用。",
    "那本小说以二战期间的法国小镇为背景展开叙事。",
    "传统的豆腐制作工艺需要经过浸泡、磨浆、煮沸、点卤四步。",
    "这家咖啡店的手冲豆子来自埃塞俄比亚的耶加雪菲产区。",
]

def make_distractor(n_tokens_target):
    """构造约 n_tokens_target 个中文 token 的无关文本（按 ~1.5 char/token 估算）。"""
    rng = random.Random(42)
    n_chars = int(n_tokens_target * 1.5)
    parts, total = [], 0
    while total < n_chars:
        s = rng.choice(NEUTRAL_SENTENCES)
        parts.append(s)
        total += len(s) + 1
    return "".join(p + "" for p in parts)[:n_chars]


LEVELS = [0, 500, 2000, 7000]  # 目标干扰 token 数


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--data", nargs="+", required=True)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    # 加载模型
    if args.model == "laya-multi":
        from laya_adapter import LayaAdapter
        adapter = LayaAdapter(subfolder="multilingual")
    elif args.model == "laya-en":
        from laya_adapter import LayaAdapter
        adapter = LayaAdapter(subfolder=None)
    elif args.model == "qwen":
        from qwen_adapter import QwenAdapter
        adapter = QwenAdapter()
    elif args.model == "neohorse":
        from neohorse_adapter import NeoHorseAdapter
        adapter = NeoHorseAdapter()
    elif args.model == "jev":
        from jev_adapter import JevAdapter
        adapter = JevAdapter()
    elif args.model == "typic":
        from typic_adapter import TypicAdapter
        adapter = TypicAdapter()
    else:
        raise SystemExit(f"未知模型 {args.model}")

    items = []
    for f in args.data:
        items += [json.loads(l) for l in open(f, encoding="utf-8") if l.strip()]
    if args.limit:
        items = items[:args.limit]

    print(f"模型: {args.model} | 条目: {len(items)} | 干扰级别: {LEVELS}")

    # 找基线 run
    run_files = sorted(Path("results/raw").glob(f"v0*{args.model}*.jsonl"),
                       key=lambda p: p.stat().st_mtime)
    if not run_files:
        run_files = sorted(Path("results/raw").glob(f"{args.model}*.jsonl"),
                           key=lambda p: p.stat().st_mtime)
    base = {}
    for rf in run_files:
        for line in open(rf, encoding="utf-8"):
            d = json.loads(line)
            if "_meta" not in d:
                base[d["item_id"]] = d
    print(f"基线 run: {run_files[-1].name if run_files else '无'} ({len(base)} 条)")

    out_path = Path(f"results/tables/distract_{args.model}.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    rows = ["model,level,items,flip_rate,acc_at_level,base_acc,tokens_est"]

    for level in LEVELS:
        if level == 0:
            # 基线：直接用已有 run
            flips, corrects = [], []
            for it in items:
                b = base.get(it["id"])
                if not b:
                    continue
                pred = int(np.argmax(b["probs"]))
                flips.append(0)  # 与自身一致
                corrects.append(int(pred == b["gold_idx"]))
            fr = 0.0
            acc = np.mean(corrects) if corrects else float("nan")
            print(f"  level=0 (baseline): acc={acc:.3f}")
            rows.append(f"{args.model},0,{len(corrects)},{fr:.4f},{acc:.4f},{acc:.4f},0")
            continue

        distractor = make_distractor(level)
        flips, corrects = [], []
        for i, it in enumerate(items):
            b = base.get(it["id"])
            if not b:
                continue
            noisy = {**it, "state": distractor + it["state"]}
            try:
                preds = adapter.predict_item(noisy)
            except Exception as e:
                print(f"    !! {it['id']} 失败: {str(e)[:60]}")
                continue
            qname = list(it["questions"].keys())[0]
            p = preds[qname]
            pred = int(np.argmax(p["probs"]))
            base_pred = int(np.argmax(b["probs"]))
            flips.append(int(pred != base_pred))
            corrects.append(int(pred == b["gold_idx"]))
            if (i + 1) % 50 == 0:
                print(f"    {i+1}/{len(items)} done", flush=True)

        fr = np.mean(flips) if flips else float("nan")
        acc = np.mean(corrects) if corrects else float("nan")
        base_acc = np.mean([int(np.argmax(base[it["id"]]["probs"]) == base[it["id"]]["gold_idx"])
                            for it in items if it["id"] in base]) if base else float("nan")
        print(f"  level={level}: flip_rate={fr:.1%} acc={acc:.3f} (base {base_acc:.3f})")
        rows.append(f"{args.model},{level},{len(flips)},{fr:.4f},{acc:.4f},{base_acc:.4f},{level}")

    out_path.write_text("\n".join(rows), encoding="utf-8")
    print(f"\n已写入 {out_path}")


if __name__ == "__main__":
    main()
