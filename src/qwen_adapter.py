# -*- coding: utf-8 -*-
"""
Qwen 基线适配器：把决策题转成"选项排成 A/B/C、读首 token 字母 logits"
的经典 logit 探针口径。这是"普通小 LLM 做决策"的对照基线——
回答的问题是：决策模型类别的存在意义有多大（对比第4章的 Laya 数字）。
"""
import time

import torch

LETTERS = ["A", "B", "C", "D", "E", "F", "G", "H"]

SYSTEM = "你是分类决策助手。只输出一个选项字母，不要输出任何其他内容。"


def build_prompt(item, qname, qspec):
    lines = [f"场景：{item['state']}", f"问题：{qspec['instructions']}"]
    qtype = qspec["type"]
    if qtype == "choice":
        opts = list(qspec["criteria"].keys())
        descs = [f"{k}：{v}" for k, v in qspec["criteria"].items()]
    elif qtype == "score":
        opts = list(qspec["criteria"])
        descs = [f"等级{i+1}：{s}" for i, s in enumerate(opts)]
    elif qtype == "noul":
        opts = ["true", "false"]
        descs = [f"{qspec['criteria']['true']}（选A）",
                 f"{qspec['criteria']['false']}（选B）"]
    else:
        raise ValueError(qtype)
    lines.append("选项：")
    for i, d in enumerate(descs):
        lines.append(f"{LETTERS[i]}. {d}")
    lines.append("只输出一个选项字母。")
    return "\n".join(lines), opts


class QwenAdapter:
    def __init__(self, model_id=None):
        from pathlib import Path
        from transformers import AutoModelForCausalLM, AutoTokenizer
        self.name = "qwen"
        local = Path(__file__).parent.parent / "models" / "qwen-2b"
        if (local / "config.json").exists():
            model_id = str(local)
        self.model_id = model_id or "Qwen/Qwen3.5-2B"
        self.tok = AutoTokenizer.from_pretrained(self.model_id)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id, torch_dtype=torch.bfloat16, device_map="cuda")
        self.model.eval()
        # 字母的 token id（裸字母；聊天模板下助手回复从新 token 开始）
        self.letter_ids = [self.tok.encode(c, add_special_tokens=False)[0]
                           for c in LETTERS]

    def predict_item(self, item):
        out = {}
        t_all = time.perf_counter()
        for qname, qspec in item["questions"].items():
            text, opts = build_prompt(item, qname, qspec)
            t0 = time.perf_counter()
            msgs = [{"role": "system", "content": SYSTEM},
                    {"role": "user", "content": text}]
            try:
                prompt = self.tok.apply_chat_template(
                    msgs, tokenize=False, add_generation_prompt=True,
                    enable_thinking=False)
            except TypeError:  # 模板不支持 enable_thinking 参数时
                prompt = self.tok.apply_chat_template(
                    msgs, tokenize=False, add_generation_prompt=True)
            inputs = self.tok(prompt, return_tensors="pt").to(self.model.device)
            with torch.no_grad():
                gen = self.model.generate(
                    **inputs, max_new_tokens=1, do_sample=False,
                    return_dict_in_generate=True, output_scores=True)
            logits = gen.scores[0][0]  # 首个生成 token 的词表 logits
            ids = torch.tensor(self.letter_ids[:len(opts)], device=logits.device)
            sel = logits[ids]
            probs = torch.softmax(sel, dim=-1).float().cpu().tolist()
            out[qname] = {"labels": opts, "probs": probs,
                          "confidence": None, "answer_confidence": max(probs)}
            qspec.setdefault("_lat", None)
            out.setdefault("_latencies", {})[qname] = (time.perf_counter() - t0) * 1000
        out["_latency_ms"] = (time.perf_counter() - t_all) * 1000 / max(1, len(item["questions"]))
        out["_usage"] = {}
        return out
