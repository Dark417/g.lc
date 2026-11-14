"""`adk:memory`: the vertex branch's state suite (docs/design/07-state-and-memory.md).

ADK's state model *is* Vertex AI Agent Engine's:
  Session            ordered events + key-value state       VertexAiSessionService on vertex
  state scopes       "x" session | "user:x" all of a user's sessions | "app:x" all users |
                     "temp:x" this invocation only (never persisted)
  MemoryService      long-term, cross-session               VertexAiMemoryBankService on vertex
                     PreloadMemoryTool (every turn) and load_memory (when the model asks)
  App configs        events_compaction_config  LLM summary replaces old events in the context
                     resumability_config       a failed invocation resumes by invocation_id
                     context_cache_config      Gemini context caching (server-side prefix cache)
  Runner             rewind_async              roll a session back to before an invocation

Everything below is ADK-native except the crash switch used to demonstrate recovery.
"""

from typing import Any

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.context_cache_config import ContextCacheConfig
from google.adk.apps.app import EventsCompactionConfig, ResumabilityConfig
from google.adk.apps.llm_event_summarizer import LlmEventSummarizer
from google.adk.models.llm_request import LlmRequest
from google.adk.tools import load_memory
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.adk.tools.tool_context import ToolContext


class SimulatedCrash(RuntimeError):
    pass


async def save_preference(key: str, value: str, tool_context: ToolContext) -> dict:
    """Save a user preference that applies to all of this user's future conversations.

    Args:
        key: Short name, e.g. "region" or "language".
        value: The preference value, e.g. "us-east-1".
    """
    prefs = dict(tool_context.state.get("user:preferences", {}))
    prefs[key] = value
    tool_context.state["user:preferences"] = prefs  # user scope: every session of this user
    tool_context.state["app:preferences_saved"] = (
        tool_context.state.get("app:preferences_saved", 0) + 1
    )
    tool_context.state["temp:last_tool"] = "save_preference"  # invocation scope: never persisted
    return {"status": "saved", "preferences": prefs}


async def add_note(text: str, tool_context: ToolContext) -> dict:
    """Add a note to this conversation's scratchpad (visible only in this session).

    Args:
        text: The note.
    """
    notes = list(tool_context.state.get("notes", []))  # session scope
    notes.append(text)
    tool_context.state["notes"] = notes
    return {"status": "noted", "count": len(notes)}


def count_turn(callback_context: CallbackContext) -> None:
    """after_agent_callback: writes go through callback_context.state, so they land in an event's
    state_delta and are persisted by the session service."""
    callback_context.state["turns"] = callback_context.state.get("turns", 0) + 1
    callback_context.state["user:total_turns"] = (
        callback_context.state.get("user:total_turns", 0) + 1
    )


def crash_switch(crash_on: int | None):
    calls = {"n": 0}

    def before_model(callback_context: CallbackContext, llm_request: LlmRequest):
        calls["n"] += 1
        if crash_on and calls["n"] == crash_on:
            raise SimulatedCrash(
                'simulated model outage; recover with {"resume": {"recover": true}}'
            )
        return None

    return before_model


def memory_agent(k) -> LlmAgent:
    return LlmAgent(
        name="memory_assistant",
        model=k.model("assistant"),
        instruction=(
            "You are an engineering research assistant with memory. "
            "User preferences: {user:preferences?}. Session notes: {notes?}. "
            "Save lasting preferences with save_preference and session-only notes with add_note. "
            "Use load_memory to search earlier conversations when the user refers to them."
        ),
        tools=[
            *k.tools("calculator", "current_time", "search_docs"),
            save_preference,
            add_note,
            load_memory,
            PreloadMemoryTool(),
        ],
        before_model_callback=crash_switch(k.options.get("crash_on_model_call")),
        after_agent_callback=count_turn,
        output_key="last_answer",
    )


def memory_app_config(k) -> dict[str, Any]:
    return {
        "resumability_config": ResumabilityConfig(is_resumable=True),
        "events_compaction_config": EventsCompactionConfig(
            compaction_interval=int(k.options.get("compaction_interval", 3)),  # every N invocations
            overlap_size=int(k.options.get("overlap_size", 1)),
            summarizer=LlmEventSummarizer(llm=k.model("summarizer")),
        ),
        # Gemini only (explicit context caching on Vertex / Gemini API); a no-op for other models.
        "context_cache_config": ContextCacheConfig(
            cache_intervals=10, ttl_seconds=1800, min_tokens=4096
        ),
    }
