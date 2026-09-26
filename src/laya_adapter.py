# -*- coding: utf-8 -*-
"""
laya 适配器：把 predict() 的真实输出（probe_laya.py 探测到的格式）
统一转成 (labels, probs) 概率向量。

输出格式备忘（2026-09-25 实测 laya 0.3.20）：
- choice: answers[q]["probabilities"] 按标签名给全分布
- score:  answers[q]["probabilities"] 按等级下标字符串("0"/"1"/...)给分布，
          legend 映射回 criteria 顺序
- noul:   answers[q]["noul"] 是一个数 = P(true)
"""
import time


class LayaAdapter:
    def __init__(self, subfolder="multilingual"):
        import laya
        from pathlib import Path
        self.name = f"laya-{subfolder or 'root'}"
        if subfolder:
            self.agent = laya.load("convaiinnovations/laya", subfolder=subfolder)
        else:  # 英文 root：优先用本地下载好的权重（HF下载器在Windows上不稳定）
            local = Path(__file__).parent.parent / "models" / "laya-en"
            if (local / "model.safetensors").exists():
                self.agent = laya.load(str(local))
            else:
                self.agent = laya.load("convaiinnovations/laya")

    def predict_item(self, item):
        """对一条评测题调用模型，返回 {question_name: {"labels": [...], "probs": [...]}}"""
        t0 = time.perf_counter()
        result = self.agent.predict(state=item["state"], questions=item["questions"])
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
                labels = list(qspec["criteria"])  # 有序等级列表
                p = ans.get("probabilities", {})
                probs = [float(p.get(str(i), 0.0)) for i in range(len(labels))]
            elif qtype == "noul":
                labels = ["true", "false"]
                pt = float(ans.get("noul", 0.5))
                probs = [pt, 1.0 - pt]
            else:
                raise ValueError(f"未知题型 {qtype}")
            s = sum(probs)
            if s > 0:
                probs = [x / s for x in probs]  # 归一化，防浮点误差
            out[qname] = {"labels": labels, "probs": probs,
                          "confidence": ans.get("confidence"),
                          "answer_confidence": ans.get("answer_confidence")}
        out["_latency_ms"] = latency_ms
        out["_usage"] = result.get("usage", {})
        return out
