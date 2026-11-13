package com.lc.x.x03_02_dynamodb.service;

import com.lc.x.x03_02_dynamodb.domain.CursorPage;
import com.lc.x.x03_02_dynamodb.domain.IdempotencyKeyReuseException;
import com.lc.x.x03_02_dynamodb.domain.IdempotencyRecord;
import com.lc.x.x03_02_dynamodb.domain.Order;
import com.lc.x.x03_02_dynamodb.domain.OrderKeys;
import com.lc.x.x03_02_dynamodb.domain.OrderRef;
import com.lc.x.x03_02_dynamodb.domain.OrderStatus;
import com.lc.x.x03_02_dynamodb.domain.OrderStore;
import com.lc.x.x03_02_dynamodb.domain.OrderSummary;
import com.lc.x.x03_02_dynamodb.domain.PlaceAttempt;
import com.lc.x.x03_02_dynamodb.domain.PlaceOrderCommand;
import com.lc.x.x03_02_dynamodb.domain.PlaceOrderResult;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.HexFormat;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;

/**
 * Use cases on top of the OrderStore port.
 * - placeOrder: idempotent create, built on ONE transaction (order + idempotency record + profile counters).
 * - Because both items commit atomically there is no "in progress" idempotency state to recover from.
 */
@Service
@ConditionalOnProperty(name = "x.dynamodb.enabled", havingValue = "true")
public class OrderService {

    private final OrderStore store;
    private final Clock clock;
    private final Duration idempotencyRetention;

    public OrderService(
            OrderStore store,
            @Value("${x.dynamodb.idempotency-retention:PT24H}") Duration idempotencyRetention) {
        this.store = store;
        this.clock = Clock.systemUTC();
        this.idempotencyRetention = idempotencyRetention;
    }

    // Idempotent "place order": same key + same body -> the original order (replayed=true), never a second one.
    // Same key + different body -> IdempotencyKeyReuseException (HTTP 422).
    // Catch: retention must exceed the client's retry horizon, or a very late retry creates a duplicate.
    public PlaceOrderResult placeOrder(PlaceOrderCommand cmd) {
        Instant now = clock.instant().truncatedTo(ChronoUnit.MILLIS); // keys store millis; keep the record equal
        String scopedKey = OrderKeys.scopedIdempotencyKey(cmd.customerId(), cmd.idempotencyKey());
        String hash = requestHash(cmd);
        Order order = Order.newPending(cmd.customerId(), UUID.randomUUID().toString(), now, cmd.amountCents());
        IdempotencyRecord record = new IdempotencyRecord(
                scopedKey, hash, order.customerId(), order.orderId(), OrderKeys.iso(order.createdAt()),
                now.plus(idempotencyRetention).getEpochSecond());

        PlaceAttempt attempt = store.placeOrder(order, record, now);
        return switch (attempt.status()) {
            case COMMITTED -> new PlaceOrderResult(order, false);
            case KEY_ALREADY_USED -> replay(attempt.existing(), hash, scopedKey);
            // A fresh UUID collided with an existing order: practically impossible; fail loudly.
            case ORDER_ALREADY_EXISTS -> throw new IllegalStateException("order id collision");
        };
    }

    private PlaceOrderResult replay(IdempotencyRecord existing, String hash, String scopedKey) {
        if (!existing.requestHash().equals(hash)) {
            throw new IdempotencyKeyReuseException(scopedKey);
        }
        // Strong read: the order committed in the same transaction as the record, so it must exist.
        // Returns the order's CURRENT state; store a response snapshot in the record if exact replay matters.
        OrderRef ref = new OrderRef(existing.customerId(), OrderKeys.parseIso(existing.orderCreatedAtIso()),
                existing.orderId());
        Order stored = store.getOrder(ref, true)
                .orElseThrow(() -> new IllegalStateException("idempotency record points to a missing order"));
        return new PlaceOrderResult(stored, true);
    }

    public Optional<Order> getOrder(OrderRef ref, boolean consistentRead) {
        return store.getOrder(ref, consistentRead);
    }

    // Pagination contract: the client sends back nextCursor unchanged; null nextCursor = no more pages.
    public CursorPage<Order> listOrders(String customerId, int limit, String cursor) {
        int bounded = Math.max(1, Math.min(limit, 100)); // cap page size: bounded latency and RCU per call
        return store.listOrders(customerId, bounded, cursor);
    }

    public List<OrderSummary> listByStatus(OrderStatus status, int limit) {
        return store.listByStatus(status, Math.max(1, Math.min(limit, 100)));
    }

    public Order changeStatus(OrderRef ref, OrderStatus newStatus, long expectedVersion) {
        return store.changeStatus(ref, newStatus, expectedVersion);
    }

    /** Hash of the fields that define "the same request"; excludes the key itself and server-generated values. */
    static String requestHash(PlaceOrderCommand cmd) {
        try {
            MessageDigest sha = MessageDigest.getInstance("SHA-256");
            byte[] digest = sha.digest((cmd.customerId() + "|" + cmd.amountCents()).getBytes(StandardCharsets.UTF_8));
            return HexFormat.of().formatHex(digest);
        } catch (NoSuchAlgorithmException e) {
            throw new IllegalStateException(e);
        }
    }
}
