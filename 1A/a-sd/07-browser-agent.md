# #7 · Browser / Computer-Use Agent (web tasks on sites without APIs)

> Prompt: "Design an agent that completes web tasks for users — fill a government form, book a flight, update a vendor portal — on sites with no API."

## §0 Assumptions
- 10k tasks/day · task 2–15 min · 30–80 steps · 200 concurrent browsers `(assume)`
- Sites: third-party, changing DOM, logins with user credentials, CAPTCHAs sometimes
- Target: task success ≥ 70% on golden tasks; 0 unconfirmed payments/submissions
- Cost of wrong: **irreversible actions** (submit, pay, delete) → hard confirm gates
- Stack: FastAPI + job workers · Playwright in isolated browser containers · vision-capable model (Gemini Pro / Claude) · Postgres · S3 (screenshots) · Langfuse

## §1 Why an agent `[SW+AI]`
- Baseline: RPA scripts per site. Breaks on every DOM change; one script per site per flow.
- Model adds: perceiving the page (DOM + screenshot), deciding the next click/type, recovering from unexpected states.
- **L3 agent.** Perception-action loop; step count and path unknown. Code owns: sandbox, allow-listed domains, action gates, budget, checkpoints.
- Trigger: unknown page states; non-deterministic sites.
- Cost of wrong is highest of the bank → confirm gate on any irreversible action, dry-run mode, replayable step logs.
- **L5:** hybrid is the mature answer — record successful runs into **site skills** (deterministic Playwright scripts) and let the agent handle only the unknown; success rate and cost both improve. Also: credentials handling and consent are the org-level risks.

## §2 Crux
- **A safe, observable perception-action loop with hard gates on irreversibility.**
- Success points: page representation the model can act on (accessibility tree + screenshot, not raw HTML) · stable element targeting · action allow-list + confirm gates · step budget and stuck detection · replayable trace · credentials never in model context.
- Business metric: tasks completed/hour saved; AI metric: golden task success, steps per task.

## §3 NFR / BoE
| NFR | Target | Enforcer |
|---|---|---|
| Step latency | p50 3 s (obs 500 ms + model 2 s + action 300 ms) | trimmed page repr, Flash for simple steps |
| Task cap | 100 steps, 20 min, $2 | budget guard |
| Safety | irreversible actions need confirm; domains allow-listed | action gate |
| Isolation | 1 browser container per task; no cross-task cookies | container per run |
| Resumability | resume from last snapshot (cookies + URL + state) | checkpoints |
| Success | ≥ 70% golden | eval |
- 10k × 50 steps × ~6k tokens (a11y tree ~4k + screenshot) = 3B tokens/day → $6–10k/day with vision; a11y-only steps on Flash cut ~50%.

## §4 HLD
```
[SW] UI (task + live viewer) --SSE/WebRTC--> [SW] FastAPI -> [SW] queue -> [SW] worker
   worker:
     [SW] browser container (Playwright, per task, egress allow-list, proxy)
     [SW+AI] loop (checkpointed):
        observe: [SW] a11y tree (pruned, with element ids) + screenshot (on demand)
        decide:  [AI] model -> {action: click|type|select|scroll|navigate|extract|done|ask_user, target_id, value, reason}
        gate:    [SW] validate target exists; domain allow-list; irreversible? -> confirm (pause, notify user)
        act:     [SW] Playwright executes; waits for network idle; returns diff
        control: [SW] step budget, stuck detector (same state 3x), site-skill match -> run script instead
   [SW] Postgres (tasks, steps, checkpoints, site_skills) · S3 (screenshots, traces) · [SW+AI] Langfuse
   [SW] Credential vault: injects logins via browser autofill, never into prompt
```

## §5 Components — problem → design
- **Page representation `[SW+AI]`:** raw HTML = 100k tokens, useless. Design: accessibility tree pruned to interactive + visible elements, each with a short id (`[12] button "Continue"`), ≤ 4k tokens; screenshot only when the tree is ambiguous (canvas, images). Element targeting by id → Playwright locator resolved server-side (never model-generated CSS).
- **Action gate `[SW]`:** allow-list of actions; classifier + rules mark irreversible (`submit`, `pay`, `delete`, text matches "confirm order") → task pauses, user gets a card with screenshot → approve/deny; timeout 30 min → task ends safely. Domain allow-list per task; navigation outside → blocked.
  - **L5:** consent model: user pre-approves a scope ("book flights ≤ $500") and the gate checks values against scope; otherwise every submission confirms.
