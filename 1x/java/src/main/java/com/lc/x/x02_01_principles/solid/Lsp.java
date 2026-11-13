package com.lc.x.x02_01_principles.solid;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

/**
 * 1.3 LSP — a subtype keeps every promise of its base type.
 * - Violation: GiftCardPayment inherits refund() and throws, so callers need instanceof checks.
 * - Fix: split the capability; only refundable payments implement Refundable.
 * - Catch: compilers check signatures, not behavior; a shared contract test catches the rest.
 */
public final class Lsp {

    private Lsp() {
    }

    // ===== Violation: subtype weakens the base contract =====

    public static final class Violation {

        private Violation() {
        }

        /** Base promise: refund() returns a refund id for any captured payment. */
        public static class Payment {
            protected final BigDecimal amount;

            public Payment(BigDecimal amount) {
                this.amount = amount;
            }

            public String refund() {
                return "refund-" + amount;
            }
        }

        /** Breaks the promise: callers written against Payment now crash. */
        public static class GiftCardPayment extends Payment {
            public GiftCardPayment(BigDecimal amount) {
                super(amount);
            }

            @Override
            public String refund() {
                throw new UnsupportedOperationException("gift cards are not refundable");
            }
        }

        /** Caller forced to know subtypes: the smell that tells you LSP is broken. */
        public static List<String> refundAll(List<Payment> payments) {
            List<String> out = new ArrayList<>();
            for (Payment p : payments) {
                if (p instanceof GiftCardPayment) {
                    out.add("skipped gift card");
                    continue;
                }
                out.add(p.refund());
            }
            return out;
        }
    }

    // ===== Fix: capability interfaces; every implementation keeps its promises =====

    public static final class Fix {

        private Fix() {
        }

        public interface Payment {
            BigDecimal amount();
        }

        /** Only types that can honor refund() implement it; no throwing overrides. */
        public interface Refundable extends Payment {
            String refund();
        }

        public record CardPayment(BigDecimal amount) implements Refundable {
            public String refund() {
                return "refund-card-" + amount;
            }
        }

        public record WalletPayment(BigDecimal amount) implements Refundable {
            public String refund() {
                return "refund-wallet-" + amount;
            }
        }

        public record GiftCardPayment(BigDecimal amount) implements Payment {
        }

        public static List<String> refundAll(List<? extends Refundable> refundables) {
            List<String> out = new ArrayList<>();
            for (Refundable r : refundables) {
                out.add(r.refund());
            }
            return out;
        }

        // Contract test in miniature: run the same behavioral checks against every implementation.
        // Use for every interface with more than one implementation.
        // Catch: it only checks what you wrote down; unstated promises (rounding, latency) still drift.
        public static boolean contractHolds(Refundable r) {
            String id = r.refund();
            return id != null && id.startsWith("refund-") && id.endsWith(r.amount().toPlainString());
        }
    }

    // Shows the instanceof smell vs a type-safe capability split, plus the contract check.
    // Use when a subtype "can't" do something the base promises.
    // Catch: the JDK itself breaks LSP in List.of(...).add() ("optional operations").
    public static String demo() {
        BigDecimal ten = new BigDecimal("10");
        List<Violation.Payment> mixed = List.of(new Violation.Payment(ten), new Violation.GiftCardPayment(ten));
        List<Fix.Refundable> refundables = List.of(new Fix.CardPayment(ten), new Fix.WalletPayment(ten));
        boolean contract = refundables.stream().allMatch(Fix::contractHolds);
        String jdk;
        try {
            List.of(1).add(2);
            jdk = "added";
        } catch (UnsupportedOperationException e) {
            jdk = "List.of(..).add -> UnsupportedOperationException";
        }
        return "LSP violation: " + Violation.refundAll(mixed)
                + "\nLSP fix:       " + Fix.refundAll(refundables) + " contractHolds=" + contract
                + "\nJDK trade-off: " + jdk;
    }
}
