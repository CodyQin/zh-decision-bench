# -*- coding: utf-8 -*-
"""
校准与决策质量指标。
指标体系参照 arXiv:2609.29429 (Just Ask Jev) 论文，
全部基于"每题一个概率向量 + 一个正确选项下标"的统一格式。

probs:  shape (N, K) 的 numpy 数组，每行和为 1
labels: shape (N,)   的 numpy 数组，取值 0..K-1
"""
import numpy as np
from sklearn.metrics import roc_auc_score


def _check(probs, labels):
    probs = np.asarray(probs, dtype=float)
    labels = np.asarray(labels, dtype=int)
    assert probs.ndim == 2
    assert len(probs) == len(labels)
    return probs, labels


def accuracy(probs, labels):
    probs, labels = _check(probs, labels)
    return float((probs.argmax(axis=1) == labels).mean())


def nll(probs, labels, eps=1e-12):
    """平均负对数似然：错误且自信会受重罚。"""
    probs, labels = _check(probs, labels)
    p = np.clip(probs[np.arange(len(labels)), labels], eps, 1.0)
    return float(-np.log(p).mean())


def brier(probs, labels):
    """多类 Brier 分数：sum_k (p_k - y_k)^2 的样本均值，越小越好。"""
    probs, labels = _check(probs, labels)
    Y = np.zeros_like(probs)
    Y[np.arange(len(labels)), labels] = 1.0
    return float(((probs - Y) ** 2).sum(axis=1).mean())


def ece(probs, labels, n_bins=15):
    """Top-label 期望校准误差：按最大概率分箱，|置信度-准确度| 加权平均。"""
    probs, labels = _check(probs, labels)
    conf = probs.max(axis=1)
    correct = (probs.argmax(axis=1) == labels).astype(float)
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    ece_val, total = 0.0, len(conf)
    for lo, hi in zip(bins[:-1], bins[1:]):
        m = (conf > lo) & (conf <= hi)
        if m.sum() == 0:
            continue
        ece_val += m.sum() / total * abs(conf[m].mean() - correct[m].mean())
    return float(ece_val)


def base_rate_gap(probs, labels):
    """论文中的 base-rate mismatch：|平均置信度 - 准确率|。"""
    probs, labels = _check(probs, labels)
    return float(abs(probs.max(axis=1).mean() - (probs.argmax(axis=1) == labels).mean()))


def auroc_macro(probs, labels):
    """macro 平均 AUROC：置信度的排序质量（与校准无关，衡量区分度）。"""
    probs, labels = _check(probs, labels)
    K = probs.shape[1]
    if K == 2:
        return float(roc_auc_score(labels, probs[:, 1]))
    return float(roc_auc_score(labels, probs, multi_class="ovr",
                               average="macro", labels=list(range(K))))


def coverage_accuracy(conf, correct, fractions=(0.5,)):
    """选择性预测：只保留置信度最高的前 f 比例样本时的准确率。"""
    conf = np.asarray(conf)
    correct = np.asarray(correct, dtype=float)
    order = np.argsort(-conf)
    out = {}
    for f in fractions:
        k = max(1, int(round(f * len(order))))
        out[f] = float(correct[order[:k]].mean())
    return out


def bootstrap_ci(fn, probs, labels, n_boot=1000, seed=42, alpha=0.05):
    """任意指标 fn(probs, labels) 的 Bootstrap 95% 置信区间。
    probs 可以是 (N,K) 概率矩阵，也可以是 (N,) 的 top-label 置信度向量。"""
    probs = np.asarray(probs, dtype=float)
    labels = np.asarray(labels)
    assert len(probs) == len(labels)
    rng = np.random.default_rng(seed)
    N = len(labels)
    stats = []
    for _ in range(n_boot):
        idx = rng.integers(0, N, N)
        stats.append(fn(probs[idx], labels[idx]))
    lo, hi = np.percentile(stats, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return float(lo), float(hi)


def fit_temperature(log_probs, labels, grid=None):
    """
    温度重标定（E2 核心）。
    log_probs: 未归一化的对数几率 (N, K)，来自模型原始输出。
    返回使 NLL 最小的温度 T。模型卡建议按 (题型, 选项数) 分桶分别拟合。
    """
    log_probs = np.asarray(log_probs, dtype=float)
    labels = np.asarray(labels, dtype=int)
    if grid is None:
        grid = np.exp(np.linspace(-3, 3, 401))  # T in [0.05, 20]
    best_T, best_nll = 1.0, np.inf
    for T in grid:
        z = log_probs / T
        z = z - z.max(axis=1, keepdims=True)
        p = np.exp(z)
        p /= p.sum(axis=1, keepdims=True)
        v = -np.log(np.clip(p[np.arange(len(labels)), labels], 1e-12, 1.0)).mean()
        if v < best_nll:
            best_T, best_nll = float(T), float(v)
    return best_T, best_nll


def apply_temperature(log_probs, T):
    z = np.asarray(log_probs, dtype=float) / T
    z = z - z.max(axis=1, keepdims=True)
    p = np.exp(z)
    return p / p.sum(axis=1, keepdims=True)
