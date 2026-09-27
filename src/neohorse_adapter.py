# -*- coding: utf-8 -*-
"""
NeoHorse-Jev-4B（基元律动/TokenRhythm，Apache 2.0）适配器。
原生接口 DecisionEngine.predict 与 systemone 同构：
- 请求需带 model 字段（'NeoHorse-Jev-4B'）
- choice: probabilities 按标签；noul: noul = P(true)；score: probabilities 按序号
与 laya/jev 适配器的解析逻辑一致。
"""
import time
from pathlib import Path

MODEL_ID = "NeoHorse-Jev-4B"


class NeoHorseAdapter:
    def __init__(self):
        from neohorse_decision import DecisionEngine
        model_dir = Path(__file__).parent.parent / "models" / "neohorse-4b"
        self.name = "neohorse"
        self.engine = DecisionEngine(str(model_dir), device="cuda")

    def predict_item(self, item):
        payload = {"model": MODEL_ID, "state": item["state"],
                   "questions": item["questions"]}
        t0 = time.perf_counter()
        result = self.engine.predict(payload)
        latency_ms = (time.perf_counter() - t0) * 1000
        out = {}
        for qname, qspec in item["questions"].items():
            ans = result["answers"][qname]
            qtype = qspec["type"]
            if qtype == "choice":
                labels = list(qspec["criteria"].keys())
                p = ans.get("probabilities", {})
                probs = [float(p.get(l, 0.0)) for l in labels]
            elif qtype == "score":
                labels = list(qspec["criteria"])
                p = ans.get("probabilities", {})
                probs = [float(p.get(str(i), 0.0)) for i in range(len(labels))]
            elif qtype == "noul":
                labels = ["true", "false"]
                pt = float(ans.get("noul", 0.5))
                probs = [pt, 1.0 - pt]
            else:
                raise ValueError(qtype)
            s = sum(probs)
            if s > 0:
                probs = [x / s for x in probs]
            out[qname] = {"labels": labels, "probs": probs,
                          "confidence": ans.get("confidence"),
                          "answer_confidence": ans.get("answer_confidence")}
        out["_latency_ms"] = latency_ms
        out["_usage"] = result.get("usage", {})
        return out
