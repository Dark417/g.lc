"""Context management: what part of the conversation is sent to the model.

The stored conversation (LoopState.messages) is never changed here. Each strategy returns a
*view* plus extra system text:

  full          everything (fine until it isn't)
  window        last N messages
  token_budget  drop oldest until the estimate fits a budget
  summary       fold old messages into a rolling summary (an LLM call), send summary + recent
  server        send everything; Anthropic compacts server-side (beta compact_20260112) and clears
                stale tool results (context editing, clear_tool_uses_20250919)

Rule for every client-side cut: a view must start at a real user message, never at a tool_result,
or the API rejects the orphaned tool_result (its tool_use was cut away).
"""

import json
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field

from app.adapters.diy.state import LoopState

SUMMARIZE_MARKER = "[diy:summarize]"


@dataclass
class ContextView:
    messages: list[dict]
    system_extra: list[str] = field(default_factory=list)
    request_extra: dict = field(default_factory=dict)  # extra API params (server strategy)
    info: dict = field(default_factory=dict)


def approx_tokens(messages: list[dict]) -> int:
    """~4 characters per token. PRODUCTION: client.messages.count_tokens for exact numbers."""
    return len(json.dumps(messages, default=str)) // 4


def is_turn_start(msg: dict) -> bool:
    """A user message that is not a tool_result carrier: a safe place to start a view."""
    if msg["role"] != "user":
        return False
    content = msg["content"]
    return isinstance(content, str) or not any(
        isinstance(b, dict) and b.get("type") == "tool_result" for b in content
    )


def safe_cut(messages: list[dict], start: int) -> int:
    """Move `start` forward to the next turn start (or to the end)."""
    i = max(0, start)
    while i < len(messages) and not is_turn_start(messages[i]):
        i += 1
    return min(i, len(messages) - 1) if messages else 0


def _window(state: LoopState, opts: dict) -> ContextView:
    n = int(opts.get("window", 12))
    cut = safe_cut(state.messages, len(state.messages) - n)
    return ContextView(state.messages[cut:], info={"dropped": cut})


def _token_budget(state: LoopState, opts: dict) -> ContextView:
    budget = int(opts.get("token_budget", 3000))
    cut = 0
    while approx_tokens(state.messages[cut:]) > budget:
        nxt = safe_cut(state.messages, cut + 1)
        if nxt <= cut or nxt >= len(state.messages) - 1:
            break  # keep at least the current turn, even if it alone is over budget
        cut = nxt
    return ContextView(state.messages[cut:], info={"dropped": cut, "budget": budget})


Summarizer = Callable[[str, list[dict]], Awaitable[str]]


async def _summary(state: LoopState, opts: dict, summarize: Summarizer) -> ContextView:
    keep = int(opts.get("keep_recent", 6))
    trigger = int(opts.get("summarize_after", 10))
    unsummarized = len(state.messages) - state.summarized_upto
    if unsummarized > trigger:
        cut = safe_cut(state.messages, len(state.messages) - keep)
        if cut > state.summarized_upto:
            # The summary is *state*: it is checkpointed with everything else.
            state.summary = await summarize(
                state.summary, state.messages[state.summarized_upto : cut]
            )
            state.summarized_upto = cut
    extra = [f"Summary of the earlier conversation:\n{state.summary}"] if state.summary else []
    return ContextView(
        state.messages[state.summarized_upto :],
        extra,
        info={"summarized_upto": state.summarized_upto},
    )


def _server(state: LoopState, opts: dict) -> ContextView:
    return ContextView(
        list(state.messages),
        request_extra={
            "betas": ["compact-2026-01-12", "context-management-2025-06-27"],
            "context_management": {
                "edits": [
                    {"type": "clear_tool_uses_20250919"},
                    {"type": "compact_20260112"},
                ]
            },
        },
    )


async def build_context(state: LoopState, opts: dict, summarize: Summarizer) -> ContextView:
    strategy = opts.get("context", "window")
    if strategy == "full":
        view = ContextView(list(state.messages))
    elif strategy == "window":
        view = _window(state, opts)
    elif strategy == "token_budget":
        view = _token_budget(state, opts)
    elif strategy == "summary":
        view = await _summary(state, opts, summarize)
    elif strategy == "server":
        view = _server(state, opts)
    else:
        raise ValueError(f"unknown context strategy {strategy!r}")
    view.info.update(
        strategy=strategy,
        stored_messages=len(state.messages),
        sent_messages=len(view.messages),
        approx_tokens=approx_tokens(view.messages),
    )
    return view
