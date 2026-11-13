package com.lc.x.x02_01_principles.solid;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * 1.5 DIP — policy owns the interface; details implement it.
 * - Violation: OrderService news up a Postgres table and an SMTP mailer (domain depends on details).
 * - Fix: OrderService depends on OrderRepository + Notifier ports; adapters are injected.
 * - Catch: invert at I/O and vendor boundaries only; shape ports on domain needs, not vendor APIs.
 */
public final class Dip {

    private Dip() {
    }

    public record Order(String id, String customerId) {
    }

    // ===== Violation: high-level policy depends on low-level details =====

    public static final class Violation {

        private Violation() {
        }

        /** Stand-in for a JDBC table class; imagine it opens a real connection. */
        public static final class PostgresOrderTable {
            public void insert(String id) {
                // would execute INSERT INTO orders ...
            }
        }

        /** Stand-in for an SMTP client. */
        public static final class SmtpMailer {
            public void send(String to, String body) {
                // would open an SMTP socket
            }
        }

        /** Untestable without Postgres and SMTP; swapping either means editing this class. */
        public static final class OrderService {
            private final PostgresOrderTable table = new PostgresOrderTable();
            private final SmtpMailer mailer = new SmtpMailer();

            public String place(Order order) {
                table.insert(order.id());
                mailer.send(order.customerId(), "placed " + order.id());
                return "placed " + order.id() + " via hard-wired Postgres + SMTP";
            }
        }
    }

    // ===== Fix: ports owned by the domain, adapters at the edge =====

    public static final class Fix {

        private Fix() {
        }

        /** Port shaped on domain needs (save an order), not on a vendor API (putItem, KeyCondition). */
        public interface OrderRepository {
            void save(Order order);
        }

        public interface Notifier {
            void notify(String customerId, String message);
        }

        /** Policy: imports only its own ports. */
        public static final class OrderService {
            private final OrderRepository repo;
            private final Notifier notifier;

            public OrderService(OrderRepository repo, Notifier notifier) {
                this.repo = repo;
                this.notifier = notifier;
            }

            public String place(Order order) {
                repo.save(order);
                notifier.notify(order.customerId(), "placed " + order.id());
                return "placed " + order.id();
            }
        }

        /** Adapter used in tests and in this demo; a JDBC or DynamoDB adapter would sit in infra. */
        public static final class InMemoryOrderRepository implements OrderRepository {
            private final Map<String, Order> rows = new LinkedHashMap<>();

            public void save(Order order) {
                rows.put(order.id(), order);
            }

            public int size() {
                return rows.size();
            }
        }

        public static final class RecordingNotifier implements Notifier {
            private final List<String> sent = new ArrayList<>();

            public void notify(String customerId, String message) {
                sent.add(customerId + ":" + message);
            }

            public List<String> sent() {
                return sent;
            }
        }
    }

    // Shows the policy running with in-memory adapters: no database, no SMTP.
    // Use at architectural boundaries (I/O, vendors, other teams).
    // Catch: a one-to-one "header interface" for every class is indirection without benefit.
    public static String demo() {
        Fix.InMemoryOrderRepository repo = new Fix.InMemoryOrderRepository();
        Fix.RecordingNotifier notifier = new Fix.RecordingNotifier();
        String result = new Fix.OrderService(repo, notifier).place(new Order("o-1", "c-9"));
        return "DIP violation: " + new Violation.OrderService().place(new Order("o-0", "c-0"))
                + "\nDIP fix:       " + result + " stored=" + repo.size() + " notified=" + notifier.sent();
    }
}
