# -*- coding: utf-8 -*-
"""
生成报告图表（reports/figs/*.png）：
1. 可靠性图（reliability diagram）
2. 各场景准确率 / ECE 模型对比（双面板小倍数，单轴原则）
3. coverage-accuracy 选择性预测曲线
配色：dataviz 校验过的默认色板（浅色模式，GitHub README 用）。
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
               "qwen": "#1baf7a", "jev": "#eda100"}
MODEL_LABEL = {"laya-multi": "Laya 多语言 322M", "laya-en": "Laya 英文 421M",
               "qwen": "Qwen3.5-2B", "jev": "Jev API"}

plt.rcParams.update({
    "font.sans-serif": ["Microsoft YaHei", "SimHei", "sans-serif"],
    "axes.unicode_minus": False,
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "axes.edgecolor": AXIS, "axes.linewidth": 0.8,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "text.color": INK, "axes.labelcolor": INK2,
    "font.size": 11,
})

SCN_LABEL = {"voice_assistant_routing": "语音指令路由", "ecommerce_cs": "电商客服",
             "content_moderation": "内容风控"}
Q_LABEL = {"route": "路由", "urgency": "紧急度", "escalate": "转人工", "scam": "诈骗识别"}


def load_all():
    recs = []
    for p in sorted(Path("results/raw").glob("*.jsonl")):
        for line in open(p, encoding="utf-8"):
            d = json.loads(line)
            if "_meta" not in d:
                recs.append(d)
    return recs


def reliability(ax, recs, title):
    conf = np.array([max(r["probs"]) for r in recs])
    correct = np.array([int(np.argmax(r["probs"]) == r["gold_idx"]) for r in recs])
    bins = np.linspace(0, 1, 11)
    centers, accs, fracs = [], [], []
    for lo, hi in zip(bins[:-1], bins[1:]):
        m = (conf > lo) & (conf <= hi)
        if m.sum() >= 3:
            centers.append((lo + hi) / 2)
            accs.append(correct[m].mean())
            fracs.append(m.sum() / len(conf))
    ax.plot([0, 1], [0, 1], color=AXIS, lw=1, ls="--", label="完美校准")
    w = 0.09
    for c, a, f in zip(centers, accs, fracs):
        ax.bar(c, a, width=w * (0.6 + 0.4 * min(f / 0.3, 1)), bottom=0,
               color=MODEL_COLOR["laya-multi"], alpha=0.85, edgecolor=SURFACE, linewidth=1)
    ax.set_xlabel("模型置信度")
    ax.set_ylabel("实际准确率")
    ax.set_title(title, color=INK, fontsize=12)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)


def main():
    recs = load_all()
    models = sorted({r["model"] for r in recs})
    out = Path("reports/figs"); out.mkdir(parents=True, exist_ok=True)
    multi = [r for r in recs if r["model"] == "laya-multi"]

    # 1. 可靠性图（laya-multi：两个代表场景）
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 4.2))
    reliability(axes[0], [r for r in multi
                          if r["domain"] == "voice_assistant_routing"],
                "语音指令路由（ECE 0.061）")
    reliability(axes[1], [r for r in multi
                          if r["domain"] == "ecommerce_cs" and r["question"] == "route"],
                "电商客服路由（ECE 0.271）")
    fig.suptitle("Laya 多语言版（322M）中文可靠性图：什么时候置信度可信",
                 color=INK, fontsize=13)
    fig.tight_layout()
    fig.savefig(out / "reliability_laya_multi.png", dpi=150)
    plt.close(fig)

    # 2. 模型对比（准确率 / ECE 双面板，每场景分组条形）
    groups = ["voice_assistant_routing", "ecommerce_cs", "content_moderation"]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    x = np.arange(len(groups))
    bw = 0.8 / max(len(models), 1)
    for pi, (ax, key, ylab, title) in enumerate(zip(
            axes, ["acc", "ece"], ["准确率", "ECE（越小越好）"],
            ["准确率对比", "校准误差对比"])):
        for mi, m in enumerate(models):
            vals = []
            for g in groups:
                rs = [r for r in recs if r["model"] == m and r["domain"] == g]
                conf = np.array([max(r["probs"]) for r in rs])
                corr = np.array([int(np.argmax(r["probs"]) == r["gold_idx"]) for r in rs])
                if key == "acc":
                    vals.append(corr.mean() if len(rs) else np.nan)
                else:
                    # top-label ECE（10 bin）
                    v, tot = 0.0, max(len(rs), 1)
                    bins = np.linspace(0, 1, 11)
                    for lo, hi in zip(bins[:-1], bins[1:]):
                        msk = (conf > lo) & (conf <= hi)
                        if msk.sum():
                            v += msk.sum() / tot * abs(conf[msk].mean() - corr[msk].mean())
                    vals.append(v if len(rs) else np.nan)
            bars = ax.bar(x + (mi - (len(models) - 1) / 2) * bw, vals, bw * 0.92,
                          color=MODEL_COLOR.get(m, MUTED), label=MODEL_LABEL.get(m, m),
                          edgecolor=SURFACE, linewidth=1)
            for b, v in zip(bars, vals):
                if not np.isnan(v):
                    ax.text(b.get_x() + b.get_width() / 2, v + 0.02, f"{v:.2f}",
                            ha="center", va="bottom", fontsize=8.5, color=INK2)
        ax.set_xticks(x)
        ax.set_xticklabels([SCN_LABEL[g] for g in groups])
        ax.set_ylabel(ylab)
        ax.set_title(title, color=INK, fontsize=12)
        ax.set_ylim(0, 1.0)
        if pi == 0:
            ax.legend(frameon=False, fontsize=9)
    fig.suptitle("中文决策场景：模型 × 场景（各场景全部问题汇总，top-label 口径）",
                 color=INK, fontsize=13)
    fig.tight_layout()
    fig.savefig(out / "model_comparison.png", dpi=150)
    plt.close(fig)

    # 3. coverage-accuracy 曲线（路由类问题）
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
                marker="o", ms=3.5, label=MODEL_LABEL.get(m, m))
    ax.set_xlabel("自动处理覆盖率（按置信度排序保留前 x%）")
    ax.set_ylabel("该覆盖率下的准确率")
    ax.set_title("选择性预测：只自动处理最有把握的部分，准确率能到多少",
                 color=INK, fontsize=12)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.legend(frameon=False, fontsize=9)
    fig.tight_layout()
    fig.savefig(out / "coverage_accuracy.png", dpi=150)
    plt.close(fig)

    print(f"已生成 3 张图 -> {out}")


if __name__ == "__main__":
    main()
