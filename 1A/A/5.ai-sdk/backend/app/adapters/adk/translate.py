"""ADK Event -> neutral Events.

An ADK Event carries an author (agent name), content parts (text, function_call,
function_response), actions (state_delta, transfer, escalate, route), `partial` for streamed
chunks, and in ADK 2 an `output` for workflow nodes.
"""

from dataclasses import dataclass
from typing import Any

from google.adk.events import Event as AdkEvent

from app.schemas import Event


@dataclass
class TranslateState:
    last_author: str | None = None
    last_text: str | None = None
    workflow_output: Any = None


def translate(ev: AdkEvent, st: TranslateState) -> list[Event]:
    out: list[Event] = []
    author = ev.author
    if author and author != "user" and author != st.last_author:
        out.append(Event(type="agent", agent=author))
        st.last_author = author
    parts = ev.content.parts if ev.content and ev.content.parts else []
    for part in parts:
        if part.thought:
            continue
        if part.function_call:
            fc = part.function_call
            out.append(
                Event(
                    type="tool_call", agent=author, name=fc.name, id=fc.id, args=dict(fc.args or {})
                )
            )
        elif part.function_response:
            fr = part.function_response
            out.append(
                Event(type="tool_result", agent=author, name=fr.name, id=fr.id, result=fr.response)
            )
        elif part.text:
            if ev.partial:
                out.append(Event(type="delta", agent=author, text=part.text))
            else:
                out.append(Event(type="message", agent=author, text=part.text))
                st.last_text = part.text
    delta = {k: v for k, v in (ev.actions.state_delta or {}).items() if not k.startswith("temp:")}
    if delta and not ev.partial:
        out.append(Event(type="state", agent=author, data=delta))
    output = getattr(ev, "output", None)
    if output is not None:
        st.workflow_output = output
    return out
