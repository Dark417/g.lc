"""ADK patterns: one builder per pattern, each showing a different part of ADK.

single       LlmAgent + FunctionTool + McpToolset + PreloadMemoryTool + callbacks (+ native RAG on vertex)
sequential   SequentialAgent: researcher -> writer, state passed via output_key / {notes}
parallel     ParallelAgent fan-out inside a SequentialAgent, then a synthesizer fan-in
loop         LoopAgent: drafter <-> critic until the critic calls exit_loop
coordinator  LLM-driven delegation two ways: sub_agents (transfer) and AgentTool (call + return)
custom       BaseAgent subclass: deterministic, code-first routing (no LLM decides the route)
workflow     ADK 2 graph Workflow: function node routes to agent nodes, then a function node formats
"""

import re
from collections.abc import AsyncGenerator, Callable
from dataclasses import dataclass, field
from typing import Any

from google.adk.agents import BaseAgent, LlmAgent, LoopAgent, ParallelAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event as AdkEvent
from google.adk.events import EventActions
from google.adk.models import BaseLlm
from google.adk.tools import FunctionTool, exit_loop
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.adk.workflow import START, Workflow

from app.adapters.adk.callbacks import add_run_context, tool_policy
from app.adapters.adk.memory import memory_agent, memory_app_config
from app.config import Settings
from app.core.adapter import PatternInfo
from app.mcp.clients import server_specs
from app.providers.profile import ProviderProfile
from app.tools import tools_for

CITE = "Cite the `source` of any passage you use from search_docs."


@dataclass
class AdkKit:
    """What a pattern builder may use. Built fresh per run (an ADK agent can have one parent)."""

    profile: ProviderProfile
    settings: Settings
    options: dict[str, Any]
    model_for: Callable[[str], BaseLlm]
    toolsets: list[Any] = field(default_factory=list)  # opened MCP toolsets, closed after the run

    def model(self, role: str) -> BaseLlm:
        return self.model_for(role)

    def tools(self, *names: str) -> list[FunctionTool]:
        return [FunctionTool(f) for f in tools_for(self.profile, list(names) or None)]

    def mcp(self) -> list[Any]:
        """One McpToolset per MCP server (ours + Playwright MCP if enabled)."""
        if not self.options.get("mcp", True):
            return []
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        for spec in server_specs(self.settings):
            params = StdioServerParameters(
                command=spec.command, args=spec.args, env=spec.env, cwd=spec.cwd
            )
            self.toolsets.append(
                McpToolset(
                    connection_params=StdioConnectionParams(server_params=params, timeout=30)
                )
            )
        return list(self.toolsets)

    @property
    def before_tool(self):
        return tool_policy(set(self.options.get("deny_tools", [])))

    def native_rag(self) -> list[Any]:
        """Vertex RAG Engine as ADK's built-in retrieval tool (Gemini only).

        Gemini rejects built-in retrieval mixed with function declarations in one request, so it
        lives in its own agent, exposed to the parent through AgentTool: the standard ADK fix.
        """
        s = self.settings
        if not (
            self.profile.name == "vertex"
            and s.vertex_rag_corpus
            and self.profile.vendor(None) == "gemini"
        ):
            return []
        from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
        from vertexai import rag

        rag_agent = LlmAgent(
            name="rag_agent",
            model=self.model("rag_agent"),
            description="Retrieves passages from the Vertex AI RAG Engine corpus.",
            instruction="Answer from the retrieved passages only and name their sources.",
            tools=[
                VertexAiRagRetrieval(
                    name="retrieve_rag_corpus",
                    description="Search the managed RAG corpus.",
                    rag_resources=[rag.RagResource(rag_corpus=s.vertex_rag_corpus)],
                    similarity_top_k=4,
                )
            ],
        )
        return [AgentTool(rag_agent)]


# ---------------------------------------------------------------------------- single


