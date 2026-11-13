"""Retry helper: exponential backoff + full jitter.

- delay = random(0, min(cap, base * 2**attempt))
- Full jitter spreads retries so clients don't retry in lockstep (AWS Architecture Blog, 2015).
- Catch: only retry idempotent work, or work guarded by an idempotency key / condition.
"""

import random
import time
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def backoff(attempt: int, base: float = 0.1, cap: float = 5.0) -> float:
    return random.uniform(0, min(cap, base * (2 ** min(attempt, 30))))


def call_with_retry(
    fn: Callable[[], T],
    retryable: Callable[[Exception], bool],
    max_attempts: int = 5,
    base: float = 0.1,
    cap: float = 5.0,
) -> T:
    for attempt in range(max_attempts):
        try:
            return fn()
        except Exception as e:  # noqa: BLE001 - the predicate decides
            if not retryable(e) or attempt == max_attempts - 1:
                raise
            time.sleep(backoff(attempt, base, cap))
    raise RuntimeError("unreachable")
