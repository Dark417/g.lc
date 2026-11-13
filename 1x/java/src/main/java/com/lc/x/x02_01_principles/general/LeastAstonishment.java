package com.lc.x.x02_01_principles.general;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

/**
 * 2.13 Principle of least astonishment — behavior matches what the name suggests.
 * - Violation: getDiscount() writes an audit row; calling it twice writes twice.
 * - Fix: pure discountFor() + explicit recordDiscountAudit().
 * - Catch: astonishment is audience-relative; follow ecosystem conventions (and know the JDK's own traps).
 */
public final class LeastAstonishment {

    private LeastAstonishment() {
    }

    // ===== Violation =====

    public static final class Violation {

        private Violation() {
        }

        /** A getter with a hidden side effect. */
        public static BigDecimal getDiscount(String customerId, List<String> audit) {
            audit.add("discount looked up for " + customerId);
            return customerId.startsWith("vip") ? new BigDecimal("0.10") : BigDecimal.ZERO;
        }
    }

    // ===== Fix =====

    public static final class Fix {

        private Fix() {
        }

        /** Pure: the name promises a value and nothing else. */
        public static BigDecimal discountFor(String customerId) {
            return customerId.startsWith("vip") ? new BigDecimal("0.10") : BigDecimal.ZERO;
        }

        /** The side effect is in the name. */
        public static void recordDiscountAudit(String customerId, List<String> audit) {
            audit.add("discount applied for " + customerId);
        }
    }

    // Shows hidden writes from a getter, then the JDK's own List.remove(int) vs remove(Object) trap.
    // Use when naming any method with side effects.
    // Catch: Java readers expect getters, Python readers expect properties — match the codebase.
    public static String demo() {
        List<String> audit = new ArrayList<>();
        Violation.getDiscount("vip-1", audit);
        Violation.getDiscount("vip-1", audit);
        List<String> audit2 = new ArrayList<>();
        BigDecimal d = Fix.discountFor("vip-1");
        Fix.discountFor("vip-1");
        Fix.recordDiscountAudit("vip-1", audit2);

        List<Integer> ids = new ArrayList<>(List.of(1, 2, 3));
        ids.remove(1);                       // removes index 1 (value 2), not value 1
        List<Integer> ids2 = new ArrayList<>(List.of(1, 2, 3));
        ids2.remove(Integer.valueOf(1));     // removes value 1
        return "POLA violation: 2 reads wrote " + audit.size() + " audit rows"
                + "\nPOLA fix:       2 reads, discount=" + d + ", audit rows=" + audit2.size()
                + "\nJDK trap:       remove(1) -> " + ids + ", remove(Integer.valueOf(1)) -> " + ids2;
    }
}
