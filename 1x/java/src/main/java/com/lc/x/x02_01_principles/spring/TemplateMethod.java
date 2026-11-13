package com.lc.x.x02_01_principles.spring;

import com.lc.x.shared.Retry;
import java.time.Duration;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;
import org.springframework.jdbc.core.JdbcTemplate;

/**
 * 3.7 Template-style boilerplate removal — the template owns open/retry/translate/close; callers pass a callback.
 * - Violation: every DAO method copies the resource-handling skeleton.
 * - Fix: MiniTemplate.execute(callback), the same shape as JdbcTemplate / TransactionTemplate / RestClient.
 * - Catch: one-line template calls hide cost (N+1 queries in a loop).
 */
public final class TemplateMethod {

    private TemplateMethod() {
    }

    // ===== A fake resource so the demo runs without a DataSource =====

    /** Driver-level transient error (like a SQLState 40001 serialization failure). */
    public static final class TransientDbError extends RuntimeException {
        public TransientDbError(String msg) {
            super(msg);
        }
    }

    /** Framework-level error (like Spring's DataAccessException); callers never see driver types. */
    public static final class DataAccessFailure extends RuntimeException {
        public DataAccessFailure(String msg, Throwable cause) {
            super(msg, cause);
        }
    }

    public static final class FakeConnection implements AutoCloseable {
        private final AtomicInteger open;
        private final boolean fail;

        FakeConnection(AtomicInteger open, boolean fail) {
            this.open = open;
            this.fail = fail;
            open.incrementAndGet();
        }

        public String query(String sql, String arg) {
            if (fail) {
                throw new TransientDbError("serialization failure");
            }
            return sql.replace("?", arg) + " -> row";
        }

        @Override
        public void close() {
            open.decrementAndGet();
        }
    }

    /** Hands out connections; the first `failures` connections fail their query. */
    public static final class FakeDataSource {
        private final AtomicInteger open = new AtomicInteger();
        private final AtomicInteger handedOut = new AtomicInteger();
        private final int failures;

        public FakeDataSource(int failures) {
            this.failures = failures;
        }

        public FakeConnection getConnection() {
            return new FakeConnection(open, handedOut.getAndIncrement() < failures);
        }

        public int openConnections() {
            return open.get();
        }

        public int handedOut() {
            return handedOut.get();
        }
    }

    // ===== Violation: copied skeleton =====

    public static final class Violation {

        private Violation() {
        }

        /** Skeleton copy #1; copy #2 (loadCustomer) would repeat it, and one copy will forget close(). */
        public static String loadOrder(FakeDataSource ds, String id) {
            for (int attempt = 1; ; attempt++) {
                FakeConnection c = ds.getConnection();
                try {
                    return c.query("SELECT * FROM orders WHERE id = ?", id);
                } catch (TransientDbError e) {
                    if (attempt == 3) {
                        throw new DataAccessFailure("loadOrder failed", e);
                    }
                } finally {
                    c.close();
                }
            }
        }
    }

    // ===== Fix: template + callback =====

    public static final class Fix {

        private Fix() {
        }

        @FunctionalInterface
        public interface ConnectionCallback<T> {
            T doInConnection(FakeConnection c);
        }

        /** Owns the fixed steps once; reuses the shared full-jitter Retry for transient errors only. */
        public static final class MiniTemplate {
            private final FakeDataSource ds;
            private final Retry retry;

            public MiniTemplate(FakeDataSource ds, int maxAttempts) {
                this.ds = ds;
                this.retry = new Retry(maxAttempts, Duration.ofMillis(1), Duration.ofMillis(5));
            }

            // The template method: open -> callback -> close always -> translate driver errors.
            // Use for any resource with a fixed lifecycle (connections, HTTP clients, transactions).
            // Catch: retry is only safe because the callback here is a read; writes need idempotency.
            public <T> T execute(ConnectionCallback<T> callback) {
                try {
                    return retry.call(() -> {
                        try (FakeConnection c = ds.getConnection()) {
                            return callback.doInConnection(c);
                        }
                    }, e -> e instanceof TransientDbError);
                } catch (TransientDbError e) {
                    throw new DataAccessFailure("query failed after retries", e);
                }
            }

            public String loadOrder(String id) {
                return execute(c -> c.query("SELECT * FROM orders WHERE id = ?", id));
            }

            public String loadCustomer(String id) {
                return execute(c -> c.query("SELECT * FROM customers WHERE id = ?", id));
            }
        }
    }

    // The real thing: JdbcTemplate does the same steps around a RowMapper callback.
    // Use when a DataSource exists (the Aurora slice); not called here, so no DataSource bean is needed.
    // Catch: calling this inside a loop over customers is N+1; use IN lists or batch queries.
    public static List<String> findOrderIds(JdbcTemplate jdbc, String customerId) {
        return jdbc.query("SELECT id FROM orders WHERE customer_id = ?", (rs, rowNum) -> rs.getString("id"), customerId);
    }

    // Shows a transient failure retried by the template, with every connection closed.
    // Use as the runnable entry point for GET /principles/template.
    // Catch: exception translation hides SQLState; inspect getCause() when retry depends on it.
    public static String demo(int maxAttempts) {
        FakeDataSource ds1 = new FakeDataSource(1);
        String bad = Violation.loadOrder(ds1, "o-1");
        FakeDataSource ds2 = new FakeDataSource(1);
        Fix.MiniTemplate template = new Fix.MiniTemplate(ds2, maxAttempts);
        String good = template.loadOrder("o-1") + " | " + template.loadCustomer("c-1");
        return "Template violation: " + bad + " (skeleton copied per method) open=" + ds1.openConnections()
                + "\nTemplate fix:       " + good + " connections=" + ds2.handedOut() + " open=" + ds2.openConnections();
    }
}
