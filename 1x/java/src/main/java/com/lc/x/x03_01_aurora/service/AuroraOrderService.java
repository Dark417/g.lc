package com.lc.x.x03_01_aurora.service;

import com.lc.x.shared.Retry;
import com.lc.x.x03_01_aurora.domain.BatchResult;
import com.lc.x.x03_01_aurora.domain.CustomerSummary;
import com.lc.x.x03_01_aurora.domain.InventoryRepository;
import com.lc.x.x03_01_aurora.domain.Job;
import com.lc.x.x03_01_aurora.domain.JobQueue;
import com.lc.x.x03_01_aurora.domain.NewOrder;
import com.lc.x.x03_01_aurora.domain.Order;
import com.lc.x.x03_01_aurora.domain.OrderNotFoundException;
import com.lc.x.x03_01_aurora.domain.OrderRepository;
import com.lc.x.x03_01_aurora.domain.OrderStatus;
import com.lc.x.x03_01_aurora.domain.Page;
import com.lc.x.x03_01_aurora.domain.ReplicaLagProbe;
import com.lc.x.x03_01_aurora.domain.StockLevel;
import com.lc.x.x03_01_aurora.domain.VersionConflictException;
import com.lc.x.x03_01_aurora.infra.AuroraErrors;
import com.lc.x.x03_01_aurora.infra.AuroraJdbcRepository;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Supplier;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;
import org.springframework.transaction.support.TransactionSynchronizationManager;

/**
 * Use cases the API calls. Not transactional itself: it sits OUTSIDE the transactions so it can retry them.
 * - Retry: whole transaction per attempt, only on transient SQLSTATEs, only for idempotent work.
 * - Read routing: reader endpoint by default, writer when the caller needs its own writes.
 */
@Service
@ConditionalOnProperty(name = "x.aurora.enabled", havingValue = "true")
public class AuroraOrderService {

    /** Demo invariant for the SERIALIZABLE example; a real limit lives in a customer table. */
    static final long CREDIT_LIMIT_CENTS = 100_000;
    static final int IMPORT_CHUNK_SIZE = 500;
    static final int MAX_PAGE_SIZE = 100;
    static final int JOB_MAX_ATTEMPTS = 5;

    // Budget meant to span an Aurora failover (AWS: typically < 60 s, often < 30 s): 8 attempts, 200 ms base, 8 s cap.
    // Each attempt can also wait connectionTimeout (3 s) for a connection, so keep the HTTP deadline above this.
    private final Retry retry = new Retry(8, Duration.ofMillis(200), Duration.ofSeconds(8));

    private final AuroraOrderTx tx;
    private final OrderRepository orders;
    private final InventoryRepository inventory;
    private final JobQueue jobs;
    private final ReplicaLagProbe lagProbe;
    private final AuroraJdbcRepository schema;

    public AuroraOrderService(AuroraOrderTx tx, OrderRepository orders, InventoryRepository inventory, JobQueue jobs,
            ReplicaLagProbe lagProbe, AuroraJdbcRepository schema) {
        this.tx = tx;
        this.orders = orders;
        this.inventory = inventory;
        this.jobs = jobs;
        this.lagProbe = lagProbe;
        this.schema = schema;
    }

    // ================================================================ retry at the transaction boundary

    // Runs one attempt per call of `attempt` (each call = a fresh transaction through the AuroraOrderTx proxy)
    // and retries on 40001 / 40P01 / 08xxx / 57P0x / 25006 / 55P03 with full-jitter backoff.
    // When to use: around every transactional use case whose writes are idempotent. Catch: refuses to run inside an
    // active transaction, because retrying inside an aborted transaction only yields 25P02.
    public <T> T withRetry(String operation, Supplier<T> attempt) {
        if (TransactionSynchronizationManager.isActualTransactionActive()) {
            throw new IllegalStateException(operation + ": retry must wrap the transaction, not run inside one");
        }
        return retry.call(attempt, AuroraErrors::isRetryable);
    }

    // ================================================================ create

    // Create without an idempotency key: NOT retried. A lost commit ack leaves the client unsure whether the order exists.
    public Order createOrderOnce(NewOrder cmd) {
        return orders.insert(cmd);
    }

    // Create + reserve stock, retried safely: the idempotency key makes a replayed attempt return the first result.
    // Catch: the key must be unique per logical request (client-generated UUID), not per user or per session.
    public Order placeOrder(NewOrder cmd) {
        requireKey(cmd);
        return withRetry("placeOrder", () -> tx.placeOrder(cmd));
    }

    // SERIALIZABLE credit-limit check: 40001 is the expected outcome under contention, and retry makes it correct.
    public Order placeOrderWithinCreditLimit(NewOrder cmd) {
        requireKey(cmd);
        return withRetry("placeOrderWithinCreditLimit", () -> tx.placeOrderWithinCreditLimit(cmd, CREDIT_LIMIT_CENTS));
    }

    // ================================================================ optimistic update, made retry-safe

    // Version-guarded status change. A retry after a lost commit ack sees version+1 and would report a false conflict,
    // so on attempts > 1 a conflict whose current state equals the requested state counts as success.
    // Catch: a concurrent writer making the identical change is indistinguishable from our own replay (same outcome).
    public Order changeStatus(long id, int expectedVersion, OrderStatus status) {
        AtomicInteger attempts = new AtomicInteger();
        return withRetry("changeStatus", () -> {
            int n = attempts.incrementAndGet();
            try {
                return tx.changeStatus(id, expectedVersion, status);
            } catch (VersionConflictException e) {
                if (n > 1) {
                    Order current = orders.findById(id).orElseThrow(() -> new OrderNotFoundException(id));
                    if (current.status() == status && current.version() == expectedVersion + 1) {
                        return current;
                    }
                }
                throw e;
            }
        });
    }

