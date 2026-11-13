package com.lc.x.x02_01_principles.general;

import java.math.BigDecimal;
import java.util.List;

/**
 * 2.9 Law of Demeter — talk only to your immediate collaborators.
 * - Violation: checkout walks order -> customer -> wallet -> balance.
 * - Fix: order.canPay(amount); each object asks only its own direct collaborator.
 * - Catch: chains over plain data and fluent APIs (streams, builders) are fine; LoD targets behavior.
 */
public final class LawOfDemeter {

    private LawOfDemeter() {
    }

    // ===== Violation =====

    public static final class Violation {

        private Violation() {
        }

        public record Wallet(BigDecimal balance) {
        }

        public record Customer(String id, Wallet wallet) {
        }

        public record Order(String id, Customer customer) {
        }

        public static final class Checkout {
            /** Knows the shape of three distant objects; moving wallet onto an Account breaks it. */
            public boolean canPay(Order order, BigDecimal amount) {
                return order.customer().wallet().balance().compareTo(amount) >= 0;
            }
        }
    }

    // ===== Fix =====

    public static final class Fix {

        private Fix() {
        }

        public static final class Wallet {
            private final BigDecimal balance;

            public Wallet(BigDecimal balance) {
                this.balance = balance;
            }

            public boolean covers(BigDecimal amount) {
                return balance.compareTo(amount) >= 0;
            }
        }

        public static final class Customer {
            private final Wallet wallet;

            public Customer(Wallet wallet) {
                this.wallet = wallet;
            }

            public boolean canAfford(BigDecimal amount) {
                return wallet.covers(amount);
            }
        }

        public static final class Order {
            private final Customer customer;

            public Order(Customer customer) {
                this.customer = customer;
            }

            /** Checkout calls this only; the internal path can change freely. */
            public boolean canPay(BigDecimal amount) {
                return customer.canAfford(amount);
            }
        }
    }

    // Shows the same answer with and without reaching through objects; plus an allowed fluent chain.
    // Use for behavior-rich domain objects.
    // Catch: strict LoD on a middle object grows dozens of forwarding methods.
    public static String demo() {
        BigDecimal amt = new BigDecimal("20");
        boolean bad = new Violation.Checkout().canPay(
                new Violation.Order("o-1", new Violation.Customer("c-1", new Violation.Wallet(new BigDecimal("50")))), amt);
        boolean good = new Fix.Order(new Fix.Customer(new Fix.Wallet(new BigDecimal("50")))).canPay(amt);
        long fluentOk = List.of(1, 2, 3).stream().filter(i -> i > 1).map(i -> i * 2).count(); // not a LoD violation
        return "LoD violation: canPay=" + bad + " via order.customer().wallet().balance()"
                + "\nLoD fix:       canPay=" + good + " via order.canPay(amount)"
                + "\nfluent chain:  stream().filter().map().count()=" + fluentOk + " is fine";
    }
}
