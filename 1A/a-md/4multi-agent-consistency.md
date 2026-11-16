# Multi-Agent Consistency — Distributed Systems First, Agents Second

> Part A answers every question as if there were no LLM anywhere: workers, a coordinator, a DB, third-party APIs.
> Part B re-answers with LLM agents as the workers and judges the video's claims.
> The core message: **nothing in the video is an "AI" problem. It is Saga + idempotency + optimistic concurrency + durable state + leases, with one new twist: the decomposer is non-deterministic.**

---

## 0. Concepts from the screenshots — 中 / EN

| 中文 | English | Standard DS name |
|---|---|---|
| 多 Agent 协作一致性 | multi-agent collaboration consistency | distributed workflow consistency |
| 全局任务 / 子任务 | global task / sub-task | job / step (fan-out) |
| 任务拆分粒度不当 → 语义重叠 | wrong decomposition granularity → semantic overlap | overlapping work partitions |
| 重复执行同一段业务 | duplicate execution of the same business op | duplicate side effects |
| 失败重试产生脏数据 | retry after failure creates dirty data | non-idempotent retry |
| 通信延迟 → 共享数据读写竞态 → 覆盖 | comm latency → shared-data race → lost update | lost update / write skew |
| 调度中心宕机 → 状态丢失 → 重发 / 漏发 | scheduler crash → state loss → resend / miss | coordinator failure; at-least-once vs at-most-once |
| 异构 Agent 协议不统一 | heterogeneous agents, no common protocol | protocol adapter / anti-corruption layer |
| 全局任务状态机 | global task state machine | workflow state machine |
| 子任务幂等 | sub-task idempotency | idempotency key |
| 最终一致性补偿 | eventual-consistency compensation | Saga with compensating transactions |
| 任务语义去重 / 语义指纹 (semantic_hash) | semantic dedup / semantic fingerprint | dedup key (normalized) |
| 共享资源乐观锁 | optimistic lock on shared resource | optimistic concurrency control (version column) |
| 调度高可用 | scheduler high availability | stateless coordinator + durable state |
| 结果校验 | result validation | output schema / invariant check |
| 数据库唯一约束 | DB unique constraint | uniqueness as the dedup gate |
| 状态流转：待拆分 / 执行中 / 汇总中 / 已完成 / 补偿中 / 已失败 | states: pending-split / running / aggregating / done / compensating / failed | state machine transitions |
| 更新影响行数为零 | update affected 0 rows | CAS failed → conflict |
| 分布式状态机 + 幂等 + 补偿 | distributed state machine + idempotency + compensation | durable execution / Saga |
| 协议适配层 | protocol adapter layer | adapter / gateway |
| 同一个数据库事务 | same DB transaction | local atomicity |
| 归档到历史表 | archive to history table | hot/cold tiering |
| 任务重复率 / 状态冲突率 / 补偿成功率 | duplicate rate / conflict rate / compensation success rate | SLIs |
| 降级为单 Agent 串行 + 人工对账 | degrade to single-agent serial + manual reconciliation | degraded mode + reconciliation |

---

## 0.1 Your questions, organized

- **Q1 Decompose**: one big task → parallel sub-tasks; how to avoid overlap; how to validate sub-task semantics.
- **Q2 Assign**: how to actually hand sub-tasks to different agents/workers.
- **Q3 Retry / partial failure**: some succeed, some fail; retry may fail again; retry causes dual write; partial third-party transaction.
- **Q4 Race / conflict**: agents see different data states due to latency; how to avoid write conflicts.
- **Q5 Coordinator loss**: orchestrator restarts, state lost; no duplicates, no missing; alternatives to a single orchestrator (idempotency + compensation?).
- **Q6 Async / heterogeneous agents**: agents that don't participate in the orchestrator's protocol.
- **Q7 Aggregate / converge**: fan-in results, avoid duplicates, data out of sync.
- **Q8 Overall**: how to achieve multi-agent consistency (or eventual consistency).
- **Q9 Tool calling** single-instance vs pooled → separate file.

---

# Part A — Pure distributed systems (no LLM)

