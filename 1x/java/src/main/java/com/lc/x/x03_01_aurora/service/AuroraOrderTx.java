package com.lc.x.x03_01_aurora.service;

import com.lc.x.x03_01_aurora.domain.BusinessRuleException;
import com.lc.x.x03_01_aurora.domain.CustomerSummary;
import com.lc.x.x03_01_aurora.domain.InventoryRepository;
import com.lc.x.x03_01_aurora.domain.NewOrder;
import com.lc.x.x03_01_aurora.domain.Order;
import com.lc.x.x03_01_aurora.domain.OrderRepository;
import com.lc.x.x03_01_aurora.domain.OrderStatus;
import com.lc.x.x03_01_aurora.infra.AuroraConfig;
import java.util.List;
import java.util.Optional;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Isolation;
import org.springframework.transaction.annotation.Transactional;

/**
 * Transaction boundaries: one public method = one database transaction.
 * - Never retried from inside: after an error PostgreSQL rejects every statement until rollback (25P02).
 *   AuroraOrderService wraps these calls in a retry, so each attempt is a fresh transaction.
 * - Every method names the transaction manager: several exist (writer, reader), so a bare @Transactional is ambiguous.
 */
@Service
@ConditionalOnProperty(name = "x.aurora.enabled", havingValue = "true")
public class AuroraOrderTx {

    private final OrderRepository orders;
    private final InventoryRepository inventory;
    private final AuroraAuditService audit;

    public AuroraOrderTx(OrderRepository orders, InventoryRepository inventory, AuroraAuditService audit) {
        this.orders = orders;
        this.inventory = inventory;
        this.audit = audit;
    }

    // ================================================================ REQUIRED vs REQUIRES_NEW, FOR UPDATE

    // Place an order and reserve stock atomically (READ COMMITTED, PostgreSQL's default).
    // Shows: idempotent insert, FOR UPDATE on the stock row, REQUIRES_NEW attempt log vs REQUIRED placed log.
    // Catch: on insufficient stock the order insert and ORDER_PLACED roll back; ORDER_ATTEMPT stays (own transaction).
    @Transactional(transactionManager = AuroraConfig.WRITER_TX)
    public Order placeOrder(NewOrder cmd) {
        audit.recordIndependent("ORDER_ATTEMPT", cmd.idempotencyKey()); // commits now on a second connection
        Optional<Order> created = orders.insertIdempotent(cmd);
        if (created.isEmpty()) {
            // Replay: an earlier attempt committed (its ack may have been lost in a failover). Do not reserve twice.
            return replayOf(cmd);
        }
        int onHand = inventory.lockStockForUpdate(cmd.sku()); // row lock until commit; concurrent buyers queue here
        if (onHand < cmd.quantity()) {
            throw new BusinessRuleException("insufficient stock for " + cmd.sku() + ": " + onHand + " < " + cmd.quantity());
        }
        inventory.decrementStock(cmd.sku(), cmd.quantity());
        audit.recordJoined("ORDER_PLACED", "order " + created.get().id());
        return created.get();
    }

    // ================================================================ SERIALIZABLE (write skew)

    // Enforce "open orders of a customer <= credit limit" across rows. Under READ COMMITTED or REPEATABLE READ two
    // concurrent calls both read the old total and both insert (write skew); SERIALIZABLE (SSI) aborts one with 40001.
    // Catch: correctness now depends on the caller retrying 40001; the retry re-reads and sees the other order.
    @Transactional(transactionManager = AuroraConfig.WRITER_TX, isolation = Isolation.SERIALIZABLE)
    public Order placeOrderWithinCreditLimit(NewOrder cmd, long creditLimitCents) {
        Optional<Order> existing = orders.findByIdempotencyKey(cmd.idempotencyKey());
        if (existing.isPresent()) {
            return checkSameRequest(existing.get(), cmd); // replay after a lost commit ack
        }
        long open = orders.sumOpenAmountCents(cmd.customerId());
        if (open + cmd.amountCents() > creditLimitCents) {
            throw new BusinessRuleException("credit limit exceeded: open " + open + " + " + cmd.amountCents()
                    + " > " + creditLimitCents);
        }
        // A concurrent insert of the same key that our snapshot cannot see raises 40001 here, not a silent no-op.
        return orders.insertIdempotent(cmd).orElseGet(() -> replayOf(cmd));
    }

    // ================================================================ optimistic lock + REQUIRED audit

    // Status change guarded by the version column; the audit row joins the same transaction (both or neither).
    // Catch: VersionConflictException is unchecked => rollback (nothing was written anyway); the API returns 409.
    @Transactional(transactionManager = AuroraConfig.WRITER_TX)
    public Order changeStatus(long id, int expectedVersion, OrderStatus status) {
        Order updated = orders.updateStatusIfVersion(id, expectedVersion, status);
        audit.recordJoined("STATUS_CHANGED", "order " + id + " -> " + status + " v" + updated.version());
        return updated;
    }

    // ================================================================ batch chunk

    // One chunk of a bulk import = one transaction: all rows or none (a constraint error aborts the chunk).
    // Catch: big chunks hold locks and WAL longer; the service picks the chunk size and reports failed chunks.
    @Transactional(transactionManager = AuroraConfig.WRITER_TX)
    public int importChunk(List<NewOrder> chunk) {
        return orders.batchInsert(chunk);
    }

    // ================================================================ REPEATABLE READ snapshot on the reader

    // Two queries, one snapshot: count/sum and the latest rows agree even while writes continue.
    // When to use: reports and pages built from several queries. Catch: the snapshot itself may lag the writer
    // (replica), and SERIALIZABLE is not available on readers; REPEATABLE READ is the strongest there.
    @Transactional(transactionManager = AuroraConfig.READER_TX, readOnly = true, isolation = Isolation.REPEATABLE_READ)
    public CustomerSummary customerSummary(String customerId) {
        long[] countAndSum = orders.countAndSumOnReader(customerId);
        List<Order> latest = orders.latestOnReader(customerId, 5);
        return new CustomerSummary(customerId, countAndSum[0], countAndSum[1], latest);
    }

    // ================================================================ helpers

    private Order replayOf(NewOrder cmd) {
        Order existing = orders.findByIdempotencyKey(cmd.idempotencyKey())
                .orElseThrow(() -> new IllegalStateException("conflict on " + cmd.idempotencyKey() + " but no row"));
        return checkSameRequest(existing, cmd);
    }

    // Same key with a different body is a client bug, not a replay: reject instead of returning someone else's order.
    private static Order checkSameRequest(Order existing, NewOrder cmd) {
        boolean same = existing.customerId().equals(cmd.customerId())
                && existing.sku().equals(cmd.sku())
                && existing.quantity() == cmd.quantity()
                && existing.amountCents() == cmd.amountCents();
        if (!same) {
            throw new BusinessRuleException("idempotency key " + cmd.idempotencyKey() + " reused with a different request");
        }
        return existing;
    }
}
