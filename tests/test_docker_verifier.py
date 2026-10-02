from types import SimpleNamespace
from graph_reasoning_research.types import Candidate
from graph_reasoning_research.verification.docker import DockerPythonVerifier

def test_docker_verifier_refuses_unpinned_image():
    verifier=DockerPythonVerifier("python:3.11")
    result=verifier.evaluate_visible(Candidate("c","t","def solve(): return 1",metadata={"visible_tests":{"assertions":["assert True"]}}))
    assert result.objective_result=="INFRASTRUCTURE_ERROR"
    assert result.failure_class=="unpinned_docker_image"

def test_docker_command_enforces_sandbox(monkeypatch):
    calls=[]
    monkeypatch.setattr("shutil.which",lambda name:"/usr/bin/docker")
    monkeypatch.setattr("subprocess.run",lambda *args,**kwargs: calls.append((args[0],kwargs)) or SimpleNamespace(returncode=0,stdout="",stderr=""))
    candidate=Candidate("c","t","def solve(): return 1",metadata={"entry_point":"solve","visible_tests":{"setup":"","assertions":["assert candidate() == 1"]}})
    result=DockerPythonVerifier("python:3.11-slim-trixie@sha256:"+"a"*64).evaluate_visible(candidate)
    assert result.objective_result=="PASS"
    command=calls[0][0]
    assert "--network=none" in command
    assert "--read-only" in command
    assert "--cap-drop=ALL" in command
    assert "--security-opt=no-new-privileges" in command
    assert "--platform=linux/amd64" in command
