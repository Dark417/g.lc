package com.lc.x.x03_01_aurora.infra;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.lc.x.x03_01_aurora.domain.AuditLog;
import com.lc.x.x03_01_aurora.domain.BusinessRuleException;
import com.lc.x.x03_01_aurora.domain.InventoryRepository;
import com.lc.x.x03_01_aurora.domain.Job;
import com.lc.x.x03_01_aurora.domain.JobQueue;
import com.lc.x.x03_01_aurora.domain.JobStatus;
import com.lc.x.x03_01_aurora.domain.LeaseLostException;
import com.lc.x.x03_01_aurora.domain.NewOrder;
import com.lc.x.x03_01_aurora.domain.Order;
import com.lc.x.x03_01_aurora.domain.OrderNotFoundException;
import com.lc.x.x03_01_aurora.domain.OrderRepository;
import com.lc.x.x03_01_aurora.domain.OrderStatus;
import com.lc.x.x03_01_aurora.domain.Page;
import com.lc.x.x03_01_aurora.domain.ReplicaLagProbe;
import com.lc.x.x03_01_aurora.domain.StockLevel;
import com.lc.x.x03_01_aurora.domain.VersionConflictException;
import java.nio.charset.StandardCharsets;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.time.Duration;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.Base64;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import javax.sql.DataSource;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.core.io.ClassPathResource;
import org.springframework.dao.EmptyResultDataAccessException;
import org.springframework.jdbc.core.namedparam.MapSqlParameterSource;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.jdbc.datasource.init.ResourceDatabasePopulator;
import org.springframework.stereotype.Repository;
import org.springframework.transaction.support.TransactionSynchronizationManager;

/**
 * Aurora PostgreSQL showcase: one public method per scenario, in the order of docs/03.01.aurora-postgres.md.
 * - writer = cluster endpoint pool: every write and every read that must see the latest commit.
 * - reader = reader endpoint pool: lists, search, reports; may lag the writer by milliseconds.
 * - Methods join the caller's Spring transaction when one is active (same DataSource as the tx manager);
 *   otherwise each statement autocommits.
 */
@Repository
@ConditionalOnProperty(name = "x.aurora.enabled", havingValue = "true")
public class AuroraJdbcRepository implements OrderRepository, InventoryRepository, JobQueue, AuditLog, ReplicaLagProbe {

    private static final String ORDER_COLUMNS =
            "id, customer_id, sku, quantity, amount_cents, status, version, idempotency_key, attrs, created_at, updated_at";
    private static final String JOB_COLUMNS = "id, kind, payload, status, attempts, locked_by, locked_until";
    private static final int JDBC_BATCH_SIZE = 500;
    private static final TypeReference<Map<String, Object>> JSON_MAP = new TypeReference<>() {
    };

    private final NamedParameterJdbcTemplate writer;
    private final NamedParameterJdbcTemplate reader;
    private final ObjectMapper json;

    public AuroraJdbcRepository(
            @Qualifier(AuroraConfig.WRITER_JDBC) NamedParameterJdbcTemplate writer,
            @Qualifier(AuroraConfig.READER_JDBC) NamedParameterJdbcTemplate reader,
            ObjectMapper json) {
        this.writer = writer;
        this.reader = reader;
        this.json = json;
    }

    // =================================================================== schema

    // Runs src/main/resources/x03_01_aurora/schema.sql on the writer (idempotent: IF NOT EXISTS everywhere).
    // When to use: local setup and demos. Catch: N pods racing DDL at startup; real projects run Flyway/Liquibase once.
    public void applySchema() {
        DataSource ds = Objects.requireNonNull(writer.getJdbcTemplate().getDataSource(), "writer DataSource");
        new ResourceDatabasePopulator(new ClassPathResource("x03_01_aurora/schema.sql")).execute(ds);
    }

    // =================================================================== CRUD

    // Plain INSERT ... RETURNING: one round trip returns the generated id, defaults and timestamps.
    // When to use: creates that are never retried. Catch: without an idempotency key a lost commit ack is unrecoverable.
    @Override
    public Order insert(NewOrder o) {
        String sql = "INSERT INTO x_order (customer_id, sku, quantity, amount_cents, idempotency_key, attrs) "
                + "VALUES (:customerId, :sku, :quantity, :amountCents, :idempotencyKey, CAST(:attrs AS jsonb)) "
                + "RETURNING " + ORDER_COLUMNS;
        return writer.queryForObject(sql, orderParams(o), this::mapOrder);
    }

