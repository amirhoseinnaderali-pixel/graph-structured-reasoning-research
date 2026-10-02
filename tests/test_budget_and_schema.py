import json
from graph_reasoning_research.budgeting.budget import BudgetLedger
from graph_reasoning_research.logging.schema import validate_record, append_jsonl
from graph_reasoning_research.types import RunRecord

def test_budget_fails_closed():
    b=BudgetLedger(max_candidate_calls=1,max_generation_tokens=10,max_embedding_calls=1,max_verification_executions=1); b.reserve_generation(10)
    try: b.reserve_generation(1); assert False
    except RuntimeError: pass

def test_result_schema_roundtrip(tmp_path):
    r=RunRecord(experiment_id='EXP-001',run_id='r',task_id='t',seed=42,aggregation_method='x',representation_method='hash',graph_method=None,candidate_id='c',selected_candidate_id='c',objective_result='PASS',generation_tokens=0,representation_tokens=0,embedding_latency_ms=.5,similarity_latency_ms=.5,representation_latency_ms=1.0,graph_construction_latency_ms=1.0,graph_scoring_latency_ms=1.0,aggregation_latency_ms=3.0,verification_latency_ms=1.0,candidate_set_hash='ch',representation_hash='rh',graph_stats={})
    p=tmp_path/'r.jsonl'; append_jsonl(p,r); row=json.loads(p.read_text()); assert validate_record(row)==[]; assert row['experiment_id']=='EXP-001'
