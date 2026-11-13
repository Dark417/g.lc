package com.lc.x.x02_01_principles.general;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

/**
 * 2.4 Separation of Concerns — parsing, rules, persistence and logging live apart.
 * - Violation: one handler does all four, so testing the discount needs string input and a fake DB.
 * - Fix: parse -> DiscountRule -> OrderSink port, coordinated by OrderHandler.
 * - Catch: concerns are not only layers; package by feature first, cross-cutting via AOP/decorators.
 */
public final class SeparationOfConcerns {

    private SeparationOfConcerns() {
    }

    // ===== Violation: four concerns interleaved =====

    public static final class Violation {

        private Violation() {
        }

        /** Input format, business rule, SQL and logging tangled; each change risks the others. */
        public static String handle(String raw, List<String> sqlLog) {
            String[] parts = raw.split(",");                                   // parsing
            BigDecimal amount = new BigDecimal(parts[1].trim());
            if (amount.compareTo(new BigDecimal("100")) >= 0) {                // business rule
                amount = amount.multiply(new BigDecimal("0.9"));
            }
            sqlLog.add("INSERT INTO orders VALUES ('" + parts[0] + "', " + amount + ")"); // persistence (and injectable)
            System.out.println("handled " + parts[0]);                         // logging
            return parts[0] + "=" + amount;
        }
    }

    // ===== Fix: one concern per piece =====

    public static final class Fix {

        private Fix() {
        }

        public record OrderRequest(String id, BigDecimal amount) {
        }

        /** Parsing concern only. */
        public static OrderRequest parse(String raw) {
            String[] parts = raw.split(",");
            if (parts.length != 2) {
                throw new IllegalArgumentException("expected 'id,amount' but got " + raw);
            }
            return new OrderRequest(parts[0].trim(), new BigDecimal(parts[1].trim()));
        }

        /** Business concern only: testable with plain values. */
        public static final class DiscountRule {
            public BigDecimal apply(BigDecimal amount) {
                return amount.compareTo(new BigDecimal("100")) >= 0 ? amount.multiply(new BigDecimal("0.9")) : amount;
            }
        }

        /** Persistence concern behind a port; the adapter would use bound parameters. */
        public interface OrderSink {
            void save(String id, BigDecimal amount);
        }

        public static final class ListSink implements OrderSink {
            private final List<String> rows = new ArrayList<>();

            public void save(String id, BigDecimal amount) {
                rows.add(id + "=" + amount);
            }

            public List<String> rows() {
                return rows;
            }
        }

        /** Coordinator: wires concerns, owns none of their rules. */
        public static final class OrderHandler {
            private final DiscountRule discount;
            private final OrderSink sink;

            public OrderHandler(DiscountRule discount, OrderSink sink) {
                this.discount = discount;
                this.sink = sink;
            }

            public String handle(String raw) {
                OrderRequest req = parse(raw);
                BigDecimal amount = discount.apply(req.amount());
                sink.save(req.id(), amount);
                return req.id() + "=" + amount;
            }
        }
    }

    // Shows identical results; only the fix lets you test the discount with two BigDecimals.
    // Use whenever a unit mixes I/O format, rules and storage.
    // Catch: splitting by layer alone scatters one feature across many packages.
    public static String demo() {
        List<String> sql = new ArrayList<>();
        String bad = Violation.handle("o-1, 120", sql);
        Fix.ListSink sink = new Fix.ListSink();
        String good = new Fix.OrderHandler(new Fix.DiscountRule(), sink).handle("o-1, 120");
        return "SoC violation: " + bad + " sql=" + sql
                + "\nSoC fix:       " + good + " rows=" + sink.rows();
    }
}
