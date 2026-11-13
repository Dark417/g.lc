package com.lc.x.x02_01_principles.general;

import java.math.BigDecimal;

/**
 * 2.10 Tell, don't ask — tell the object to act; don't pull its state and decide for it.
 * - Violation: service reads balance, checks it, writes it back (invariant lives outside the wallet).
 * - Fix: wallet.debit(amount) enforces "no overdraft" in one place.
 * - Catch: queries for display are fine (CQS); don't push I/O into entities.
 */
public final class TellDontAsk {

    private TellDontAsk() {
    }

    // ===== Violation =====

    public static final class Violation {

        private Violation() {
        }

        /** Anemic: any caller can set a negative balance. */
        public static final class Wallet {
            private BigDecimal balance;

            public Wallet(BigDecimal balance) {
                this.balance = balance;
            }

            public BigDecimal getBalance() {
                return balance;
            }

            public void setBalance(BigDecimal balance) {
                this.balance = balance;
            }
        }

        public static final class PaymentService {
            /** The overdraft rule is here, and must be copied into every other caller. */
            public boolean charge(Wallet wallet, BigDecimal amount) {
                if (wallet.getBalance().compareTo(amount) >= 0) {
                    wallet.setBalance(wallet.getBalance().subtract(amount));
                    return true;
                }
                return false;
            }
        }
    }

    // ===== Fix =====

    public static final class Fix {

        private Fix() {
        }

        public static final class InsufficientFunds extends RuntimeException {
            public InsufficientFunds(String msg) {
                super(msg);
            }
        }

        /** Invariant guarded next to the data; synchronized so the check and the write are one step. */
        public static final class Wallet {
            private BigDecimal balance;

            public Wallet(BigDecimal balance) {
                this.balance = balance;
            }

            public synchronized void debit(BigDecimal amount) {
                if (amount.signum() <= 0) {
                    throw new IllegalArgumentException("amount must be > 0");
                }
                if (balance.compareTo(amount) < 0) {
                    throw new InsufficientFunds("balance " + balance + " < " + amount);
                }
                balance = balance.subtract(amount);
            }

            /** A query for display is fine. */
            public synchronized BigDecimal balance() {
                return balance;
            }
        }
    }

    // Shows the invariant moving into the wallet; the bypass via setBalance is gone.
    // Use for stateful domain objects with invariants.
    // Catch: in Spark/Databricks transforms data is plain and functions operate on it — TDA does not apply.
    public static String demo() {
        Violation.Wallet anemic = new Violation.Wallet(new BigDecimal("10"));
        new Violation.PaymentService().charge(anemic, new BigDecimal("4"));
        anemic.setBalance(new BigDecimal("-100")); // nothing stops this
        Fix.Wallet wallet = new Fix.Wallet(new BigDecimal("10"));
        wallet.debit(new BigDecimal("4"));
        String overdraft;
        try {
            wallet.debit(new BigDecimal("100"));
            overdraft = "allowed";
        } catch (Fix.InsufficientFunds e) {
            overdraft = "rejected: " + e.getMessage();
        }
        return "TDA violation: balance=" + anemic.getBalance() + " (setter bypassed the rule)"
                + "\nTDA fix:       balance=" + wallet.balance() + " overdraft " + overdraft;
    }
}