    // Idempotent create: ON CONFLICT (idempotency_key) DO NOTHING RETURNING; empty = the key already exists.
    // When to use: any create that may be retried (failover, timeouts). Catch: on conflict RETURNING yields nothing,
    // so the caller re-reads by key; under REPEATABLE READ/SERIALIZABLE a conflicting row the snapshot can't see
    // raises 40001 instead (retry, and the next attempt's re-read finds it).
    @Override
    public Optional<Order> insertIdempotent(NewOrder o) {
        Objects.requireNonNull(o.idempotencyKey(), "idempotencyKey is required for an idempotent insert");
        String sql = "INSERT INTO x_order (customer_id, sku, quantity, amount_cents, idempotency_key, attrs) "
                + "VALUES (:customerId, :sku, :quantity, :amountCents, :idempotencyKey, CAST(:attrs AS jsonb)) "
                + "ON CONFLICT (idempotency_key) DO NOTHING "
                + "RETURNING " + ORDER_COLUMNS;
        return writer.query(sql, orderParams(o), this::mapOrder).stream().findFirst();
    }

    // Read by primary key on the writer: always sees the latest commit.
    // When to use: read-your-writes, or right before a write decision. Catch: every such read is writer load.
    @Override
    public Optional<Order> findById(long id) {
        String sql = "SELECT " + ORDER_COLUMNS + " FROM x_order WHERE id = :id";
        return writer.query(sql, Map.of("id", id), this::mapOrder).stream().findFirst();
    }

    // Read by idempotency key (unique index): resolves the replay of an earlier attempt.
    // Catch: in READ COMMITTED each statement takes a new snapshot, so it sees a row committed a moment ago.
    @Override
    public Optional<Order> findByIdempotencyKey(String idempotencyKey) {
        String sql = "SELECT " + ORDER_COLUMNS + " FROM x_order WHERE idempotency_key = :key";
        return writer.query(sql, Map.of("key", idempotencyKey), this::mapOrder).stream().findFirst();
    }

    // DELETE by id; returns whether a row was removed. Naturally idempotent, so safe to retry.
    // Catch: MVCC leaves the old row version as a dead tuple until VACUUM reclaims it.
    @Override
    public boolean delete(long id) {
        return writer.update("DELETE FROM x_order WHERE id = :id", Map.of("id", id)) == 1;
    }

    // =================================================================== batch insert

    // JDBC batch: one prepared statement, rows sent in groups of JDBC_BATCH_SIZE; with reWriteBatchedInserts=true
    // pgjdbc rewrites them into multi-row VALUES. When to use: bulk loads inside one transaction (all-or-nothing).
    // Catch: with the rewrite the driver reports SUCCESS_NO_INFO (-2) per row, so the exact inserted count
    // (ON CONFLICT skips) is unknown; for millions of rows COPY is faster still.
    @Override
    public int batchInsert(List<NewOrder> orders) {
        String sql = "INSERT INTO x_order (customer_id, sku, quantity, amount_cents, idempotency_key, attrs) "
                + "VALUES (?, ?, ?, ?, ?, CAST(? AS jsonb)) ON CONFLICT (idempotency_key) DO NOTHING";
        int[][] counts = writer.getJdbcTemplate().batchUpdate(sql, orders, JDBC_BATCH_SIZE, (ps, o) -> {
            ps.setString(1, o.customerId());
            ps.setString(2, o.sku());
            ps.setInt(3, o.quantity());
            ps.setLong(4, o.amountCents());
            ps.setString(5, o.idempotencyKey());
            ps.setString(6, toJson(o.attrs()));
        });
        int known = 0;
        for (int[] group : counts) {
            for (int c : group) {
                if (c == Statement.SUCCESS_NO_INFO) {
                    return orders.size(); // rows sent; per-row outcome not reported by the rewritten batch
                }
                known += Math.max(c, 0);
            }
        }
        return known;
    }

    // =================================================================== upsert

    // INSERT ... ON CONFLICT (sku) DO UPDATE: atomic insert-or-update, no SELECT-then-INSERT race.
    // When to use: "set to this value" writes keyed by a natural key. Catch: SET on_hand = EXCLUDED.on_hand is
    // idempotent; an additive SET on_hand = x_inventory.on_hand + EXCLUDED.on_hand is NOT safe to retry.
    @Override
    public StockLevel upsertStock(String sku, int onHand) {
        String sql = "INSERT INTO x_inventory (sku, on_hand) VALUES (:sku, :onHand) "
                + "ON CONFLICT (sku) DO UPDATE SET on_hand = EXCLUDED.on_hand, updated_at = now() "
                + "RETURNING sku, on_hand, updated_at";
        return writer.queryForObject(sql, Map.of("sku", sku, "onHand", onHand),
                (rs, n) -> new StockLevel(rs.getString("sku"), rs.getInt("on_hand"), instant(rs, "updated_at")));
    }

