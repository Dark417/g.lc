package com.lc.x.x02_01_principles.general;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;

/**
 * 2.7 Program to an interface — depend on the narrowest contract you need.
 * - Violation: totalOf(ArrayList) returns HashMap; callers with a Set or List.of must copy.
 * - Fix: totalOf(Collection) returns Map; the implementation (TreeMap) can change freely.
 * - Catch: interfaces don't state cost — List.get(i) is O(1) on ArrayList, O(n) on LinkedList.
 */
public final class ProgramToInterface {

    private ProgramToInterface() {
    }

    public record Order(String customerId, BigDecimal amount) {
    }

    // ===== Violation =====

    public static final class Violation {

        private Violation() {
        }

        /** Bound to concrete types on both sides. */
        public static HashMap<String, BigDecimal> totalOf(ArrayList<Order> orders) {
            HashMap<String, BigDecimal> totals = new HashMap<>();
            for (Order o : orders) {
                totals.merge(o.customerId(), o.amount(), BigDecimal::add);
            }
            return totals;
        }
    }

    // ===== Fix =====

    public static final class Fix {

        private Fix() {
        }

        /** Widest useful input, interface output; switching HashMap -> TreeMap breaks no caller. */
        public static Map<String, BigDecimal> totalOf(Collection<Order> orders) {
            Map<String, BigDecimal> totals = new TreeMap<>();
            for (Order o : orders) {
                totals.merge(o.customerId(), o.amount(), BigDecimal::add);
            }
            return totals;
        }
    }

    // Shows a caller holding an immutable List / Set: the violation forces a copy, the fix does not.
    // Use for parameters and return types of every public method.
    // Catch: returning too narrow a type (Iterable) forces callers to copy again.
    public static String demo() {
        List<Order> orders = List.of(new Order("c-1", BigDecimal.ONE), new Order("c-1", BigDecimal.TEN));
        Map<String, BigDecimal> bad = Violation.totalOf(new ArrayList<>(orders)); // forced copy
        Map<String, BigDecimal> good = Fix.totalOf(orders);
        Map<String, BigDecimal> fromSet = Fix.totalOf(Set.of(new Order("c-2", BigDecimal.ONE)));
        return "Interface violation: " + bad + " (needed new ArrayList<>(...))"
                + "\nInterface fix:       " + good + " and from a Set " + fromSet;
    }
}