def single(k: AdkKit) -> BaseAgent:
    return LlmAgent(
        name="assistant",
        model=k.model("assistant"),
        description="Engineering research assistant with local, CLI, browser, RAG, memory and MCP tools.",
        instruction=(
            "You are an engineering research assistant. Use tools instead of guessing: calculator "
            "for math, search_docs for agent frameworks and cloud services, browse for URLs, "
            "run_cli for allowlisted commands, the workbench tools for tickets, remember/recall "
            f"for durable user facts. {CITE} Be concise."
        ),
        tools=[*k.tools(), *k.mcp(), *k.native_rag(), PreloadMemoryTool()],
        before_model_callback=add_run_context,
        before_tool_callback=k.before_tool,
        output_key="last_answer",
    )


# ---------------------------------------------------------------------------- sequential


def sequential(k: AdkKit) -> BaseAgent:
    researcher = LlmAgent(
        name="researcher",
        model=k.model("researcher"),
        instruction=(
            "Research the user's question with your tools. Output concise bullet notes with "
            "sources. Do not write the final answer."
        ),
        tools=k.tools("search_docs", "browse", "calculator"),
        before_tool_callback=k.before_tool,
        output_key="notes",
    )
    writer = LlmAgent(
        name="writer",
        model=k.model("writer"),
        instruction=(
            "Write the final answer to the user's question using only these research notes:\n"
            "{notes}\nKeep the sources."
        ),
        output_key="answer",
    )
    return SequentialAgent(name="research_pipeline", sub_agents=[researcher, writer])


# ---------------------------------------------------------------------------- parallel


def parallel(k: AdkKit) -> BaseAgent:
    docs = LlmAgent(
        name="docs_researcher",
        model=k.model("docs_researcher"),
        instruction=f"Find what the knowledge base says about the user's question. {CITE} Bullet notes only.",
        tools=k.tools("search_docs"),
        output_key="docs_findings",
    )
    web = LlmAgent(
        name="web_researcher",
        model=k.model("web_researcher"),
        instruction=(
            "If the user's message contains a URL, browse it and summarise what is relevant. "
            "Otherwise reply exactly: no web findings."
        ),
        tools=k.tools("browse", "current_time"),
        output_key="web_findings",
    )
    synthesizer = LlmAgent(
        name="synthesizer",
        model=k.model("synthesizer"),
        instruction=(
            "Answer the user's question by merging both research results.\n"
            "Knowledge base: {docs_findings}\nWeb: {web_findings}"
        ),
        output_key="answer",
    )
    return SequentialAgent(
        name="fan_out_fan_in",
        sub_agents=[ParallelAgent(name="researchers", sub_agents=[docs, web]), synthesizer],
    )


# ---------------------------------------------------------------------------- loop


def loop(k: AdkKit) -> BaseAgent:
    drafter = LlmAgent(
        name="drafter",
        model=k.model("drafter"),
        instruction=(
            "Answer the user's question. If there is a critique, revise your previous draft to "
            f"address it.\nPrevious draft: {{draft?}}\nCritique: {{critique?}}\n{CITE}"
        ),
        tools=k.tools("search_docs", "calculator"),
        output_key="draft",
    )
    critic = LlmAgent(
        name="critic",
        model=k.model("critic"),
        instruction=(
            "Review this draft answer:\n{draft}\nIf it is accurate, complete, and cites sources, "
            "call exit_loop and say nothing else. Otherwise reply with one short, specific critique."
        ),
        tools=[exit_loop],
        output_key="critique",
    )
    return LoopAgent(
        name="refine_loop",
        sub_agents=[drafter, critic],
        max_iterations=int(k.options.get("max_iterations", 3)),
    )


# ---------------------------------------------------------------------------- coordinator


