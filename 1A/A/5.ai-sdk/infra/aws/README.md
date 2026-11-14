# AWS: the `bedrock` branch

Each step is optional. Unset IDs fall back to the local implementation, so you can adopt one service at a time.

## 0. Credentials and models

- Use the standard AWS chain (`aws sso login`, a profile, or an instance/IRSA role).
- In `backend/.env`:
  - `AWS_REGION=us-east-1`
  - `BEDROCK_MODEL_ID=<a Converse model id or inference profile>`
- In the Bedrock console → **Model access**, enable the models you use:
  - the Converse model, e.g. a Claude inference profile `us.anthropic.claude-…`;
  - `anthropic.claude-opus-5` for the Messages API pattern.
- Attach `iam-policy.json` to the runtime identity. Scope `Resource` down to your ARNs for production.
  - The Messages API pattern goes through Claude in Amazon Bedrock (`AnthropicBedrockMantle`). Check that page of the Bedrock docs for any extra permission it needs in your account.

## 1. AgentCore Memory

Used by:

- the `remember`/`recall` tools;
- ADK `AgentCoreMemoryService`;
- LangGraph `AgentCoreMemorySaver`/`Store`;
- Strands `AgentCoreMemorySessionManager`.

```bash
cd backend
uv run python ../infra/aws/setup_agentcore.py --region us-east-1
# -> AGENTCORE_MEMORY_ID=...   put it in backend/.env
```

## 2. Bedrock Knowledge Base

Used by `search_docs`, and natively by the LangGraph `graph` pattern.

```bash
aws s3 mb s3://<bucket>
aws s3 sync backend/data/corpus s3://<bucket>/corpus/
```

- In the console: **Bedrock → Knowledge Bases → Create**.
  - Data source: S3 `s3://<bucket>/corpus/`.
  - Embeddings: Titan Text Embeddings v2.
  - Vector store: *Quick create* (S3 Vectors or OpenSearch Serverless).
- Sync the data source, then set `BEDROCK_KB_ID`.

```bash
aws bedrock-agent start-ingestion-job --knowledge-base-id <kb> --data-source-id <ds>   # after corpus edits
```

## 3. Guardrail

- In the console: **Bedrock → Guardrails → Create**. Add, for example:
  - a denied topic;
  - PII: email = *mask*, AWS access key = *block*.
- Set `BEDROCK_GUARDRAIL_ID` and `BEDROCK_GUARDRAIL_VERSION` (`DRAFT` or a version number).
- Where it applies:
  - `RunService` calls `ApplyGuardrail` on input and output for every framework.
  - The Strands `BedrockModel` also attaches it natively to each model call.

## 4. AgentCore Browser and Code Interpreter

```bash
AGENTCORE_BROWSER=true            # `browse` -> managed Chromium over CDP (Playwright connect_over_cdp)
AGENTCORE_CODE_INTERPRETER=true   # enables `run_code` (sandboxed Python)
```

- Both use the default system resources: `aws.browser.v1` and `aws.codeinterpreter.v1`.
- No setup is needed beyond IAM.

## 5. Host on AgentCore Runtime

`app/runtimes/agentcore_app.py` wraps `RunService` in `BedrockAgentCoreApp`. All four frameworks become one AgentCore agent.

```bash
pip install bedrock-agentcore-starter-toolkit
cd backend
agentcore configure --entrypoint app/runtimes/agentcore_app.py --name ai_sdk
agentcore launch                    # builds the container (CodeBuild), pushes to ECR, creates the runtime
agentcore invoke '{"framework": "strands", "pattern": "single", "message": "What is 17% of 2340?"}'
```

- Alternative: build `backend/Dockerfile`, push to ECR, and create the runtime with `CMD ["python", "-m", "app.runtimes.agentcore_app"]`, port 8080.
- The CLI surface of the starter toolkit changes quickly. Check `agentcore --help` against the [AgentCore docs](https://docs.aws.amazon.com/bedrock-agentcore/).

## 6. State: checkpointers and the cache server

`langgraph:memory` (and every LangGraph pattern) on bedrock picks its checkpointer with `LANGGRAPH_CHECKPOINTER`:

| Value | Needs | Trade-off |
|---|---|---|
| `agentcore` | `AGENTCORE_MEMORY_ID` | checkpoints become AgentCore Memory events; one service for short and long term |
| `dynamodb` | `uv run python ../infra/aws/setup_state.py` (table `PK`/`SK`, TTL `ttl`); optional `S3_CHECKPOINT_BUCKET` | durable, serverless, pay per request; big states offloaded to S3 |
| `valkey` | an ElastiCache for Valkey endpoint in `VALKEY_URL` (or `REDIS_URL`) | fastest; in-memory, so use MemoryDB or snapshots if checkpoints must survive node loss |

```bash
aws elasticache create-serverless-cache --serverless-cache-name ai-sdk --engine valkey --region us-east-1
# endpoint -> REDIS_URL=rediss://<endpoint>:6379/0   (serverless caches require TLS)
```

- The same `REDIS_URL` also gives every framework the distributed session lock and registry.
- It also backs the DIY loop's checkpoint and LLM caches, and LangGraph's `ValkeyCache` node cache.
- Allow the runtime to reach it: same VPC, security group on port 6379.

## 7. Observability

- Point `OTEL_EXPORTER_OTLP_ENDPOINT` at an ADOT collector (`awsxray` + `awsemf` exporters).
- Or enable **CloudWatch Transaction Search**. AgentCore Runtime agents then appear in the GenAI Observability dashboard.
- AgentCore Evaluations scores those traces (correctness, helpfulness, tool selection) online or on demand. Configure evaluators in the console.
