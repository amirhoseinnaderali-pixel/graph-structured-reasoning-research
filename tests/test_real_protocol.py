from graph_reasoning_research.experiments.config import load_yaml
from graph_reasoning_research.experiments.runner import _prepare_generator
from graph_reasoning_research.graph.builders import knn_graph, threshold_graph
import numpy as np

def test_real_generator_is_not_mock():
    cfg=load_yaml("configs/experiments/EXP-001.yaml")
    generator=_prepare_generator(__import__("pathlib").Path("."),cfg,"real")
    assert generator.__class__.__name__=="OpenAICandidateGenerator"

def test_c6_factorial_ablation_has_sixteen_conditions():
    cfg=load_yaml("configs/graph/EXP-001.yaml")
    specs=[(b,w,s) for b in ("threshold","knn") for w in (True,False) for s in cfg["scoring"]["methods"]]
    assert len(specs)==16

def test_graph_builder_does_not_require_candidate_metadata():
    ids=("a","b","c")
    sim=np.eye(3)
    assert threshold_graph(ids,sim,0.5,True).nodes==ids
    assert knn_graph(ids,sim,2,False).nodes==ids
