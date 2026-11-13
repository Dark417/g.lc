package com.lc.x.x02_01_principles.general;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

/**
 * 2.12 Fail fast — reject bad input at the first boundary.
 * - Violation: Order accepts negative amounts and null currency; the failure appears far away.
 * - Fix: compact constructor validates; batches validate per record and quarantine bad rows.
 * - Catch: fail fast per record, not per system — one bad row must not kill a million-row job.
 */
public final class FailFast {

    private FailFast() {
    }

    // ===== Violation =====

    public static final class Violation {

        private Violation() {
        }

        /** Accepts anything; a downstream job divides by currency rate and throws hours later. */
        public record Order(String id, BigDecimal amount, String currency) {
        }
    }

    // ===== Fix =====

    public static final class Fix {

        private Fix() {
        }

        /** Invalid objects cannot exist; the error names the field at the point of creation. */
        public record Order(String id, BigDecimal amount, String currency) {
            public Order {
                Objects.requireNonNull(id, "id");
                Objects.requireNonNull(amount, "amount");
                if (amount.signum() <= 0) {
                    throw new IllegalArgumentException("amount must be > 0, got " + amount);
                }
                if (currency == null || currency.length() != 3) {
                    throw new IllegalArgumentException("currency must be ISO-4217, got " + currency);
                }
            }
        }

        public record BatchResult(List<Order> accepted, List<String> quarantined) {
        }

        // Per-record fail fast: each bad row is rejected with a reason; the batch continues.
        // Use for pipelines (Databricks jobs, Kafka consumers) where one row must not stop the rest.
        // Catch: alert on the quarantine rate, or silent data loss replaces loud failure.
        public static BatchResult validateBatch(List<String[]> rows) {
            List<Order> ok = new ArrayList<>();
            List<String> bad = new ArrayList<>();
            for (String[] r : rows) {
                try {
                    ok.add(new Order(r[0], new BigDecimal(r[1]), r[2]));
                } catch (RuntimeException e) {
                    bad.add(String.join(",", r) + " -> " + e.getMessage());
                }
            }
            return new BatchResult(ok, bad);
        }
    }

    // Shows invalid data accepted silently vs rejected at construction, and per-record batch handling.
    // Use at every trust boundary (HTTP input, files, config).
    // Catch: Java asserts are off by default and python -O strips asserts; use explicit checks.
    public static String demo() {
        Violation.Order silent = new Violation.Order("o-1", new BigDecimal("-5"), null);
        String rejected;
        try {
            new Fix.Order("o-1", new BigDecimal("-5"), "USD");
            rejected = "accepted";
        } catch (IllegalArgumentException e) {
            rejected = e.getMessage();
        }
        Fix.BatchResult batch = Fix.validateBatch(List.of(
                new String[] {"o-1", "10", "USD"},
                new String[] {"o-2", "-1", "USD"},
                new String[] {"o-3", "7", "EURO"}));
        return "FailFast violation: accepted " + silent
                + "\nFailFast fix:       " + rejected
                + "\nbatch:              accepted=" + batch.accepted().size() + " quarantined=" + batch.quarantined();
    }
}
