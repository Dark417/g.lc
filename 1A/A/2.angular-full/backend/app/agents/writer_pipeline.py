"""Workflow agents: a draft -> critique loop, then a finalizer.

Shows the two non-LLM "orchestration" agents ADK gives you:
- LoopAgent runs its children in order, repeatedly, until max_iterations or a child escalates.
- SequentialAgent runs its children once, in order.

State (`output_key`) is how children talk to each other; `{key?}` in an instruction reads it.
"""

from google.adk.agents import LlmAgent, LoopAgent, SequentialAgent
from google.adk.tools import ToolContext


def approve_draft(tool_context: ToolContext) -> dict:
    """Call this when the draft needs no further changes. It ends the revision loop."""
    tool_context.actions.escalate = True  # <- this is what stops a LoopAgent
    return {"status": "approved"}


def build_writer_pipeline(model: str, max_iterations: int = 3) -> SequentialAgent:
    drafter = LlmAgent(
        name="drafter",
        model=model,
        instruction=(
            "Write the text the user asked for (email, announcement, summary...).\n"
            "Previous draft (may be empty): {draft?}\n"
            "Critique to apply (may be empty): {critique?}\n"
            "Output only the text itself, no commentary."
        ),
        output_key="draft",
    )
    critic = LlmAgent(
        name="critic",
        model=model,
        instruction=(
            "You are a strict editor. Review this draft:\n\n{draft?}\n\n"
            "If it is clear, correct, and complete, call approve_draft. "
            "Otherwise reply with 2-3 concrete, actionable changes and nothing else."
        ),
        tools=[approve_draft],
        output_key="critique",
    )
    loop = LoopAgent(
        name="revision_loop", sub_agents=[drafter, critic], max_iterations=max_iterations
    )
    finalizer = LlmAgent(
        name="finalizer",
        model=model,
        instruction="Output exactly the following text and nothing else:\n\n{draft?}",
    )
    return SequentialAgent(
        name="writer",
        description=(
            "Writes polished text (emails, announcements, summaries) through a "
            "draft-critique-revise loop. Pass the full request including audience and key points."
        ),
        sub_agents=[loop, finalizer],
    )
