package com.lc.x.x02_01_principles.solid;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

/**
 * 1.4 ISP — clients depend only on the methods they call.
 * - Violation: one fat OrderStore; the read-only report must fake save/purge/export too.
 * - Fix: role interfaces (reader, writer, admin); one adapter implements all three.
 * - Catch: split by client role, not one interface per method.
 */
public final class Isp {

    private Isp() {
    }

    public record Order(String id, String status) {
    }

    // ===== Violation: fat interface =====

    public static final class Violation {

        private Violation() {
        }

        /** Every client sees every method; a change to purge() touches the report's fakes. */
        public interface OrderStore {
            Optional<Order> find(String id);

            List<Order> findAll();

            void save(Order order);

            int purgeOlderThanDays(int days);

            String exportCsv();
        }

        /** The report's test fake must stub four methods it never calls. */
        public static final class ReportFake implements OrderStore {
            public Optional<Order> find(String id) {
                return Optional.empty();
            }

            public List<Order> findAll() {
                return List.of(new Order("o-1", "PAID"));
            }

            public void save(Order order) {
                throw new UnsupportedOperationException();
            }

            public int purgeOlderThanDays(int days) {
                throw new UnsupportedOperationException();
            }

            public String exportCsv() {
                throw new UnsupportedOperationException();
            }
        }
    }

    // ===== Fix: role interfaces sized to each client =====

    public static final class Fix {

        private Fix() {
        }

        public interface OrderReader {
            Optional<Order> find(String id);

            List<Order> findAll();
        }

        public interface OrderWriter {
            void save(Order order);
        }

        public interface OrderAdmin {
            int purgeOlderThanDays(int days);
        }

        /** One adapter can still implement every role; clients just see less of it. */
        public static final class InMemoryOrderStore implements OrderReader, OrderWriter, OrderAdmin {
            private final Map<String, Order> rows = new LinkedHashMap<>();

            public Optional<Order> find(String id) {
                return Optional.ofNullable(rows.get(id));
            }

            public List<Order> findAll() {
                return new ArrayList<>(rows.values());
            }

            public void save(Order order) {
                rows.put(order.id(), order);
            }

            public int purgeOlderThanDays(int days) {
                return 0;
            }
        }

        /** Client depends on the reader role only; its fake is a one-liner lambda-sized class. */
        public static final class NightlyReport {
            private final OrderReader reader;

            public NightlyReport(OrderReader reader) {
                this.reader = reader;
            }

            public String run() {
                long paid = reader.findAll().stream().filter(o -> o.status().equals("PAID")).count();
                return "paid=" + paid;
            }
        }
    }

    // Shows the fat fake vs a reader-only dependency.
    // Use when different clients use disjoint parts of an interface.
    // Catch: in Python a Protocol lets the client declare this without the provider changing.
    public static String demo() {
        Violation.OrderStore fat = new Violation.ReportFake();
        Fix.InMemoryOrderStore store = new Fix.InMemoryOrderStore();
        store.save(new Order("o-1", "PAID"));
        store.save(new Order("o-2", "NEW"));
        return "ISP violation: fake stubs 5 methods, uses 1 -> rows=" + fat.findAll().size()
                + "\nISP fix:       NightlyReport(OrderReader) -> " + new Fix.NightlyReport(store).run();
    }
}
