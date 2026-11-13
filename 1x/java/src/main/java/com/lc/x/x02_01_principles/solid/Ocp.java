package com.lc.x.x02_01_principles.solid;

import java.math.BigDecimal;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * 1.2 OCP — add a payment method by adding a class, not by editing tested code.
 * - Violation: a switch on the method name that every new method edits.
 * - Fix: PaymentMethod interface + registry built from a list (Spring can inject List&lt;PaymentMethod&gt;).
 * - Catch: you only close against variation you have seen; for a closed set an exhaustive switch is fine.
 */
public final class Ocp {

    private Ocp() {
    }

    // ===== Violation: every new payment method edits and retests this switch =====

    public static final class Violation {

        private Violation() {
        }

        /** Closed for extension: adding "APPLE_PAY" means editing pay() and every other switch like it. */
        public static final class PaymentProcessor {
            public String pay(String method, BigDecimal amount) {
                switch (method) {
                    case "CARD":
                        return "card charged " + amount;
                    case "PAYPAL":
                        return "paypal charged " + amount;
                    default:
                        throw new IllegalArgumentException("unsupported method " + method);
                }
            }
        }
    }

    // ===== Fix: stable interface + registry; new method = new class =====

    public static final class Fix {

        private Fix() {
        }

        /** The stable abstraction; implementations are additive. */
        public interface PaymentMethod {
            String name();

            String charge(BigDecimal amount);
        }

        public record Card() implements PaymentMethod {
            public String name() {
                return "CARD";
            }

            public String charge(BigDecimal amount) {
                return "card charged " + amount;
            }
        }

        public record PayPal() implements PaymentMethod {
            public String name() {
                return "PAYPAL";
            }

            public String charge(BigDecimal amount) {
                return "paypal charged " + amount;
            }
        }

        /** Added later without touching PaymentProcessor, Card or PayPal. */
        public record ApplePay() implements PaymentMethod {
            public String name() {
                return "APPLE_PAY";
            }

            public String charge(BigDecimal amount) {
                return "apple pay charged " + amount;
            }
        }

        /** Registry replaces the switch; duplicate names fail fast at construction. */
        public static final class PaymentProcessor {
            private final Map<String, PaymentMethod> methods = new LinkedHashMap<>();

            public PaymentProcessor(List<PaymentMethod> all) {
                for (PaymentMethod m : all) {
                    if (methods.putIfAbsent(m.name(), m) != null) {
                        throw new IllegalStateException("duplicate payment method " + m.name());
                    }
                }
            }

            public String pay(String method, BigDecimal amount) {
                PaymentMethod m = methods.get(method);
                if (m == null) {
                    throw new IllegalArgumentException("unsupported method " + method + "; known=" + methods.keySet());
                }
                return m.charge(amount);
            }
        }

        /**
         * Closed set (the catch): fee kinds are fixed by contract, so an enum switch expression is fine.
         * Java 17 checks exhaustiveness for enum switch expressions; a new constant breaks the build here.
         */
        public enum FeeKind { FLAT, PERCENT }

        public static BigDecimal fee(FeeKind kind, BigDecimal amount) {
            return switch (kind) {
                case FLAT -> new BigDecimal("0.30");
                case PERCENT -> amount.multiply(new BigDecimal("0.029"));
            };
        }
    }

    // Shows a new method (ApplePay) added with zero edits to the processor.
    // Use when variants arrive over time and each is independent.
    // Catch: if variants were speculative, the interface is YAGNI debt.
    public static String demo() {
        String bad = new Violation.PaymentProcessor().pay("CARD", new BigDecimal("10"));
        Fix.PaymentProcessor good = new Fix.PaymentProcessor(List.of(new Fix.Card(), new Fix.PayPal(), new Fix.ApplePay()));
        return "OCP violation: " + bad
                + "\nOCP fix:       " + good.pay("APPLE_PAY", new BigDecimal("10"))
                + "\nclosed set:    fee(PERCENT, 10) = " + Fix.fee(Fix.FeeKind.PERCENT, new BigDecimal("10"));
    }
}
