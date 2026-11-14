"""Golden verdict suite. See docs/design/08-evals.md.

    python -m app.evals.run               # AssessmentService directly (isolates the pipeline)
    python -m app.evals.run --via-agent   # full agent loop: also checks the model calls the tool

Needs a model (GOOGLE_API_KEY or Vertex AI) and the seed rules (`python -m app.cli seed`).
Exit code 0 only when accuracy >= 0.9, zero safety failures, and citation recall >= 0.8.
"""

import argparse
import asyncio
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from app.container import get_container

CASES = Path(__file__).resolve().parents[2] / "evals" / "verdicts.json"
ACCURACY, RECALL = 0.9, 0.8


@dataclass
class CaseResult:
    id: str
    expected: str
    got: str
    verdict_ok: bool
    safe: bool
    citation_recall: float
    cited: list[str]


def score_case(case: dict, verdict: dict) -> CaseResult:
    got = verdict.get("verdict", "")
    acceptable = set(case.get("acceptable_verdicts") or [case["expected_verdict"]])
    flagged = [
        f["rule_code"]
        for f in verdict.get("findings", [])
        if f["status"] in ("violated", "unclear")
    ]
    must = case.get("must_cite", [])
    recall = sum(c in flagged for c in must) / len(must) if must else 1.0
    return CaseResult(
        id=case["id"],
        expected=case["expected_verdict"],
        got=got,
        verdict_ok=got in acceptable,
        safe=got not in case.get("must_not_verdict", []),
        citation_recall=recall,
        cited=flagged,
    )


def summarize(results: list[CaseResult]) -> dict:
    n = len(results) or 1
    return {
        "cases": len(results),
        "accuracy": sum(r.verdict_ok for r in results) / n,
        "safety_failures": sum(not r.safe for r in results),
        "citation_recall": sum(r.citation_recall for r in results) / n,
    }


def passed(summary: dict) -> bool:
    return (
        summary["accuracy"] >= ACCURACY
        and summary["safety_failures"] == 0
        and summary["citation_recall"] >= RECALL
    )


async def _verdict_via_agent(chat, case: dict) -> dict:
    res = await chat.chat(
        user_id="eval@system", session_id=None, message=f"Can we do this? {case['proposal']}"
    )
    return res["verdicts"][-1] if res["verdicts"] else {"verdict": "NO_TOOL_CALL", "findings": []}


async def main(via_agent: bool = False) -> int:
    c = get_container()
    await c.init()
    chat = None
    if via_agent:
        from google.adk.runners import Runner

        from app.agents.builder import build_app
        from app.services.chat import ChatService

        runner = Runner(
            app=build_app(c),
            session_service=c.sessions,
            memory_service=c.memory,
            artifact_service=c.artifacts,
        )
        chat = ChatService(runner=runner, sessions=c.sessions, app_name=c.settings.app_name)

    results = []
    for case in json.loads(CASES.read_text()):
        if chat:
            verdict = await _verdict_via_agent(chat, case)
        else:
            verdict = (
                await c.assessment.assess(case["proposal"], user_id="eval@system")
            ).model_dump(mode="json")
        r = score_case(case, verdict)
        results.append(r)
        mark = "ok " if r.verdict_ok and r.safe else "FAIL"
        print(
            f"{mark} {r.id:<32} expected={r.expected:<24} got={r.got:<24} recall={r.citation_recall:.2f} cited={r.cited}"
        )

    summary = summarize(results)
    print("\n" + json.dumps(summary, indent=2))
    out = Path(c.settings.doc_store_path).parent / "eval-report.json"
    out.write_text(
        json.dumps({"summary": summary, "results": [asdict(r) for r in results]}, indent=2)
    )
    print(f"report: {out}")
    await c.close()
    return 0 if passed(summary) else 1


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--via-agent", action="store_true")
    raise SystemExit(asyncio.run(main(p.parse_args().via_agent)))
