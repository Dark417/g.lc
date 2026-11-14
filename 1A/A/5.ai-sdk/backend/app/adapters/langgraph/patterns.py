"""LangGraph patterns: each builds a compiled graph from a LgKit.

react       prebuilt create_react_agent + checkpointer + store via pre/post model hooks
graph       hand-built StateGraph: retrieve node -> agent <-> ToolNode loop (tools_condition)
middleware  langchain.agents.create_agent + built-in and custom middleware
supervisor  supervisor routes with Command(goto) to worker agents that are compiled subgraphs
map_reduce  plan -> Send() one branch per sub-question (parallel) -> reduce
hitl        interrupt() before sensitive tools; resume with Command(resume=...)
"""

import asyncio
import json
import logging
import operator
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Annotated, Any, Literal, TypedDict

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import BaseTool, StructuredTool
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.config import get_config, get_store
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, create_react_agent, tools_condition
from langgraph.store.base import BaseStore
from langgraph.types import Command, Send, interrupt
from pydantic import BaseModel, Field

from app.adapters.langgraph.memory import memory, memory_input
from app.adapters.langgraph.persistence import save_message, search_memories
from app.config import Settings
from app.core.adapter import PatternInfo
from app.providers.profile import ProviderProfile
from app.tools import SENSITIVE, tools_for

log = logging.getLogger(__name__)

SYSTEM = (
    "You are an engineering research assistant. Use tools instead of guessing: calculator for "
    "math, search_docs for agent frameworks and cloud services, browse for URLs, run_cli for "
    "allowlisted commands, workbench tools for tickets. Cite the `source` of passages you use."
)


def lc_tool(fn) -> StructuredTool:
    """Neutral async function -> LangChain tool (schema from signature + Google docstring)."""
    return StructuredTool.from_function(coroutine=fn, name=fn.__name__, parse_docstring=True)


@dataclass
class LgKit:
    profile: ProviderProfile
    settings: Settings
    options: dict[str, Any]
    model_for: Callable[[str], BaseChatModel]
    checkpointer: BaseCheckpointSaver
    store: BaseStore
    mcp_tools: list[BaseTool] = field(default_factory=list)
    cache: Any = None  # LangGraph node cache (InMemoryCache / ValkeyCache)

    def model(self, role: str) -> BaseChatModel:
        return self.model_for(role)

    def tools(self, *names: str) -> list[BaseTool]:
        return [lc_tool(f) for f in tools_for(self.profile, list(names) or None)]

    def text_of(self, msg: AnyMessage) -> str:
        return msg.text if isinstance(msg.text, str) else str(msg.content)


# ---------------------------------------------------------------------------- react


async def recall_hook(state: dict) -> dict:
    """pre_model_hook: prepend long-term memories (Store) to what the model sees this step.

    Returns `llm_input_messages`, so memories are shown to the model but not saved in history.
    """
    cfg = get_config()["configurable"]
    last_user = next((m for m in reversed(state["messages"]) if isinstance(m, HumanMessage)), None)
    memories = await search_memories(
        get_store(), cfg["user_id"], last_user.text if last_user else ""
    )
    prefix = [SystemMessage(f"Facts from earlier conversations: {memories}")] if memories else []
    return {"llm_input_messages": prefix + state["messages"]}


async def remember_hook(state: dict) -> dict:
    """post_model_hook: write the user's message to the Store (long-term, cross-thread), once per
    turn: right after the first model call that followed it.

    On bedrock the Store is AgentCore Memory, which extracts facts from these events.
    """
    msgs = state["messages"]
    if len(msgs) >= 2 and isinstance(msgs[-2], HumanMessage):
        cfg = get_config()["configurable"]
        await save_message(get_store(), cfg["user_id"], cfg["thread_id"], msgs[-2])
    return {}


def react(k: LgKit):
    return create_react_agent(
        k.model("agent"),
        tools=[*k.tools(), *k.mcp_tools],
        prompt=SYSTEM,
        pre_model_hook=recall_hook,
        post_model_hook=remember_hook,
        checkpointer=k.checkpointer,
        store=k.store,
        name="react_agent",
    )


# ---------------------------------------------------------------------------- graph


class RagState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]  # reducer: append, dedupe by id
    context: str
    retrieval_backend: str


