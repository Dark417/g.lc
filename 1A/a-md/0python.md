# 0python — Python For Backend And AI Roles (L4 / L5)

> What Python-first backend and AI-app interviews probe, area by area: the L4 bar, what L5 adds, the "defeater" question that separates them, and one line to say aloud.
> Source: chat "X.Python/Fastapi" (Aug 26, 2026), map §2–§9 and §18. Pydantic added as its own section.
> FastAPI and service engineering live in [0fastapi.md](0fastapi.md).
> Ratings are from Aug 2026: 🟢 defensible, 🟡 thin under probing, 🔴 gap.

## Index
- [0. One-minute version](#0-one-minute-version)
- [1. Weighting by loop type](#1-weighting-by-loop-type)
- [2. Language core and data model](#2-language-core-and-data-model)
- [3. Execution model: GIL, threads, processes, asyncio](#3-execution-model-gil-threads-processes-asyncio)
- [4. Multithreading and synchronization](#4-multithreading-and-synchronization)
- [5. asyncio in depth](#5-asyncio-in-depth)
- [6. Typing and contracts](#6-typing-and-contracts)
- [7. Pydantic v2](#7-pydantic-v2)
- [8. Packaging, imports, runtime](#8-packaging-imports-runtime)
- [9. Testing](#9-testing)
- [10. Performance and memory](#10-performance-and-memory)
- [11. Coding interviews in Python](#11-coding-interviews-in-python)
- [12. Gaps and drill order](#12-gaps-and-drill-order)
- [Where this fits](#where-this-fits)
- [References](#references)

---

## 0. One-minute version
- **What:** Python is the default language for agents and AI services.
- **Why it's tested:** in a Python-role loop, every resume line with asyncio or FastAPI becomes a live question.
- **How:** know the data model, the GIL, asyncio, typing and Pydantic well enough to explain the mechanism.
- **Catch:** most Java engineers write correct but "Java-flavored" Python, and interviewers notice.
- 🗣 "Threads for I/O, processes for CPU, asyncio for thousands of sockets, and Pydantic at every boundary."

---

## 1. Weighting by loop type

Plain idea: how much of this file matters depends on the kind of loop.

```
                 Big tech (Amzn SDE II / Google L4)      Python AI-app role
  Coding (DSA)   ████████████████████ 45%                ████████ 15%
  Exec model     ████ 10%                                ████████████ 25%
  API/cache/res  ████ 10% (inside sys design)            ████████████████ 30%
  Typing/test    ██ 5%                                   ████████ 15%
  AI integration ─                                       ██████ 10%
  Behavioral     ██████████ 25%                          ██ 5%
```
- Order of magnitude, from the Aug chat; not a sourced number.
- **Big tech:** Python is the vehicle, not the subject.
  - §11 dominates; §3 and §5 show up only inside design questions.
- **Python-app role:** resume cross-examination.
  - Every FastAPI, asyncio or Redis bullet becomes a live question.
- 🗣 "In a Python-role loop, the language is the system-design question."

---

## 2. Language core and data model

Plain idea: Python has no interfaces or access modifiers. The "dunder" protocols (`__len__`, `__iter__`, `__enter__`) are how objects plug into the language.

```
  object ──> __dunder__ protocols ──> descriptors ──> class creation (metaclass)
     |            (len/iter/enter)      (property, methods bind)
     └─ MRO (C3) ─ super() ─ __slots__
```

- **L4: correct, idiomatic, bounded**
  - Comprehensions vs generator expressions: laziness and memory.
  - `*args / **kwargs`; closures, and late binding in loops.
  - Decorators with `functools.wraps`.
  - `dataclasses`: `frozen`, `field(default_factory=)`, `__post_init__`.
  - `enum`; `with` and `contextlib.contextmanager`.
  - `__eq__` / `__hash__` contract; `is` vs `==`; shallow vs deep copy.
  - Mutable default argument bug.
  - Dict insertion order is a language guarantee since 3.7.
  - `collections`: `deque`, `Counter`, `defaultdict`, `OrderedDict.move_to_end`.
- **L5: mechanism**
  - Descriptors: `@property` and bound methods are `__get__` in action.
  - `__slots__`: less memory, no `__dict__`; breaks multiple inheritance with slotted bases.
  - MRO (C3) and cooperative `super()` in mixins.
  - `__init_subclass__` as the boring alternative to metaclasses.
  - Iterators vs generators vs `itertools`.
    - Defeater: `groupby` needs sorted input.
  - `functools.lru_cache`: unhashable args fail; unbounded without `maxsize`.
  - `singledispatch` for type-based overloads.
  - Import resolution and the `sys.modules` cache.
    - Circular imports: import inside the function, or restructure.
- **Fake-Python tells**
  - `for i in range(len(xs))`, getters / setters, bare `except:`, `XManager` classes.
- 🗣 "Python has no private, no interfaces, no compile step. The data model protocols are the interfaces."
- Rating: 🟡, correct but Java-flavored.
  - Fix: *Fluent Python* 2e, ch. 1, 5, 7, 13, 17, 21.

---

## 3. Execution model: GIL, threads, processes, asyncio

Plain idea: in standard CPython, only one thread runs Python code at a time. So you pick threads, processes or asyncio by what the work waits on.

```
  CPU-bound  ──> multiprocessing / ProcessPool  (pickling tax, memory xN)
  I/O-bound  ──> threads (GIL released on syscalls)  or  asyncio (one thread, many sockets)
  mixed      ──> asyncio + to_thread / run_in_executor bridges
```

- **L4**
  - **GIL** (global interpreter lock): one thread executes Python bytecode at a time.
    - Threads give concurrency, not parallelism, for pure-Python CPU work.
  - CPU-bound work: `multiprocessing` or `ProcessPoolExecutor`.
  - Many concurrent I/O waits: `asyncio`.
  - Rule: never block the event loop.
- **L5: defeaters**
  - The GIL is released during blocking syscalls and inside many C extensions.
    - numpy, `hashlib` and I/O do run in parallel on threads.
    - "Threads are useless in Python" is wrong.
  - Free-threaded build: PEP 703, experimental in 3.13; officially supported but optional from 3.14 (PEP 779).
    - Not the default build. Say "optional", don't overclaim.
  - Multiprocessing hidden tax:
    - Arguments and results are pickled.
    - Start methods: spawn is the default on macOS and Windows; fork plus threads can deadlock.
    - 3.14 moved the POSIX default away from fork. Verify for your version.
    - Shared data: `multiprocessing.shared_memory` or Arrow.
  - Escalation ladder: `concurrent.futures`, then Celery / RQ, then Ray / Dask, then Spark.
    - Deciding variable: must the work survive process death and be observable? Then a queue, not a pool.
- 🗣 "Threads for I/O, processes for CPU, asyncio for thousands of sockets. One sync call inside the loop voids all three."
- Rating: 🟡, concept known, never debugged a wrong-primitive incident.

---

## 4. Multithreading and synchronization

Plain idea: threads share memory, so any shared mutable state needs a lock or, better, a queue.

```
  ThreadPoolExecutor ─ submit/map ─ Future ─ as_completed
        |
     Lock / RLock / Semaphore / Event / Condition / Barrier
        |
     queue.Queue (thread-safe; bounded = backpressure)
```

- **L4**
  - Prefer `ThreadPoolExecutor` over raw `threading.Thread`.
    - Default `max_workers` is `min(32, cpus + 4)` (Python docs).
  - `Future.result(timeout=)`.
  - Daemon threads die with the process, so data can be lost on shutdown.
  - `queue.Queue` producer / consumer with a sentinel value to stop.
  - `Lock` around shared mutable state.
  - Race example: `count += 1` is not atomic. It is load, add, store.
  - What is "atomic enough":
    - Single bytecode ops on `dict` / `list` (`append`, `get`) are safe under the GIL.
    - Compound ops (check-then-set, `+=`) are not.
    - Defeater: don't rely on this in free-threaded builds.
- **L5**
  - Deadlocks: lock ordering, timeouts on `acquire`, always `with lock`.
    - `RLock` allows re-entry; needing it is a smell.
  - `Condition` for wait / notify; `Event` for shutdown signals; `Barrier` is rare.
  - Per-thread state: `threading.local`.
    - Under asyncio use `contextvars` instead (request IDs, DB sessions).
  - Graceful shutdown: `executor.shutdown(wait=True, cancel_futures=True)` (3.9+), signal handling, drain queues.
  - `asyncio.to_thread` uses the loop's default executor.
    - Its size can conflict with FastAPI's thread pool (see 0fastapi.md).
  - Java mapping:
    - `ExecutorService` ≈ `ThreadPoolExecutor`.
    - `CompletableFuture` ≈ `Future` / `asyncio.Task`.
    - `synchronized` ≈ `with lock`; `ThreadLocal` ≈ `contextvars`.
- **Failure (canonical pattern):** worker threads append to a shared list; results interleave or vanish under load.
  - Fix: `queue.Queue`, or return values through futures.
- 🗣 "In Python you reach for `queue.Queue` before you reach for a `Lock`."
- Rating: 🟡; rewrite pool, producer / consumer and deadlock answers in Python by hand.

---

## 5. asyncio in depth

Plain idea: one thread runs many tasks by switching at every `await`. It's concurrency through waiting, not parallel CPU.

```
  event loop ─ selector (epoll/kqueue) ─ ready queue
     |
   Task (wraps coroutine) ── await ── Future (result / exception / cancel)
     |
   TaskGroup (3.11+)  Semaphore  Queue  timeout()  to_thread()
```

- **L4**
  - `async def` / `await`, `asyncio.run`.
  - `gather`, with `return_exceptions=True` when partial failure is fine.
  - `create_task`: keep a reference, or the task can be garbage-collected (documented gotcha).
  - `asyncio.sleep`, never `time.sleep`.
  - `httpx.AsyncClient`; `pytest-asyncio` for tests.
  - Saying "asyncio makes it parallel" fails the question.
- **L5**
  - Coroutine vs task vs future. The scheduler is cooperative, so a CPU-heavy loop starves everything.
  - **Cancellation**
    - `task.cancel()` raises `CancelledError` inside the coroutine at its next `await`.
    - Never swallow it; clean up in `finally`.
    - `asyncio.shield` for work that must finish.
    - `asyncio.timeout()` (3.11+) vs older `wait_for`, which cancels the inner task.
  - **Structured concurrency**
    - `TaskGroup` cancels siblings on the first failure and raises an `ExceptionGroup` (`except*`).
    - `gather` keeps siblings running.
    - Deciding variable: is a partial result still worth something?
  - **Backpressure**
    - `Semaphore(n)` around outbound calls, e.g. LLM provider rate limits.
    - Bounded `asyncio.Queue`; `Queue.join()`.
  - **Sync bridges**
    - `to_thread` / `run_in_executor` for blocking libraries.
    - Defeater: boto3 is sync. Use aioboto3, or a thread.
    - CPU work: `loop.run_in_executor(process_pool, fn)`.
  - Async pools (`asyncpg`, `httpx` limits) are hidden concurrency caps.
  - Debug: `PYTHONASYNCIODEBUG=1` flags callbacks slower than 100 ms by default; `asyncio.all_tasks()` to find leaks.
- 🗣 "`gather` is optimistic, `TaskGroup` is pessimistic. Pick by whether a partial answer is still an answer."
- Rating: 🔴, the top gap; every agent role probes cancellation and backpressure.

---

## 6. Typing and contracts

Plain idea: type hints don't change how Python runs. They're checked by tools (mypy) and enforced at runtime only by libraries like Pydantic.

- **L4**
  - Annotate everything.
  - `X | None`, `TypedDict`, `Literal`, `Enum`.
  - mypy or pyright in CI.
  - `dataclass` = plain container; Pydantic `BaseModel` = validated container.
- **L5**
  - `Protocol` (structural typing) vs ABC (nominal typing).
    - Deciding variable: do you control the implementers?
  - `TypeVar`, `Generic`, `ParamSpec` for typed decorators; `overload`.
  - Strict-mode paydown: per-module `strict`, `# type: ignore[code]` with codes.
  - Your anchor: ADK `output_key` handoffs are untyped.
    - Pydantic validation in `before_agent_callback` makes typing the contract between agents.
- 🗣 "Type hints are the only interface Python has; Pydantic is the runtime that enforces them."
- Rating: 🟡; 🟢 once edgar-mcp passes `mypy --strict`.

---

## 7. Pydantic v2

Plain idea: Pydantic turns a type-hinted class into a validator. Untrusted data goes in; a typed object or a clear error comes out.

- **Where you meet it**
  - FastAPI request and response models.
  - LLM structured output: the schema you send, and the parser on the way back (see [2prompt.md](2prompt.md)).
  - ADK, OpenAI and Anthropic SDKs, LangChain tool schemas.
  - Settings from env vars (`pydantic-settings`).
- **How it works**
  1. Declare fields with types and `Field(...)` constraints.
  2. `Model.model_validate(data)` parses and coerces, or raises `ValidationError`.
  3. `model_dump()` gives a dict; `model_dump_json()` gives JSON.
  4. `Model.model_json_schema()` emits JSON Schema. That's what goes to an LLM or OpenAPI.

```python
from typing import Literal
from pydantic import BaseModel, Field, field_validator

class Refund(BaseModel):
    order_id: str = Field(pattern=r"^ORD-\d+$")
    amount: float = Field(gt=0, le=500)
    reason: Literal["damaged", "late", "other"]

    @field_validator("order_id")
    @classmethod
    def upper(cls, v: str) -> str:
        return v.upper()

r = Refund.model_validate({"order_id": "ORD-12", "amount": 20, "reason": "late"})
```

- **L4**
  - `BaseModel`, `Field` constraints, `field_validator`, `model_validator(mode="after")`.
  - `model_validate` / `model_dump`; `model_config = ConfigDict(extra="forbid")`.
  - Optional vs required: `x: int | None = None`.
  - Lax mode coerces `"5"` to `5`; `strict=True` refuses.
- **L5**
  - The core is written in Rust (`pydantic-core`), but validation still costs on hot paths.
    - `model_construct()` skips validation for trusted data.
  - `model_dump(mode="json")` (JSON-safe dict) vs `model_dump_json()` (string).
  - Discriminated unions: `Field(discriminator="type")` for tool-call and message schemas.
    - Faster and clearer errors than trying each union member.
  - `TypeAdapter` validates non-model types, e.g. `list[Refund]`.
  - Schema drift: `json_schema_extra`, field aliases, and version fields for long-lived schemas.
  - Defeater: LLM providers support only part of JSON Schema.
    - Constraints like `gt` or `pattern` may be dropped from the sent schema. Validate again after parsing.
- **dataclass vs TypedDict vs Pydantic**

| Option | Validates at runtime | Good at | Choose when |
|---|---|---|---|
| `dataclass` | No | cheap internal objects | data you already trust |
| `TypedDict` | No | typing plain dicts | JSON-shaped dicts, no runtime cost |
| Pydantic `BaseModel` | Yes | boundaries: HTTP, LLM, config | data from outside the process |

- Default: Pydantic at every boundary, dataclass inside.
- 🗣 "Validate at the edges, trust inside. Pydantic is the edge."

---

## 8. Packaging, imports, runtime

Plain idea: most Python production incidents are environment drift. The lockfile is what you actually deploy.

- **L4**
  - One venv per project; `pyproject.toml`; `uv` or `pip` with a lockfile.
  - `python -m pkg`; absolute imports; `if __name__ == "__main__"`; entry points.
- **L5**
  - `uv.lock` is deterministic; `requirements.txt` without hashes is not.
  - Docker multi-stage with `uv sync --frozen` and a wheel cache.
  - `sys.path` hacks are a smell; namespace packages.
  - Lambda cold start grows with dependency size: move numpy / pandas to layers, or drop them.
  - Import-time side effects; `-X importtime` finds slow startups.
- 🗣 "Most Python prod incidents are environment drift, not logic. The lockfile is the deploy artifact."
- Rating: 🟢 (uv, Docker, Terraform daily).

---

## 9. Testing

Plain idea: pytest fixtures replace setup code; patching replaces dependencies. Most bugs in tests come from patching the wrong place.

- **L4**
  - Fixtures and scopes: function, module, session.
  - `parametrize`, `monkeypatch`, `conftest.py`.
  - `mock.patch` target rule: patch where the name is looked up, not where it's defined.
  - `pytest-asyncio`; `httpx.AsyncClient` against a FastAPI app.
- **L5**
  - `conftest` layering; factory fixtures instead of global state.
  - Hypothesis property tests, e.g. idempotency: `f(f(x)) == f(x)`.
  - Mutation testing (`mutmut`).
  - Contract tests from OpenAPI (Schemathesis).
  - Snapshot tests for LLM output, with a judge tolerance.
  - `respx` / `pytest-httpx` to mock providers; `freezegun` for time.
  - Test cancellation and timeouts deterministically.
- 🗣 "If the mock target is the definition module, the test is testing the mock."
- Rating: 🟡, strong Java test culture, pytest idioms unwritten.

---

## 10. Performance and memory

Plain idea: profile first. The usual fix is moving work into C-backed code, not tuning Python.

- **L4**
  - Profile before optimizing: `cProfile`, `py-spy top` on a live process.
  - Set membership, not list; `''.join`; generators for streams; `orjson` over `json`.
- **L5**
  - C-backed paths: pandas to polars / pyarrow; compiled `re`.
  - `tracemalloc` snapshots; refcounting plus the cyclic GC; `__slots__`; `weakref`.
  - asyncio doesn't speed up CPU work.
  - Capacity model: uvicorn workers × async concurrency per worker.
  - Escalate only after profiling: Cython, numba, Rust (pyo3).
- Rating: 🟡.

---

## 11. Coding interviews in Python

Plain idea: in big-tech loops, Python is just the tool. Know the standard library cold, so you never fight the language.

- **Muscle memory (timed, not read)**
  - `collections`: `deque`, `Counter`, `defaultdict`.
  - `heapq`: min-heap only; negate for max; `nsmallest`.
  - `bisect`; `sorted(key=, reverse=)`; `enumerate` / `zip`.
  - `itertools.accumulate` / `product`.
  - `@lru_cache` for memoized DP.
    - Recursion limit: `sys.setrecursionlimit`, or go iterative.
  - Strings are immutable: build with `join`.
  - No integer overflow; `//` and `%` on negatives; `float('inf')`; `math.isqrt`.
- **L5 signal**
  - Clean helpers, type hints, no mutable defaults, `dataclass` for nodes.
  - Explain cost in Python terms: dict ops amortized O(1); `list.pop(0)` is O(n), so use `deque`.
- Rating: 🟡; DP is still the gap.

---

## 12. Gaps and drill order

| Priority | Area | Rating | Drill (recall, not reading) |
|---|---|---|---|
| 1 | §5 asyncio | 🔴 | From memory: bounded fetcher with `TaskGroup` + `Semaphore` + timeout + cancel cleanup |
| 2 | §7 Pydantic | 🟡 | Write a discriminated-union tool schema; validate LLM output against it |
| 3 | §4 threads | 🟡 | Rewrite pool, producer / consumer and deadlock answers in Python |
| 4 | §6 typing | 🟡 | `mypy --strict` on edgar-mcp until green |
| 5 | §2 data model | 🟡 | *Fluent Python* ch. 1, 5, 7, 13, 17, 21, one per day |
| 6 | §9 testing | 🟡 | Fixture scoping and patch-target exercise |

- Skip: Django, metaclasses, Cython / numba, free-threading beyond one sentence.

---

## Where this fits
- **Place:** L1 base of [1a-bp.md](../1a-bp.md). It's the language under every agent you build.
- **Time it deserves:** after the C3 AI interview. Tomorrow, only §5 and §7 matter.
- **I should be able to…**
  - Explain the GIL and when threads still help.
  - Write a bounded async fetcher with cancellation from memory.
  - Turn a Pydantic model into JSON Schema and validate output against it.

## References
1. [asyncio tasks docs](https://docs.python.org/3/library/asyncio-task.html) — tasks, cancellation, `TaskGroup`, `timeout`.
2. [Pydantic docs](https://docs.pydantic.dev/latest/) — models, validators, JSON Schema, unions.
3. [PEP 703](https://peps.python.org/pep-0703/) and [PEP 779](https://peps.python.org/pep-0779/) — free-threaded CPython.
4. *Fluent Python*, 2nd ed. (Ramalho) — data model and concurrency chapters only.
