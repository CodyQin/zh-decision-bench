# -*- coding: utf-8 -*-
"""
Jev API 适配器。协议与 laya-serve 相同（POST /v1/systemone，Bearer 认证，
body: {"state":..., "questions":{...}}，返回 answers 概率结构）。
key 从项目根目录 .env 的 TYPESAFE_API_KEY 读取。
"""
import json
import os
import time
from pathlib import Path

import requests

BASE_URL = os.environ.get("TYPESAFE_BASE_URL", "https://api.typesafe.ai")
OPENROUTER_URL = "https://openrouter.ai/api/v1/systemone"
OPENROUTER_MODEL = "typesafe/jev-1.13"
VERCEL_URL = "https://ai-gateway.vercel.sh/v1/evaluate"
VERCEL_MODEL = "typesafe-ai/jev"


def _read_env(name):
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith(name + "="):
                v = line.split("=", 1)[1].strip()
                if v and "在这里" not in v and "粘贴" not in v:
                    return v
    return os.environ.get(name)


class JevAdapter:
    def __init__(self, probe=False):
        self.name = "jev"
        self.key = _read_env("TYPESAFE_API_KEY")
        self.base = BASE_URL
        self.via = "typesafe-direct"
        if not self.key:
            # Vercel AI Gateway：每月$5免费额度、无需绑卡（Hobby计划）
            self.key = _read_env("AI_GATEWAY_API_KEY")
            self.base = VERCEL_URL
            self.via = "vercel"
        if not self.key:
            self.key = _read_env("OPENROUTER_API_KEY")
            self.base = OPENROUTER_URL
            self.via = "openrouter"
        if not self.key:
            raise SystemExit("未找到 key：在 .env 里配 AI_GATEWAY_API_KEY（Vercel，免费）"
                             "、TYPESAFE_API_KEY（直连）或 OPENROUTER_API_KEY")
        self.session = requests.Session()
        headers = {"Authorization": f"Bearer {self.key}",
                   "Content-Type": "application/json"}
        if self.via == "openrouter":
            headers["HTTP-Referer"] = "https://github.com/CodyQin/zh-decision-bench"
            headers["X-Title"] = "zh-decision-bench"
        self.session.headers.update(headers)
        self.probe = probe  # True 时打印首条原始返回，用于核对格式

    def _post(self, payload, retries=4):
        if self.via == "openrouter":
            payload = {"model": OPENROUTER_MODEL, **payload}
        elif self.via == "vercel":
            # Vercel /v1/evaluate 的请求体与 systemone 同构，仅多 model 字段；
            # 返回 answers.{name}.probabilities / probability(boolean)，与现有解析兼容
            payload = {"model": VERCEL_MODEL, **payload}
        for i in range(retries):
            try:
                r = self.session.post(self.base, json=payload, timeout=60)
                if r.status_code == 200:
                    return r.json()
                if r.status_code in (429, 500, 502, 503):
                    wait = 2 ** i
                    print(f"  [jev] HTTP {r.status_code}，{wait}s 后重试")
                    time.sleep(wait)
                    continue
                raise RuntimeError(f"Jev HTTP {r.status_code}: {r.text[:300]}")
            except requests.RequestException as e:
                if i == retries - 1:
                    raise
                print(f"  [jev] 网络错误 {e}，重试")
                time.sleep(2 ** i)
        raise RuntimeError("Jev 重试次数用尽")

    def predict_item(self, item):
        payload = {"state": item["state"], "questions": item["questions"]}
        t0 = time.perf_counter()
        result = self._post(payload)
        latency_ms = (time.perf_counter() - t0) * 1000
        if self.probe:
            print(json.dumps(result, ensure_ascii=False, indent=2)[:2000])
            self.probe = False
        out = {}
        for qname, qspec in item["questions"].items():
            ans = result.get("answers", {}).get(qname, {})
            qtype = qspec["type"]
            if qtype == "choice":
                labels = list(qspec["criteria"].keys())
                p = ans.get("probabilities", {})
                probs = [float(p.get(l, 0.0)) for l in labels]
            elif qtype == "score":
                labels = list(qspec["criteria"])
                p = ans.get("probabilities", {})
                probs = [float(p.get(str(i), p.get(l, 0.0)))
                         for i, l in enumerate(labels)]
            elif qtype == "noul":
                labels = ["true", "false"]
                pt = float(ans.get("noul", ans.get("probability", 0.5)))
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
