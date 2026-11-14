"""The harness with a fake runner and judge; then (opt-in) the real thing."""

import os
from pathlib import Path

import pytest

from app.evals.harness import (
    EvalCase,
    Verdict,
    format_report,
    load_cases,
    run_suite,
    trajectory_matches,
)
from app.schemas import ChatResponse, TraceEvent

CASES = Path(__file__).resolve().parents[1] / "evals" / "cases.json"


def test_cases_file_is_valid():
    cases = load_cases(CASES)
    assert len(cases) >= 3 and all(c.rubric for c in cases)


def test_trajectory_suffix_match():
    assert trajectory_matches(["calculate"], ["mcp__local__calculate", "Task"])
    assert not trajectory_matches(["calculate", "Task"], ["mcp__local__calculate"])
    assert trajectory_matches([], [])


async def test_suite_with_fakes():
    async def runner(message: str) -> ChatResponse:
        tool = "mcp__local__calculate" if "*" in message else "Task"
        return ChatResponse(
            session_id="s",
            reply="84" if "*" in message else "meh",
            events=[TraceEvent(type="tool_call", author="orchestrator", name=tool, args={})],
        )

    async def judge(case: EvalCase, reply: str) -> Verdict:
        return Verdict(score=5 if reply == "84" else 2, reasoning="scripted")

    cases = [
        EvalCase(id="ok", input="12 * 7", expected_tools=["calculate"], rubric="84", min_score=4),
        EvalCase(
            id="bad_answer", input="policy?", expected_tools=["Task"], rubric="x", min_score=4
        ),
        EvalCase(id="bad_tools", input="policy?", expected_tools=["calculate"], rubric="x"),
    ]
    results = await run_suite(cases, runner, judge)
    assert [r.passed for r in results] == [True, False, False]
    assert results[1].trajectory_ok and results[1].verdict.score == 2
    assert not results[2].trajectory_ok
    assert "1/3 passed" in format_report(results)


@pytest.mark.eval
@pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"), reason="needs ANTHROPIC_API_KEY")
async def test_real_agent_against_cases():
    from app.evals.run import main

    assert await main() == 0
