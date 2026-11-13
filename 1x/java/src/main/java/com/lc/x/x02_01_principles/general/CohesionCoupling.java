package com.lc.x.x02_01_principles.general;

import java.math.BigDecimal;
import java.time.LocalDate;

/**
 * 2.5 High cohesion / low coupling — strong inside a module, thin between modules.
 * - Violation: OrderUtils grab-bag (low cohesion) that digs through order.customer().address() (high coupling).
 * - Fix: ShippingQuote owns the zone rule; Order exposes only shippingZip().
 * - Catch: replacing typed calls with maps/events hides coupling instead of removing it.
 */
public final class CohesionCoupling {

    private CohesionCoupling() {
    }

    public record Address(String street, String zip) {
    }

    public record Customer(String id, Address address) {
    }

    // ===== Violation =====

    public static final class Violation {

        private Violation() {
        }

        public record Order(String id, Customer customer, BigDecimal weightKg) {
        }

        /** Unrelated helpers in one place; the shipping rule knows the full Order -> Customer -> Address shape. */
        public static final class OrderUtils {
            public static String formatDate(LocalDate d) {
                return d.toString();
            }

            public static String slackMessage(String text) {
                return ":package: " + text;
            }

            public static BigDecimal shippingCost(Order order) {
                String zip = order.customer().address().zip();
                return zip.startsWith("9") ? new BigDecimal("15") : new BigDecimal("8");
            }
        }
    }

    // ===== Fix =====

    public static final class Fix {

        private Fix() {
        }

        /** Order hides how the zip is stored; callers ask for what they need. */
        public record Order(String id, Customer customer, BigDecimal weightKg) {
            public String shippingZip() {
                return customer.address().zip();
            }
        }

        /** Cohesive: every field and method is about quoting shipping. */
        public static final class ShippingQuote {
            private final BigDecimal westCoast;
            private final BigDecimal standard;

            public ShippingQuote(BigDecimal westCoast, BigDecimal standard) {
                this.westCoast = westCoast;
                this.standard = standard;
            }

            public BigDecimal quoteFor(Order order) {
                return order.shippingZip().startsWith("9") ? westCoast : standard;
            }
        }
    }

    // Shows the same quote; in the fix an Address refactor touches Order only.
    // Use co-change history to decide what belongs together.
    // Catch: zero coupling is impossible; make the remaining coupling explicit and typed.
    public static String demo() {
        Customer c = new Customer("c-1", new Address("1 Main", "94105"));
        BigDecimal bad = Violation.OrderUtils.shippingCost(new Violation.Order("o-1", c, BigDecimal.ONE));
        BigDecimal good = new Fix.ShippingQuote(new BigDecimal("15"), new BigDecimal("8"))
                .quoteFor(new Fix.Order("o-1", c, BigDecimal.ONE));
        return "Cohesion violation: OrderUtils.shippingCost=" + bad + " (plus formatDate, slackMessage)"
                + "\nCohesion fix:       ShippingQuote.quoteFor=" + good;
    }
}
