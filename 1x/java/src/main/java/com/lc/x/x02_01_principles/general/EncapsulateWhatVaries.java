package com.lc.x.x02_01_principles.general;

import java.math.BigDecimal;
import java.util.Map;

/**
 * 2.8 Encapsulate what varies — put a stable interface in front of the axis of change.
 * - Violation: region fee rules inline in checkout; every quarterly change edits checkout.
 * - Fix: FeePolicy per region, chosen from a map; checkout never changes for fee updates.
 * - Catch: you must have observed the variation; rates that business edits belong in config, not classes.
 */
public final class EncapsulateWhatVaries {

    private EncapsulateWhatVaries() {
    }

    // ===== Violation =====

    public static final class Violation {

        private Violation() {
        }

        public static final class Checkout {
            /** Volatile rules mixed into stable checkout flow. */
            public BigDecimal fee(String region, BigDecimal amount) {
                if (region.equals("US")) {
                    return amount.multiply(new BigDecimal("0.03"));
                } else if (region.equals("EU")) {
                    return amount.multiply(new BigDecimal("0.02")).add(new BigDecimal("0.25"));
                } else {
                    return new BigDecimal("1.00");
                }
            }
        }
    }

    // ===== Fix =====

    public static final class Fix {

        private Fix() {
        }

        /** The varying part, walled off. */
        public interface FeePolicy {
            BigDecimal fee(BigDecimal amount);
        }

        public record PercentFee(BigDecimal rate, BigDecimal fixed) implements FeePolicy {
            public BigDecimal fee(BigDecimal amount) {
                return amount.multiply(rate).add(fixed);
            }
        }

        /** Stable part: checkout logic that does not change when fees do. */
        public static final class Checkout {
            private final Map<String, FeePolicy> policies;
            private final FeePolicy fallback;

            public Checkout(Map<String, FeePolicy> policies, FeePolicy fallback) {
                this.policies = policies;
                this.fallback = fallback;
            }

            public BigDecimal fee(String region, BigDecimal amount) {
                return policies.getOrDefault(region, fallback).fee(amount);
            }
        }
    }

    // Shows the same fees; the fix lets the rates come from config (PercentFee is data).
    // Use when one part changes on a different schedule than the rest.
    // Catch: abstracting a part that never changes is pure overhead.
    public static String demo() {
        BigDecimal amt = new BigDecimal("100");
        Fix.Checkout checkout = new Fix.Checkout(Map.of(
                "US", new Fix.PercentFee(new BigDecimal("0.03"), BigDecimal.ZERO),
                "EU", new Fix.PercentFee(new BigDecimal("0.02"), new BigDecimal("0.25"))),
                a -> new BigDecimal("1.00"));
        return "Encapsulate violation: EU=" + new Violation.Checkout().fee("EU", amt)
                + "\nEncapsulate fix:       EU=" + checkout.fee("EU", amt) + " APAC=" + checkout.fee("APAC", amt);
    }
}