## A.0 Ground truth to say first

- Exactly-once delivery across machines is impossible. You get at-least-once and make effects **idempotent** → "effectively once".
- Atomicity exists only inside one DB transaction. Anything that crosses a network hop (another service, a third party) is a Saga.
- Consistency you can promise: **the ledger (state table) is always correct; the world catches up to it.**
- The coordinator must be **stateless**; the state must be **durable**; therefore any coordinator can die and any other can resume.

## A.1 Schema — everything hangs off this

```sql
CREATE TABLE job (
  job_id        uuid PRIMARY KEY,
  status        text NOT NULL,          -- PENDING | RUNNING | AGGREGATING | DONE | COMPENSATING | FAILED
  version       int  NOT NULL DEFAULT 0,
  input         jsonb,
  result        jsonb,
  created_at    timestamptz, updated_at timestamptz
);

CREATE TABLE step (
  job_id        uuid REFERENCES job,
  step_id       text,                   -- deterministic: "order:123:refund"
  dedup_key     text NOT NULL,          -- normalized business key
  status        text NOT NULL,          -- PENDING | LEASED | DONE | FAILED | COMPENSATED
  version       int  NOT NULL DEFAULT 0,
  attempt       int  NOT NULL DEFAULT 0,
  lease_owner   text, lease_until timestamptz,
  idem_key      text NOT NULL,          -- sent to every side-effecting call
  result        jsonb, error jsonb,
  PRIMARY KEY (job_id, step_id),
  UNIQUE (dedup_key)                    -- duplicate work rejected at insert
);

CREATE TABLE outbox (                   -- for calls to other services / 3rd parties
  id bigserial PRIMARY KEY,
  job_id uuid, step_id text, idem_key text,
  payload jsonb, status text, created_at timestamptz
);
```

- `UNIQUE(dedup_key)` is the dedup mechanism. Not a hash of prose. A normalized business key.
- `version` is the optimistic lock.
- `lease_*` is how you know a worker died.
- `idem_key` is how the outside world dedups you.

## A.2 Q1 — Decompose without overlap

- Decompose by **data partition**, never by description.
  - Bad: "agent A handles refunds, agent B handles disputes" → same order touched twice.
  - Good: shard by key: `order_id % N`, or by entity list: `[orders 1..100] → A, [101..200] → B`.
- Each step gets a **deterministic step_id** from its inputs. Same inputs → same id → second insert fails on PK/unique.
- Validate decomposition **before** dispatch:
  - Coverage: union of partitions == whole input set.
  - Disjointness: pairwise intersection empty.
  - Both are set operations in code, testable.
- If overlap can't be avoided by design → make the overlapping op idempotent so duplicate execution is harmless.

## A.3 Q2 — Assign

- Don't push to workers. **Workers pull** with a lease.
  - Pull = natural backpressure, dead workers just stop pulling.

```sql
-- claim one step atomically
UPDATE step SET status='LEASED', lease_owner=$worker, lease_until=now()+interval '60s',
                attempt=attempt+1, version=version+1
WHERE (job_id, step_id) = (
  SELECT job_id, step_id FROM step
  WHERE status='PENDING' OR (status='LEASED' AND lease_until < now())
  ORDER BY created_at LIMIT 1 FOR UPDATE SKIP LOCKED)
RETURNING *;
```

- `FOR UPDATE SKIP LOCKED` = N workers claim N different rows, no coordinator round-trip.
- Alternative: queue (SQS / Pub/Sub) with visibility timeout — same semantics, the queue holds the lease.
- Routing by capability: a `required_capability` column; worker pulls only rows it can run.

## A.4 Q3 — Partial failure, retry, dual write, third parties

- **Classify errors first**: retryable (timeout, 429, 5xx) vs terminal (validation, 404, auth). Terminal → FAILED immediately, no retry.
- **Retry only the failed step**, never the job. Successful steps are DONE in the ledger; the scheduler never re-leases DONE rows.
- **Dual write on retry** — the scenario:
  - Worker calls third party (e.g. payment API), call succeeds, worker dies before writing DONE.
  - Retry sees PENDING → calls again → double charge.
