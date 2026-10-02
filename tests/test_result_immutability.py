from pathlib import Path
import pytest
from graph_reasoning_research.logging.schema import write_jsonl_exclusive
from graph_reasoning_research.types import RunRecord

def _record():
    return RunRecord(
        experiment_id="EXP-001",run_id="r",task_id="t",seed=42,aggregation_method="x",
        representation_method="feature_hash_tfidf",representation_config_hash="r",graph_method=None,
        graph_config_hash=None,candidate_id="c",selected_candidate_id="c",objective_result="PASS",
        generation_model_id="m",generation_config_hash="g",generation_calls=1,generation_input_tokens=0,
        generation_output_tokens=0,representation_calls=1,representation_tokens=0,embedding_latency_ms=0,
        similarity_latency_ms=0,representation_latency_ms=0,graph_construction_latency_ms=0,
        graph_scoring_latency_ms=0,aggregation_latency_ms=0,visible_verification_latency_ms=0,
        hidden_verification_latency_ms=0,candidate_set_hash="csh",representation_hash="rh",
        similarity_config={},graph_stats={})

def test_result_artifact_is_immutable(tmp_path:Path):
    path=tmp_path/"run.jsonl"
    write_jsonl_exclusive(path,[_record()])
    with pytest.raises(FileExistsError):
        write_jsonl_exclusive(path,[_record()])
