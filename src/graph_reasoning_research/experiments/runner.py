from __future__ import annotations
import hashlib, time
from pathlib import Path
from graph_reasoning_research.aggregation.baselines import consensus, first_candidate, graph_ranking, objective_verification, random_candidate, similarity_ranking
from graph_reasoning_research.budgeting.budget import BudgetLedger
from graph_reasoning_research.generation.base import MockCandidateGenerator
from graph_reasoning_research.graph.builders import knn_graph, threshold_graph
from graph_reasoning_research.logging.schema import append_jsonl
from graph_reasoning_research.representations.base import HashEmbeddingProvider
from graph_reasoning_research.similarity.cosine import cosine_similarity_matrix
from graph_reasoning_research.types import RunRecord, Selection
from graph_reasoning_research.verification.objective import MockObjectiveVerifier

def _run_id(seed:int,task_id:str)->str: return hashlib.sha256(f'EXP-001|{seed}|{task_id}'.encode()).hexdigest()[:16]

def run_mock(config:dict,output_path:str|Path)->list[dict]:
    generator=MockCandidateGenerator(); rep=HashEmbeddingProvider(); verifier=MockObjectiveVerifier(); rows=[]
    tasks=[('mock-001','return 1'),('mock-002','return 0')]
    for seed in config['seeds']:
      for task_id,problem in tasks:
        ledger=BudgetLedger(max_candidate_calls=1,max_generation_tokens=8192,max_embedding_calls=8,max_verification_executions=8)
        ledger.reserve_generation(config['candidate_count']); candidate_set=generator.generate(task_id,problem,config['candidate_count'],seed)
        candidates=[]
        for c in candidate_set.candidates:
          score=1.0 if c.answer=='1' else 0.0
          candidates.append(c.__class__(c.candidate_id,c.task_id,c.text,c.answer,c.generator_id,{'mock_objective':score}))
        candidate_set=candidate_set.__class__(candidate_set.task_id,tuple(candidates),candidate_set.candidate_set_hash)
        ledger.reserve_embedding(); t0=time.perf_counter(); batch=rep.encode(candidate_set); embedding_ms=(time.perf_counter()-t0)*1000
        t0=time.perf_counter(); sim=cosine_similarity_matrix(batch.embeddings); similarity_ms=(time.perf_counter()-t0)*1000
        node_ids=candidate_set.ids(); t0=time.perf_counter(); graph=threshold_graph(node_ids,sim,threshold=0.25,weighted=True); graph_knn=knn_graph(node_ids,sim,k=2,weighted=False); graph_construction_ms=(time.perf_counter()-t0)*1000
        t0=time.perf_counter(); methods=[first_candidate(candidate_set),random_candidate(candidate_set,seed),consensus(candidate_set),similarity_ranking(candidate_set,sim),graph_ranking(candidate_set,graph,'weighted_degree'),graph_ranking(candidate_set,graph_knn,'degree_centrality')]; graph_scoring_ms=(time.perf_counter()-t0)*1000
        objective_by_id={c.candidate_id:float(c.metadata['mock_objective']) for c in candidate_set.candidates}; graph_sel=methods[-2]; ordered=sorted(graph_sel.scores,key=lambda cid:(-float(graph_sel.scores[cid]),cid)); shortlist=ordered[:2]; shortlist_scores={cid:objective_by_id[cid] for cid in shortlist}
        methods.append(objective_verification(candidate_set,objective_by_id)); shortlist_set=candidate_set.__class__(candidate_set.task_id,tuple(c for c in candidate_set.candidates if c.candidate_id in shortlist),candidate_set.candidate_set_hash); c5=objective_verification(shortlist_set,shortlist_scores); methods.append(Selection('graph+objective_verification',c5.selected_candidate_id,c5.scores,{'graph_priority':True,'shortlist':shortlist}))
        representation_ms=embedding_ms+similarity_ms; agg_ms=representation_ms+graph_construction_ms+graph_scoring_ms
        graph_stats={'nodes':len(graph.nodes),'edges':len(graph.edges),'density':(2*len(graph.edges))/(len(graph.nodes)*(len(graph.nodes)-1)) if len(graph.nodes)>1 else 0.0}
        for sel in methods:
          ledger.reserve_verification(); t1=time.perf_counter(); ev=verifier.evaluate(next(c for c in candidate_set.candidates if c.candidate_id==sel.selected_candidate_id)); ver_ms=(time.perf_counter()-t1)*1000
          row=RunRecord(experiment_id='EXP-001',run_id=_run_id(seed,task_id),task_id=task_id,seed=seed,aggregation_method=sel.method,representation_method=batch.method,graph_method=(graph.builder if sel.method.startswith('graph:') else None),candidate_id=sel.selected_candidate_id,selected_candidate_id=sel.selected_candidate_id,objective_result=ev.objective_result,generation_tokens=ledger.generation_tokens,representation_tokens=0,embedding_latency_ms=embedding_ms,similarity_latency_ms=similarity_ms,representation_latency_ms=representation_ms,graph_construction_latency_ms=graph_construction_ms,graph_scoring_latency_ms=graph_scoring_ms,aggregation_latency_ms=agg_ms,verification_latency_ms=ver_ms,candidate_set_hash=candidate_set.candidate_set_hash,representation_hash=batch.representation_hash,graph_stats=graph_stats,metadata={'validation_only':True,'budget':ledger.__dict__,'scores':sel.scores})
          append_jsonl(output_path,row); rows.append(row.__dict__)
    return rows
