"""A hand-rolled eval harness, so you can see what ADK's evaluator does under the hood.

Two checks per case:
1. Tool trajectory: did the agent call the tools we expected? (deterministic, cheap)
2. Response quality: an LLM judge scores the reply against a rubric (structured output).

`run_suite` takes a `runner` (message -> ChatResponse) and a `judge`, both injectable, so the
harness itself is unit-tested with fakes and only `pytest -m eval` spends money.
"""

import json
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from pathlib import Path

from pydantic import BaseModel

from app.schemas import ChatResponse


class EvalCase(BaseModel):
    id: str
    input: str
    expected_tools: list[str] = []  # match on tool-name suffix, e.g. "calculate"
    rubric: str = ""  # what a good answer must contain / avoid
    min_score: int = 3  # 1-5


class Verdict(BaseModel):
    score: int  # 1 (wrong) .. 5 (excellent)
    reasoning: str


@dataclass
class CaseResult:
    case_id: str
    reply: str
    tools_called: list[str]
    trajectory_ok: bool
    verdict: Verdict | None
    passed: bool
    events: list[dict] = field(default_factory=list)


Runner = Callable[[str], Awaitable[ChatResponse]]
Judge = Callable[[EvalCase, str], Awaitable[Verdict]]

JUDGE_SYSTEM = (
    "You grade an assistant's reply against a rubric. Be strict and literal. "
    "Score 5 only if every rubric point is satisfied and nothing is invented."
)


def load_cases(path: Path) -> list[EvalCase]:
    return [EvalCase.model_validate(c) for c in json.loads(path.read_text())]


def trajectory_matches(expected: list[str], called: list[str]) -> bool:
    """Every expected tool appears (by suffix) in the calls, in any order."""
    return all(any(c.endswith(e) for c in called) for e in expected)


async def run_case(case: EvalCase, runner: Runner, judge: Judge | None) -> CaseResult:
    res = await runner(case.input)
    called = [e.name or "" for e in res.events if e.type == "tool_call"]
    trajectory_ok = trajectory_matches(case.expected_tools, called)
    verdict = await judge(case, res.reply) if (judge and case.rubric) else None
    passed = trajectory_ok and (verdict is None or verdict.score >= case.min_score)
    return CaseResult(
        case_id=case.id,
        reply=res.reply,
        tools_called=called,
        trajectory_ok=trajectory_ok,
        verdict=verdict,
        passed=passed,
        events=[e.model_dump() for e in res.events],
    )


async def run_suite(cases: list[EvalCase], runner: Runner, judge: Judge | None) -> list[CaseResult]:
    return [await run_case(c, runner, judge) for c in cases]


def format_report(results: list[CaseResult]) -> str:
    lines = [f"{'case':<28} {'traj':<5} {'score':<6} pass"]
    for r in results:
        score = r.verdict.score if r.verdict else "-"
        lines.append(f"{r.case_id:<28} {str(r.trajectory_ok):<5} {score!s:<6} {r.passed}")
    n_pass = sum(r.passed for r in results)
    lines.append(f"\n{n_pass}/{len(results)} passed")
    return "\n".join(lines)


def build_claude_judge(model: str, api_key: str | None = None) -> Judge:
    """LLM-as-judge via structured outputs. Uses the Messages API directly."""
    from anthropic import AsyncAnthropic

    from app.agents.llm import parse_structured

    client = AsyncAnthropic(api_key=api_key or None)

    async def judge(case: EvalCase, reply: str) -> Verdict:
        prompt = (
            f"User asked:\n{case.input}\n\nRubric:\n{case.rubric}\n\n"
            f"Assistant replied:\n{reply}\n\nScore the reply."
        )
        return await parse_structured(
            client, model=model, system=JUDGE_SYSTEM, prompt=prompt, schema=Verdict
        )

    return judge