    // =================================================================== pagination

    // OFFSET page (reader): ORDER BY created_at DESC, id DESC LIMIT n OFFSET page*n.
    // When to use: small sets or admin UIs that need "jump to page k". Catch: the server reads and discards
    // page*n rows, so cost grows with depth; inserts between requests shift rows (duplicates / skips).
    @Override
    public Page<Order> pageByOffset(String customerId, int page, int size) {
        String sql = "SELECT " + ORDER_COLUMNS + " FROM x_order WHERE customer_id = :customerId "
                + "ORDER BY created_at DESC, id DESC LIMIT :limit OFFSET :offset";
        MapSqlParameterSource params = new MapSqlParameterSource()
                .addValue("customerId", customerId)
                .addValue("limit", size + 1)                 // one extra row tells us whether a next page exists
                .addValue("offset", (long) page * size);
        List<Order> rows = reader.query(sql, params, this::mapOrder);
        boolean more = rows.size() > size;
        return new Page<>(more ? rows.subList(0, size) : rows, more ? Integer.toString(page + 1) : null);
    }

    // Keyset (seek) page (reader): WHERE (created_at, id) < (cursor) ORDER BY created_at DESC, id DESC LIMIT n.
    // When to use: APIs and infinite scroll. Catch: needs the unique tie-breaker id (rows of one transaction share
    // now()) and the index (customer_id, created_at, id); cannot jump to page k.
    @Override
    public Page<Order> pageByKeyset(String customerId, String cursor, int size) {
        MapSqlParameterSource params = new MapSqlParameterSource()
                .addValue("customerId", customerId)
                .addValue("limit", size + 1);
        String seek = "";
        if (cursor != null && !cursor.isBlank()) {
            Cursor c = Cursor.decode(cursor);
            seek = " AND (created_at, id) < (:createdAt, :id)";
            params.addValue("createdAt", OffsetDateTime.ofInstant(c.createdAt(), ZoneOffset.UTC)).addValue("id", c.id());
        }
        String sql = "SELECT " + ORDER_COLUMNS + " FROM x_order WHERE customer_id = :customerId" + seek
                + " ORDER BY created_at DESC, id DESC LIMIT :limit";
        List<Order> rows = reader.query(sql, params, this::mapOrder);
        if (rows.size() <= size) {
            return new Page<>(rows, null);
        }
        List<Order> pageRows = rows.subList(0, size);
        Order last = pageRows.get(size - 1);
        return new Page<>(pageRows, new Cursor(last.createdAt(), last.id()).encode());
    }

    /** Opaque keyset cursor: base64url("createdAt|id"). Opaque so the sort key can change without breaking clients. */
    record Cursor(Instant createdAt, long id) {

        String encode() {
            String raw = createdAt + "|" + id;
            return Base64.getUrlEncoder().withoutPadding().encodeToString(raw.getBytes(StandardCharsets.UTF_8));
        }

        static Cursor decode(String token) {
            try {
                String raw = new String(Base64.getUrlDecoder().decode(token), StandardCharsets.UTF_8);
                int bar = raw.lastIndexOf('|');
                return new Cursor(Instant.parse(raw.substring(0, bar)), Long.parseLong(raw.substring(bar + 1)));
            } catch (RuntimeException e) {
                throw new IllegalArgumentException("invalid cursor", e);
            }
        }
    }

    // =================================================================== optimistic lock

    // UPDATE ... WHERE id = ? AND version = ? RETURNING: succeeds only if nobody changed the row since the read.
    // When to use: low-contention edits with think time between read and write (no lock held meanwhile).
    // Catch: 0 rows is ambiguous (deleted vs changed), so a follow-up read tells 404 from 409.
    @Override
    public Order updateStatusIfVersion(long id, int expectedVersion, OrderStatus newStatus) {
        String sql = "UPDATE x_order SET status = :status, version = version + 1, updated_at = now() "
                + "WHERE id = :id AND version = :expected RETURNING " + ORDER_COLUMNS;
        Map<String, Object> params = Map.of("status", newStatus.name(), "id", id, "expected", expectedVersion);
        Optional<Order> updated = writer.query(sql, params, this::mapOrder).stream().findFirst();
        if (updated.isPresent()) {
            return updated.get();
        }
        Order current = findById(id).orElseThrow(() -> new OrderNotFoundException(id));
        throw new VersionConflictException(
                "order " + id + " is at version " + current.version() + ", expected " + expectedVersion);
    }

