# -*- coding: utf-8 -*-
"""把 v0.2 结果总表渲染为图片（中英双语），供 X 文章等不支持表格的场合使用。"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SURFACE, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9"

plt.rcParams.update({
    "font.sans-serif": ["Microsoft YaHei", "Segoe UI", "sans-serif"],
    "figure.facecolor": SURFACE, "savefig.facecolor": SURFACE,
})

DATA = {
    "zh": {
        "cols": ["中文任务", "Jev", "NeoHorse\n4B", "Laya\n322M", "Qwen\n2B"],
        "rows": [
            ("语音路由（n=323）",      ["**0.960**", "0.950", "0.870", "0.938"]),
            ("客服路由（n=34）",       ["0.882", "**0.912**", "0.618", "0.882"]),
            ("紧急度分级",             ["**0.676**", "0.471", "0.647", "0.529"]),
            ("诈骗识别",               ["**0.952**", "0.810", "0.714", "0.524"]),
            ("是否转人工",             ["0.600", "**0.618**", "0.564", "0.473"]),
            ("选项顺序翻转率",         ["1.9%", "2.9%", "**20.6%**", "2.9%"]),
        ],
        "title": "zh-decision-bench v0.2 · 五模型中文实测（准确率，加粗=单项第一）",
    },
    "en": {
        "cols": ["zh task", "Jev", "NeoHorse\n4B", "Laya\n322M", "Qwen\n2B"],
        "rows": [
            ("Voice routing (n=323)",  ["**0.960**", "0.950", "0.870", "0.938"]),
            ("CS routing (n=34)",      ["0.882", "**0.912**", "0.618", "0.882"]),
            ("Urgency grading",        ["**0.676**", "0.471", "0.647", "0.529"]),
            ("Scam detection",         ["**0.952**", "0.810", "0.714", "0.524"]),
            ("Escalation",             ["0.600", "**0.618**", "0.564", "0.473"]),
            ("Option-order flip rate", ["1.9%", "2.9%", "**20.6%**", "2.9%"]),
        ],
        "title": "zh-decision-bench v0.2 · five models on Chinese tasks (accuracy; bold = best)",
    },
}


def render(lang):
    d = DATA[lang]
    n_rows, n_cols = len(d["rows"]) + 1, len(d["cols"])
    fig_h = 0.62 * n_rows + 0.9
    fig, ax = plt.subplots(figsize=(9.2, fig_h))
    ax.axis("off")
    table = ax.table(cellText=[[c.replace("**", "") for c in r[1]] for r in d["rows"]],
                     rowLabels=[r[0] for r in d["rows"]],
                     colLabels=d["cols"], cellLoc="center", loc="upper center")
    table.auto_set_font_size(False)
    table.set_fontsize(11.5)
    table.scale(1, 1.75)

    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor(GRID)
        cell.set_linewidth(0.7)
        if row == 0:  # 表头
            cell.set_facecolor("#f0efec")
            cell.set_text_props(weight="bold", color=INK)
        elif col == -1:  # 行名
            cell.set_text_props(color=INK2, ha="left")
            cell.set_facecolor(SURFACE)
        else:
            raw = d["rows"][row - 1][1][col]
            cell.set_facecolor(SURFACE)
            if raw.startswith("**"):
                cell.set_text_props(weight="bold", color="#1c5cab")

    ax.set_title(d["title"], color=INK, fontsize=13, pad=18)
    out = Path("reports/figs") / f"results_table_{lang}.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"已生成 {out}")


for lang in ("zh", "en"):
    render(lang)
