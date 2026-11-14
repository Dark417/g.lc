"""Fakes for the Claude adapter.

- FakeSDKClient / fake_query replace the Claude Code CLI: they record the ClaudeAgentOptions they
  receive and replay scripted SDK messages.
- messages_client() returns a *real* AsyncAnthropic whose HTTP transport is scripted, so the real
  tool runner calls our real tools.
"""

import json
from typing import Any

import httpx2
from anthropic import AsyncAnthropic
from claude_agent_sdk import (
    AssistantMessage,
    ResultMessage,
    TextBlock,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
)


def tool_use(id_: str, name: str, parent: str | None = None, **args) -> AssistantMessage:
    return AssistantMessage(
        content=[ToolUseBlock(id=id_, name=name, input=args)],
        model="claude",
        parent_tool_use_id=parent,
    )


def tool_result(
    id_: str, value: Any, parent: str | None = None, is_error: bool = False
) -> UserMessage:
    text = json.dumps(value) if not isinstance(value, str) else value
    return UserMessage(
        content=[
            ToolResultBlock(
                tool_use_id=id_, content=[{"type": "text", "text": text}], is_error=is_error
            )
        ],
        parent_tool_use_id=parent,
    )


def text(t: str, parent: str | None = None) -> AssistantMessage:
    return AssistantMessage(content=[TextBlock(text=t)], model="claude", parent_tool_use_id=parent)


def result(answer: str, session_id: str = "cli-session-1", is_error: bool = False) -> ResultMessage:
    return ResultMessage(
        subtype="error_during_execution" if is_error else "success",
        duration_ms=10,
        duration_api_ms=5,
        is_error=is_error,
        num_turns=2,
        session_id=session_id,
        total_cost_usd=0.001,
        usage={"input_tokens": 10, "output_tokens": 5},
        result=answer,
    )


class CliScript:
    """Shared by FakeSDKClient and fake_query; records every options object."""

    def __init__(self, *turns: list[Any]):
        self.turns = list(turns)
        self.options: list[Any] = []
        self.prompts: list[str] = []

    def client_cls(self, options):
        script = self

        class FakeSDKClient:
            def __init__(self):
                script.options.append(options)

            async def __aenter__(self):
                return self

            async def __aexit__(self, *exc):
                return False

            async def query(self, prompt: str):
                script.prompts.append(prompt)

            async def receive_response(self):
                for msg in script.turns.pop(0):
                    yield msg

        return FakeSDKClient()

    async def query_fn(self, *, prompt: str, options):
        self.options.append(options)
        self.prompts.append(prompt)
        for msg in self.turns.pop(0):
            yield msg


def messages_client(*responses: dict) -> tuple[Any, list[dict]]:
    """A real AsyncAnthropic with a scripted transport. Returns (factory, captured requests)."""
    queue, captured = list(responses), []

    def handler(request: httpx2.Request) -> httpx2.Response:
        captured.append(json.loads(request.content))
        return httpx2.Response(200, json=queue.pop(0))

    client = AsyncAnthropic(
        api_key="test", http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler))
    )
    return (lambda profile: client), captured


def api_message(*blocks: dict, stop: str = "end_turn") -> dict:
    return {
        "id": "msg_1",
        "type": "message",
        "role": "assistant",
        "model": "claude-opus-5",
        "content": list(blocks),
        "stop_reason": stop,
        "stop_sequence": None,
        "usage": {"input_tokens": 10, "output_tokens": 5},
    }


def api_tool_use(id_: str, name: str, **args) -> dict:
    return {"type": "tool_use", "id": id_, "name": name, "input": args}


def api_text(t: str) -> dict:
    return {"type": "text", "text": t}


def routed_messages_client(main: list[dict], summarize: list[str] = (), extract: list[str] = ()):
    """Like messages_client, but internal calls get their own queues, routed by the marker in the
    system prompt: summarisation and memory extraction never consume the main script."""
    from app.adapters.diy.context import SUMMARIZE_MARKER
    from app.adapters.diy.longterm import EXTRACT_MARKER

    queues = {"main": list(main), "summarize": list(summarize), "extract": list(extract)}
    captured: dict[str, list[dict]] = {"main": [], "summarize": [], "extract": []}

    def handler(request: httpx2.Request) -> httpx2.Response:
        body = json.loads(request.content)
        system = body.get("system", "")
        text = system if isinstance(system, str) else " ".join(b.get("text", "") for b in system)
        route = (
            "summarize"
            if SUMMARIZE_MARKER in text
            else "extract"
            if EXTRACT_MARKER in text
            else "main"
        )
        captured[route].append(body)
        if route == "main":
            return httpx2.Response(200, json=queues["main"].pop(0))
        reply = (
            queues[route].pop(0)
            if queues[route]
            else ('{"facts": []}' if route == "extract" else "summary")
        )
        return httpx2.Response(200, json=api_message(api_text(reply)))

    client = AsyncAnthropic(
        api_key="test", http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler))
    )
    return (lambda profile: client), captured