    // =================================================================== pessimistic lock

    // SELECT ... FOR UPDATE with SET LOCAL lock_timeout: lock the stock row until the transaction ends.
    // When to use: read-check-write on one hot row. Catch: must run inside a transaction (else the lock is released
    // at statement end); lock_timeout turns an endless wait into 55P03; lock several rows in key order (deadlock 40P01).
    @Override
    public int lockStockForUpdate(String sku) {
        requireTransaction("lockStockForUpdate");
        writer.getJdbcTemplate().execute("SET LOCAL lock_timeout = '2s'"); // LOCAL: reverts at commit/rollback
        try {
            Integer onHand = writer.queryForObject(
                    "SELECT on_hand FROM x_inventory WHERE sku = :sku FOR UPDATE", Map.of("sku", sku), Integer.class);
            return Objects.requireNonNull(onHand);
        } catch (EmptyResultDataAccessException e) {
            throw new BusinessRuleException("unknown sku " + sku);
        }
    }

    // Plain decrement, meant to follow lockStockForUpdate in the same transaction.
    // Catch: alone (without the lock and the check) it is a blind write; the CHECK (on_hand >= 0) is the last guard.
    @Override
    public void decrementStock(String sku, int quantity) {
        requireTransaction("decrementStock");
        writer.update("UPDATE x_inventory SET on_hand = on_hand - :q, updated_at = now() WHERE sku = :sku",
                Map.of("q", quantity, "sku", sku));
    }

    // Atomic conditional UPDATE: check and write in one statement, no explicit lock, no transaction needed.
    // When to use: the check is expressible in WHERE (often better than FOR UPDATE). Catch: READ COMMITTED re-evaluates
    // the WHERE on the newest row version after a concurrent update, which is exactly why this is safe.
    @Override
    public boolean decrementStockIfAvailable(String sku, int quantity) {
        return writer.update(
                "UPDATE x_inventory SET on_hand = on_hand - :q, updated_at = now() WHERE sku = :sku AND on_hand >= :q",
                Map.of("q", quantity, "sku", sku)) == 1;
    }

    // =================================================================== SERIALIZABLE support

    // Sum of open orders for one customer: the read half of the credit-limit invariant.
    // Catch: under SERIALIZABLE this read takes SIREAD predicate locks on the index range; with no index on
    // customer_id it would lock the whole table and cause many false-positive 40001s.
    @Override
    public long sumOpenAmountCents(String customerId) {
        Long sum = writer.queryForObject(
                "SELECT COALESCE(SUM(amount_cents), 0) FROM x_order WHERE customer_id = :c AND status IN ('NEW', 'PAID')",
                Map.of("c", customerId), Long.class);
        return sum == null ? 0L : sum;
    }

    // =================================================================== job queue (SKIP LOCKED + lease)

    // Enqueue a job row. Catch: no dedup key here, so the caller must not blindly retry (a lost ack => duplicate job).
    @Override
    public long enqueue(String kind, Map<String, Object> payload) {
        Long id = writer.queryForObject(
                "INSERT INTO x_job (kind, payload) VALUES (:kind, CAST(:payload AS jsonb)) RETURNING id",
                new MapSqlParameterSource().addValue("kind", kind).addValue("payload", toJson(payload)), Long.class);
        return Objects.requireNonNull(id);
    }

    // Claim up to `limit` jobs in ONE statement: lock READY rows with FOR UPDATE SKIP LOCKED, mark them RUNNING with a lease.
    // When to use: N workers polling one table; each gets different rows, nobody waits. Catch: process AFTER this
    // statement commits (never hold the row lock while working); delivery is at least once, so handlers are idempotent.
    @Override
    public List<Job> claim(String workerId, int limit, Duration lease) {
        String sql = "WITH next AS ("
                + "  SELECT id FROM x_job WHERE status = 'READY' AND run_after <= now()"
                + "  ORDER BY run_after, id LIMIT :limit FOR UPDATE SKIP LOCKED) "
                + "UPDATE x_job j SET status = 'RUNNING', locked_by = :worker, attempts = j.attempts + 1, "
                + "  locked_until = now() + (:leaseSeconds * interval '1 second') "
                + "FROM next WHERE j.id = next.id "
                + "RETURNING j.id, j.kind, j.payload, j.status, j.attempts, j.locked_by, j.locked_until";
        MapSqlParameterSource params = new MapSqlParameterSource()
                .addValue("limit", limit)
                .addValue("worker", workerId)
                .addValue("leaseSeconds", lease.toSeconds());
        return writer.query(sql, params, this::mapJob);
    }

