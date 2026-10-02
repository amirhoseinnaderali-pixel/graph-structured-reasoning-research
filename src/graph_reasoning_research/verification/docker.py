from __future__ import annotations
import json, shutil, subprocess, tempfile
from dataclasses import dataclass
from pathlib import Path
from graph_reasoning_research.types import Candidate, CandidateEvaluation

RUNNER_SCRIPT = r"""
import importlib.util, json, sys
candidate_path, suite_path, entry_point = sys.argv[1], sys.argv[2], sys.argv[3]
spec = importlib.util.spec_from_file_location("candidate_module", candidate_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
suite = json.load(open(suite_path, encoding="utf-8"))
candidate = getattr(module, entry_point)
setup = suite.get("setup", "")
if setup.strip():
    exec(setup, {"candidate": candidate}, {"candidate": candidate})
for assertion in suite.get("assertions", []):
    try:
        exec(assertion, {"candidate": candidate}, {"candidate": candidate})
    except AssertionError:
        print(json.dumps({"status":"FAIL","failure_class":"wrong_answer"}))
        raise SystemExit(10)
    except Exception as exc:
        print(json.dumps({"status":"INFRASTRUCTURE_ERROR","failure_class":"runtime_error","error":str(exc)[:500]}))
        raise SystemExit(20)
print(json.dumps({"status":"PASS"}))
"""

@dataclass(frozen=True)
class DockerPythonVerifier:
    image: str
    timeout_seconds: int = 10
    memory: str = "512m"
    cpus: str = "1"
    pids_limit: str = "64"
    platform: str = "linux/amd64"

    def _evaluate(self, candidate: Candidate, suite: dict | None) -> CandidateEvaluation:
        if "@sha256:" not in self.image:
            return CandidateEvaluation(candidate.candidate_id,"INFRASTRUCTURE_ERROR",failure_class="unpinned_docker_image")
        docker = shutil.which("docker")
        if docker is None:
            return CandidateEvaluation(candidate.candidate_id,"INFRASTRUCTURE_ERROR",failure_class="docker_unavailable")
        if not suite or not isinstance(suite.get("assertions"), list):
            return CandidateEvaluation(candidate.candidate_id,"INFRASTRUCTURE_ERROR",failure_class="missing_test_material")
        entry_point = str(candidate.metadata.get("entry_point","candidate"))
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/"candidate.py").write_text(candidate.text,encoding="utf-8")
            (root/"tests.json").write_text(json.dumps(suite),encoding="utf-8")
            (root/"runner.py").write_text(RUNNER_SCRIPT,encoding="utf-8")
            command=[docker,"run","--rm",f"--platform={self.platform}","--network=none","--cap-drop=ALL",
                     "--security-opt=no-new-privileges","--read-only","--ipc=none",f"--pids-limit={self.pids_limit}",
                     f"--memory={self.memory}",f"--cpus={self.cpus}","--tmpfs=/tmp:rw,noexec,nosuid,size=64m",
                     "-v",f"{root}:/work:ro",self.image,"python","/work/runner.py","/work/candidate.py",
                     "/work/tests.json",entry_point]
            try:
                proc=subprocess.run(command,capture_output=True,text=True,timeout=self.timeout_seconds)
            except subprocess.TimeoutExpired:
                return CandidateEvaluation(candidate.candidate_id,"TIMEOUT",failure_class="timeout")
            except OSError:
                return CandidateEvaluation(candidate.candidate_id,"INFRASTRUCTURE_ERROR",failure_class="docker_invocation_error")
            if proc.returncode==0: return CandidateEvaluation(candidate.candidate_id,"PASS")
            if proc.returncode==10: return CandidateEvaluation(candidate.candidate_id,"FAIL",failure_class="wrong_answer")
            if proc.returncode==20: return CandidateEvaluation(candidate.candidate_id,"INFRASTRUCTURE_ERROR",failure_class="runtime_error")
            return CandidateEvaluation(candidate.candidate_id,"INFRASTRUCTURE_ERROR",failure_class="docker_runtime_error")

    def evaluate_visible(self,candidate): return self._evaluate(candidate,candidate.metadata.get("visible_tests"))
    def evaluate_hidden(self,candidate): return self._evaluate(candidate,candidate.metadata.get("hidden_tests"))
