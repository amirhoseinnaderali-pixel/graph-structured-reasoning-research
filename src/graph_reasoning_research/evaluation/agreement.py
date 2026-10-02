from __future__ import annotations
from graph_reasoning_research.evaluation.metrics import kendall_tau, spearman

def rank_order(scores: dict[str, float]) -> list[str]: return sorted(scores, key=lambda k: (-float(scores[k]), k))
def agreement(a: dict[str, float], b: dict[str, float]) -> dict[str, float | bool]:
    order_a=rank_order(a); order_b=rank_order(b); ranks_a={x:i for i,x in enumerate(order_a)}; ranks_b={x:i for i,x in enumerate(order_b)}
    ra=[ranks_a[x] for x in order_a]; rb=[ranks_b[x] for x in order_a]
    return {"selected_candidate_agreement": order_a[0]==order_b[0], "kendall_tau": kendall_tau(order_a, order_b), "spearman": spearman(ra, rb)}
