"""The hand-rolled draft/critique loop with a scripted LLM."""

from app.agents.writer_loop import CRITIC_SYSTEM, build_writer_tool, refine


class ScriptedLLM:
    """Drafts 'draft N'; the critic approves on the given iteration."""

    def __init__(self, approve_on: int) -> None:
        self.approve_on, self.drafts, self.prompts = approve_on, 0, []

    async def __call__(self, *, system: str, prompt: str) -> str:
        self.prompts.append(prompt)
        if system == CRITIC_SYSTEM:
            if self.drafts >= self.approve_on:
                return '{"approved": true}'
            return '{"approved": false, "changes": ["shorter", "add a greeting"]}'
        self.drafts += 1
        return f"draft {self.drafts}"


async def test_loop_exits_on_approval_and_feeds_critique_back():
    llm = ScriptedLLM(approve_on=2)
    res = await refine("write an email", llm, max_iterations=3)
    assert res.approved and res.iterations == 2 and res.text == "draft 2"
    assert "- shorter" in llm.prompts[2]  # second draft prompt carries the critique


async def test_loop_respects_max_iterations():
    res = await refine("write an email", ScriptedLLM(approve_on=99), max_iterations=3)
    assert not res.approved and res.iterations == 3 and res.text == "draft 3"


async def test_writer_tool_shape():
    tool = build_writer_tool(ScriptedLLM(approve_on=1))
    assert tool.__name__ == "write_polished_text" and "Args:" in tool.__doc__
    out = await tool("announce free shipping")
    assert out == {"status": "ok", "text": "draft 1", "iterations": 1, "approved": True}