def graph(k: LgKit):
    tools = [*k.tools("calculator", "browse", "current_time"), *k.mcp_tools]
    model = k.model("agent").bind_tools(tools)

    async def retrieve(state: RagState) -> dict:
        """RAG node: always retrieve before the first model call. Native retriever on bedrock."""
        query = next(m for m in reversed(state["messages"]) if isinstance(m, HumanMessage)).text
        s = k.settings
        if k.profile.name == "bedrock" and s.bedrock_kb_id:
            from langchain_aws.retrievers import AmazonKnowledgeBasesRetriever

            retriever = AmazonKnowledgeBasesRetriever(
                knowledge_base_id=s.bedrock_kb_id,
                region_name=s.aws_region,
                retrieval_config={"vectorSearchConfiguration": {"numberOfResults": 4}},
            )
            docs = await retriever.ainvoke(query)
            chunks = [f"[{d.metadata.get('location', {})}] {d.page_content}" for d in docs]
            backend = "AmazonKnowledgeBasesRetriever"
        else:
            passages = await k.profile.retriever.search(query, k=4)
            chunks = [f"[{p.source}] {p.text[:800]}" for p in passages]
            backend = k.profile.retriever.name
        return {"context": "\n\n".join(chunks), "retrieval_backend": backend}

    async def agent(state: RagState) -> dict:
        system = SystemMessage(f"{SYSTEM}\n\nRetrieved context:\n{state.get('context', '')}")
        return {"messages": [await model.ainvoke([system, *state["messages"]])]}

    builder = StateGraph(RagState)
    builder.add_node("retrieve", retrieve)
    builder.add_node("agent", agent)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "retrieve")
    builder.add_edge("retrieve", "agent")
    builder.add_conditional_edges("agent", tools_condition)  # -> "tools" or END
    builder.add_edge("tools", "agent")
    return builder.compile(checkpointer=k.checkpointer, name="rag_graph")


# ---------------------------------------------------------------------------- middleware


@dataclass
class UserContext:
    user_id: str


def middleware(k: LgKit):
    from langchain.agents import create_agent
    from langchain.agents.middleware import (
        ModelCallLimitMiddleware,
        PIIMiddleware,
        SummarizationMiddleware,
        ToolCallLimitMiddleware,
        ToolRetryMiddleware,
        before_model,
        dynamic_prompt,
        wrap_tool_call,
    )

    @dynamic_prompt
    def personalised_prompt(request) -> str:
        """Built per model call from runtime context (not baked into the graph)."""
        return f"{SYSTEM}\nThe user id is {request.runtime.context.user_id}."

    @before_model
    def log_model_call(state, runtime) -> None:
        log.info("model call #%d messages", len(state["messages"]))
        return None

    deny = set(k.options.get("deny_tools", []))

    @wrap_tool_call
    async def tool_policy(request, handler):
        """Around every tool call: enforce a deny-list, then time the call."""
        name = request.tool_call["name"]
        if name in deny:
            return ToolMessage(
                content=json.dumps({"status": "denied", "error": f"{name} disabled by policy"}),
                tool_call_id=request.tool_call["id"],
                name=name,
            )
        loop = asyncio.get_running_loop()
        started = loop.time()
        result = await handler(request)
        log.info("tool %s took %.2fs", name, loop.time() - started)
        return result

    return create_agent(
        k.model("agent"),
        tools=[*k.tools(), *k.mcp_tools],
        middleware=[
            personalised_prompt,
            PIIMiddleware("email", strategy="redact", apply_to_input=True),
            PIIMiddleware("credit_card", strategy="mask", apply_to_input=True),
            SummarizationMiddleware(
                model=k.model("summarizer"), trigger=("messages", 40), keep=("messages", 20)
            ),
            ModelCallLimitMiddleware(run_limit=k.settings.max_llm_calls, exit_behavior="end"),
            ToolCallLimitMiddleware(tool_name="browse", run_limit=3),
            ToolRetryMiddleware(max_retries=1, tools=["browse"], initial_delay=0.5),
            log_model_call,
            tool_policy,
        ],
        context_schema=UserContext,
        checkpointer=k.checkpointer,
        name="middleware_agent",
    )


# ---------------------------------------------------------------------------- supervisor


class Route(BaseModel):
    """Pick who acts next."""

    next: Literal["researcher", "calculator", "FINISH"] = Field(
        description="researcher for docs/web questions, calculator for math, FINISH when answered"
    )


class SupervisorState(MessagesState):
    next: str