    // Complete only if this worker still owns the lease; DONE keeps locked_by so a retried complete is a no-op success.
    // Catch: 0 rows = the lease expired and another worker re-claimed the job (our work may be duplicated).
    @Override
    public void complete(long jobId, String workerId) {
        int rows = writer.update(
                "UPDATE x_job SET status = 'DONE', locked_until = NULL "
                        + "WHERE id = :id AND locked_by = :worker AND status IN ('RUNNING', 'DONE')",
                Map.of("id", jobId, "worker", workerId));
        if (rows == 0) {
            throw new LeaseLostException(jobId, workerId);
        }
    }

    // Release a failed job: back to READY after retryDelay (backoff), or FAILED once attempts reach maxAttempts.
    // Catch: guarded by lease ownership like complete(); a lost ack is harmless because the lease expires anyway.
    @Override
    public void fail(long jobId, String workerId, String error, Duration retryDelay, int maxAttempts) {
        int rows = writer.update(
                "UPDATE x_job SET status = CASE WHEN attempts >= :max THEN 'FAILED' ELSE 'READY' END, "
                        + "run_after = now() + (:delaySeconds * interval '1 second'), "
                        + "locked_by = NULL, locked_until = NULL, last_error = :error "
                        + "WHERE id = :id AND locked_by = :worker AND status = 'RUNNING'",
                new MapSqlParameterSource()
                        .addValue("max", maxAttempts)
                        .addValue("delaySeconds", retryDelay.toSeconds())
                        .addValue("error", error)
                        .addValue("id", jobId)
                        .addValue("worker", workerId));
        if (rows == 0) {
            throw new LeaseLostException(jobId, workerId);
        }
    }

    // Reaper: jobs whose lease expired (worker crashed or hung) go back to READY, or FAILED after maxAttempts.
    // When to use: run periodically from any one node. Catch: lease must exceed the slowest legitimate job,
    // or a live worker loses its job to a second worker.
    @Override
    public int requeueExpired(int maxAttempts) {
        return writer.update(
                "UPDATE x_job SET status = CASE WHEN attempts >= :max THEN 'FAILED' ELSE 'READY' END, "
                        + "locked_by = NULL, locked_until = NULL, last_error = 'lease expired' "
                        + "WHERE status = 'RUNNING' AND locked_until < now()",
                Map.of("max", maxAttempts));
    }

    // =================================================================== JSONB + GIN

    // Containment query attrs @> '{"channel":"web"}' served by the GIN (jsonb_path_ops) index; runs on the reader.
    // When to use: filtering on sparse, schema-less attributes. Catch: the JSONB '?' (key exists) operator clashes
    // with JDBC '?' placeholders, so prefer @> or jsonb_exists(); hot filter keys deserve real typed columns.
    @Override
    public List<Order> findByAttrs(Map<String, Object> containment, int limit) {
        String sql = "SELECT " + ORDER_COLUMNS + " FROM x_order WHERE attrs @> CAST(:filter AS jsonb) "
                + "ORDER BY id DESC LIMIT :limit";
        MapSqlParameterSource params = new MapSqlParameterSource()
                .addValue("filter", toJson(containment))
                .addValue("limit", limit);
        return reader.query(sql, params, this::mapOrder);
    }

    // =================================================================== reader endpoint

    // Read by id on the reader endpoint: offloads the writer. When to use: data that tolerates lag.
    // Catch: read-after-write is NOT guaranteed (replica lag, usually < 100 ms); the service falls back to the writer.
    @Override
    public Optional<Order> findByIdOnReader(long id) {
        String sql = "SELECT " + ORDER_COLUMNS + " FROM x_order WHERE id = :id";
        return reader.query(sql, Map.of("id", id), this::mapOrder).stream().findFirst();
    }

