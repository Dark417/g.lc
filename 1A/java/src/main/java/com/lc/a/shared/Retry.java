package com.lc.a.shared;

import java.time.Duration;
import java.util.concurrent.ThreadLocalRandom;
import java.util.function.Predicate;
import java.util.function.Supplier;

/**
 * Retry helper: exponential backoff + full jitter (AWS Architecture Blog, "Exponential Backoff and Jitter", 2015).
 * - sleep = random(0, min(cap, base * 2^attempt))
 * - Full jitter spreads retries so many clients don't retry in lockstep (thundering herd).
 * - Catch: only retry idempotent work, or work guarded by an idempotency key / condition.
 */
public final class Retry {

    private final int maxAttempts;
    private final Duration base;
    private final Duration cap;

    public Retry(int maxAttempts, Duration base, Duration cap) {
        if (maxAttempts < 1) {
            throw new IllegalArgumentException("maxAttempts must be >= 1");
        }
        this.maxAttempts = maxAttempts;
        this.base = base;
        this.cap = cap;
    }

    /** Sensible default: 5 attempts, 100 ms base, 5 s cap. */
    public static Retry defaults() {
        return new Retry(5, Duration.ofMillis(100), Duration.ofSeconds(5));
    }

    /** Runs the call; retries while {@code retryable} says the failure is transient. */
    public <T> T call(Supplier<T> call, Predicate<Throwable> retryable) {
        RuntimeException last = null;
        for (int attempt = 0; attempt < maxAttempts; attempt++) {
            try {
                return call.get();
            } catch (RuntimeException e) {
                last = e;
                if (!retryable.test(e) || attempt == maxAttempts - 1) {
                    throw e;
                }
                sleep(backoff(attempt));
            }
        }
        throw last; // unreachable: loop either returns or throws
    }

    /** Full-jitter delay for a 0-based attempt number. */
    public Duration backoff(int attempt) {
        long ceiling = Math.min(cap.toMillis(), base.toMillis() * (1L << Math.min(attempt, 30)));
        return Duration.ofMillis(ThreadLocalRandom.current().nextLong(ceiling + 1));
    }

    public static void sleep(Duration d) {
        try {
            Thread.sleep(d.toMillis());
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new IllegalStateException("interrupted during backoff", e);
        }
    }
}
