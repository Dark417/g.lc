package com.lc.x.x02_01_principles.general;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

/**
 * 2.2 KISS — the simplest design that meets the real requirements.
 * - Violation: a generic rule engine (string fields, string operators) for a two-rule shipping fee.
 * - Fix: a five-line function.
 * - Catch: simple is not simplistic; keep the essential requirements (here: input validation).
 */
public final class Kiss {

    private Kiss() {
    }

    // ===== Violation: accidental complexity =====

    public static final class Violation {

        private Violation() {
        }

        public record Rule(String field, String op, BigDecimal threshold, BigDecimal fee) {
        }

        /** Stringly-typed engine: typos fail at runtime, and readers must simulate it to know the fee. */
        public static final class RuleEngine {
            private final List<Rule> rules;

            public RuleEngine(List<Rule> rules) {
                this.rules = rules;
            }

            public BigDecimal evaluate(Map<String, Object> facts) {
                BigDecimal fee = BigDecimal.ZERO;
                for (Rule r : rules) {
                    BigDecimal value = new BigDecimal(String.valueOf(facts.get(r.field())));
                    boolean hit = switch (r.op()) {
                        case "gt" -> value.compareTo(r.threshold()) > 0;
                        case "eq" -> value.compareTo(r.threshold()) == 0;
                        default -> throw new IllegalArgumentException("op " + r.op());
                    };
                    if (hit) {
                        fee = fee.add(r.fee());
                    }
                }
                return fee;
            }
        }
    }

    // ===== Fix: direct code =====

    public static final class Fix {

        private Fix() {
        }

        /** Readable in one glance; still validates input (simple, not simplistic). */
        public static BigDecimal shippingFee(BigDecimal weightKg, boolean express) {
            if (weightKg.signum() < 0) {
                throw new IllegalArgumentException("weight must be >= 0");
            }
            BigDecimal fee = weightKg.compareTo(new BigDecimal("5")) > 0 ? new BigDecimal("12") : new BigDecimal("5");
            return express ? fee.add(new BigDecimal("10")) : fee;
        }
    }

    // Shows both computing the same fee; one needs a mental interpreter.
    // Use when rules are few and owned by engineers.
    // Catch: if business users must edit hundreds of rules without deploys, an engine may be essential.
    public static String demo() {
        Violation.RuleEngine engine = new Violation.RuleEngine(List.of(
                new Violation.Rule("weight", "gt", new BigDecimal("-1"), new BigDecimal("5")),
                new Violation.Rule("weight", "gt", new BigDecimal("5"), new BigDecimal("7")),
                new Violation.Rule("express", "eq", BigDecimal.ONE, new BigDecimal("10"))));
        BigDecimal bad = engine.evaluate(Map.of("weight", "7", "express", "1"));
        return "KISS violation: engine fee=" + bad
                + "\nKISS fix:       shippingFee(7, express) = " + Fix.shippingFee(new BigDecimal("7"), true);
    }
}
