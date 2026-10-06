from __future__ import annotations

import math
import random
from collections import Counter

import numpy as np

from graph_reasoning_research.graph.scoring import (
    degree_centrality,
    local_neighborhood_agreement,
    pagerank,
    weighted_degree,
)
from graph_reasoning_research.types import CandidateSet, GraphData, Selection


def first_candidate(candidate_set: CandidateSet) -> Selection:
    c = candidate_set.candidates[0]
    return Selection("first_candidate", c.candidate_id, {x.candidate_id: float(i == 0) for i, x in enumerate(candidate_set.candidates)})


def random_candidate(candidate_set: CandidateSet, seed: int) -> Selection:
    rng = random.Random(seed)
    idx = rng.randrange(len(candidate_set.candidates))
    scores = {c.candidate_id: float(i == idx) for i, c in enumerate(candidate_set.candidates)}
    return Selection("random_candidate", candidate_set.candidates[idx].candidate_id, scores, {"seed": seed})


def consensus(candidate_set: CandidateSet) -> Selection:
    answers = [c.answer for c in candidate_set.candidates]
    counts = Counter(answers)
    best_answer, _ = sorted(counts.items(), key=lambda kv: (-kv[1], str(kv[0])))[0]
    ranked = sorted(candidate_set.candidates, key=lambda c: (-counts[c.answer], c.candidate_id))
    scores = {c.candidate_id: float(counts[c.answer]) for c in candidate_set.candidates}
    return Selection("consensus", ranked[0].candidate_id, scores, {"consensus_value": best_answer})


def similarity_ranking(candidate_set: CandidateSet, similarity: np.ndarray) -> Selection:
    if similarity.shape != (len(candidate_set.candidates), len(candidate_set.candidates)):
        raise ValueError("similarity shape mismatch")
    scores = similarity.sum(axis=1) - np.diag(similarity)
    best = sorted(range(len(scores)), key=lambda i: (-float(scores[i]), candidate_set.candidates[i].candidate_id))[0]
    return Selection("similarity_ranking", candidate_set.candidates[best].candidate_id, {candidate_set.candidates[i].candidate_id: float(scores[i]) for i in range(len(scores))})


def graph_ranking(candidate_set: CandidateSet, graph: GraphData, scoring_method: str) -> Selection:
    score_fn = {
        "weighted_degree": weighted_degree,
        "degree_centrality": degree_centrality,
        "pagerank": pagerank,
        "local_neighborhood_agreement": local_neighborhood_agreement,
    }.get(scoring_method)
    if score_fn is None:
        raise ValueError(f"unknown graph scoring method: {scoring_method}")
    scores = score_fn(graph)
    best = sorted(scores, key=lambda cid: (-float(scores[cid]), cid))[0]
    return Selection(f"graph:{graph.builder}:{scoring_method}", best, scores, {"graph": graph.config})


def objective_verification(candidate_set: CandidateSet, objective_scores: dict[str, float]) -> Selection:
    # The verifier's scores are external to graph computation.
    missing = [c.candidate_id for c in candidate_set.candidates if c.candidate_id not in objective_scores]
    if missing:
        raise ValueError(f"objective scores missing: {missing}")
    best = sorted(objective_scores, key=lambda cid: (-float(objective_scores[cid]), cid))[0]
    return Selection("objective_verification", best, dict(objective_scores))
