import json
from graph_reasoning_research.budgeting.budget import BudgetLedger
from graph_reasoning_research.logging.schema import append_jsonl, validate_record
from graph_reasoning_research.types import RunRecord

def test_budget_fails_closed():
    budget=BudgetLedger(max_generation_calls=1,max_generation_input_tokens=10,max_generation_output_tokens=10,
                        max_representation_calls=1,max_visible_verifications=1,max_hidden_verifications=1)
    budget.reserve_generation(10,10)
    try:
        budget.reserve_generation(1,1)
        assert False
    except RuntimeError as exc:
        assert "budget_ineligibility" in str(exc)

def test_verification_budget_is_separate():
    budget=BudgetLedger(max_generation_calls=1,max_generation_input_tokens=10,max_generation_output_tokens=10,
                        max_representation_calls=1,max_visible_verifications=1,max_hidden_verifications=1)
    budget.reserve_visible_verification()
    budget.reserve_hidden_verification()
    try:
        budget.reserve_visible_verification()
        assert False
    except RuntimeError:
        pass

def test_result_schema_roundtrip(tmp_path):
    record=RunRecord(experiment_id="EXP-001",run_id="r",task_id="t",seed=42,aggregation_method="x",
        representation_method="feature_hash_tfidf",representation_config_hash="rch",graph_method=None,
        graph_config_hash=None,candidate_id="c",selected_candidate_id="c",objective_result="PASS",
        generation_model_id="mock",generation_config_hash="gch",generation_calls=1,generation_input_tokens=0,
        generation_output_tokens=0,representation_calls=1,representation_tokens=0,embedding_latency_ms=0.5,
        similarity_latency_ms=0.5,representation_latency_ms=1.0,graph_construction_latency_ms=0.0,
        graph_scoring_latency_ms=0.0,aggregation_latency_ms=1.0,visible_verification_latency_ms=1.0,
        hidden_verification_latency_ms=0.0,candidate_set_hash="ch",representation_hash="rh",
        similarity_config={"function":"cosine"},graph_stats={},benchmark_hash="bh")
    path=tmp_path/"r.jsonl"
    append_jsonl(path,record)
    row=json.loads(path.read_text())
    assert validate_record(row)==[]
    assert row["experiment_id"]=="EXP-001"
    assert row["status"]=="SUCCESS"
