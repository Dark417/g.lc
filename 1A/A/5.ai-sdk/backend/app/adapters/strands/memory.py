"""`strands:memory`: only what Strands does differently (docs/design/07-state-and-memory.md).

agent.state                      key-value state persisted by the session manager and NOT sent
                                 to the model; tools read/write it through ToolContext
SummarizingConversationManager   when context must shrink, summarise the oldest messages with a
                                 separate summarisation agent instead of dropping them
CompactWhenLong (hook)           an explicit trigger: reduce_context() before an invocation when
                                 the stored history is longer than N messages (Strands also
                                 offers proactive_compression by token utilisation)
session managers                 File (raw/vertex), S3 or AgentCore Memory (bedrock): the agent's
                                 messages + state are restored when a new Agent object is built
"""

from typing import Any

from strands import Agent, ToolContext, tool
from strands.agent.conversation_manager import SummarizingConversationManager
from strands.hooks import BeforeInvocationEvent, HookProvider, HookRegistry

AGENT_ID = "memory_assistant"


@tool(context=True)
def set_preference(key: str, value: str, tool_context: ToolContext) -> dict:
    """Save a user preference in the agent's state (persisted, not shown to the model).

    Args:
        key: Short name, e.g. "region".
        value: The value, e.g. "us-east-1".
    """
    prefs = dict(tool_context.agent.state.get("preferences") or {})
    prefs[key] = value
    tool_context.agent.state.set("preferences", prefs)
    return {"status": "saved", "preferences": prefs}


@tool(context=True)
def get_preferences(tool_context: ToolContext) -> dict:
    """Read the saved user preferences from the agent's state."""
    return {"preferences": tool_context.agent.state.get("preferences") or {}}


class CompactWhenLong(HookProvider):
    def __init__(self, max_messages: int):
        self.max_messages = max_messages
        self.compactions = 0

    def register_hooks(self, registry: HookRegistry, **kwargs: Any) -> None:
        registry.add_callback(BeforeInvocationEvent, self.before_invocation)

    def before_invocation(self, event: BeforeInvocationEvent) -> None:
        agent = event.agent
        if len(agent.messages) > self.max_messages:
            agent.conversation_manager.reduce_context(agent)
            self.compactions += 1


def memory(k) -> Agent:
    summarizer = Agent(
        model=k.model("summarizer"),
        system_prompt="Summarise the conversation so far in under 120 words. Keep facts and decisions.",
        callback_handler=None,
    )
    return k.agent(
        "memory_assistant",
        "You are an engineering research assistant. Save lasting user preferences with "
        "set_preference; read them with get_preferences (they are not in your context otherwise).",
        [*k.tools("calculator", "search_docs"), set_preference, get_preferences],
        agent_id=AGENT_ID,
        conversation_manager=SummarizingConversationManager(
            summary_ratio=0.5,
            preserve_recent_messages=int(k.options.get("keep_recent", 4)),
            summarization_agent=summarizer,
        ),
        session_manager=k.sessions(),
        extra_hooks=[CompactWhenLong(int(k.options.get("max_messages", 12)))],
    )
