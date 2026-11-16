# #4 · Coding Agent (GitHub issue → tested PR)

> Prompt: "Design an agent that takes a GitHub issue, makes the change in a repo, runs tests, and opens a PR for review."

## §0 Assumptions
- 500 engineers · 200 issues/day assigned to the agent · runs are 5–40 min · 30 concurrent `(assume)`
- Repos: 50–500k LOC, mono + multi; CI exists; tests take 1–15 min
- Target: ≥ 40% of runs produce a mergeable PR; 0 secret leaks; 0 pushes to protected branches
- Cost ceiling: $5/run avg
- Stack: orchestrator (FastAPI + LangGraph or ADK) · sandbox per run (Firecracker/gVisor, e.g. E2B or self-hosted) · Claude/Gemini coding model · Postgres · object store · Langfuse

## §1 Why an agent `[SW+AI]`
- Baseline: humans; codemods for mechanical changes. Breaks: long tail of small tasks, context switching.
- Model adds: understanding the issue, locating code, writing changes, interpreting test failures.
- **L3 agent.** Tool sequence (`search → read → edit → run tests → read failure → edit …`) is unknown until execution feedback arrives. Code decides budget, sandbox, verification gates; model decides steps.
- Not L4: one agent with a planner *prompt*, not a planner *agent*; add a reviewer agent only when measured false-positive PR rate justifies it.
- Cost of wrong: low if PR is reviewed and can't self-merge; high if it can push/deploy → hard gates.
- **L5:** verification-by-execution is the moat; make "run tests" mandatory before PR and track *why* runs fail (no repro, wrong file, flaky CI) to steer investment.

## §2 Crux
- **Turn an open-ended edit loop into a bounded, verifiable job**: sandbox isolation, budget caps, execution feedback, PR as the only side-effect.
- Success points: repo context retrieval (right files fast) · reliable edit tool (diff apply, not full rewrites) · test loop · safe sandbox (no secrets, egress-limited) · resumable runs · PR quality signals.
- Business metric: merged-PR rate × engineer hours saved; AI metric: pass@1 on internal golden tasks (SWE-bench-style).

## §3 NFR / BoE
| NFR | Target | Enforcer |
|---|---|---|
| Run time | p50 12 min, hard cap 60 min | job timeout |
| Budget | ≤ 300k tokens / $5 / 60 tool calls per run | budget guard in loop |
| Isolation | no secrets in sandbox; egress allow-list (package registries, GitHub) | sandbox network policy |
| Side-effects | only `open_pr` to a branch `agent/*`; never merge | GitHub App scopes |
| Resumability | worker death → resume from last checkpoint ≤ 1 iteration lost | checkpointer |
| Quality | mergeable ≥ 40%; golden pass@1 ≥ 35% | offline eval |
- 200 runs × 300k tokens = 60M tokens/day ≈ $600–1,000/day. Sandboxes: 30 concurrent × 2 vCPU/4 GB.

## §4 HLD
```
[SW] GitHub webhook (label: agent) -> [SW] FastAPI -> [SW] job queue (SQS) -> [SW] worker pool
      worker:
        [SW] provision sandbox (clone repo @ sha, install deps from cache, no secrets)
        [SW+AI] agent loop (LangGraph, checkpointed to Postgres):
            plan -> search_code(ripgrep/ctags/embeddings) -> read_file -> apply_patch -> run_cmd(tests, lint)
            -> interpret failure -> loop (budget guard) -> summarize -> open_pr
        [SW] verification gate: tests pass + lint + diff size < N + no forbidden paths
        [SW] GitHub App: push branch agent/<issue>, open PR with run report
[SW] Postgres (runs, checkpoints, tool_calls, evals) · [SW] S3 (sandbox snapshots, logs) · [SW+AI] Langfuse
[SW] Human: reviews PR; comments re-trigger a *new* bounded run
```

## §5 Components — problem → design
- **Job runner `[SW]`:** runs are minutes-long → never an HTTP request. Queue + worker; run row with `status`, `budget_used`; heartbeat; on worker death, another worker resumes from checkpoint. Idempotent on `(repo, issue, head_sha)`.
- **Sandbox `[SW]`:** problem = model runs arbitrary commands. Design: microVM per run, non-root, read-only secrets mount absent, egress allow-list, CPU/mem/time limits, disk snapshot for resume, destroyed on finish. Dependency cache layer per repo to cut install time from 5 min to 30 s.
  - **L5:** warm pools (pre-cloned base images) cut p50 by minutes; cost/perf tradeoff tracked as $/run.
