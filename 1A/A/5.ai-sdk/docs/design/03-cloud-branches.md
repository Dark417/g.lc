# 03 · Cloud branches: raw, bedrock, vertex

## What a provider branch swaps

| Capability | `raw` (self-managed) | `bedrock` (AWS-managed) | `vertex` (GCP-managed) |
|---|---|---|---|
| Model hosting | Anthropic API, Gemini API | Bedrock Converse (any model); Claude in Bedrock (Messages API, "Mantle") | Vertex Gemini; Claude on Vertex (Model Garden) |
| Short-term state (the conversation) | SQLite / files in `DATA_DIR` | AgentCore Memory **events** | Agent Engine **Sessions** |
| Long-term memory (facts across sessions) | SQLite keyword store | AgentCore Memory **strategies** (semantic, summary, user preference) | Agent Engine **Memory Bank** |
| RAG | Hashing-vector store (ILLUSTRATION) | Bedrock **Knowledge Bases** | Vertex **RAG Engine** |
| Browser | local Playwright Chromium | AgentCore **Browser** (managed Chromium, CDP) | local Playwright (no managed browser) |
| Code sandbox | none | AgentCore **Code Interpreter** | none (see gaps) |
| Guardrails | regex | Bedrock **Guardrails** (`ApplyGuardrail`) | **Model Armor** |
| MCP hosting | stdio subprocess | AgentCore **Gateway** (doc + script) | Cloud Run streamable HTTP (doc) |
| Agent hosting | Docker / k8s (`deploy/`) | AgentCore **Runtime** (`BedrockAgentCoreApp`) | Agent Engine (`AdkApp`) / Cloud Run |
| Tracing | OTLP → Jaeger | ADOT → CloudWatch / X-Ray | Cloud Trace |
| Evals | our harness | AgentCore **Evaluations** | Gen AI **evaluation service** |

## Configuration (env vars, read only in `app/config.py`)

### raw

```bash
ANTHROPIC_API_KEY=...            # Claude API (adapters: all four)
GOOGLE_API_KEY=...               # Gemini API (adk, langgraph, strands)
RAW_VENDOR=anthropic             # anthropic | gemini: which one the non-Claude frameworks use by default
ANTHROPIC_MODEL=claude-opus-5
GEMINI_MODEL=gemini-2.5-flash
```

### bedrock

```bash
AWS_REGION=us-east-1             # credentials: the default AWS chain (profile, SSO, role, env)
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-5-20250929-v1:0   # Converse id/inference profile (adk, langgraph, strands)
BEDROCK_ANTHROPIC_MODEL=anthropic.claude-opus-5                  # Claude in Bedrock Messages API (claude/messages_api)
BEDROCK_CLAUDE_CODE_MODEL=                                       # optional ANTHROPIC_MODEL for the Agent SDK on Bedrock
AGENTCORE_MEMORY_ID=...          # from infra/aws/setup_agentcore.py
BEDROCK_KB_ID=...                # Knowledge Base id (optional; falls back to local RAG)
BEDROCK_GUARDRAIL_ID=... BEDROCK_GUARDRAIL_VERSION=DRAFT          # optional
AGENTCORE_BROWSER=true           # browse via AgentCore Browser instead of local Chromium
AGENTCORE_CODE_INTERPRETER=true  # enable run_code
```

### vertex

```bash
GOOGLE_CLOUD_PROJECT=my-proj  GOOGLE_CLOUD_LOCATION=us-central1   # credentials: ADC
VERTEX_VENDOR=gemini              # gemini | anthropic
VERTEX_GEMINI_MODEL=gemini-2.5-flash
VERTEX_CLAUDE_MODEL=claude-opus-5  VERTEX_CLAUDE_REGION=global
AGENT_ENGINE_ID=...               # Sessions + Memory Bank (infra/gcp/setup_vertex.py)
VERTEX_RAG_CORPUS=projects/.../ragCorpora/...                     # optional; falls back to local RAG
MODEL_ARMOR_TEMPLATE=projects/.../locations/.../templates/...     # optional
```

- A provider is **available** when its required settings are present.
  - `GET /v1/catalog` shows availability and lists the missing variables.
- Optional managed services (KB, Memory, Guardrail, Browser) **degrade to the local implementation** when unset.
  - This lets you adopt AWS or GCP one service at a time.

## How each framework meets each cloud

