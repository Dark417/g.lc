"""LangGraph stream chunks -> neutral Events.

We stream with stream_mode="updates", subgraphs=True: each chunk is (namespace, {node: update}).
`namespace` is () for the top graph and ("researcher:<task id>",) inside a subgraph, so we can
tell which agent produced a message. "__interrupt__" marks a paused graph.
"""

import json
from dataclasses import dataclass
from typing import Any

from langchain_core.messages import AIMessage, ToolMessage

from app.schemas import Event

_SKIP_STATE = {"messages", "llm_input_messages", "remaining_steps", "structured_response"}


def _text(msg: AIMessage) -> str:
    return msg.text if isinstance(msg.text, str) else str(msg.content)


def _result(content: Any) -> Any:
    if isinstance(content, str):
        try:
            return json.loads(content)
        except ValueError:
            return content
    return content


@dataclass
class TranslateState:
    last_agent: str | None = None


def translate(namespace: tuple, chunk: dict, st: TranslateState) -> list[Event]:
    out: list[Event] = []
    meta = chunk.get("__metadata__") or {}  # e.g. {"cached": True} when a node-cache hit served it
    for node, update in chunk.items():
        if node == "__metadata__":
            continue
        if meta.get("cached"):
            out.append(Event(type="state", agent=node, data={"cached": True}))
        if node == "__interrupt__":
            for intr in update:
                out.append(Event(type="interrupt", data=getattr(intr, "value", intr)))
            continue
        agent = namespace[-1].split(":")[0] if namespace else node
        if agent != st.last_agent:
            out.append(Event(type="agent", agent=agent))
            st.last_agent = agent
        if not isinstance(update, dict):
            continue
        for msg in update.get("messages") or []:
            if isinstance(msg, AIMessage):
                for tc in msg.tool_calls:
                    out.append(
                        Event(
                            type="tool_call",
                            agent=agent,
                            name=tc["name"],
                            id=tc.get("id"),
                            args=tc["args"],
                        )
                    )
                if _text(msg):
                    out.append(Event(type="message", agent=agent, text=_text(msg)))
            elif isinstance(msg, ToolMessage):
                out.append(
                    Event(
                        type="tool_result",
                        agent=agent,
                        name=msg.name,
                        id=msg.tool_call_id,
                        result=_result(msg.content),
                    )
                )
        state = {k: v for k, v in update.items() if k not in _SKIP_STATE}
        if state:
            out.append(
                Event(type="state", agent=agent, data=json.loads(json.dumps(state, default=str)))
            )
    return out


def final_output(values: dict) -> Any:
    if values.get("final"):
        return values["final"]
    for msg in reversed(values.get("messages") or []):
        if isinstance(msg, AIMessage) and _text(msg) and not msg.tool_calls:
            return _text(msg)
    return None
