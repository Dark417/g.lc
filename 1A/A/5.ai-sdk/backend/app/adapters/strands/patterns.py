"""Strands patterns.

single           Agent + @tool + MCPClient tools + hooks + conversation manager + session manager
                 (+ strands_tools AgentCore Browser / Code Interpreter on bedrock)
agents_as_tools  orchestrator Agent calls specialist Agents wrapped in @tool functions
swarm            Swarm: agents hand off to each other autonomously (handoff_to_agent)
graph            GraphBuilder DAG with a conditional edge
structured       structured_output_model -> a validated Pydantic object
"""

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, Field
from strands import Agent, tool
from strands.agent.conversation_manager import SlidingWindowConversationManager
from strands.models import Model
from strands.multiagent import GraphBuilder, Swarm

from app.adapters.strands.memory import memory
from app.adapters.strands.state import ToolPolicyHooks, session_manager
from app.config import Settings
from app.core.adapter import PatternInfo
from app.providers.profile import ProviderProfile
from app.tools import tools_for

SYSTEM = (
    "You are an engineering research assistant. Use tools instead of guessing: calculator for "
    "math, search_docs for agent frameworks and cloud services, browse for URLs, run_cli for "
    "allowlisted commands, workbench tools for tickets. Cite the `source` of passages you use."
)


@dataclass
class StrandsKit:
    profile: ProviderProfile
    settings: Settings
    options: dict[str, Any]
    model_for: Callable[[str], Model]
    session_id: str
    user_id: str
    mcp_tools: list[Any] = field(default_factory=list)

    def model(self, role: str) -> Model:
        return self.model_for(role)

    def tools(self, *names: str) -> list[Any]:
        """Neutral async functions -> Strands tools via the @tool decorator."""
        return [tool(f) for f in tools_for(self.profile, list(names) or None)]

    def hooks(self) -> list[ToolPolicyHooks]:
        return [
            ToolPolicyHooks(set(self.options.get("deny_tools", [])), self.settings.max_llm_calls)
        ]

    def sessions(self, suffix: str = "") -> Any:
        return session_manager(
            self.profile.name, self.settings, self.session_id + suffix, self.user_id
        )

    def agent(self, name: str, prompt: str, tools: list[Any], extra_hooks=(), **kw) -> Agent:
        return Agent(
            name=name,
            model=self.model(name),
            system_prompt=prompt,
            tools=tools,
            hooks=[*self.hooks(), *extra_hooks],
            callback_handler=None,  # we consume stream_async instead of printing
            trace_attributes={"session.id": self.session_id, "user.id": self.user_id},
            **kw,
        )

    def native_aws_tools(self) -> list[Any]:
        """strands_tools wrappers for AgentCore Browser and Code Interpreter (bedrock only)."""
        s, out = self.settings, []
        if self.profile.name != "bedrock":
            return out
        if s.agentcore_browser:
            from strands_tools.browser import AgentCoreBrowser

            out.append(AgentCoreBrowser(region=s.aws_region).browser)
        if s.agentcore_code_interpreter:
            from strands_tools.code_interpreter import AgentCoreCodeInterpreter

            out.append(AgentCoreCodeInterpreter(region=s.aws_region).code_interpreter)
        return out


# ---------------------------------------------------------------------------- single


def single(k: StrandsKit) -> Agent:
    return k.agent(
        "assistant",
        SYSTEM,
        [*k.tools(), *k.mcp_tools, *k.native_aws_tools()],
        conversation_manager=SlidingWindowConversationManager(window_size=20),
        session_manager=k.sessions(),
    )


# ---------------------------------------------------------------------------- agents_as_tools


def agents_as_tools(k: StrandsKit) -> Agent:
    research = k.agent(
        "research_assistant",
        f"{SYSTEM} Answer research questions only.",
        k.tools("search_docs", "browse"),
    )
    math = k.agent(
        "math_assistant",
        "Compute exactly with the calculator; reply with the result.",
        k.tools("calculator"),
    )

    @tool
    async def research_assistant(query: str) -> str:
        """Ask the research specialist about agent frameworks, cloud services, or a URL.

        Args:
            query: A complete, self-contained research question.
        """
        return str(await research.invoke_async(query)).strip()

    @tool
    async def math_assistant(problem: str) -> str:
        """Ask the math specialist to compute something exactly.

        Args:
            problem: The calculation in words or symbols.
        """
        return str(await math.invoke_async(problem)).strip()

    return k.agent(
        "orchestrator",
        "Delegate: research questions to research_assistant, math to math_assistant. Then combine their answers.",
        [research_assistant, math_assistant],
        session_manager=k.sessions(),
    )


# ---------------------------------------------------------------------------- swarm