### Bedrock

- **Strands** is the native citizen.
  - `BedrockModel` speaks Converse.
  - `AgentCoreMemorySessionManager` plugs AgentCore Memory in as the session store.
  - `strands_tools.browser` / `code_interpreter` / `retrieve` wrap AgentCore Browser, Code Interpreter, and Bedrock KB.
  - Guardrails are a model config field (`guardrail_id`).
- **LangGraph** uses `langchain-aws` and `langgraph-checkpoint-aws`:
  - `ChatBedrockConverse`;
  - `AgentCoreMemorySaver` (checkpoints as AgentCore events);
  - `AgentCoreMemoryStore` (long-term);
  - `AmazonKnowledgeBasesRetriever`.
- **ADK** has no AWS-native services.
  - The model goes through `LiteLlm("bedrock/converse/...")`.
  - We implement `BaseMemoryService` over AgentCore Memory: `AgentCoreMemoryService`, about 60 lines.
  - This is the lesson: ADK's service interfaces are the extension point.
- **Claude Agent SDK**: `CLAUDE_CODE_USE_BEDROCK=1`. The CLI calls Bedrock with your AWS credentials.
  - Messages API: `AsyncAnthropicBedrockMantle`.
- **Hosting**:
  - `app/runtimes/agentcore_app.py` wraps `RunService` in `BedrockAgentCoreApp`.
  - All four frameworks become one AgentCore Runtime agent. The `/invocations` payload is our `RunRequest`.

### Vertex

- **ADK** is the native citizen:
  - `VertexAiSessionService` and `VertexAiMemoryBankService` (both on Agent Engine);
  - the `VertexAiRagRetrieval` tool;
  - `Claude` model class for Claude on Vertex;
  - `AdkApp` for Agent Engine hosting.
- **LangGraph** uses `langchain-google-vertexai`:
  - `ChatVertexAI`;
  - `ChatAnthropicVertex`;
  - hosting through the Agent Engine `LanggraphAgent` template.
- **Strands**: `GeminiModel` with a Vertex-mode `genai.Client`. No GCP session manager ships (gap).
- **Claude Agent SDK**: `CLAUDE_CODE_USE_VERTEX=1`, `CLOUD_ML_REGION`, `ANTHROPIC_VERTEX_PROJECT_ID`.
  - Messages API: `AsyncAnthropicVertex`.
- **Hosting**:
  - `app/runtimes/agent_engine_app.py` deploys the ADK `single` agent with `AdkApp`.
  - Cloud Run runs the whole FastAPI service, same image as k8s.

## Documented gaps (and why we don't paper over them)

| Gap | Why | Production path |
|---|---|---|
| Vertex code sandbox | Agent Engine Code Execution is in preview and its client surface still moves | Use ADK's `BuiltInCodeExecutor` (Gemini code execution) inside ADK, or a Cloud Run sandbox job |
| Vertex managed browser | GCP has no AgentCore Browser equivalent | Playwright in Cloud Run; or a remote browser vendor over CDP, same code path as AgentCore |
| LangGraph / Strands managed sessions on GCP | No first-party saver or repository | Agent Engine (LangGraph template) or a custom Strands `SessionRepository` on Firestore |
| Claude Agent SDK managed sessions | The CLI keeps sessions on local disk | Sticky sessions, or sync `~/.claude/projects` to S3/GCS between turns |
| ADK on AWS-native sessions | ADK ships no DynamoDB or AgentCore `SessionService` | `DatabaseSessionService` on RDS/Aurora (works today); a custom `BaseSessionService` if you need AgentCore |

## Least-privilege IAM (what the runtime identity needs)

- **AWS**:
  - `bedrock:InvokeModel*`, `bedrock:Converse*`;
  - `bedrock-agentcore:CreateEvent|ListEvents|RetrieveMemoryRecords|GetMemory`;
  - `bedrock-agentcore:StartBrowserSession|...` and `StartCodeInterpreterSession|InvokeCodeInterpreter|...`;
  - `bedrock:Retrieve` on the KB;
  - `bedrock:ApplyGuardrail`.
  - See `infra/aws/iam-policy.json`.
- **GCP**:
  - `roles/aiplatform.user` (models, RAG Engine, Agent Engine sessions and memories);
  - `roles/modelarmor.user`;
  - `roles/cloudtrace.agent`.