def coordinator(k: AdkKit) -> BaseAgent:
    math_agent = LlmAgent(
        name="math_agent",
        model=k.model("math_agent"),
        description="Does exact arithmetic with a calculator and returns just the result.",
        instruction="Compute what is asked with the calculator. Reply with the number only.",
        tools=k.tools("calculator"),
    )
    researcher = LlmAgent(
        name="researcher",
        model=k.model("researcher"),
        description="Answers questions about agent frameworks and cloud agent services.",
        instruction=f"Answer with search_docs (and browse for URLs). {CITE}",
        tools=k.tools("search_docs", "browse"),
    )
    ops_agent = LlmAgent(
        name="ops_agent",
        model=k.model("ops_agent"),
        description="Creates and lists tickets, runs allowlisted CLI commands, tells the time.",
        instruction="Do the operational task with your tools and confirm what you did.",
        tools=[*k.tools("run_cli", "current_time"), *k.mcp()],
        before_tool_callback=k.before_tool,
    )
    return LlmAgent(
        name="coordinator",
        model=k.model("coordinator"),
        instruction=(
            "You coordinate specialists. For arithmetic, call the math_agent tool and keep control. "
            "For research questions transfer to researcher; for tickets, CLI, or time transfer to "
            "ops_agent."
        ),
        tools=[AgentTool(math_agent)],  # call-and-return delegation
        sub_agents=[researcher, ops_agent],  # transfer-of-control delegation
    )


# ---------------------------------------------------------------------------- custom


class KeywordRouter(BaseAgent):
    """A custom agent: Python decides which sub-agent runs. Cheaper and more predictable than an
    LLM router when the routing rule is simple; same idea as 0.learn's code-first orchestrator."""

    routes: list[tuple[str, str]]  # (regex, sub-agent name); first match wins, last is default

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[AdkEvent, None]:
        text = "".join(p.text or "" for p in (ctx.user_content.parts if ctx.user_content else []))
        target = next(
            (name for rx, name in self.routes if re.search(rx, text, re.I)), self.routes[-1][1]
        )
        yield AdkEvent(
            author=self.name,
            invocation_id=ctx.invocation_id,
            actions=EventActions(state_delta={"route": target}),
        )
        agent = self.find_sub_agent(target)
        async for event in agent.run_async(ctx):
            yield event


def custom(k: AdkKit) -> BaseAgent:
    math_agent = LlmAgent(
        name="math_agent",
        model=k.model("math_agent"),
        instruction="Compute the answer with the calculator; show the expression and result.",
        tools=k.tools("calculator"),
    )
    ops_agent = LlmAgent(
        name="ops_agent",
        model=k.model("ops_agent"),
        instruction="Answer with run_cli or current_time.",
        tools=k.tools("run_cli", "current_time"),
        before_tool_callback=k.before_tool,
    )
    researcher = LlmAgent(
        name="researcher",
        model=k.model("researcher"),
        instruction=f"Answer with search_docs. {CITE}",
        tools=k.tools("search_docs"),
    )
    return KeywordRouter(
        name="router",
        sub_agents=[math_agent, ops_agent, researcher],
        routes=[
            (r"\d\s*[-+*/%^]\s*\d|\bpercent\b|%|\bcalculate\b", "math_agent"),
            (r"\b(time|date|run|command|cli|uname|ls)\b", "ops_agent"),
            (r".*", "researcher"),
        ],
    )


# ---------------------------------------------------------------------------- workflow


def classify(node_input: str) -> AdkEvent:
    """Function node: deterministic routing; the emitted route selects the outgoing edge."""
    text = str(node_input)
    if re.search(r"\d\s*[-+*/%^]\s*\d|\bpercent\b|%", text, re.I):
        route = "math"
    elif re.search(r"\bticket", text, re.I):
        route = "ops"
    else:
        route = "research"
    return AdkEvent(output=text, route=route, state={"route": route})


def format_answer(node_input: str) -> str:
    """Function node: post-processing every branch shares."""
    return f"{str(node_input).strip()}\n\n— via ADK Workflow"


