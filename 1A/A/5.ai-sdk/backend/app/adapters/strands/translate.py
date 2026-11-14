"""Strands stream events -> neutral Events.

Agent.stream_async yields dicts: {"data": chunk} for text deltas, {"message": {...}} for every
message added (assistant toolUse/text, user toolResult), {"result": AgentResult} at the end.
Swarm/Graph.stream_async wrap those in {"type": "multiagent_node_stream", "node_id", "event"},
with multiagent_node_start / _stop / _handoff / _result around them.
"""

import ast
import json
from dataclasses import dataclass, field
from typing import Any

from app.schemas import Event


def _parse(value: Any) -> Any:
    """Strands returns tool output as text blocks (JSON or a Python repr of a dict)."""
    if not isinstance(value, str):
        return value
    for parse in (json.loads, ast.literal_eval):
        try:
            return parse(value)
        except (ValueError, SyntaxError):
            continue
    return value


@dataclass
class TranslateState:
    tool_names: dict[str, str] = field(default_factory=dict)  # toolUseId -> name
    last_agent: str | None = None
    result: Any = None


def _agent_event(e: dict, agent: str, st: TranslateState) -> list[Event]:
    out: list[Event] = []
    if "data" in e and isinstance(e["data"], str) and e["data"]:
        out.append(Event(type="delta", agent=agent, text=e["data"]))
    elif "message" in e:
        msg = e["message"]
        for block in msg.get("content", []):
            if "toolUse" in block:
                tu = block["toolUse"]
                st.tool_names[tu["toolUseId"]] = tu["name"]
                out.append(
                    Event(
                        type="tool_call",
                        agent=agent,
                        name=tu["name"],
                        id=tu["toolUseId"],
                        args=tu.get("input"),
                    )
                )
            elif "toolResult" in block:
                tr = block["toolResult"]
                content = tr.get("content", [])
                result = _parse(next((c.get("json", c.get("text")) for c in content), None))
                out.append(
                    Event(
                        type="tool_result",
                        agent=agent,
                        name=st.tool_names.get(tr["toolUseId"]),
                        id=tr["toolUseId"],
                        result=result
                        if tr.get("status") == "success"
                        else {"status": tr.get("status"), "error": result},
                    )
                )
            elif "text" in block and msg.get("role") == "assistant":
                out.append(Event(type="message", agent=agent, text=block["text"]))
    elif "result" in e:
        st.result = e["result"]
    return out


def translate(e: Any, default_agent: str, st: TranslateState) -> list[Event]:
    if not isinstance(e, dict):
        return []
    kind = e.get("type")
    if kind == "multiagent_node_start":
        st.last_agent = e["node_id"]
        return [Event(type="agent", agent=e["node_id"])]
    if kind == "multiagent_node_stream":
        return _agent_event(e.get("event") or {}, e["node_id"], st)
    if kind == "multiagent_handoff":
        data = {k: v for k, v in e.items() if k in ("from_node_ids", "to_node_ids", "message")}
        return [Event(type="state", data={"handoff": data})] if data else []
    if kind == "multiagent_result":
        st.result = e.get("result")
        return []
    if st.last_agent is None:
        st.last_agent = default_agent
        return [Event(type="agent", agent=default_agent), *_agent_event(e, default_agent, st)]
    return _agent_event(e, default_agent, st)


def final_output(result: Any) -> Any:
    """AgentResult -> text or structured object; Swarm/Graph result -> last node's text."""
    if result is None:
        return None
    if getattr(result, "structured_output", None) is not None:
        return result.structured_output.model_dump()
    order = getattr(result, "execution_order", None) or getattr(result, "node_history", None)
    if order is not None and getattr(result, "results", None):
        last = order[-1].node_id
        return str(result.results[last].result).strip()
    return str(result).strip()