    // DELETE is idempotent (second call returns false), so it may be retried freely.
    public boolean deleteOrder(long id) {
        return withRetry("deleteOrder", () -> orders.delete(id));
    }

    // ================================================================ batch with partial failure

    // Bulk import in chunks; each chunk = one transaction, retried on transient errors (rows carry idempotency keys,
    // so a replayed chunk is a no-op). A chunk that still fails is reported, the others stay committed.
    // Catch: rows without an idempotency key are not deduplicated on replay; require keys for retried imports.
    public BatchResult importOrders(List<NewOrder> rows) {
        int inserted = 0;
        List<String> failures = new ArrayList<>();
        for (int from = 0; from < rows.size(); from += IMPORT_CHUNK_SIZE) {
            int to = Math.min(from + IMPORT_CHUNK_SIZE, rows.size());
            List<NewOrder> chunk = List.copyOf(rows.subList(from, to));
            try {
                inserted += withRetry("importChunk", () -> tx.importChunk(chunk));
            } catch (RuntimeException e) {
                String state = AuroraErrors.sqlState(e);
                failures.add("rows " + from + ".." + (to - 1) + ": " + (state == null ? "" : state + " ")
                        + e.getClass().getSimpleName());
            }
        }
        return new BatchResult(rows.size(), inserted, failures);
    }

    // ================================================================ reads: routing + read-after-write

    // Read routing. strong=true -> writer. Otherwise reader first; fall back to the writer when the reader misses
    // the row or shows a version older than minVersion (the version the client last wrote = read-your-writes token).
    // Catch: every fallback is writer load; without minVersion a stale-but-present row (old status) is returned.
    public Order getOrder(long id, boolean strong, Integer minVersion) {
        return withRetry("getOrder", () -> {
            if (!strong) {
                var fromReader = orders.findByIdOnReader(id);
                if (fromReader.isPresent() && (minVersion == null || fromReader.get().version() >= minVersion)) {
                    return fromReader.get();
                }
                // miss or stale on the replica: replica lag, not necessarily absence
            }
            return orders.findById(id).orElseThrow(() -> new OrderNotFoundException(id));
        });
    }

    // Keyset page on the reader. Contract: pass back `next` verbatim; null next = last page.
    public Page<Order> listByKeyset(String customerId, String cursor, int size) {
        int n = clampPageSize(size);
        return withRetry("listByKeyset", () -> orders.pageByKeyset(customerId, cursor, n));
    }

    // OFFSET page on the reader, kept for comparison: latency grows with page number.
    public Page<Order> listByOffset(String customerId, int page, int size) {
        int n = clampPageSize(size);
        return withRetry("listByOffset", () -> orders.pageByOffset(customerId, Math.max(0, page), n));
    }

    // JSONB containment search on the reader.
    public List<Order> search(Map<String, Object> containment, int limit) {
        return withRetry("search", () -> orders.findByAttrs(containment, clampPageSize(limit)));
    }

    // Consistent multi-query report (REPEATABLE READ on the reader).
    public CustomerSummary customerSummary(String customerId) {
        return withRetry("customerSummary", () -> tx.customerSummary(customerId));
    }

    // ================================================================ upsert

    // "Set stock to N" upsert: idempotent, so retrying is safe.
    public StockLevel restock(String sku, int onHand) {
        return withRetry("restock", () -> inventory.upsertStock(sku, onHand));
    }

    // ================================================================ job queue

    // Enqueue is NOT retried: the job table has no dedup key, so a lost ack + retry would enqueue twice.
    public long enqueueJob(String kind, Map<String, Object> payload) {
        return jobs.enqueue(kind, payload);
    }

    // Claim is retried: a lost ack leaves jobs RUNNING under our lease; they return to READY when it expires.
    public List<Job> claimJobs(String workerId, int limit, Duration lease) {
        return withRetry("claimJobs", () -> jobs.claim(workerId, Math.min(Math.max(1, limit), MAX_PAGE_SIZE), lease));
    }

    // Complete is retried: DONE keeps locked_by, so a replayed complete is a no-op success.
    public void completeJob(long jobId, String workerId) {
        withRetry("completeJob", () -> {
            jobs.complete(jobId, workerId);
            return null;
        });
    }

    // Fail is not retried: if the ack is lost the lease simply expires and the reaper requeues (same end state).
    public void failJob(long jobId, String workerId, String error) {
        jobs.fail(jobId, workerId, error, Duration.ofSeconds(30), JOB_MAX_ATTEMPTS);
    }

    // Reaper for expired leases; idempotent, run on a schedule by any node.
    public int requeueExpiredJobs() {
        return withRetry("requeueExpiredJobs", () -> jobs.requeueExpired(JOB_MAX_ATTEMPTS));
    }

    // ================================================================ ops

    public Map<String, Long> replicaLag() {
        return lagProbe.replicaLagMillis();
    }

    public void applySchema() {
        schema.applySchema();
    }

    // ================================================================ helpers

    private static void requireKey(NewOrder cmd) {
        if (cmd.idempotencyKey() == null || cmd.idempotencyKey().isBlank()) {
            throw new IllegalArgumentException("Idempotency-Key is required for retried writes");
        }
    }

    private static int clampPageSize(int size) {
        return Math.min(Math.max(1, size), MAX_PAGE_SIZE);
    }
}
