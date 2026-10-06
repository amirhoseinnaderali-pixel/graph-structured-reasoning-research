from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from graph_reasoning_research.types import Candidate, CandidateEvaluation


RUNNER_SCRIPT = r"""
import importlib.util
import json
import sys

path, tests_path = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location("candidate", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
tests = json.load(open(tests_path, encoding="utf-8"))
for test in tests:
    fn = getattr(module, test["function"])
    got = fn(*test.get("args", []), **test.get("kwargs", {}))
    if got != test.get("expected"):
        print(json.dumps({"status": "FAIL", "expected": test.get("expected"), "got": got}))
        raise SystemExit(10)
print(json.dumps({"status": "PASS"}))
"""


@dataclass(frozen=True)
class DockerPythonVerifier:
    image_digest: str
    timeout_seconds: int = 10
    memory: str = "512m"
    cpus: str = "1"
    pids_limit: str = "64"

    def _evaluate(self, candidate: Candidate, tests: list[dict] | None) -> CandidateEvaluation:
        if not self.image_digest.startswith("sha256:"):
            raise RuntimeError("Docker verifier requires a pinned image digest")
        docker = shutil.which("docker")
        if docker is None:
            return CandidateEvaluation(candidate.candidate_id, "INFRASTRUCTURE_ERROR", failure_class="docker_unavailable")
        if not tests:
            return CandidateEvaluation(candidate.candidate_id, "INFRASTRUCTURE_ERROR", failure_class="missing_test_material")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "candidate.py").write_text(candidate.text, encoding="utf-8")
            (root / "tests.json").write_text(json.dumps(tests), encoding="utf-8")
            (root / "runner.py").write_text(RUNNER_SCRIPT, encoding="utf-8")
            command = [
                docker,
                "run",
                "--rm",
                "--network=none",
                "--cap-drop=ALL",
                "--security-opt=no-new-privileges",
                "--read-only",
                "--ipc=none",
                f"--pids-limit={self.pids_limit}",
                f"--memory={self.memory}",
                f"--cpus={self.cpus}",
                "--tmpfs=/tmp:rw,noexec,nosuid,size=64m",
                "-v",
                f"{root}:/work:ro",
                self.image_digest,
                "python",
                "/work/runner.py",
                "/work/candidate.py",
                "/work/tests.json",
            ]
            try:
                proc = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout_seconds,
                )
            except subprocess.TimeoutExpired:
                return CandidateEvaluation(candidate.candidate_id, "TIMEOUT", failure_class="timeout")
            if proc.returncode == 0:
                return CandidateEvaluation(candidate.candidate_id, "PASS")
            if proc.returncode == 10:
                return CandidateEvaluation(candidate.candidate_id, "FAIL", failure_class="wrong_answer")
            return CandidateEvaluation(candidate.candidate_id, "INFRASTRUCTURE_ERROR", failure_class="runtime_error")

    def evaluate_visible(self, candidate: Candidate) -> CandidateEvaluation:
        return self._evaluate(candidate, candidate.metadata.get("visible_tests"))

    def evaluate_hidden(self, candidate: Candidate) -> CandidateEvaluation:
        return self._evaluate(candidate, candidate.metadata.get("hidden_tests"))
