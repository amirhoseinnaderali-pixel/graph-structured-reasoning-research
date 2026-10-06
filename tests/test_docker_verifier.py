from graph_reasoning_research.types import Candidate
from graph_reasoning_research.verification.docker import DockerPythonVerifier


def test_docker_verifier_refuses_unpinned_image():
    verifier = DockerPythonVerifier("python:3.11")
    try:
        verifier.evaluate_visible(Candidate("c", "t", "def solve(): return 1"))
        assert False
    except RuntimeError as exc:
        assert "pinned image digest" in str(exc)
