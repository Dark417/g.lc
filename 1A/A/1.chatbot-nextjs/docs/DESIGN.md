# Design: 1.chatbot-nextjs

## Problem

Learn the smallest complete shape of an LLM chat app: browser → HTTP API → agent runtime → model, with server-side conversation memory. Everything after this project adds capabilities to this skeleton, so the skeleton must be deployable from day one.

## Who it's for

Me, as a tutorial. Secondary: a template to fork for real projects.

## Success metric

- `docker compose up` gives a working multi-turn chat in under 5 minutes with only an API key.
- `kubectl apply -k deploy/k8s` works once an image registry is filled in.
- Backend tests pass with no API key.

## Non-goals

- Streaming (project 2).
- Tools, RAG, MCP (project 2).
- Auth, rate limiting, persistence across restarts.
- A pretty UI.

## Approach

```
Next.js (browser)  --POST /api/v1/chat-->  FastAPI  -->  AdkChatService  -->  ADK Runner  -->  Gemini
                                                              |
                                                     InMemorySessionService
```

- **Backend** is layered: `api/` (HTTP only) → `services/` (use case) → `agent/` (ADK definition). The API depends on a `ChatService` Protocol, so tests inject a fake and never touch ADK or the network.
- **Session** is created server-side and its id returned. The client stores it in component state and sends it back. This is the minimum "memory": ADK's session service replays history into the model each turn.
- **Frontend** has exactly one module that knows the backend (`src/lib/api.ts`) and one component.
- **Deploy**: two images, two Deployments, one Ingress with `/api` → backend. Config via ConfigMap, key via Secret.

## Build-vs-buy

| Choice | Why |
|---|---|
| Google ADK over raw `google-genai` | The Runner/Session/Event model is the same one used for tools, MCP, evals in project 2. Learning it now pays off. |
| FastAPI over ADK's built-in `get_fast_api_app` | We want to own the HTTP surface (auth, schemas, versioning) and keep ADK behind a service boundary. ADK's server is great for `adk web` debugging, not as your product API. |
| In-memory sessions | Simplest thing that demonstrates memory. Swapping is one constructor argument (`DatabaseSessionService`). |
| Next.js App Router, no state library | One component, one fetch. Anything more is noise. |

## MVP ladder

- **MVP0** (this project): text in, text out, multi-turn, deployable.
- MVP1 (project 2): tools + DB + RAG + MCP.
- MVP2 (project 2): streaming + trace panel + evals.

## Tradeoffs and failure modes

- Browser calls the backend directly (CORS). In prod the Ingress makes it same-origin. Alternative: proxy through Next.js route handlers, which hides the backend but adds a hop.
- `replicas: 1` on the backend because in-memory sessions are per-pod. Sticky sessions are a hack; a DB session service is the fix.
- No request timeout on the model call. Add one before exposing publicly.
