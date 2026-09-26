# -*- coding: utf-8 -*-
"""
从 data/*.jsonl 生成人类可读的审核表格（markdown），
供人工审定标注使用。改完标注后重新生成即可。
"""
import json
import sys
from pathlib import Path

def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "data/synthetic_items.jsonl"
    out = Path("reports/review_" + Path(src).stem + ".md")
    out.parent.mkdir(parents=True, exist_ok=True)

    rows = [json.loads(l) for l in open(src, encoding="utf-8") if l.strip()]
    lines = [f"# 标注审核表：{Path(src).name}（共 {len(rows)} 条）",
             "",
             "逐条看 state 和 gold 是否同意。不同意的记下编号和你的判断。",
             ""]
    cur_domain = None
    for i, r in enumerate(rows, 1):
        if r["domain"] != cur_domain:
            cur_domain = r["domain"]
            lines += [f"## 场景：{cur_domain}", ""]
        gold_str = "；".join(f"{k}={v}" for k, v in r["gold"].items())
        q_names = "、".join(r["questions"].keys())
        lines.append(f"{i}. **[{r['id']}]** {r['state']}")
        lines.append(f"   - 问题：{q_names}　|　gold：{gold_str}　|　难度：{r['difficulty']}")
        if r.get("notes"):
            lines.append(f"   - 备注：{r['notes']}")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"已生成 {out}")

if __name__ == "__main__":
    main()
