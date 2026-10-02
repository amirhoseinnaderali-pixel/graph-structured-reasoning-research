from __future__ import annotations
import json
import os
import time
import urllib.error
import urllib.request

from graph_reasoning_research.generation.base import candidate_output_hash, candidate_set_hash, generation_config_hash
from graph_reasoning_research.types import Candidate, CandidateSet

class OpenAICandidateGenerator:
    def __init__(self, config: dict):
        self.config = config
        self.model_id = config["model_id"]
        self.generation_config = {
            "provider": config["provider"],
            "adapter": config["adapter"],
            "model_id": config["model_id"],
            "model_revision": config["model_revision"],
            "temperature": config["temperature"],
            "top_p": config["top_p"],
            "max_tokens": config["max_tokens"],
            "response_format": config["response_format"],
            "candidate_count": config["candidate_count"],
            "seed_policy": config["seed_policy"],
        }

    def _call(self, prompt: str, seed: int) -> tuple[dict, float]:
        key = os.environ.get(self.config["credential_env"])
        if not key:
            raise RuntimeError("missing credential environment variable")
        url = self.config["base_url"].rstrip("/") + "/chat/completions"
        payload = {
            "model": self.config["model_id"],
            "messages": [
                {"role": "system", "content": "Generate independent Python implementations. Never use hidden tests or evaluation feedback."},
                {"role": "user", "content": prompt},
            ],
            "temperature": self.config["temperature"],
            "top_p": self.config["top_p"],
            "max_tokens": self.config["max_tokens"],
            "seed": seed,
            "response_format": self.config["response_format"],
        }
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            method="POST",
        )
        started = time.perf_counter()
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"model API HTTP {exc.code}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError("model API network error") from exc
        return body, (time.perf_counter() - started) * 1000.0

    def generate(self, task_id: str, problem: str, n: int, seed: int, entry_point: str) -> tuple[CandidateSet, dict]:
        if n != int(self.config["candidate_count"]):
            raise ValueError("candidate count does not match frozen model config")
        prompt = (
            f"Generate exactly {n} independent implementations for function {entry_point}.\n"
            'Return JSON of the form {"candidates":[{"code":"...", "answer":"..."}]}. '
            f"The array must contain exactly {n} candidates. No markdown fences.\n\n{problem}"
        )
        last_error = None
        attempts = int(self.config.get("retry_policy", {}).get("max_attempts", 1))
        for attempt in range(max(1, attempts)):
            try:
                body, latency = self._call(prompt, seed)
                parsed = json.loads(body["choices"][0]["message"]["content'])
                items = parsed["candidates"]
                if not isinstance(items, list) or len(items) != n:
                    raise RuntimeError("candidate array length mismatch")
                cfg_hash = generation_config_hash(self.generation_config)
                candidates = []
                for i, item in enumerate(items):
                    code = str(item["code"]).strip()
                    answer = str(item.get("answer", "")).strip() or None
                    candidates.append(
                        Candidate(
                            candidate_id=f"{task_id}-c{i}",
                            task_id=task_id,
                            text=code,
                            answer=answer,
                            generator_model_id=self.model_id,
                            seed=seed,
                            generation_config_hash=cfg_hash,
                            output_hash=candidate_output_hash(code, answer),
                        )
                    )
                usage = body.get("usage", {})
                return CandidateSet(task_id, tuple(candidates), candidate_set_hash(candidates)), {
                    "provider": self.config["provider"],
                    "model_id": self.model_id,
                    "calls": attempt + 1,
                    "prompt_tokens": int(usage.get("prompt_tokens", 0)),
                    "completion_tokens": int(usage.get("completion_tokens", 0)),
                    "total_tokens": int(usage.get("total_tokens", 0)),
                    "latency_ms": latency,
                    "retry_count": attempt,
                }
            except Exception as exc:
                last_error = exc
        raise RuntimeError(f"candidate_generation_failed: {last_error}") from last_error
