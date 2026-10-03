# -*- coding: utf-8 -*-
"""
typic-bert 适配器（396M，Ettin/ModernBERT 编码器，Apache 2.0）。
原生 API：decide(question, options, context) / is_true(question, context)
score 类型通过 decide + 有序标签实现。
"""
import sys
import time
from pathlib import Path

REPO_ID = "minar-svn/typic-bert"


class TypicAdapter:
    def __init__(self):
        from huggingface_hub import hf_hub_download
        token = None
        env = Path(__file__).parent.parent / ".env"
        if env.exists():
            for line in env.read_text(encoding="utf-8").splitlines():
                if line.startswith("HF_TOKEN="):
                    token = line.split("=", 1)[1].strip()
        import os
        os.environ["HF_TOKEN"] = token or ""
        # 获取自定义 modeling 代码（带 token）
        modeling_path = hf_hub_download(REPO_ID, "modeling_typic.py", token=token)
        sys.path.insert(0, str(Path(modeling_path).parent))
        from modeling_typic import TypicModel

        import torch
        self.name = "typic"
        self.model = TypicModel.from_pretrained(REPO_ID, token=token)
        # TypicModel 可能不是标准 nn.Module——尝试常见属性名迁移到 GPU
        if torch.cuda.is_available():
            for attr in ("model", "encoder", "backbone", "_model"):
                inner = getattr(self.model, attr, None)
                if inner is not None and hasattr(inner, "cuda"):
                    setattr(self.model, attr, inner.cuda())
                    break
            # 也试 .to()
            if hasattr(self.model, "to"):
                try:
                    self.model.to("cuda")
                except Exception:
                    pass
        if hasattr(self.model, "eval"):
            self.model.eval()

    def predict_item(self, item):
        state = item["state"]
        out = {}
        t_all = time.perf_counter()
        for qname, qspec in item["questions"].items():
            qtype = qspec["type"]
            instructions = qspec.get("instructions", "")
            t0 = time.perf_counter()
            if qtype == "choice":
                labels = list(qspec["criteria"].keys())
                descs = [f"{k}: {v}" for k, v in qspec["criteria"].items()]
                q = f"{instructions}（选项：{'；'.join(labels)}）"
                result = self.model.decide(q, descs, context=state)
                # result = [(option_str, prob), ...]
                probs = [0.0] * len(labels)
                for opt_str, p in result:
                    for i, d in enumerate(descs):
                        if d in opt_str or opt_str in d:
                            probs[i] = float(p)
                            break
                    else:
                        # fallback: try matching by label
                        for i, l in enumerate(labels):
                            if l in opt_str:
                                probs[i] = float(p)
                                break
            elif qtype == "score":
                labels = list(qspec["criteria"])
                q = f"{instructions}（等级从低到高：{'；'.join(labels)}）"
                descs = [f"等级{i}: {s}" for i, s in enumerate(labels)]
                result = self.model.decide(q, descs, context=state)
                probs = [0.0] * len(labels)
                for opt_str, p in result:
                    for i in range(len(labels)):
                        if f"等级{i}" in opt_str or str(i) in opt_str:
                            probs[i] = float(p)
                            break
            elif qtype == "noul":
                labels = ["true", "false"]
                q = instructions
                p_true = self.model.is_true(q, context=state)
                if hasattr(p_true, "item"):
                    p_true = p_true.item()
                pt = float(p_true)
                probs = [pt, 1.0 - pt]
            else:
                raise ValueError(qtype)

            s = sum(probs)
            if s > 0:
                probs = [x / s for x in probs]
            out[qname] = {"labels": labels, "probs": probs,
                          "confidence": None, "answer_confidence": max(probs) if probs else None}
        out["_latency_ms"] = (time.perf_counter() - t_all) * 1000 / max(1, len(item["questions"]))
        out["_usage"] = {}
        return out