def supervisor(k: LgKit):
    workers = {
        "researcher": create_react_agent(
            k.model("researcher"),
            tools=k.tools("search_docs", "browse"),
            prompt=SYSTEM,
            name="researcher",
        ),
        "calculator": create_react_agent(
            k.model("calculator"),
            tools=k.tools("calculator"),
            prompt="Compute exactly with the calculator.",
            name="calculator",
        ),
    }
    router = k.model("supervisor").bind_tools([Route], tool_choice="Route")

    async def supervise(
        state: SupervisorState,
    ) -> Command[Literal["researcher", "calculator", "__end__"]]:
        """Structured routing via a forced tool call (what with_structured_output does underneath)."""
        system = SystemMessage(
            "You supervise a researcher and a calculator. Given the conversation, choose who acts "
            "next, or FINISH when the user's question is fully answered."
        )
        resp = await router.ainvoke([system, *state["messages"]])
        nxt = resp.tool_calls[0]["args"]["next"] if resp.tool_calls else "FINISH"
        return Command(goto=END if nxt == "FINISH" else nxt, update={"next": nxt})

    def worker_node(name: str):
        async def run(state: SupervisorState) -> Command[Literal["supervisor"]]:
            result = await workers[name].ainvoke({"messages": state["messages"]})
            answer = k.text_of(result["messages"][-1])
            return Command(
                goto="supervisor", update={"messages": [AIMessage(content=answer, name=name)]}
            )

        return run

    builder = StateGraph(SupervisorState)
    builder.add_node("supervisor", supervise)
    for name in workers:
        builder.add_node(name, worker_node(name))
    builder.add_edge(START, "supervisor")
    return builder.compile(checkpointer=k.checkpointer, name="supervisor_graph")


# ---------------------------------------------------------------------------- map_reduce


class Plan(BaseModel):
    """Split the question into independent sub-questions."""

    sub_questions: list[str] = Field(description="2-4 self-contained sub-questions")


class MapReduceState(TypedDict):
    question: str
    sub_questions: list[str]
    answers: Annotated[list[str], operator.add]  # reducer: parallel branches append
    final: str


class OneQuestion(TypedDict):
    q: str


def map_reduce(k: LgKit):
    planner = k.model("planner").bind_tools([Plan], tool_choice="Plan")
    worker, reducer = k.model("worker"), k.model("reducer")

    async def plan(state: MapReduceState) -> dict:
        resp = await planner.ainvoke(
            [
                SystemMessage("Decompose the question for parallel research."),
                HumanMessage(state["question"]),
            ]
        )
        subs = resp.tool_calls[0]["args"]["sub_questions"] if resp.tool_calls else []
        return {"sub_questions": subs[:4] or [state["question"]]}

    def fan_out(state: MapReduceState) -> list[Send]:
        return [Send("answer_one", {"q": q}) for q in state["sub_questions"]]

    async def answer_one(state: OneQuestion) -> dict:
        passages = await k.profile.retriever.search(state["q"], k=3)
        context = "\n".join(f"[{p.source}] {p.text[:600]}" for p in passages)
        resp = await worker.ainvoke(
            [
                SystemMessage(f"Answer briefly from this context, citing sources:\n{context}"),
                HumanMessage(state["q"]),
            ]
        )
        return {"answers": [f"Q: {state['q']}\nA: {k.text_of(resp)}"]}

    async def reduce(state: MapReduceState) -> dict:
        joined = "\n\n".join(state["answers"])
        resp = await reducer.ainvoke(
            [
                SystemMessage("Combine these partial answers into one answer with sources."),
                HumanMessage(f"{state['question']}\n\n{joined}"),
            ]
        )
        return {"final": k.text_of(resp)}

    builder = StateGraph(MapReduceState)
    builder.add_node("plan", plan)
    builder.add_node("answer_one", answer_one)
    builder.add_node("reduce", reduce)
    builder.add_edge(START, "plan")
    builder.add_conditional_edges("plan", fan_out, ["answer_one"])
    builder.add_edge("answer_one", "reduce")
    builder.add_edge("reduce", END)
    return builder.compile(checkpointer=k.checkpointer, name="map_reduce")


def map_reduce_input(message: str, user_id: str) -> dict:
    return {"question": message, "answers": []}


# ---------------------------------------------------------------------------- hitl


