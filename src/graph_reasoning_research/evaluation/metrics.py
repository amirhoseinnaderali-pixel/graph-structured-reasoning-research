from __future__ import annotations

import math
import random
from collections import defaultdict
from typing import Iterable


def accuracy(values: Iterable[bool]) -> float:
    xs = list(values)
    return sum(xs) / len(xs) if xs else float("nan")


def spearman(rank_a: list[int], rank_b: list[int]) -> float:
    if len(rank_a) != len(rank_b) or len(rank_a) < 2:
        raise ValueError("rank lists must have equal length >= 2")
    n = len(rank_a)
    d2 = sum((a - b) ** 2 for a, b in zip(rank_a, rank_b))
    return 1.0 - 6.0 * d2 / (n * (n * n - 1))


def kendall_tau(order_a: list[str], order_b: list[str]) -> float:
    pos = {x: i for i, x in enumerate(order_b)}
    pairs = 0
    concordant = 0
    discordant = 0
    for i in range(len(order_a)):
        for j in range(i + 1, len(order_a)):
            pairs += 1
            a = pos[order_a[i]] - pos[order_a[j]]
            concordant += int(a < 0)
            discordant += int(a > 0)
    return (concordant - discordant) / pairs if pairs else 0.0


def _cluster_means(values: list[float], clusters: list[str]) -> list[float]:
    if len(values) != len(clusters):
        raise ValueError("values and clusters must have equal length")
    grouped = defaultdict(list)
    for value, cluster in zip(values, clusters):
        grouped[cluster].append(value)
    return [sum(grouped[key]) / len(grouped[key]) for key in sorted(grouped)]


def bootstrap_ci(
    values: list[float],
    seed: int = 42,
    n_resamples: int = 10000,
    alpha: float = 0.05,
    clusters: list[str] | None = None,
) -> tuple[float, float]:
    if clusters is not None:
        values = _cluster_means(values, clusters)
    if not values:
        return (float("nan"), float("nan"))
    rng = random.Random(seed)
    n = len(values)
    means = []
    for _ in range(n_resamples):
        sample = [values[rng.randrange(n)] for _ in range(n)]
        means.append(sum(sample) / n)
    means.sort()
    lo = means[int((alpha / 2) * n_resamples)]
    hi = means[int((1 - alpha / 2) * n_resamples) - 1]
    return lo, hi


def paired_difference_ci(
    a: list[float],
    b: list[float],
    seed: int = 42,
    clusters: list[str] | None = None,
) -> tuple[float, float]:
    if len(a) != len(b):
        raise ValueError("paired samples must be equal length")
    diffs = [x - y for x, y in zip(a, b)]
    if clusters is not None:
        return bootstrap_ci(diffs, seed=seed, clusters=clusters)
    return bootstrap_ci(diffs, seed=seed)