def swarm(k: StrandsKit) -> Swarm:
    researcher = k.agent(
        "researcher",
        f"{SYSTEM} Gather facts with tools, then hand off to the writer with your notes.",
        k.tools("search_docs", "browse", "calculator"),
    )
    writer = k.agent(
        "writer",
        "Write a clear answer from the researcher's notes, then hand off to the reviewer.",
        [],
    )
    reviewer = k.agent(
        "reviewer",
        "Check the answer for accuracy and sources. If fine, reply with the final answer; otherwise hand back to the writer.",
        [],
    )
    return Swarm(
        [researcher, writer, reviewer],
        entry_point=researcher,
        max_handoffs=int(k.options.get("max_handoffs", 6)),
        max_iterations=k.settings.max_llm_calls,
        execution_timeout=300.0,
    )


# ---------------------------------------------------------------------------- graph

_MATH = re.compile(r"\d\s*[-+*/%^]\s*\d|\bpercent\b|%", re.I)


def needs_math(state) -> bool:
    """Edge condition: only route to the calculator node when the task contains arithmetic."""
    return bool(_MATH.search(str(state.task)))


def graph(k: StrandsKit):
    builder = GraphBuilder()
    builder.add_node(
        k.agent(
            "research", f"{SYSTEM} Research the task; bullet notes only.", k.tools("search_docs")
        ),
        "research",
    )
    builder.add_node(
        k.agent(
            "calculate", "Do any arithmetic in the task with the calculator.", k.tools("calculator")
        ),
        "calculate",
    )
    builder.add_node(
        k.agent("report", "Write the final answer from the upstream results. Keep sources.", []),
        "report",
    )
    # A Strands graph node runs once per satisfied incoming edge, so the two paths into
    # `report` are made mutually exclusive: via `calculate` when there is math, direct otherwise.
    builder.add_edge("research", "calculate", condition=needs_math)
    builder.add_edge("research", "report", condition=lambda state: not needs_math(state))
    builder.add_edge("calculate", "report")
    builder.set_entry_point("research")
    builder.set_max_node_executions(6)
    builder.set_execution_timeout(300.0)
    return builder.build()


# ---------------------------------------------------------------------------- structured


class ResearchBrief(BaseModel):
    """A short, structured research brief."""

    topic: str = Field(description="What the brief is about")
    summary: str = Field(description="Two or three sentences")
    key_points: list[str] = Field(description="3-5 bullet points")
    sources: list[str] = Field(description="Corpus files or URLs used")


def structured(k: StrandsKit) -> Agent:
    return k.agent(
        "brief_writer",
        f"{SYSTEM} Research with search_docs, then return a ResearchBrief.",
        k.tools("search_docs"),
        structured_output_model=ResearchBrief,
    )


@dataclass(frozen=True)
class Pattern:
    info: PatternInfo
    build: Callable[[StrandsKit], Any]
    uses_mcp: bool = False


PATTERNS: dict[str, Pattern] = {
    p.info.name: p
    for p in [
        Pattern(
            PatternInfo(
                "single",
                "One model-driven Agent with every tool type, hooks, and persistent sessions.",
                (
                    "Agent",
                    "@tool",
                    "MCPClient",
                    "HookProvider (BeforeModelCall/BeforeToolCall/AfterToolCall)",
                    "SlidingWindowConversationManager",
                    "FileSessionManager / AgentCoreMemorySessionManager",
                    "strands_tools AgentCoreBrowser / AgentCoreCodeInterpreter (bedrock)",
                    "BedrockModel guardrail_id (bedrock)",
                ),
            ),
            single,
            uses_mcp=True,
        ),
        Pattern(
            PatternInfo(
                "agents_as_tools",
                "An orchestrator calls specialist agents wrapped as tools.",
                (
                    "Agent",
                    "@tool wrapping Agent.invoke_async",
                    "session manager on the orchestrator",
                ),
            ),
            agents_as_tools,
        ),
        Pattern(
            PatternInfo(
                "swarm",
                "researcher -> writer -> reviewer hand off autonomously with shared context.",
                ("Swarm", "handoff_to_agent (auto-injected)", "max_handoffs", "execution_timeout"),
            ),
            swarm,
        ),
        Pattern(
            PatternInfo(
                "graph",
                "Deterministic DAG with a conditional edge to a calculator node.",
                (
                    "GraphBuilder",
                    "add_edge(condition=...)",
                    "set_entry_point",
                    "set_max_node_executions",
                ),
            ),
            graph,
        ),
        Pattern(
            PatternInfo(
                "structured",
                "Returns a validated Pydantic ResearchBrief instead of free text.",
                ("structured_output_model", "Pydantic", "forced structured-output tool"),
            ),
            structured,
        ),
        Pattern(
            PatternInfo(
                "memory",
                "Strands-specific state: agent.state, summarising conversation manager, session "
                "managers (File / S3 / AgentCore Memory) restoring a fresh Agent each request.",
                (
                    "agent.state via ToolContext",
                    "SummarizingConversationManager + summarization_agent",
                    "reduce_context hook (CompactWhenLong)",
                    "FileSessionManager / S3SessionManager / AgentCoreMemorySessionManager",
                ),
            ),
            memory,
        ),
    ]
}
