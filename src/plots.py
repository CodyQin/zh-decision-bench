# -*- coding: utf-8 -*-
"""
生成报告图表（reports/figs/），中英双语双版本：
  *_zh.png / *_en.png，README 中英文版各引各的。
1. 可靠性图  2. 各场景准确率/ECE 对比  3. coverage-accuracy 曲线
配色：dataviz 校验过的默认色板（浅色模式）。
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

# ---- 设计参数（dataviz 参考色板，浅色模式）----
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
MODEL_COLOR = {"laya-multi": "#2a78d6", "laya-en": "#eb6834",
               "qwen": "#1baf7a", "jev": "#eda100", "neohorse": "#4a3aa7"}

L = {
    "zh": {
        "models": {"laya-multi": "Laya 多语言 322M", "laya-en": "Laya 英文 421M",
                   "qwen": "Qwen3.5-2B", "jev": "Jev API", "neohorse": "NeoHorse-Jev-4B"},
        "scn": {"voice_assistant_routing": "语音指令路由", "ecommerce_cs": "电商客服",
                "content_moderation": "内容风控"},
        "xlabel_conf": "模型置信度", "ylabel_acc": "实际准确率",
        "perfect": "完美校准",
        "rel_title": "Laya 多语言版（322M）中文可靠性图：什么时候置信度可信",
        "rel1": "语音指令路由（ECE 0.056）", "rel2": "电商客服路由（ECE 0.311）",
        "cmp_title": "中文决策场景：模型 × 场景（top-label 口径）",
        "cmp_acc": "准确率对比", "cmp_ece": "校准误差对比",
        "ylabel_acc2": "准确率", "ylabel_ece": "ECE（越小越好）",
        "cov_title": "选择性预测：只自动处理最有把握的部分，准确率能到多少",
        "cov_x": "自动处理覆盖率（按置信度排序保留前 x%）", "cov_y": "该覆盖率下的准确率",
    },
    "en": {
        "models": {"laya-multi": "Laya multilingual 322M", "laya-en": "Laya english 421M",
                   "qwen": "Qwen3.5-2B", "jev": "Jev API", "neohorse": "NeoHorse-Jev-4B"},
        "scn": {"voice_assistant_routing": "Voice routing", "ecommerce_cs": "E-commerce CS",
                "content_moderation": "Moderation"},
        "xlabel_conf": "Model confidence", "ylabel_acc": "Empirical accuracy",
        "perfect": "Perfect calibration",
        "rel_title": "Laya multilingual (322M) reliability on zh: when confidence is trustworthy",
        "rel1": "Voice routing (ECE 0.056)", "rel2": "CS routing (ECE 0.311)",
        "cmp_title": "zh decision scenarios: model x scenario (top-label metrics)",
        "cmp_acc": "Accuracy", "cmp_ece": "Calibration error (ECE, lower is better)",
        "ylabel_acc2": "Accuracy", "ylabel_ece": "ECE (lower is better)",
        "cov_title": "Selective prediction: accuracy when auto-handling only the most confident",
        "cov_x": "Coverage (keep top x% by confidence)", "cov_y": "Accuracy at coverage",
    },
}

plt.rcParams.update({
    "font.sans-serif": ["Microsoft YaHei", "Segoe UI", "SimHei", "sans-serif"],
    "axes.unicode_minus": False,
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "axes.edgecolor": AXIS, "axes.linewidth": 0.8,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "text.color": INK, "axes.labelcolor": INK2,
    "font.size": 11,
})


def load_all():
    recs = []
    for p in sorted(Path("results/raw").glob("v0*.jsonl")):
        for line in open(p, encoding="utf-8"):
            d = json.loads(line)
            if "_meta" not in d:
                recs.append(d)
    return recs


def reliability(ax, recs, title, T):
    conf = np.array([max(r["probs"]) for r in recs])
    correct = np.array([int(np.argmax(r["probs"]) == r["gold_idx"]) for r in recs])
    bins = np.linspace(0, 1, 11)
    ax.plot([0, 1], [0, 1], color=AXIS, lw=1, ls="--", label=T["perfect"])
    for lo, hi in zip(bins[:-1], bins[1:]):
        m = (conf > lo) & (conf <= hi)
        if m.sum() >= 3:
            c = (lo + hi) / 2
            w = 0.09 * (0.6 + 0.4 * min(m.sum() / len(conf) / 0.3, 1))
            ax.bar(c, correct[m].mean(), width=w, color=MODEL_COLOR["laya-multi"],
                   alpha=0.85, edgecolor=SURFACE, linewidth=1)
    ax.set_xlabel(T["xlabel_conf"])
    ax.set_ylabel(T["ylabel_acc"])
    ax.set_title(title, color=INK, fontsize=12)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)


def main():
    recs = load_all()
    models = sorted({r["model"] for r in recs})
    out = Path("reports/figs")
    out.mkdir(parents=True, exist_ok=True)
    multi = [r for r in recs if r["model"] == "laya-multi"]
    groups = ["voice_assistant_routing", "ecommerce_cs", "content_moderation"]

    for lang, T in L.items():
        # 1. 可靠性图
        fig, axes = plt.subplots(1, 2, figsize=(9.5, 4.2))
        reliability(axes[0], [r for r in multi if r["domain"] == "voice_assistant_routing"], T["rel1"], T)
        reliability(axes[1], [r for r in multi if r["domain"] == "ecommerce_cs" and r["question"] == "route"], T["rel2"], T)
        fig.suptitle(T["rel_title"], color=INK, fontsize=13)
        fig.tight_layout()
        fig.savefig(out / f"reliability_laya_multi_{lang}.png", dpi=150)
        plt.close(fig)

        # 2. 模型对比（双面板）
        fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
        x = np.arange(len(groups))
        bw = 0.8 / max(len(models), 1)
        for pi, (ax, key, ylab, title) in enumerate(zip(
                axes, ["acc", "ece"], [T["ylabel_acc2"], T["ylabel_ece"]],
                [T["cmp_acc"], T["cmp_ece"]])):
            for mi, m in enumerate(models):
                vals = []
                for g in groups:
                    rs = [r for r in recs if r["model"] == m and r["domain"] == g]
                    conf = np.array([max(r["probs"]) for r in rs])
                    corr = np.array([int(np.argmax(r["probs"]) == r["gold_idx"]) for r in rs])
                    if key == "acc":
                        vals.append(corr.mean() if len(rs) else np.nan)
                    else:
                        v, tot = 0.0, max(len(rs), 1)
                        bins = np.linspace(0, 1, 11)
                        for lo, hi in zip(bins[:-1], bins[1:]):
                            msk = (conf > lo) & (conf <= hi)
                            if msk.sum():
                                v += msk.sum() / tot * abs(conf[msk].mean() - corr[msk].mean())
                        vals.append(v if len(rs) else np.nan)
                bars = ax.bar(x + (mi - (len(models) - 1) / 2) * bw, vals, bw * 0.92,
                              color=MODEL_COLOR.get(m, MUTED), label=T["models"].get(m, m),
                              edgecolor=SURFACE, linewidth=1)
                for b, v in zip(bars, vals):
                    if not np.isnan(v):
                        ax.text(b.get_x() + b.get_width() / 2, v + 0.02, f"{v:.2f}",
                                ha="center", va="bottom", fontsize=8.5, color=INK2)
            ax.set_xticks(x)
            ax.set_xticklabels([T["scn"][g] for g in groups])
            ax.set_ylabel(ylab)
            ax.set_title(title, color=INK, fontsize=12)
            ax.set_ylim(0, 1.0)
            if pi == 0:
                ax.legend(frameon=False, fontsize=9)
        fig.suptitle(T["cmp_title"], color=INK, fontsize=13)
        fig.tight_layout()
        fig.savefig(out / f"model_comparison_{lang}.png", dpi=150)
        plt.close(fig)

        # 3. coverage-accuracy
        fig, ax = plt.subplots(figsize=(6.4, 4.2))
        for m in models:
            rs = [r for r in recs if r["model"] == m and r["question"] == "route"]
            if not rs:
                continue
            conf = np.array([max(r["probs"]) for r in rs])
            corr = np.array([int(np.argmax(r["probs"]) == r["gold_idx"]) for r in rs])
            order = np.argsort(-conf)
            fracs = np.linspace(0.05, 1.0, 20)
            accs = [corr[order[:max(1, int(f * len(order)))]].mean() for f in fracs]
            ax.plot(fracs, accs, color=MODEL_COLOR.get(m, MUTED), lw=2,
                    marker="o", ms=3.5, label=T["models"].get(m, m))
        ax.set_xlabel(T["cov_x"])
        ax.set_ylabel(T["cov_y"])
        ax.set_title(T["cov_title"], color=INK, fontsize=12)
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)
        ax.legend(frameon=False, fontsize=9)
        fig.tight_layout()
        fig.savefig(out / f"coverage_accuracy_{lang}.png", dpi=150)
        plt.close(fig)

    print(f"已生成双语图表 -> {out}")


if __name__ == "__main__":
    main()
