# -*- coding: utf-8 -*-
"""
把 MASSIVE zh-CN（Amazon，CC BY 4.0）原始文件转换为本项目决策题格式。

输入：data/raw/massive_zh-CN.jsonl（官方 tar 包中提取，每行含
      id/split/domain/intent/utt/annot_utt/slots）
设计：选 6 个功能域，每域抽样 30 条真人语音指令，共 180 条 choice 题。
      所有题共用同一套 6 选项 criteria，概率矩阵统一为 (N, 6)。
输出：data/massive_items.jsonl
"""
import argparse
import json
import random
from collections import Counter
from pathlib import Path

# MASSIVE domain 名 -> 中文选项
SCENARIOS = {
    "calendar": "日历安排",
    "alarm": "闹钟计时",
    "audio": "音量控制",
    "music": "音乐点播",
    "weather": "天气查询",
    "transport": "交通出行",
}
PER_DOMAIN = 30
SEED = 42

CRITERIA = {
    "日历安排": "日程、会议、活动、事件安排",
    "闹钟计时": "闹钟、定时提醒、倒计时、定时器",
    "音量控制": "音量调节、静音、播放控制",
    "音乐点播": "点歌、播放列表、歌手、专辑",
    "天气查询": "天气、气温、降水、穿衣建议",
    "交通出行": "打车、导航、公交、路况",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default="data/raw/massive_zh-CN.jsonl")
    ap.add_argument("--out", default="data/massive_items.jsonl")
    ap.add_argument("--per-domain", type=int, default=PER_DOMAIN)
    ap.add_argument("--split", default="dev")  # 用 dev 分集，避免与任何训练集撞车
    args = ap.parse_args()

    rows = []
    with open(args.raw, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    print(f"原始行数: {len(rows)}")

    # 官方字段：partition（train/dev/test）、scenario、intent
    if rows and "partition" in rows[0]:
        rows = [r for r in rows if r["partition"] == args.split]
        print(f"取 {args.split} 分集: {len(rows)}")

    # 质量过滤：只保留全部人工评审判定 intent 标签正确的条目
    def intent_clean(r):
        js = r.get("judgments", [])
        return bool(js) and all(j.get("intent_score") == 1 for j in js)

    rng = random.Random(SEED)
    by_domain = {s: [] for s in SCENARIOS}
    for r in rows:
        d = r.get("scenario")
        if d in by_domain and intent_clean(r):
            by_domain[d].append(r)

    items = []
    for dom_en, dom_cn in SCENARIOS.items():
        cands = [r for r in by_domain[dom_en] if 4 <= len(r["utt"].strip()) <= 60]
        sampled = rng.sample(cands, min(args.per_domain, len(cands)))
        for r in sampled:
            items.append({
                "id": f"mass_{len(items):04d}",
                "domain": "voice_assistant_routing",
                "source": "MASSIVE zh-CN (Amazon, CC BY 4.0)",
                "state": r["utt"].strip(),
                "questions": {
                    "route": {
                        "type": "choice",
                        "instructions": "判断这条语音指令属于哪个功能域",
                        "criteria": CRITERIA,
                    }
                },
                "gold": {"route": dom_cn},
                "difficulty": "mid",
                "notes": f"scenario={dom_en}, intent={r['intent']}, massive_id={r['id']}",
                "version": 1,
            })

    random.Random(SEED + 1).shuffle(items)  # 打乱，避免连续同域
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    print(f"写入 {len(items)} 条 -> {args.out}")
    print(Counter(it["gold"]["route"] for it in items))


if __name__ == "__main__":
    main()