- Fixes, in order of strength:
  1. **Idempotency key on the third-party call** (`Idempotency-Key: idem_key`). Stripe, most payment/email APIs honor it. Second call returns the first result.
  2. Third party has no idem support → **query before write**: look up by your reference id; if exists, treat as done.
  3. Neither → **outbox + reconciliation**: write intent to `outbox` in the same tx as the step claim; a separate reconciler compares outbox vs third-party statements and repairs.
- **Compensation (Saga)**: if step 3 of 5 is terminal-failed, run compensating actions for 1–2 (refund the charge, delete the created record). Compensations must themselves be idempotent and retryable.
- **Retry budget**: max attempts per step, then DLQ + human. Retrying a deterministic failure forever is the poison pill.

## A.5 Q4 — Races, stale reads, write conflicts

- Latency means every worker reads a snapshot that may be stale. You cannot prevent stale reads. You prevent **stale writes**.
- **Optimistic concurrency**:

```sql
UPDATE account SET balance=$new, version=version+1
WHERE id=$id AND version=$expected;   -- affected rows 0 → someone else wrote → re-read, redo
```

- **Fencing token** for external systems: pass `version` along; the receiver rejects a lower token than it last saw. Prevents a zombie worker with an expired lease from writing.
- **Partition to avoid contention**: if two workers can write the same row, you decomposed wrong (A.2). Conflicts should be rare exceptions, not the design.
- **Pessimistic lock** (`SELECT ... FOR UPDATE`) only for short, in-DB critical sections. Never hold a lock across a network call.
- Write skew across two rows → use serializable isolation or a single row that owns the invariant.

## A.6 Q5 — Coordinator dies

- Rule: the coordinator holds **zero state in memory that isn't also in the DB**.
- On restart: `SELECT * FROM step WHERE status IN ('PENDING','LEASED')` → resume. That's the whole recovery.
- No duplicates: DONE rows are never re-leased; idempotency keys cover in-flight ones.
- No missing: every step was inserted in the same tx as the job's PENDING→RUNNING transition; if the job is RUNNING, its steps exist.
- Stuck detection: `lease_until < now()` → re-leasable; a **reaper** cron runs the same claim query.
- Multiple coordinators: fine, because claim is atomic (SKIP LOCKED). "Single point of failure" disappears once state is in the DB and any process can run the loop.
- Yes, "idempotency + compensation" replaces the need for a stateful orchestrator — but you still need the **state table**. That's the "distributed state machine". The thing you remove is the *stateful process*, not the *state*.
- Buy option: Temporal / AWS Step Functions / Cloud Workflows implement exactly this (durable execution, retries, compensation, timers). Use one before building A.1–A.6 by hand.

## A.7 Q6 — Async / heterogeneous workers

- Workers that can't speak your protocol get an **adapter** at the boundary:
  - Inbound: translate job → their request format, attach `idem_key` and `step_id`.
  - Outbound: translate their result → your `result` schema; validate with a schema; unknown shape → FAILED, not "close enough".
- Async workers (callback / webhook / poll):
  - Step goes to `LEASED` with a long lease; the adapter registers a callback keyed by `step_id`.
  - Callback is idempotent: `UPDATE step SET status='DONE' WHERE step_id=$1 AND status='LEASED'` — a second callback affects 0 rows.
  - No callback within lease → poll their status endpoint, or mark FAILED and compensate.
- Don't let a foreign worker touch your state table directly. They return results; the adapter writes the ledger.

## A.8 Q7 — Aggregate / converge

- Fan-in trigger: job moves to AGGREGATING when `COUNT(steps WHERE status NOT IN ('DONE','FAILED','COMPENSATED')) = 0`.
  - Implement as a counter column decremented in the same tx as each step completion, or the count query in the reaper. Counter is cheaper.
- Aggregation reads results **from the ledger**, not from worker messages. Messages can duplicate; rows can't.
- Aggregation itself is a step: idempotent, versioned, can be retried.
- Merge conflicts in results (two steps claim different values for one entity) → that's a decomposition bug; surface it, don't average it.
- Validate the aggregate against invariants (sum of parts == total, no entity missing) before DONE.

