# -*- coding: utf-8 -*-
"""读取 Laya 官方 51 语言扫描结果中的中文行，供 PR 措辞参考。"""
import json
import os
import tempfile

path = os.path.join(tempfile.gettempdir(), "sweep.json")
d = json.load(open(path, encoding="utf-8"))
for part in ("part_a", "part_b"):
    if part not in d:
        continue
    cfg = d[part].get("config", {})
    print(f"{part}: config={ {k: cfg.get(k) for k in ('per_lang','n_options','seed')} }")
    for model, md in d[part].get("by_model", {}).items():
        for lang in ("zh-CN", "zh-TW"):
            r = md.get("per_language", {}).get(lang)
            if r:
                print(f"  {model} / {lang}: acc={r['accuracy']}, ece={r['ece']:.3f}, "
                      f"mean_conf={r['mean_confidence']:.3f}, n={r['n']}")
