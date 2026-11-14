"""Run eval cases against targets through RunService (the same entrance the API uses)."""

import time
import uuid
from pathlib import Path

import yaml

from app.evals.scorers import SCORERS, Case, RunResult, llm_judge
from app.schemas import RunRequest
from app.services.run_service import RunService


def load_cases(path: Path) -> list[Case]:
    return [Case(**c) for c in yaml.safe_load(path.read_text())]


def parse_target(target: str) -> tuple[str, str, str]:
    framework, pattern, *rest = target.split(":")
    return framework, pattern, rest[0] if rest else "raw"


async def run_case(service: RunService, target: str, case: Case) -> RunResult:
    framework, pattern, provider = parse_target(target)
    req = RunRequest(
        framework=framework,
        pattern=pattern,
        provider=provider,
        message=case.input,
        user_id=f"eval-{uuid.uuid4().hex[:8]}",  # fresh user: no memory leaks between cases
    )
    started = time.perf_counter()
    try:
        await service.preflight(req)
        resp = await service.run(req)
    except Exception as e:  # a broken target is a result, not a crash of the whole suite
        return RunResult(
            target, case.id, None, [], time.perf_counter() - started, f"{type(e).__name__}: {e}"
        )
    error = next((e["message"] for e in resp.events if e["type"] == "error"), None)
    return RunResult(
        target, case.id, resp.output, resp.events, time.perf_counter() - started, error
    )


async def score(case: Case, run: RunResult, judge=None) -> dict[str, float]:
    scores: dict[str, float] = {}
    for scorer in SCORERS:
        scores.update(scorer(case, run) or {})
    scores.update(await llm_judge(case, run, judge) or {})
    scores["ok"] = 0.0 if run.error else 1.0
    return scores


async def evaluate(
    service: RunService, targets: list[str], cases: list[Case], judge=None
) -> list[dict]:
    rows = []
    for target in targets:
        for case in cases:
            run = await run_case(service, target, case)
            rows.append(
                {
                    "target": target,
                    "case": case.id,
                    "scores": await score(case, run, judge),
                    "output": run.output,
                    "tools": run.tool_calls,
                    "error": run.error,
                }
            )
    return rows


def summary_table(rows: list[dict]) -> str:
    """Markdown: one row per target, mean of each quality metric across cases."""
    metrics = ["ok", "tool_recall", "contains", "judge", "tool_calls", "latency_s"]
    by_target: dict[str, list[dict]] = {}
    for r in rows:
        by_target.setdefault(r["target"], []).append(r["scores"])
    lines = ["| target | " + " | ".join(metrics) + " |", "|---" * (len(metrics) + 1) + "|"]
    for target, scores in by_target.items():
        cells = []
        for m in metrics:
            vals = [s[m] for s in scores if m in s]
            cells.append(f"{sum(vals) / len(vals):.2f}" if vals else "–")
        lines.append(f"| {target} | " + " | ".join(cells) + " |")
    return "\n".join(lines)
