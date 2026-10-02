from graph_reasoning_research.verification.docker import DockerPythonVerifier
from graph_reasoning_research.types import Candidate

def test_docker_verifier_refuses_unpinned_image():
    v=DockerPythonVerifier('python:3.11')
    try: v.evaluate(Candidate('c','t','def solve(): return 1')); assert False
    except RuntimeError as e: assert 'pinned image digest' in str(e)
