"""A complete agent loop with no agent framework: what ADK / LangGraph / Strands / the Claude SDK
do for you, written out.

    READY -> CALL_MODEL -> (end_turn) -> DONE
                 |   ^
       tool_use  v   | all results in
              RUN_TOOLS   (one checkpoint per finished tool)

Guarantees:
  - A checkpoint is written after every step, *before* the next step starts.
  - Recovery reloads the latest checkpoint and continues from its status; tools that finished
    are not run again. A crash *between* a tool finishing and its checkpoint re-runs that one tool
    (at-least-once), so tools should be idempotent or keyed by tool_use id.
  - The stored conversation is complete; the model sees a view of it (context.py).

Caches used (docs/design/07, "Cache servers"):
  checkpoint cache   CachedCheckpointStore (Redis)            our cache server
  LLM response cache LlmResponseCache (Redis)                  our cache server
  prompt cache       cache_control on the system prompt        Anthropic, server-side
"""

import json
from collections.abc import AsyncIterator
from typing import Any

from app.adapters.diy.context import SUMMARIZE_MARKER, build_context
from app.adapters.diy.longterm import FactStore, extract_and_consolidate
from app.adapters.diy.state import (
    CALL_MODEL,
    DONE,
    READY,
    RUN_TOOLS,
    Checkpoint,
    CheckpointStore,
    LoopState,
)
from app.core.adapter import AdapterError
from app.schemas import Event
from app.state.cache import LlmResponseCache
from app.tools import ToolFn

SYSTEM = (
    "You are an engineering research assistant with tools. Use them instead of guessing. "
    "Cite the `source` of passages you use. Be concise."
)


class SimulatedCrash(RuntimeError):
    """Raised by options.crash_after_step to demonstrate recovery."""


def _text(content: Any) -> str:
    if isinstance(content, str):
        return content
    return " ".join(
        b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"
    )


