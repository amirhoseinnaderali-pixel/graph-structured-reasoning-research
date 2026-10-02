from graph_reasoning_research.generation.base import MockCandidateGenerator
from graph_reasoning_research.representations.structured import StructuredReasoningProvider
from graph_reasoning_research.types import Candidate, CandidateSet


def test_structured_reasoning_steps_are_supported():
    base = MockCandidateGenerator().generate("t", "p", 2, 42)
    candidates = tuple(
        Candidate(
            c.candidate_id,
            c.task_id,
            c.text,
            c.answer,
            c.generator_model_id,
            c.seed,
            c.generation_config_hash,
            c.output_hash,
            {"reasoning_steps": ["step one", "step two"]},
        )
        for c in base.candidates
    )
    candidate_set = CandidateSet(base.task_id, candidates, base.candidate_set_hash)
    representation = StructuredReasoningProvider().encode(candidate_set)
    assert representation.method == "structured_reasoning_hash_embedding"
    assert representation.embeddings.shape[0] == 2
