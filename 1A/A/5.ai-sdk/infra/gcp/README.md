# GCP: the `vertex` branch

Each step is optional. Unset IDs fall back to the local implementation.

## 0. Credentials and models

```bash
gcloud auth application-default login
gcloud services enable aiplatform.googleapis.com modelarmor.googleapis.com cloudtrace.googleapis.com storage.googleapis.com
```

- In `backend/.env`: `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION=us-central1`.
- Claude on Vertex: enable the Claude model in **Model Garden**. `VERTEX_CLAUDE_REGION=global` works for current models.
- Runtime identity roles:
  - `roles/aiplatform.user`
  - `roles/modelarmor.user`
  - `roles/cloudtrace.agent`
  - `roles/storage.objectViewer` (RAG import)

## 1. Agent Engine (Sessions + Memory Bank) and the RAG Engine corpus

```bash
gcloud storage buckets create gs://<bucket> --location=us-central1
cd backend
uv run python ../infra/gcp/setup_vertex.py --project <project> --bucket <bucket>
# -> AGENT_ENGINE_ID=...  VERTEX_RAG_CORPUS=projects/.../ragCorpora/...
```

- With `AGENT_ENGINE_ID` set:
  - ADK uses `VertexAiSessionService` and `VertexAiMemoryBankService`;
  - `remember`/`recall` use Memory Bank.
- With `VERTEX_RAG_CORPUS` set:
  - `search_docs` uses RAG Engine;
  - the ADK `single` agent also gets the native `VertexAiRagRetrieval` tool (Gemini only).

## 2. Model Armor

```bash
gcloud model-armor templates create ai-sdk --location=us-central1 \
  --pi-and-jailbreak-filter-settings-enforcement=enabled \
  --pi-and-jailbreak-filter-settings-confidence-level=medium-and-above \
  --malicious-uri-filter-settings-enforcement=enabled \
  --rai-settings-filters='[{"filterType":"HATE_SPEECH","confidenceLevel":"MEDIUM_AND_ABOVE"}]'
```

- The filter flags evolve; check `gcloud model-armor templates create --help`. The console is the alternative.
- Set `MODEL_ARMOR_TEMPLATE=projects/<project>/locations/us-central1/templates/ai-sdk`.

## 3. Hosting

- **Whole service on Cloud Run** (same image as k8s):

```bash
gcloud run deploy ai-sdk --source backend --region us-central1 --memory 3Gi \
  --set-env-vars OTEL_EXPORTER=gcp,GOOGLE_CLOUD_PROJECT=<project>,AGENT_ENGINE_ID=<id> \
  --no-allow-unauthenticated
```

- The session lock is process-local, so keep `--max-instances=1`. Or move the lock to Memorystore first (see `docs/design/04`).
- **ADK agent on Agent Engine** (managed ADK hosting, one agent):

```bash
cd backend
uv run python -m app.runtimes.agent_engine_app --local "What is 17% of 2340?"   # try AdkApp locally
uv run python -m app.runtimes.agent_engine_app --staging-bucket gs://<bucket>    # deploy
```

## 4. Cache server (Memorystore)

```bash
gcloud memorystore instances create ai-sdk --location=us-central1 --engine=valkey \
  --shard-count=1 --node-type=shared-core-nano   # flags vary by version; the console works too
```

- Set `REDIS_URL=redis://<private-ip>:6379/0`. Cloud Run reaches it through Direct VPC egress.
- It gives every framework the distributed session lock and registry, the DIY caches, and the Claude `RedisSessionStore`.
- Vertex-native state stays in Agent Engine: Sessions, Memory Bank, and resumable ADK invocations (`adk:memory`).
- Gemini context caching (`ContextCacheConfig`) is a *server-side* prompt cache. It needs no cache server.

## 5. Observability and evals

- `OTEL_EXPORTER=gcp` sends spans to Cloud Trace from every framework.
- `uv run python -m app.evals.run --targets adk:single:vertex,langgraph:react:vertex --vertex` scores outputs with the Gen AI evaluation service.
  - Pointwise question-answering quality, groundedness, and safety.
  - Results are logged to a Vertex AI Experiment.
