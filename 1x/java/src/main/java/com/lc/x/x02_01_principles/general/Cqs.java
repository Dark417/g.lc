package com.lc.x.x02_01_principles.general;

import java.util.concurrent.atomic.AtomicLong;

/**
 * 2.11 CQS — a method either changes state (command) or returns data (query), not both.
 * - Violation: nextOrderNumber() looks like a query but increments; logging it burns numbers.
 * - Fix: peekNext() query + advance() command; reserveNumber() is the deliberate atomic exception.
 * - Catch: splitting an atomic read-modify-write into peek + advance creates a check-then-act race.
 */
public final class Cqs {

    private Cqs() {
    }

    // ===== Violation =====

    public static final class Violation {

        private Violation() {
        }

        public static final class OrderNumbers {
            private long next = 1;

            /** Reads like a getter; every call (debugger, log line, retry) consumes a number. */
            public long nextOrderNumber() {
                return next++;
            }
        }
    }

    // ===== Fix =====

    public static final class Fix {

        private Fix() {
        }

        public static final class OrderNumbers {
            private final AtomicLong next = new AtomicLong(1);

            /** Query: safe to call any number of times. */
            public long peekNext() {
                return next.get();
            }

            /** Command: changes state, returns nothing. */
            public void advance() {
                next.incrementAndGet();
            }

            /** Justified CQS exception: atomic reserve-and-return, like INSERT ... RETURNING id. */
            public long reserveNumber() {
                return next.getAndIncrement();
            }
        }
    }

    // Shows a "getter" burning numbers vs a safe query; then the atomic exception.
    // Use for any API where callers might retry, log or cache calls.
    // Catch: peekNext()+advance() from two threads can hand out the same number; use reserveNumber().
    public static String demo() {
        Violation.OrderNumbers bad = new Violation.OrderNumbers();
        bad.nextOrderNumber(); // "just logging it"
        long badNumber = bad.nextOrderNumber();
        Fix.OrderNumbers good = new Fix.OrderNumbers();
        good.peekNext();
        good.peekNext();
        long reserved = good.reserveNumber();
        return "CQS violation: second 'read' returned " + badNumber + " (number 1 lost)"
                + "\nCQS fix:       peek twice then reserve -> " + reserved + ", next=" + good.peekNext();
    }
}
