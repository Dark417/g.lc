"""Scorers: pure functions over a RunResult (neutral events), so every framework scores the same."""

import json
import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Case:
    id: str
    input: str
    expect: dict[str, Any] = field(default_factory=dict)


@dataclass
class RunResult:
    target: str
    case_id: str
    output: Any
    events: list[dict[str, Any]]
    latency_s: float
    error: str | None = None

    @property
    def tool_calls(self) -> list[str]:
        return [e["name"] for e in self.events if e.get("type") == "tool_call" and e.get("name")]

    @property
    def text(self) -> str:
        return self.output if isinstance(self.output, str) else json.dumps(self.output, default=str)


def tool_trajectory(case: Case, run: RunResult) -> dict[str, float] | None:
    """Recall of expected tool names (any order); precision over all calls is reported too.

    Names only, not arguments: models paraphrase arguments, so exact-argument matching (ADK's
    default trajectory metric) fails on correct behaviour for free-text tools.
    """
    expected = set(case.expect.get("tools", []))
    if not expected:
        return None
    called = run.tool_calls
    recall = len(expected & set(called)) / len(expected)
    precision = sum(1 for c in called if c in expected) / len(called) if called else 0.0
    return {"tool_recall": recall, "tool_precision": round(precision, 3)}


def contains(case: Case, run: RunResult) -> dict[str, float] | None:
    needles = case.expect.get("contains", [])
    if not needles:
        return None
    text = run.text.lower()
    return {"contains": sum(1 for n in needles if n.lower() in text) / len(needles)}


def efficiency(case: Case, run: RunResult) -> dict[str, float]:
    return {"latency_s": round(run.latency_s, 2), "tool_calls": float(len(run.tool_calls))}


JUDGE_PROMPT = """You grade an AI assistant's answer against a rubric.
Question: {question}
Rubric: {rubric}
Answer: {answer}
Reply with only a JSON object: {{"score": <integer 1-5>, "reason": "<one sentence>"}}"""


async def llm_judge(case: Case, run: RunResult, judge) -> dict[str, float] | None:
    """`judge(prompt) -> str` is any text LLM call; see app.evals.run.claude_judge."""
    rubric = case.expect.get("rubric")
    if not rubric or judge is None or run.error:
        return None
    reply = await judge(JUDGE_PROMPT.format(question=case.input, rubric=rubric, answer=run.text))
    match = re.search(r"\{.*\}", reply, re.S)
    try:
        score = float(json.loads(match.group(0))["score"]) if match else 0.0
    except (ValueError, KeyError):
        score = 0.0
    return {"judge": score / 5}


SCORERS = (tool_trajectory, contains, efficiency)
