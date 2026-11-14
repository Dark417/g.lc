# LangGraph

LangGraph is LangChain's low-level orchestration framework for stateful agents, modelled as graphs. LangChain v1's create_agent is built on it.

## Graphs

- StateGraph(State) defines a typed state (TypedDict or Pydantic). Nodes are functions that read state and return partial updates.
- Reducers decide how updates merge, e.g. Annotated[list, add_messages] appends messages and Annotated[list, operator.add] concatenates.
- Edges connect nodes; add_conditional_edges routes on a function's return value. START and END mark entry and exit.
- Cycles are allowed, which is how an agent loops between a model node and a tool node.
- Subgraphs: a compiled graph can be a node in another graph, which is how multi-agent systems are composed.

## Prebuilt pieces

- ToolNode executes the tool calls in the last AI message; tools_condition routes to it when there are tool calls.
- create_react_agent (langgraph.prebuilt) builds the model ⇄ tools loop in one call.
- langchain.agents.create_agent is the v1 agent, with middleware: hooks before/after the model, around tool calls, and dynamic prompts. Built-in middleware includes summarization, PII redaction, human-in-the-loop, model/tool call limits, model fallback, and tool retry.

## Persistence

- A checkpointer saves the full graph state after every step, keyed by thread_id in the config. That gives multi-turn memory, time travel, and fault tolerance.
- Checkpointers: InMemorySaver, SQLite, Postgres, and cloud ones such as langgraph-checkpoint-aws (AgentCoreMemorySaver, BedrockSessionSaver, DynamoDBSaver, ValkeySaver).
- A Store (BaseStore) holds long-term memory across threads, organised by namespace tuples, with optional semantic search. Tools reach it with get_store().

## Control flow

- interrupt(value) pauses a node and surfaces value to the caller; the run resumes with Command(resume=answer) on the same thread. This is human-in-the-loop.
- Command(goto=node, update={...}) lets a node both update state and choose the next node: handoffs between agents.
- Send(node, state) creates dynamic parallel branches (map-reduce), one per item.

## Deployment and observability

- LangGraph Platform / LangSmith deployments host graphs; Vertex AI Agent Engine offers a LanggraphAgent template.
- Tracing: LangSmith natively, or OpenTelemetry via OpenInference's LangChain instrumentor.