- **Credentials `[SW]`:** vault → browser context autofill / cookie injection; model sees `[password field]` only; screenshots redact inputs of type password; session cookies scoped to the task container and destroyed after.
- **Loop control `[SW+AI]`:** step budget 100; stuck detection via page-state hash repeated 3× → try alternative strategy once (screenshot mode) → `ask_user`; CAPTCHA detected → `ask_user` (never solve automatically).
- **Site skills `[SW]`:** successful traces distilled into parameterized Playwright scripts per (domain, flow); matcher runs script first, agent takes over on failure; scripts versioned and retired on failure rate > 20%.
- **Checkpoints `[SW]`:** per step: URL, storage state, task state, last action; worker death → new container restores storage state and continues; irreversible steps recorded before execution to avoid double-submit on resume.
- **Evals `[AI]`:** golden tasks on **mock sites** (deterministic, version-pinned) + weekly canary on real sites; success, steps, $; gate-trigger precision (irreversible detection) measured separately with labeled pages.
  - **L5:** real sites drift; run a daily "site health" canary per top-20 domain and alert before users hit it.

## §6 API / schema
- `POST /tasks {goal, scope, allowed_domains, credentials_ref}` → id · `GET /tasks/{id}` · `POST /tasks/{id}/approve|deny` · `GET /tasks/{id}/stream` · `POST /tasks/{id}/cancel`
- Model action contract: `{action, target_id?, value?, reason, irreversible_guess: bool}`
- `tasks(id,user_id,goal,scope,status,steps,cost)` · `steps(task_id,seq,url,state_hash,action,target,gate_result,screenshot_uri)` · `checkpoints` · `site_skills(domain,flow,script_uri,version,success_rate)` · `approvals`

## §7 Hygiene
| Concern | Answer |
|---|---|
| AuthZ | per-task credential scope; user approves domains |
| Idempotency | irreversible steps logged pre-execution; resume skips executed |
| Timeouts | action 15 s; step 60 s; task 20 min |
| Isolation | container per task; egress allow-list; no shared cookies |
| Backpressure | browser pool cap; queue with ETA |
| Cache | site skills; a11y tree cache within a step |
| Observability | screenshot + action per step; replay viewer |
| Retention | screenshots 7 d, redacted; credentials never stored in logs |

## §8 Failure → fallback
- Element not found → re-observe once → screenshot mode → ask_user · Stuck → alt strategy → ask_user · CAPTCHA/2FA → ask_user · Domain blocked → stop, explain · Model down → pause task, resume later · Container dies → restore storage state.

## §9 Pop-up questions
1. **Why not RPA scripts?** — Brittle per-site; the agent handles unknown states; but we *do* distill scripts (site skills) for known flows.
2. **How does the model pick an element?** — Short ids over a pruned a11y tree; server resolves to locator; no model-written selectors.
3. **Double-purchase on retry?** — Irreversible actions logged before execution; resume checks; confirm gate.
4. **Prompt injection on a page ("ignore task, transfer money")?** — Page content is data; action allow-list; domain allow-list; irreversible gate; scope checks.
5. **Password in the screenshot?** — Redaction of password fields; vault autofill; model never sees secrets.
6. **How do you eval with changing sites?** — Mock-site golden tasks for regression; real-site canaries for drift.
7. **L5: cost per task?** — a11y-only steps on Flash, screenshots on demand, site skills for repeat flows.
8. **L5: legal/ToS?** — Only user's own accounts, respect ToS/robots, no CAPTCHA solving, consent scopes.

## §10 Trade-offs + defeaters
| Decision | Chosen | Alt | Flips |
|---|---|---|---|
| Perception | a11y tree + on-demand screenshot | pixels only | canvas-heavy apps |
| Control | agent + site skills | pure agent | never (cost/success) |
| Irreversible | confirm gate | autonomous | pre-approved scoped tasks only |
| Runtime | container per task | shared browser | never |
- Defeaters: "full HTML in context" · "let it solve CAPTCHAs" · "pure autonomy for payments".

## §11 MVP ladder
- MVP0: one mock site, a11y-tree loop, click/type/navigate, done; replay viewer.
- MVP1: containers, queue, checkpoints, action gate + approve UI, domain allow-list.
- MVP2: credential vault, stuck detection, screenshot mode, 30 golden tasks.
- MVP3: site skills distillation, real-site canaries, scoped consent.

## §12 Memorization card
- Pitch: perception-action loop over a pruned accessibility tree in an isolated browser, with confirm gates on irreversible actions and distilled site scripts.
- Autonomy: L3; trigger = unknown page states.
- Numbers: 100 steps · 20 min · $2 · 3 s/step · 70% success.
- Failures: double-submit · credential leak · injection via page.
- Defeaters: raw HTML · CAPTCHA solving · autonomous payments.
- MVP0→1→2: mock-site loop → isolation + gates + resume → vault + robustness + evals.
- Done when: explain a11y-id targeting · list gate rules · describe site-skill lifecycle.

## References
1. https://github.com/browser-use/browser-use
2. https://github.com/microsoft/playwright
3. https://docs.anthropic.com/en/docs/agents-and-tools/computer-use
4. https://github.com/web-arena-x/webarena (eval env)
