package com.lc.x.x02_01_principles.solid;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * 1.1 SRP — one module answers to one actor (finance, ops, marketing).
 * - Violation: one class prices, stores and emails, so three actors edit it.
 * - Fix: one class per actor plus a thin coordinator.
 * - Catch: split by actor, not by method; one-method classes everywhere is the opposite failure.
 */
public final class Srp {

    private Srp() {
    }

    public record Order(String id, String customerEmail, BigDecimal subtotal) {
    }

    // ===== Violation: three reasons to change in one class =====

    public static final class Violation {

        private Violation() {
        }

        /** God service: finance (tax), ops (storage) and marketing (email copy) all edit this class. */
        public static final class OrderService {
            private final Map<String, BigDecimal> table = new LinkedHashMap<>();
            private final List<String> outbox = new ArrayList<>();

            public String place(Order order) {
                BigDecimal total = order.subtotal().multiply(new BigDecimal("1.08"))   // finance rule
                        .setScale(2, RoundingMode.HALF_UP);
                table.put(order.id(), total);                                           // ops concern
                outbox.add("Hi! Your order " + order.id() + " costs " + total);         // marketing copy
                return "placed " + order.id() + " total=" + total + " mails=" + outbox.size();
            }
        }
    }

    // ===== Fix: one class per actor, coordinator only orchestrates =====

    public static final class Fix {

        private Fix() {
        }

        /** Finance owns this: tax and rounding rules change here only. */
        public static final class PriceCalculator {
            private final BigDecimal taxRate;

            public PriceCalculator(BigDecimal taxRate) {
                this.taxRate = taxRate;
            }

            public BigDecimal total(Order order) {
                return order.subtotal().multiply(BigDecimal.ONE.add(taxRate)).setScale(2, RoundingMode.HALF_UP);
            }
        }

        /** Ops owns this: storage engine and schema change here only. */
        public static final class OrderRepository {
            private final Map<String, BigDecimal> table = new LinkedHashMap<>();

            public void save(String orderId, BigDecimal total) {
                table.put(orderId, total);
            }

            public int count() {
                return table.size();
            }
        }

        /** Marketing owns this: wording and channel change here only. */
        public static final class OrderNotifier {
            private final List<String> outbox = new ArrayList<>();

            public void confirmed(Order order, BigDecimal total) {
                outbox.add("Order " + order.id() + " confirmed: " + total);
            }

            public int sent() {
                return outbox.size();
            }
        }

        /** Coordinator: no rules of its own, so no actor needs to edit it for their change. */
        public static final class OrderService {
            private final PriceCalculator prices;
            private final OrderRepository repo;
            private final OrderNotifier notifier;

            public OrderService(PriceCalculator prices, OrderRepository repo, OrderNotifier notifier) {
                this.prices = prices;
                this.repo = repo;
                this.notifier = notifier;
            }

            public String place(Order order) {
                BigDecimal total = prices.total(order);
                repo.save(order.id(), total);
                notifier.confirmed(order, total);
                return "placed " + order.id() + " total=" + total + " stored=" + repo.count() + " mails=" + notifier.sent();
            }
        }
    }

    // Shows both versions produce the same result; only the change cost differs.
    // Use as the runnable entry point for GET /principles/srp.
    // Catch: identical output proves nothing about design; the diff per change request does.
    public static String demo() {
        Order order = new Order("o-1", "a@example.com", new BigDecimal("100.00"));
        String bad = new Violation.OrderService().place(order);
        Fix.OrderService good = new Fix.OrderService(
                new Fix.PriceCalculator(new BigDecimal("0.08")), new Fix.OrderRepository(), new Fix.OrderNotifier());
        return "SRP violation: " + bad + "\nSRP fix:       " + good.place(order)
                + "\n-> a tax change now edits PriceCalculator only";
    }
}