    // Count + sum for a customer on the reader. Part of a multi-query report: run it inside a REPEATABLE READ
    // reader transaction so it agrees with latestOnReader. Catch: outside a transaction each query sees a different moment.
    @Override
    public long[] countAndSumOnReader(String customerId) {
        return reader.queryForObject(
                "SELECT COUNT(*) AS n, COALESCE(SUM(amount_cents), 0) AS total FROM x_order WHERE customer_id = :c",
                Map.of("c", customerId), (rs, i) -> new long[] {rs.getLong("n"), rs.getLong("total")});
    }

    // Latest N orders for a customer on the reader (second query of the report).
    @Override
    public List<Order> latestOnReader(String customerId, int limit) {
        String sql = "SELECT " + ORDER_COLUMNS + " FROM x_order WHERE customer_id = :c "
                + "ORDER BY created_at DESC, id DESC LIMIT :limit";
        return reader.query(sql, Map.of("c", customerId, "limit", limit), this::mapOrder);
    }

    // Replica lag per reader from aurora_replica_status() (Aurora-only function), queried on the writer.
    // When to use: decide whether a reader can serve read-after-write traffic; alarm on CloudWatch AuroraReplicaLag.
    // Catch: a point-in-time sample (lag spikes under write bursts), and the function may need extra privileges for x_app.
    @Override
    public Map<String, Long> replicaLagMillis() {
        Map<String, Long> lag = new LinkedHashMap<>();
        writer.query("SELECT server_id, replica_lag_in_msec FROM aurora_replica_status() "
                        + "WHERE session_id <> 'MASTER_SESSION_ID'",
                rs -> {
                    lag.put(rs.getString("server_id"), Math.round(rs.getDouble("replica_lag_in_msec")));
                });
        return lag;
    }

    // =================================================================== audit

    // Append an audit row on the writer. Whether it survives a rollback is decided by the CALLER's propagation
    // (REQUIRED joins and rolls back with it; REQUIRES_NEW commits on its own): see AuroraAuditService.
    @Override
    public void append(String action, String detail) {
        writer.update("INSERT INTO x_audit (action, detail) VALUES (:action, :detail)",
                new MapSqlParameterSource().addValue("action", action).addValue("detail", detail));
    }

    // =================================================================== helpers

    private static void requireTransaction(String op) {
        if (!TransactionSynchronizationManager.isActualTransactionActive()) {
            throw new IllegalStateException(op + " needs an active writer transaction (the row lock would end at once)");
        }
    }

    private MapSqlParameterSource orderParams(NewOrder o) {
        return new MapSqlParameterSource()
                .addValue("customerId", o.customerId())
                .addValue("sku", o.sku())
                .addValue("quantity", o.quantity())
                .addValue("amountCents", o.amountCents())
                .addValue("idempotencyKey", o.idempotencyKey())
                .addValue("attrs", toJson(o.attrs()));
    }

    private Order mapOrder(ResultSet rs, int rowNum) throws SQLException {
        return new Order(
                rs.getLong("id"),
                rs.getString("customer_id"),
                rs.getString("sku"),
                rs.getInt("quantity"),
                rs.getLong("amount_cents"),
                OrderStatus.valueOf(rs.getString("status")),
                rs.getInt("version"),
                rs.getString("idempotency_key"),
                fromJson(rs.getString("attrs")),
                instant(rs, "created_at"),
                instant(rs, "updated_at"));
    }

    private Job mapJob(ResultSet rs, int rowNum) throws SQLException {
        return new Job(
                rs.getLong("id"),
                rs.getString("kind"),
                fromJson(rs.getString("payload")),
                JobStatus.valueOf(rs.getString("status")),
                rs.getInt("attempts"),
                rs.getString("locked_by"),
                instant(rs, "locked_until"));
    }

    private static Instant instant(ResultSet rs, String column) throws SQLException {
        OffsetDateTime t = rs.getObject(column, OffsetDateTime.class); // timestamptz -> OffsetDateTime (UTC), micros kept
        return t == null ? null : t.toInstant();
    }

    private String toJson(Map<String, Object> value) {
        try {
            return json.writeValueAsString(value == null ? Map.of() : value);
        } catch (JsonProcessingException e) {
            throw new IllegalArgumentException("value is not JSON-serializable", e);
        }
    }

    private Map<String, Object> fromJson(String value) {
        if (value == null) {
            return Map.of();
        }
        try {
            return json.readValue(value, JSON_MAP);
        } catch (JsonProcessingException e) {
            throw new IllegalStateException("bad JSONB from database", e);
        }
    }
}