def workflow(k: AdkKit) -> Workflow:
    math_agent = LlmAgent(
        name="math_agent",
        model=k.model("math_agent"),
        instruction="Compute with the calculator; reply with the expression and result.",
        tools=k.tools("calculator"),
    )
    researcher = LlmAgent(
        name="researcher",
        model=k.model("researcher"),
        instruction=f"Answer with search_docs. {CITE}",
        tools=k.tools("search_docs"),
    )
    ops_agent = LlmAgent(
        name="ops_agent",
        model=k.model("ops_agent"),
        instruction="Handle the ticket request with the workbench tools; confirm the ticket id.",
        tools=k.mcp(),
    )
    return Workflow(
        name="routed_workflow",
        edges=[
            (START, classify, {"math": math_agent, "research": researcher, "ops": ops_agent}),
            (math_agent, format_answer),
            (researcher, format_answer),
            (ops_agent, format_answer),
        ],
    )


@dataclass(frozen=True)
class Pattern:
    info: PatternInfo
    build: Callable[[AdkKit], Any]
    output_key: str | None = None  # read the final answer from session state
    app_config: Callable[[AdkKit], dict] | None = None  # extra App(...) settings


PATTERNS: dict[str, Pattern] = {
    p.info.name: p
    for p in [
        Pattern(
            PatternInfo(
                "single",
                "One LlmAgent with every tool type, memory, callbacks, and an app-wide plugin.",
                (
                    "LlmAgent",
                    "FunctionTool",
                    "McpToolset",
                    "PreloadMemoryTool",
                    "before_model_callback",
                    "before_tool_callback",
                    "BasePlugin",
                    "output_key",
                    "VertexAiRagRetrieval (vertex)",
                ),
            ),
            single,
        ),
        Pattern(
            PatternInfo(
                "sequential",
                "researcher -> writer; state is the bus between them.",
                ("SequentialAgent", "output_key", "{state} instruction templating"),
            ),
            sequential,
            "answer",
        ),
        Pattern(
            PatternInfo(
                "parallel",
                "docs and web researchers run concurrently, then a synthesizer merges them.",
                ("ParallelAgent", "SequentialAgent", "output_key per branch"),
            ),
            parallel,
            "answer",
        ),
        Pattern(
            PatternInfo(
                "loop",
                "drafter and critic iterate until the critic escalates via exit_loop.",
                (
                    "LoopAgent",
                    "max_iterations",
                    "exit_loop / actions.escalate",
                    "{key?} optional state",
                ),
            ),
            loop,
            "draft",
        ),
        Pattern(
            PatternInfo(
                "coordinator",
                "LLM delegation: transfer to sub_agents, or call an agent as a tool.",
                ("sub_agents + transfer_to_agent", "AgentTool", "McpToolset"),
            ),
            coordinator,
        ),
        Pattern(
            PatternInfo(
                "custom",
                "A BaseAgent subclass routes by regex in Python; no LLM routing call.",
                ("BaseAgent._run_async_impl", "EventActions.state_delta", "find_sub_agent"),
            ),
            custom,
        ),
        Pattern(
            PatternInfo(
                "workflow",
                "ADK 2 graph: function node routes to agent nodes, a function node formats.",
                ("Workflow", "FunctionNode", "routed edges", "START", "agents as graph nodes"),
            ),
            workflow,
        ),
        Pattern(
            PatternInfo(
                "memory",
                "Vertex state suite: Agent Engine sessions, state scopes, Memory Bank, compaction, "
                "resumable invocations, rewind, Gemini context caching.",
                (
                    "VertexAiSessionService",
                    "state scopes: session / user: / app: / temp:",
                    "ToolContext.state + CallbackContext.state",
                    "{user:preferences?} templating",
                    "VertexAiMemoryBankService + PreloadMemoryTool + load_memory",
                    "EventsCompactionConfig + LlmEventSummarizer",
                    "ResumabilityConfig (resume by invocation_id)",
                    "Runner.rewind_async",
                    "ContextCacheConfig (Gemini)",
                    "output_key",
                ),
            ),
            memory_agent,
            "last_answer",
            app_config=memory_app_config,
        ),
    ]
}