def hitl(k: LgKit):
    tools = [*k.tools(), *k.mcp_tools]
    model = k.model("agent").bind_tools(tools)

    async def agent(state: MessagesState) -> dict:
        return {"messages": [await model.ainvoke([SystemMessage(SYSTEM), *state["messages"]])]}

    async def review(state: MessagesState) -> Command[Literal["tools", "agent"]]:
        """Pause for a human before sensitive tools. interrupt() saves state via the checkpointer
        and surfaces the payload; the next request with resume={...} returns it here."""
        calls = state["messages"][-1].tool_calls
        sensitive = [c for c in calls if c["name"] in SENSITIVE]
        if not sensitive:
            return Command(goto="tools")
        decision = interrupt(
            {
                "question": "Approve these tool calls?",
                "tool_calls": [{"name": c["name"], "args": c["args"]} for c in sensitive],
            }
        )
        if isinstance(decision, dict) and decision.get("approve"):
            return Command(goto="tools")
        denied = [
            ToolMessage(
                content='{"status": "denied by reviewer"}', tool_call_id=c["id"], name=c["name"]
            )
            for c in calls
        ]
        return Command(goto="agent", update={"messages": denied})

    def route(state: MessagesState) -> str:
        return "review" if state["messages"][-1].tool_calls else END

    builder = StateGraph(MessagesState)
    builder.add_node("agent", agent)
    builder.add_node("review", review)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", route, ["review", END])
    builder.add_edge("tools", "agent")
    return builder.compile(checkpointer=k.checkpointer, name="hitl_graph")


# ---------------------------------------------------------------------------- registry


@dataclass(frozen=True)
class Pattern:
    info: PatternInfo
    build: Callable[[LgKit], Any]
    to_input: Callable[[str, str], dict] = lambda m, user_id: {"messages": [HumanMessage(m)]}
    uses_mcp: bool = True
    fork_as_node: str | None = None  # node to record a forked state as (see adapter.fork)


PATTERNS: dict[str, Pattern] = {
    p.info.name: p
    for p in [
        Pattern(
            PatternInfo(
                "react",
                "Prebuilt ReAct agent with a checkpointer and a long-term Store via model hooks.",
                (
                    "create_react_agent",
                    "pre_model_hook",
                    "post_model_hook",
                    "BaseStore / get_store()",
                    "checkpointer + thread_id",
                    "MultiServerMCPClient",
                    "AgentCoreMemorySaver/Store (bedrock)",
                ),
            ),
            react,
        ),
        Pattern(
            PatternInfo(
                "graph",
                "Hand-built StateGraph: a RAG node, then an agent <-> ToolNode loop.",
                (
                    "StateGraph",
                    "TypedDict state + add_messages reducer",
                    "ToolNode",
                    "tools_condition",
                    "conditional edges",
                    "AmazonKnowledgeBasesRetriever (bedrock)",
                ),
            ),
            graph,
        ),
        Pattern(
            PatternInfo(
                "middleware",
                "LangChain v1 create_agent with built-in and custom middleware.",
                (
                    "create_agent",
                    "PIIMiddleware",
                    "SummarizationMiddleware",
                    "ModelCallLimitMiddleware",
                    "ToolCallLimitMiddleware",
                    "ToolRetryMiddleware",
                    "@dynamic_prompt",
                    "@before_model",
                    "@wrap_tool_call",
                    "context_schema",
                ),
            ),
            middleware,
        ),
        Pattern(
            PatternInfo(
                "supervisor",
                "Supervisor routes with Command(goto) to worker agents compiled as subgraphs.",
                (
                    "Command(goto, update)",
                    "subgraphs",
                    "structured routing via forced tool call",
                    "MessagesState",
                ),
            ),
            supervisor,
            uses_mcp=False,
        ),
        Pattern(
            PatternInfo(
                "map_reduce",
                "Plan sub-questions, answer them in parallel with Send, reduce into one answer.",
                (
                    "Send",
                    "Annotated[list, operator.add] reducer",
                    "parallel branches",
                    "non-message state",
                ),
            ),
            map_reduce,
            to_input=map_reduce_input,
            uses_mcp=False,
        ),
        Pattern(
            PatternInfo(
                "hitl",
                "Pauses before sensitive tools (run_cli, run_code); resume with {'approve': true}.",
                (
                    "interrupt()",
                    "Command(resume=...)",
                    "checkpointer-backed pause",
                    "Command(goto) from a node",
                ),
            ),
            hitl,
        ),
        Pattern(
            PatternInfo(
                "memory",
                "Bedrock state suite: conversation via checkpointer, long-term via store, compaction, "
                "trimming, node cache, retries, crash recovery, time travel and fork.",
                (
                    "checkpointer: AgentCoreMemorySaver / DynamoDBSaver(+S3) / AsyncValkeySaver",
                    "AgentCoreMemoryStore (long-term)",
                    "RemoveMessage + rolling summary (compaction)",
                    "trim_messages (context view)",
                    "CachePolicy + ValkeyCache (node cache)",
                    "RetryPolicy",
                    "durability modes",
                    "recover: astream(None)",
                    "aget_state_history (time travel)",
                    "aupdate_state (fork)",
                ),
            ),
            memory,
            to_input=memory_input,
            uses_mcp=False,
            fork_as_node="remember",
        ),
    ]
}
