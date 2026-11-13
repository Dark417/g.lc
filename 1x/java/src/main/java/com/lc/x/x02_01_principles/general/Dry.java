package com.lc.x.x02_01_principles.general;

import java.math.BigDecimal;
import java.math.RoundingMode;

/**
 * 2.1 DRY — one authoritative home per piece of knowledge.
 * - Violation: the tax rate is copied into checkout and invoice, and the copies already drifted.
 * - Fix: one TaxPolicy used by both.
 * - Catch: look-alike code that encodes different knowledge must stay separate (see Fix validators).
 */
public final class Dry {

    private Dry() {
    }

    // ===== Violation: the same business rule in two places =====

    public static final class Violation {

        private Violation() {
        }

        public static final class Checkout {
            public BigDecimal tax(BigDecimal subtotal) {
                return subtotal.multiply(new BigDecimal("0.08")).setScale(2, RoundingMode.HALF_UP);
            }
        }

        /** Someone updated the rate here only: invoice and checkout now disagree. */
        public static final class Invoice {
            public BigDecimal tax(BigDecimal subtotal) {
                return subtotal.multiply(new BigDecimal("0.0825")).setScale(2, RoundingMode.HALF_UP);
            }
        }
    }

    // ===== Fix: single source of truth; look-alikes with different owners stay apart =====

    public static final class Fix {

        private Fix() {
        }

        /** The knowledge "how much tax" lives here only. */
        public record TaxPolicy(BigDecimal rate) {
            public BigDecimal tax(BigDecimal subtotal) {
                return subtotal.multiply(rate).setScale(2, RoundingMode.HALF_UP);
            }
        }

        // Look alike today, different reasons to change: the API owner may tighten limits,
        // the backfill owner must accept historical rows. Merging them would couple two teams.
        public static boolean validApiAmount(BigDecimal amount) {
            return amount.signum() > 0 && amount.compareTo(new BigDecimal("10000")) <= 0;
        }

        public static boolean validBackfillAmount(BigDecimal amount) {
            return amount.signum() > 0 && amount.compareTo(new BigDecimal("10000")) <= 0;
        }
    }

    // Shows drifted copies vs one policy.
    // Use for business rules, schemas, constants with one owner.
    // Catch: "duplication is far cheaper than the wrong abstraction" when owners differ.
    public static String demo() {
        BigDecimal sub = new BigDecimal("100.00");
        Fix.TaxPolicy policy = new Fix.TaxPolicy(new BigDecimal("0.08"));
        return "DRY violation: checkout=" + new Violation.Checkout().tax(sub) + " invoice=" + new Violation.Invoice().tax(sub)
                + "\nDRY fix:       both=" + policy.tax(sub)
                + "\nkept separate: api=" + Fix.validApiAmount(sub) + " backfill=" + Fix.validBackfillAmount(sub);
    }
}
