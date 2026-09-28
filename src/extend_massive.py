# -*- coding: utf-8 -*-
"""
v0.2 扩样：语音路由每域 30 -> 60 条（同任务同选项定义，保证与 v0.1 可比）。
仅从 dev 集质量合格行中抽样，跳过 v0.1 已用过的 massive_id。追加到
data/massive_items.jsonl（原 179 条保持不动，新条目 id 延续编号）。
"""
import json
import random
import re
from collections import Counter
from pathlib import Path

# 与 convert_massive.py 完全一致的域定义与选项
SCENARIOS = {
    "calendar": "日历安排",
    "alarm": "闹钟计时",
    "audio": "音量控制",
    "music": "音乐点播",
    "weather": "天气查询",
    "transport": "交通出行",
}
CRITERIA = {
    "日历安排": "日程、会议、活动、事件安排",
    "闹钟计时": "闹钟、定时提醒、倒计时、定时器",
    "音量控制": "音量调节、静音、播放控制",
    "音乐点播": "点歌、播放列表、歌手、专辑",
    "天气查询": "天气、气温、降水、穿衣建议",
    "交通出行": "打车、导航、公交、路况",
}
TARGET_PER_DOMAIN = 60  # 每域总数（含 v0.1 已有）
NEW_SEED = 43


def intent_clean(r):
    js = r.get("judgments", [])
    return bool(js) and all(j.get("intent_score") == 1 for j in js)


def main():
    items = [json.loads(l) for l in Path("data/massive_items.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    used_massive_ids = set()
    for it in items:
        m = re.search(r"massive_id=(\d+)", it.get("notes", ""))
        if m:
            used_massive_ids.add(m.group(1))
    cur = Counter(it["gold"]["route"] for it in items)
    print("当前分布:", dict(cur), "| 已用 massive_id:", len(used_massive_ids))

    rows = []
    for line in open("data/raw/massive_zh-CN.jsonl", encoding="utf-8"):
        if line.strip():
            rows.append(json.loads(line))
    rows = [r for r in rows if r.get("partition") == "dev" and intent_clean(r)]

    rng = random.Random(NEW_SEED)
    added = 0
    for dom_en, dom_cn in SCENARIOS.items():
        need = TARGET_PER_DOMAIN - cur.get(dom_cn, 0)
        if need <= 0:
            continue
        cands = [r for r in rows
                 if r["scenario"] == dom_en
                 and str(r["id"]) not in used_massive_ids
                 and 4 <= len(r["utt"].strip()) <= 60]
        take = rng.sample(cands, min(need, len(cands)))
        for r in take:
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
                "version": 2,
            })
            added += 1
    print(f"新增 {added} 条，总计 {len(items)}")
    print(Counter(it["gold"]["route"] for it in items))
    Path("data/massive_items.jsonl").write_text(
        "\n".join(json.dumps(x, ensure_ascii=False) for x in items) + "\n", encoding="utf-8")
    print("已写回 data/massive_items.jsonl")


if __name__ == "__main__":
    main()
