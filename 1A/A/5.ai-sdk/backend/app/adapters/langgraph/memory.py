"""`langgraph:memory`: the bedrock branch's state suite (docs/design/07-state-and-memory.md).

    START -> recall -> compact -> agent <-> tools
                                   |
                                   v
                               remember -> END

Every arrow is a superstep, and after every superstep the checkpointer saves the whole state. That
single mechanism gives conversation memory (same thread_id), crash recovery (astream(None) re-runs
only what had not finished), and time travel (aget_state_history / fork from a checkpoint_id).

  recall    long-term read: store.search, AgentCore *extracted* facts on bedrock.
            Node cache (CachePolicy): same user + same question within TTL -> no store call.
  compact   state compaction: when the thread is long, fold old messages into `summary` and delete
            them with RemoveMessage. The stored thread shrinks; older checkpoints still have them.
  agent     context view: trim_messages to a token budget (view only, state untouched).
            RetryPolicy retries transient model errors in-run.
  tools     ToolNode with its own RetryPolicy.
  remember  long-term write: store.put of the user's message; AgentCore strategies extract facts.
"""

from typing import Any

from langchain_core.messages import (
    AIMessage,
    AnyMessage,
    HumanMessage,
    RemoveMessage,
    SystemMessage,
    trim_messages,
)
from langchain_core.messages.utils import count_tokens_approximately
from langgraph.config import get_config, get_store
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.types import CachePolicy, RetryPolicy

from app.adapters.langgraph.persistence import save_message, search_memories

SYSTEM = (
    "You are an engineering research assistant. Use tools instead of guessing and cite sources."
)


class SimulatedCrash(RuntimeError):
    """options.crash_on_model_call=N raises this in the agent node (recovery demo)."""


class MemoryState(MessagesState):
    user_id: str  # in state so the node-cache key can include it (see recall)
    summary: str
    memories: list[str]


def _text(msg: AnyMessage) -> str:
    return msg.text if isinstance(msg.text, str) else str(msg.content)


def _last_human(messages: list[AnyMessage]) -> str:
    return next((_text(m) for m in reversed(messages) if isinstance(m, HumanMessage)), "")


def recall_cache_key(state: dict) -> str:
    # A cache key must contain everything the result depends on. Without user_id, two users who
    # ask the same question would share one user's memories.
    return f"{state.get('user_id')}|{_last_human(state['messages'])}"


def memory(k) -> Any:
    tools = k.tools("calculator", "current_time", "search_docs")
    opts = k.options
    summarize_after = int(opts.get("summarize_after", 12))
    keep_recent = int(opts.get("keep_recent", 6))
    trim_tokens = int(opts.get("trim_tokens", 3000))
    crash_on = opts.get("crash_on_model_call")
    calls = {"model": 0}

    async def recall(state: MemoryState) -> dict:
        found = await search_memories(get_store(), state["user_id"], _last_human(state["messages"]))
        return {"memories": found}

    async def compact(state: MemoryState) -> dict:
        msgs = state["messages"]
        if len(msgs) <= summarize_after:
            return {}
        cut = len(msgs) - keep_recent
        while cut < len(msgs) and not isinstance(msgs[cut], HumanMessage):
            cut += 1  # never start the kept window with a tool result
        old = msgs[:cut]
        transcript = "\n".join(f"{m.type}: {_text(m)}" for m in old)
        reply = await k.model("summarizer").ainvoke(
            [
                SystemMessage("Update the running summary. Keep facts and decisions. <=120 words."),
                HumanMessage(
                    f"Previous summary: {state.get('summary') or '(none)'}\n\n{transcript}"
                ),
            ]
        )
        return {"summary": _text(reply), "messages": [RemoveMessage(id=m.id) for m in old]}

    async def agent(state: MemoryState) -> dict:
        calls["model"] += 1
        if crash_on and calls["model"] == int(crash_on):
            raise SimulatedCrash(
                'simulated model outage; recover with {"resume": {"recover": true}}'
            )
        system = SYSTEM
        if state.get("summary"):
            system += f"\n\nSummary of the earlier conversation:\n{state['summary']}"
        if state.get("memories"):
            system += "\n\nKnown about this user:\n" + "\n".join(
                f"- {m}" for m in state["memories"]
            )
        view = trim_messages(
            state["messages"],
            max_tokens=trim_tokens,
            token_counter=count_tokens_approximately,
            strategy="last",
            start_on="human",
            allow_partial=False,
        )
        reply = await k.model("agent").bind_tools(tools).ainvoke([SystemMessage(system), *view])
        return {"messages": [reply]}

    async def remember(state: MemoryState) -> dict:
        cfg = get_config()["configurable"]
        last = next((m for m in reversed(state["messages"]) if isinstance(m, HumanMessage)), None)
        if last is not None:
            await save_message(get_store(), state["user_id"], cfg["thread_id"], last)
        return {}

    def route(state: MemoryState) -> str:
        last = state["messages"][-1]
        return "tools" if isinstance(last, AIMessage) and last.tool_calls else "remember"

    transient = RetryPolicy(
        max_attempts=3, initial_interval=0.2, retry_on=(ConnectionError, TimeoutError)
    )
    builder = StateGraph(MemoryState)
    builder.add_node("recall", recall, cache_policy=CachePolicy(key_func=recall_cache_key, ttl=300))
    builder.add_node("compact", compact)
    builder.add_node("agent", agent, retry_policy=transient)
    builder.add_node("tools", ToolNode(tools), retry_policy=RetryPolicy(max_attempts=2))
    builder.add_node("remember", remember)
    builder.add_edge(START, "recall")
    builder.add_edge("recall", "compact")
    builder.add_edge("compact", "agent")
    builder.add_conditional_edges("agent", route, ["tools", "remember"])
    builder.add_edge("tools", "agent")
    builder.add_edge("remember", END)
    return builder.compile(
        checkpointer=k.checkpointer, store=k.store, cache=k.cache, name="memory_graph"
    )


def memory_input(message: str, user_id: str) -> dict:
    return {"messages": [HumanMessage(message)], "user_id": user_id}