## A.9 Q8 — What consistency you actually get

- **Ledger**: strongly consistent (single DB, transactions, optimistic locks).
- **External effects**: eventually consistent with the ledger, converged by idempotency + retry + compensation + reconciliation.
- **Readers**: may see intermediate states; expose `job.status` so they know.
- One sentence: *"Strong consistency on the task ledger; effectively-once side effects via idempotency keys and leases; Saga compensation for terminal failures; a stateless coordinator any replica can resume."*

---

# Part B — Multi-agent coordination

## B.0 What changes when workers are LLM agents

- **Decomposer is non-deterministic.** A model splitting "reconcile all Q3 invoices" into sub-tasks may produce overlapping, missing, or differently-worded partitions each run. This is the *only* genuinely new problem.
- **Workers are non-deterministic.** Same step can produce different tool sequences; "done" is a judgment, not a return code.
- **Side effects come through tools.** The model decides to call `refund()`; the harness executes it. Idempotency must live in the tool layer, not the prompt.
- **Results are prose unless you force schema.** Aggregation needs typed output.
- Everything else — leases, CAS, Saga, outbox, reaper — is unchanged.

## B.1 Q1 — Decomposition with an LLM

- **Prefer code decomposition.** If the input is a list (invoices, tickets, files), partition in code (A.2). Agents get partitions, not descriptions. This eliminates semantic overlap entirely.
- **If the model must decompose** (task shape unknown):
  - Force structured output: `[{step_id, target_entities[], operation, inputs}]` via schema.
  - Validate in code: coverage + disjointness on `target_entities`. Reject and re-prompt on failure; cap at 2 attempts then human.
  - `dedup_key` = normalized `(operation, sorted target_entities)`, not a hash of the sentence.
- **"Semantic hash" as in the video**: hashing prose doesn't catch "refund order 123" vs "process refund for #123". Options if you truly need semantic dedup: embedding cosine > threshold → flag for review, never auto-drop. Better: don't produce prose steps at all.
- Interview line: *"I'd move decomposition out of the model wherever the input is enumerable; the model decides how to do a step, not what the steps are."*

## B.2 Q2 — Assigning to agents

- Same lease/pull loop. The "worker" is an agent runtime (ADK `Runner` per step, or one process running N invocations).
- Routing by capability = deterministic dispatch on `operation` type. Model-based routing (`sub_agents` descriptions) only when the category can't be enumerated; then it's a classifier with an eval set.
- One step = one invocation. Give it `step_id` and `idem_key` in state so every tool call can use them.

## B.3 Q3 — Retry and dual writes through tools

- Idempotency key derivation: `idem_key = f"{job_id}:{step_id}:{tool_name}:{call_ordinal}"`.
  - Ordinal = position within the step's tool-call sequence. Retrying the step replays the same ordinals → same keys.
  - Caveat: if the model on retry takes a *different* tool path, ordinals shift. Fix: key on the **business args** instead: `hash(tool_name, canonical(args))`. Then "refund order 123 $50" is the same key regardless of path.
- Tool wrapper does the work, not the prompt:

```python
async def refund(order_id: str, amount: int, tool_context) -> dict:
    key = f"{tool_context.state['step_id']}:refund:{order_id}:{amount}"
    if (prior := await ledger.get(key)):
        return prior                      # replay, no second charge
    res = await stripe.refund(order_id, amount, idempotency_key=key)
    await ledger.put(key, res)
    return {"ok": True, "refund_id": res.id, "retryable": False}
```

- Tool errors: return `{error, retryable}`; retryable ones retried **inside the tool** with backoff; the model never sees a transient error. Model-level retry is the most expensive retry in the system.
- Step-level retry: only after the harness caps iterations or the step throws. Successful steps stay DONE.
- Compensation: a `compensate_*` tool per side-effecting tool; the Saga driver in code calls them in reverse order. Do not ask the model to "undo what you did".

## B.4 Q4 — Agents seeing different states

