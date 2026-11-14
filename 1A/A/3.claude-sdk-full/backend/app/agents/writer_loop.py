"""Draft -> critique -> revise loop, written by hand.

ADK gives you LoopAgent + escalate. The Claude Agent SDK has no equivalent primitive, so this is
the loop, in plain Python, exposed to the orchestrator as a tool (`write_polished_text`).
Seeing it spelled out is the point: an "agent loop" is a while-loop with an exit condition.
"""

import json
from collections.abc import Callable
from dataclasses import dataclass, field

from app.agents.llm import TextLLM

DRAFTER_SYSTEM = (
    "You write clear, concise business text (emails, announcements, summaries). "
    "Output only the text itself, no commentary."
)
CRITIC_SYSTEM = (
    "You are a strict editor. Reply with JSON only: "
    '{"approved": true} if the draft is clear, correct and complete, otherwise '
    '{"approved": false, "changes": ["...", "..."]} with 2-3 concrete, actionable changes.'
)


@dataclass
class WriterResult:
    text: str
    iterations: int
    approved: bool
    history: list[dict] = field(default_factory=list)


async def refine(request: str, llm: TextLLM, max_iterations: int = 3) -> WriterResult:
    draft, critique, approved = "", "", False
    history: list[dict] = []
    for i in range(1, max_iterations + 1):
        prompt = f"Request: {request}"
        if draft:
            prompt += f"\n\nPrevious draft:\n{draft}\n\nApply these changes:\n{critique}"
        draft = await llm(system=DRAFTER_SYSTEM, prompt=prompt)

        raw = await llm(system=CRITIC_SYSTEM, prompt=f"Request: {request}\n\nDraft:\n{draft}")
        verdict = _parse_verdict(raw)
        history.append({"iteration": i, "draft": draft, "verdict": verdict})
        if verdict.get("approved"):
            approved = True
            break  # <- the exit condition (ADK: tool_context.actions.escalate = True)
        critique = "\n".join(f"- {c}" for c in verdict.get("changes", [])) or raw
    return WriterResult(text=draft, iterations=len(history), approved=approved, history=history)


def _parse_verdict(raw: str) -> dict:
    try:
        start, end = raw.index("{"), raw.rindex("}") + 1
        return json.loads(raw[start:end])
    except (ValueError, json.JSONDecodeError):
        return {"approved": False, "changes": [raw.strip()[:300]]}


def build_writer_tool(llm: TextLLM, max_iterations: int = 3) -> Callable:
    async def write_polished_text(request: str) -> dict:
        """Write a polished piece of text (email, announcement, summary) via a draft-critique loop.

        Args:
            request: The full request including audience, tone, and key points to include.
        """
        res = await refine(request, llm, max_iterations)
        return {
            "status": "ok",
            "text": res.text,
            "iterations": res.iterations,
            "approved": res.approved,
        }

    return write_polished_text
