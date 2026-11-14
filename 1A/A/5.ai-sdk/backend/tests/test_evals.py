"""The eval harness itself, scored against a framework-free adapter (no model, no key)."""

from app.config import BACKEND_DIR
from app.evals.harness import evaluate, load_cases, parse_target, summary_table
from app.evals.scorers import Case, RunResult, contains, llm_judge, tool_trajectory
from tests.conftest import EchoAdapter


def result(output, tools=(), error=None) -> RunResult:
    events = [{"type": "tool_call", "name": t} for t in tools]
    return RunResult("t", "c", output, events, 0.1, error)


def test_scorers():
    case = Case(
        "c", "q", {"tools": ["calculator", "search_docs"], "contains": ["397.8", "agentcore"]}
    )
    r = result("It is 397.8", tools=["calculator", "calculator", "browse"])
    assert tool_trajectory(case, r) == {"tool_recall": 0.5, "tool_precision": 0.667}
    assert contains(case, r) == {"contains": 0.5}
    assert tool_trajectory(Case("x", "q"), r) is None


async def test_llm_judge_parses_score():
    case = Case("c", "q", {"rubric": "be right"})

    async def judge(prompt):
        assert "be right" in prompt
        return 'Sure: {"score": 4, "reason": "ok"}'

    assert await llm_judge(case, result("x"), judge) == {"judge": 0.8}
    assert await llm_judge(case, result("x", error="boom"), judge) is None


def test_cases_file_parses():
    cases = load_cases(BACKEND_DIR / "evals" / "cases.yaml")
    assert {c.id for c in cases} >= {"calc-percent", "docs-agentcore-memory"}
    assert parse_target("adk:single") == ("adk", "single", "raw")


async def test_evaluate_matrix(container):
    container.registry.register(EchoAdapter())  # calls calculator, echoes the input
    cases = [Case("calc", "17%", {"tools": ["calculator"], "contains": ["17%"]})]
    rows = await evaluate(container.runs, ["echo:single:raw", "nope:single:raw"], cases)
    assert rows[0]["scores"]["tool_recall"] == 1.0 and rows[0]["scores"]["contains"] == 1.0
    assert rows[1]["error"] and rows[1]["scores"]["ok"] == 0.0
    table = summary_table(rows)
    assert "| echo:single:raw | 1.00 | 1.00 | 1.00 |" in table
