# Design: 1.chatbot-angular

Delta over `../../1.chatbot-nextjs/docs/DESIGN.md`. Everything not mentioned here is the same.

## Problem

Same minimum chatbot, but with Angular, because that is the frontend for projects 2 and 3. This project exists so the "add capabilities" step in project 2 is not mixed with "learn a new frontend".

## Approach

```
Angular (browser) --POST /api/v1/chat--> nginx (same pod/container) --proxy /api--> FastAPI --> ADK Runner --> Gemini
```

- Backend: unchanged from project 1. Copied, not shared, so each project stays independently deployable and readable on its own.
- Frontend: Angular 21 standalone components, signals, `HttpClient` with `withFetch()`. No router, no state library.
- Serving: an **nginx** container serves the static bundle and reverse-proxies `/api/` to the backend. The browser never learns the backend's address. This is the standard SPA deployment shape and it removes the build-time URL baking Next.js needed.

## Decisions

| Choice | Alternative | Why this one |
|---|---|---|
| nginx proxy in the frontend image | Ingress path routing (`/api` → backend) like project 1 | Works identically in compose, k8s, and any static host with a proxy. One place to reason about routing. Project 1 shows the other option so you have seen both. |
| `environment.prod.ts` `apiUrl: ''` | runtime `config.json` fetch | Same-origin makes the URL a non-issue. Runtime config is the right answer once there are many envs; it is one extra `APP_INITIALIZER`. |
| Signals over RxJS state | `BehaviorSubject` | Current Angular idiom, less boilerplate, plays well with `@if`/`@for`. |
| vitest (Angular's default runner now) | Karma/Jasmine | Angular 20+ default. |

## MVP ladder

- **MVP0** (this project): chat works in Angular, deployable.
- MVP1/2: see `../../2.angular-full`.

## Failure modes

- `proxy_pass ${BACKEND_URL}` with a trailing path changes URL rewriting semantics; keep it a bare origin.
- `withFetch()` means no upload progress events; irrelevant here, but know it.
- Component style budget (`anyComponentStyle` 4kB warn) is the default; keep component CSS small or move to `styles.css`.