- **Code context `[AI]`:** problem = 500k LOC don't fit. Design: tools not RAG-dump — `search_code` (ripgrep + symbol index), `read_file(path, range)`, `repo_map` (ctags tree ≤ 4k tokens). Embeddings optional for "where is X handled" queries. Context window managed by summarizing old tool outputs after 60% budget.
- **Edit tool `[SW+AI]`:** full-file rewrites fail on large files → `apply_patch(path, old, new)` with exact-match requirement; on mismatch, return surrounding lines. Diff size cap (e.g. 800 lines) → otherwise split or stop.
- **Loop control `[SW+AI]`:** budget guard (tokens, tool calls, wall clock); "no progress" detector (same failing test 3× → stop, report); planner step writes `plan.md` in state, updated per iteration so resume has intent.
- **Verification gate `[SW]`:** PR only if: tests pass in sandbox, lint passes, no edits to `.github/`, `infra/`, secrets files; PR body auto-includes plan, commands run, test output, cost. CI still runs; agent cannot merge.
- **Feedback to review `[SW+AI]`:** reviewer comment → new run seeded with diff + comment; never long-lived "conversation" with mutable state.
- **Evals `[AI]`:** 100 internal tasks with hidden tests (like SWE-bench Verified); pass@1 per model/prompt/tool version; CI gate on the *harness* (tool changes) not just prompts; flake detection by running gold tests 3×.
  - **L5:** failure taxonomy (`no_repro`, `wrong_location`, `bad_patch`, `test_misread`, `budget`) drives roadmap; report it weekly.

## §6 API / schema
- `POST /runs {repo, issue_id}` → `run_id` · `GET /runs/{id}` (status, budget, checkpoint) · `POST /runs/{id}/cancel` · GitHub webhook → enqueue
- `runs(id, repo, issue, head_sha, status, budget_tokens, cost, sandbox_id, pr_url, failure_class)` · `checkpoints(run_id, step, state JSONB, created_at)` · `tool_calls(run_id, step, tool, args_hash, stdout_uri, exit_code, duration)` · `eval_tasks / eval_results`

## §7 Hygiene
| Concern | Answer |
|---|---|
| AuthZ | GitHub App with `contents:write` on `agent/*` branches only; no secrets in sandbox |
| Idempotency | run key (repo, issue, sha); `open_pr` idempotent on branch name |
| Timeouts | tool 10 min; run 60 min; heartbeat 30 s |
| Backpressure | bounded queue; concurrency cap = sandbox pool size; DLQ |
| Cache | dependency layer, repo clone cache, prompt prefix cache |
| Observability | span per tool with exit code, stdout size, tokens, $; failure_class metric |
| Deploy | harness + prompts versioned; golden pass@1 gate |
| Retention | sandbox logs 30 d; no source code in traces beyond diffs |

## §8 Failure → fallback
- Tests never pass → stop at budget, open **draft** PR with findings, or comment on issue · Flaky test → rerun 2×, mark suspected flake · Sandbox OOM → bump tier once, then fail · Model down → pause queue, resume from checkpoints · Patch mismatch loop → re-read file, then stop.

## §9 Pop-up questions
1. **Why an agent and not a codemod/script?** — Task shape unknown; execution feedback determines next step.
2. **Model runs `rm -rf` or curls secrets?** — MicroVM, no secrets, egress allow-list, destroyed after; command allow-list for side-effecting git ops.
3. **Worker dies at minute 25?** — Checkpoint per iteration + sandbox snapshot; resume ≤ 1 step lost.
4. **Agent keeps "fixing" the same test?** — No-progress detector, budget guard, failure_class recorded.
5. **How do you measure it?** — Hidden-test golden tasks pass@1; mergeable rate; failure taxonomy.
6. **Whole repo in context?** — No; tools (search, read ranges, repo map) + summarization.
7. **L5: reviewer agent?** — Only after measuring false-positive PR rate; cost doubles, benefit must show in merge rate.
8. **L5: 10× runs/day?** — Warm sandbox pools, per-repo dependency caches, spot instances, run tiering by issue size.

## §10 Trade-offs + defeaters
| Decision | Chosen | Alt | Flips |
|---|---|---|---|
| Runtime | LangGraph + Postgres checkpoints | Temporal | need cross-service durable workflows |
| Sandbox | microVM per run | container | trusted internal repos only |
| Edit | patch tool | full rewrite | tiny files only |
| Side-effect | PR only | auto-merge | never at L4 scope |
- Defeaters: "let it merge if CI is green" · "index the repo with RAG and skip tools" · "multi-agent planner/coder/reviewer by default".

## §11 MVP ladder
- MVP0: manual trigger, one repo, sandbox, search/read/patch/run tools, opens draft PR.
- MVP1: webhook, queue, checkpoints/resume, budget guard, Langfuse.
- MVP2: verification gate, dependency cache, failure taxonomy, 50-task golden.
- MVP3: warm pools, review-comment re-runs, cost dashboards.

## §12 Memorization card
- Pitch: bounded, checkpointed edit-test loop in a microVM sandbox whose only side-effect is a PR.
- Autonomy: L3; trigger = execution feedback decides next step.
- Numbers: 60 min cap · 300k tokens/$5 · 60 tool calls · 40% mergeable · 30 concurrent.
- Failures: no-progress loop · sandbox escape/secret leak · lost run state.
- Defeaters: auto-merge · RAG-only context · multi-agent default.
- MVP0→1→2: draft PR from one repo → queue+resume+budget → gate+cache+evals.
- Done when: describe sandbox controls in 30 s · draw run lifecycle · name failure taxonomy.

## References
1. https://github.com/SWE-agent/SWE-agent
2. https://github.com/langchain-ai/langgraph (checkpointers)
3. https://github.com/e2b-dev/E2B
4. https://www.swebench.com/