class AgentLoop:
    def __init__(
        self,
        *,
        client,
        model: str,
        store: CheckpointStore,
        facts: FactStore,
        tools: list[ToolFn],
        tool_defs: list[dict],
        opts: dict,
        llm_cache: LlmResponseCache | None = None,
        max_model_calls: int = 20,
    ):
        self.client, self.model, self.store, self.facts = client, model, store, facts
        self.tools = {f.__name__: f for f in tools}
        self.tool_defs = tool_defs
        self.opts, self.llm_cache, self.max_model_calls = opts, llm_cache, max_model_calls
        self.last_checkpoint: str | None = None
        self._steps_this_run = 0

    # ------------------------------------------------------------------ model calls

    async def _complete(self, system: str, messages: list[dict]) -> str:
        """A plain completion (no tools): used to summarise and to extract memories."""
        resp = await self.client.beta.messages.create(
            model=self.model, max_tokens=800, system=system, messages=messages
        )
        return "".join(b.text for b in resp.content if b.type == "text")

    async def _summarize(self, previous: str, messages: list[dict]) -> str:
        transcript = "\n".join(f"{m['role']}: {_text(m['content'])}" for m in messages)
        return await self._complete(
            f"{SUMMARIZE_MARKER} Update the running summary of a conversation. Keep facts, "
            "decisions, open questions. At most 120 words.",
            [
                {
                    "role": "user",
                    "content": f"Previous summary:\n{previous or '(none)'}\n\nNew messages:\n{transcript}",
                }
            ],
        )

    async def _call_model(self, state: LoopState) -> tuple[list[dict], str, dict]:
        view = await build_context(state, self.opts, self._summarize)
        system = [{"type": "text", "text": SYSTEM, "cache_control": {"type": "ephemeral"}}]
        system += [{"type": "text", "text": t} for t in view.system_extra]
        if self.opts.get("long_term", True):
            last_user = next(
                (
                    _text(m["content"])
                    for m in reversed(state.messages)
                    if m["role"] == "user" and _text(m["content"])
                ),
                "",
            )
            facts = await self.facts.search(state.user_id, last_user, k=5)
            if facts:
                known = "\n".join(f"- {f['text']}" for f in facts)
                system.append(
                    {
                        "type": "text",
                        "text": f"Known about this user from earlier conversations:\n{known}",
                    }
                )
                view.info["recalled"] = [f["text"] for f in facts]
        request = {
            "model": self.model,
            "max_tokens": 2048,
            "system": system,
            "messages": view.messages,
            "tools": self.tool_defs,
            **view.request_extra,
        }
        key = (
            self.llm_cache.key(**request)
            if self.llm_cache and self.opts.get("llm_cache", True)
            else None
        )
        cached = await self.llm_cache.get(key) if key else None
        if cached is not None:
            view.info["llm_cache"] = "hit"
            return cached["content"], cached["stop_reason"], view.info
        resp = await self.client.beta.messages.create(**request)
        content = [b.model_dump(exclude_none=True) for b in resp.content]
        state.add_usage(resp.usage.model_dump())
        if key:
            view.info["llm_cache"] = "miss"
            await self.llm_cache.put(key, {"content": content, "stop_reason": resp.stop_reason})
        return content, resp.stop_reason, view.info

    async def _run_tool(self, block: dict) -> Any:
        fn = self.tools.get(block["name"])
        if fn is None:
            return {"status": "error", "error": f"unknown tool {block['name']!r}"}
        try:
            return await fn(**block.get("input", {}))
        except Exception as e:  # a tool error is a result the model can react to
            return {"status": "error", "error": f"{type(e).__name__}: {e}"}

    # ------------------------------------------------------------------ checkpoints

    async def _checkpoint(self, state: LoopState, label: str) -> Event:
        state.step += 1
        ckpt = Checkpoint.of(state, label, self.last_checkpoint)
        await self.store.put(ckpt)
        self.last_checkpoint = ckpt.checkpoint_id
        self._steps_this_run += 1
        if self.opts.get("crash_after_step") == self._steps_this_run:
            raise SimulatedCrash(
                f"simulated crash after checkpoint {ckpt.checkpoint_id} ({label}); "
                'recover with {"resume": {"recover": true}}'
            )
        return Event(
            type="state",
            agent="diy_loop",
            data={"checkpoint": ckpt.checkpoint_id, "label": label, "status": state.status},
        )

    # ------------------------------------------------------------------ the loop

    async def run_turn(
        self, *, session_id: str, user_id: str, message: str, recover: bool
    ) -> AsyncIterator[Event]:
        latest = await self.store.latest(session_id)
        state = latest.state if latest else LoopState(session_id=session_id, user_id=user_id)
        self.last_checkpoint = latest.checkpoint_id if latest else None
        yield Event(type="agent", agent="diy_loop")

        if recover:
            if state.status in (READY, DONE):
                raise AdapterError("nothing to recover: the last turn finished")
            yield Event(
                type="state",
                agent="diy_loop",
                data={"recovered_from": self.last_checkpoint, "status": state.status},
            )
        else:
            if state.status not in (READY, DONE):
                raise AdapterError(
                    f"session has an unfinished turn (status {state.status!r}); "
                    'send {"resume": {"recover": true}} or fork from a checkpoint'
                )
            state.turn += 1
            state.vars["turn_start"] = len(state.messages)
            state.messages.append({"role": "user", "content": message})
            state.status = CALL_MODEL
            yield await self._checkpoint(state, "user")

        model_calls = 0
        while state.status != DONE:
            if state.status == CALL_MODEL:
                model_calls += 1
                if model_calls > self.max_model_calls:
                    raise AdapterError(f"model call limit ({self.max_model_calls}) reached")
                content, stop_reason, info = await self._call_model(state)
                yield Event(type="state", agent="diy_loop", data={"context": info})
                state.messages.append({"role": "assistant", "content": content})
                for block in content:
                    if block["type"] == "tool_use":
                        yield Event(
                            type="tool_call",
                            agent="diy_loop",
                            name=block["name"],
                            id=block["id"],
                            args=block.get("input"),
                        )
                    elif block["type"] == "text" and block["text"].strip():
                        yield Event(type="message", agent="diy_loop", text=block["text"])
                state.pending_tools = [b for b in content if b["type"] == "tool_use"]
                state.tool_results = []
                if state.pending_tools:
                    state.status = RUN_TOOLS
                elif stop_reason == "pause_turn":
                    state.status = CALL_MODEL  # server paused a long turn: call again to continue
                else:
                    state.status = DONE
                yield await self._checkpoint(
                    state, "model" if state.status != DONE else "model_final"
                )
            elif state.status == RUN_TOOLS:
                while state.pending_tools:
                    block = state.pending_tools[0]
                    result = await self._run_tool(block)
                    state.tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block["id"],
                            "content": json.dumps(result, default=str),
                        }
                    )
                    state.pending_tools.pop(0)
                    yield Event(
                        type="tool_result",
                        agent="diy_loop",
                        name=block["name"],
                        id=block["id"],
                        result=result,
                    )
                    yield await self._checkpoint(state, f"tool:{block['name']}")
                state.messages.append({"role": "user", "content": state.tool_results})
                state.tool_results = []
                state.status = CALL_MODEL
                yield await self._checkpoint(state, "tools_done")

        answer = next(
            (
                _text(m["content"])
                for m in reversed(state.messages)
                if m["role"] == "assistant" and _text(m["content"])
            ),
            "",
        )
        if self.opts.get("long_term", True):
            start = int(state.vars.get("turn_start", 0))
            ops = await extract_and_consolidate(
                self.facts, self._complete, user_id, session_id, state.messages[start:]
            )
            if ops:
                yield Event(type="state", agent="diy_loop", data={"memory": ops})
        state.vars["last_answer"] = answer
        yield await self._checkpoint(state, "done")
        yield Event(
            type="done",
            output=answer,
            data={"usage": state.usage, "checkpoint": self.last_checkpoint},
        )