- Agents read via tools → tools read the DB → same staleness as any service. Fix is the same: CAS on write with `version`, fencing token for external writes.
- Extra hazard: **in-context staleness**. The agent read balance=100 at step 1, did three more tool calls over 40 s, then writes based on 100. Mitigation: the write tool takes `expected_version` as a required arg and rejects on mismatch; the model must re-read. Mechanical gate beats "please re-check".
- ADK-specific: `ParallelAgent` branches share one state map; two branches writing the same key = last-write-wins race. Disjoint `output_key` per branch; never read a key another branch writes.
- Shared `temp:` namespace across sub-agents in one invocation — same collision surface.

## B.5 Q5 — Orchestrator/dispatcher loses state

- ADK `Runner` commits each event's `state_delta` before forwarding → the session store *is* your ledger for one invocation. But: **no transaction across events**, and steps ≠ invocations. So keep the `job/step` table outside ADK; the session is per-step scratch.
- Recovery = A.6 unchanged: scan PENDING/LEASED, re-lease, replay with same `idem_key`s.
- What you do *not* replay: the model's reasoning. You replay the step from its inputs; the model may take a different path; idempotency by business args (B.3) makes that safe.
- Buy option is stronger here: Temporal / LangGraph checkpointer / Agent Engine sessions give durable execution; a custom ledger is still needed for cross-step business state.

## B.6 Q6 — Async agents, foreign frameworks

- A2A is the protocol answer: task lifecycle `submitted → working → input-required → completed`. Wrap remote agents with timeout, circuit breaker, schema validation on output, and the adapter writes your ledger.
- An agent that is "async and doesn't support the orchestrator's consistency" = a worker with a webhook. A.7 applies: long lease, idempotent callback, poll on silence.
- Never let a foreign agent write your state table. It returns; you record.

## B.7 Q7 — Aggregation

- Every step returns schema-validated JSON to state/ledger. Aggregator (code, or an LLM with structured output) reads the ledger.
- If the aggregator is an LLM: give it only DONE rows, require it to cite `step_id` per claim, validate invariants in code afterward. Never let it fill gaps for FAILED steps.
- Conflicting results between steps = decomposition bug → FAILED + human, not "pick one".

## B.8 Q8 — The consistency model, stated for agents

- Ledger strongly consistent; side effects effectively-once via idempotent tools; Saga compensation in code; stateless coordinator; decomposition in code wherever enumerable; schema at every agent boundary.
- The line: *"I treat agents as unreliable workers with a non-deterministic control flow. The consistency machinery is identical to a microservice Saga; the only agent-specific work is pushing decomposition, idempotency keys and compensation into code and tools, because prompt instructions are advisory and locks are not."*

## B.9 Verdict on the video's claims

| Claim (中文要点) | Verdict | Correction / nuance |
|---|---|---|
| 一致性 = 结果正确、状态统一、无重复、无冲突 | Valid | Standard definition; add "ledger strong, world eventual". |
| 失效场景：语义重叠、失败重试脏数据、竞态覆盖、调度宕机、异构协议 | Valid | Complete list for an interview. Missing: zombie worker (expired lease still writing) → fencing token. |
| 基线 = 全局状态机 + 子任务幂等 + 最终一致性补偿 | Valid | This is Saga + durable state. Name it as such. |
| agent_collab_task 表 (global_task_id, sub_task_id, agent_id, task_status, semantic_hash, execute_result, compensate_status) | Mostly valid | Add `version`, `attempt`, `lease_owner/lease_until`, `idem_key`. Without leases you can't detect dead workers; without version the optimistic lock they describe has nothing to compare. |
| 语义分块去重 → 语义指纹 → 插入唯一约束 | Partly valid | Unique constraint as dedup gate: correct. "Semantic hash": overstated — hashing text doesn't detect paraphrased overlap. Use normalized business keys; avoid prose steps. |
| 状态机：待拆分/执行中/汇总中/已完成/补偿中/已失败 | Valid | Fine. Add `LEASED` at step level. |
| 状态变更基于当前状态乐观锁更新，第二条影响行数为零 | Valid | Textbook CAS. |
| 所有子任务幂等，重试不产生重复效果 | Valid but incomplete | Only true if the key reaches the *third party* (idempotency header) or you query-before-write. Internal idempotency alone doesn't stop a double charge. |
| 中心化调度只做分发，不做一致性；一致性靠分布式状态机 | Valid | Correct framing: stateless coordinator, state in DB. "不依赖中心化调度" is slightly misleading — you still have a coordinator; it just isn't the source of truth. |
| 异构 Agent → 协议适配层，统一幂等接口和结果格式 | Valid | Add: validate output schema; adapter writes the ledger, agent doesn't. |
| 全局状态和子任务记录写同一事务 | Valid | Correct for the ledger. Does not cover external side effects → outbox. |
| 7 天后归档，归档期间保证无重试 | Valid, minor | Simpler: only archive rows in terminal states with `updated_at < now()-7d`; terminal rows are never retried, so no window problem. |
| 监控：重复率、冲突率、补偿成功率、调度可用性 | Valid | Add: steps-per-job p99, lease-expiry rate, DLQ depth, reconciliation diff count. |
| 降级：单 Agent 串行 + 人工对账 + 结果校验 | Valid | Good degraded mode. |
| 面试考察三点：识别真实场景、无中心化调度的最终一致性、语义去重/状态机/补偿经验 | Valid as interview advice | Add the question they'll actually ask: "how do you know a worker is dead?" → leases. |

