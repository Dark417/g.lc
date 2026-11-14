"""Pins down how Claude Agent SDK messages become trace events. No CLI, no network."""

from claude_agent_sdk import (
    AssistantMessage,
    ResultMessage,
    StreamEvent,
    TextBlock,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
)

from app.services.chat_service import translate_message


def _assistant(*blocks, parent=None):
    return AssistantMessage(content=list(blocks), model="m", parent_tool_use_id=parent)


def test_root_tool_call_and_text():
    msg = _assistant(
        ToolUseBlock(id="t1", name="mcp__local__calculate", input={"expression": "6*7"}),
        TextBlock(text="Let me check."),
    )
    assert translate_message(msg) == [
        {
            "type": "tool_call",
            "author": "orchestrator",
            "name": "mcp__local__calculate",
            "args": {"expression": "6*7"},
        },
        {"type": "final_text", "text": "Let me check."},
    ]


def test_subagent_text_is_agent_text():
    msg = _assistant(TextBlock(text="Ada has 3 orders."), parent="task-1")
    assert translate_message(msg) == [
        {"type": "agent_text", "author": "subagent", "text": "Ada has 3 orders."}
    ]


def test_tool_result_extracts_text_content():
    msg = UserMessage(
        content=[
            ToolResultBlock(tool_use_id="t1", content=[{"type": "text", "text": '{"result": 42}'}])
        ]
    )
    [ev] = translate_message(msg)
    assert ev["type"] == "tool_result" and ev["result"] == '{"result": 42}' and ev["name"] == "t1"


def test_stream_delta_only_from_root():
    delta = {"type": "content_block_delta", "delta": {"type": "text_delta", "text": "Hel"}}
    assert translate_message(StreamEvent(uuid="u", session_id="s", event=delta)) == [
        {"type": "delta", "text": "Hel"}
    ]
    sub = StreamEvent(uuid="u", session_id="s", event=delta, parent_tool_use_id="task-1")
    assert translate_message(sub) == []


def test_result_message_becomes_session_event():
    msg = ResultMessage(
        subtype="success",
        duration_ms=1,
        duration_api_ms=1,
        is_error=False,
        num_turns=2,
        session_id="s1",
        total_cost_usd=0.01,
    )
    [ev] = translate_message(msg)
    assert ev == {"type": "session", "session_id": "s1", "cost_usd": 0.01, "is_error": False}