- Overall: the video is a competent Saga/idempotency explanation relabeled for agents. Two real gaps: **no leases/fencing** (dead-worker detection) and **semantic dedup by hash** is hand-waved. One misleading phrase: "no central scheduler" — it's "no *stateful* scheduler".

---

## C. Summary table

| Question | Distributed-systems answer | Agent-specific addition |
|---|---|---|
| Decompose without overlap | Partition by data/key in code; deterministic step_id; coverage+disjointness check; unique constraint | Move decomposition out of the model; if model decomposes, structured output + code validation; dedup on business keys not prose |
| Assign | Workers pull with lease; `FOR UPDATE SKIP LOCKED` or queue visibility timeout | One step = one invocation; deterministic routing on op type; model routing only if not enumerable |
| Partial failure / retry | Classify errors; retry failed steps only; retry budget; DLQ | Retry transient errors inside the tool; model never sees them; cap iterations |
| Dual write / 3rd party | Idempotency key to the third party; query-before-write; outbox + reconciler | Key derived from business args in the tool wrapper; ledger check before call |
| Compensation | Saga: compensating action per step, reverse order, idempotent | Compensation driven by code, one `compensate_*` tool per effect; never "undo yourself" |
| Race / stale state | CAS with version; fencing token; partition to avoid contention | Write tools require `expected_version`; disjoint `output_key` in ParallelAgent; `temp:` collisions |
| Coordinator loss | Stateless coordinator; scan PENDING/LEASED on restart; reaper on expired leases | Session store ≠ job ledger; keep the ledger outside the framework; replay steps, not reasoning |
| Async / heterogeneous | Adapter; idempotent callback; poll on silence; schema-validate output | A2A task lifecycle; remote agent returns, adapter writes ledger |
| Aggregate | Counter → AGGREGATING; read from ledger; validate invariants; aggregation is a retryable step | Structured outputs only; LLM aggregator cites step_id; conflicts → FAILED + human |
| Consistency model | Ledger strong; effects effectively-once; Saga eventual; stateless coordinator | Same, plus: decomposition in code, idempotency in tools, schema at every boundary |

---

## References

1. https://github.com/temporalio/samples-python — Saga, retries, idempotent activities as a library; read `saga/` and `activity_retry/` before hand-rolling A.1–A.6.
2. https://github.com/google/adk-python — `runners.py` for the per-event commit point; `agents/parallel_agent.py` for the shared-state hazard.
3. https://microservices.io/patterns/data/saga.html and https://microservices.io/patterns/data/transactional-outbox.html — canonical pattern pages.
4. https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html — fencing tokens; why a lease alone isn't enough.
5. https://a2a-protocol.org/ — task lifecycle for async/heterogeneous agents.