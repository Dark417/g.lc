package com.lc.x.x03_02_dynamodb.domain;

import java.time.Instant;

/**
 * Order aggregate as stored in "x-orders".
 * - version: optimistic-lock counter, starts at 1 on create.
 * - expiresAtEpochSeconds: TTL attribute (null = never expires); deletion is background and not exact.
 */
public record Order(
        String customerId,
        String orderId,
        Instant createdAt,
        OrderStatus status,
        long amountCents,
        long version,
        Long expiresAtEpochSeconds) {

    public static Order newPending(String customerId, String orderId, Instant createdAt, long amountCents) {
        return new Order(customerId, orderId, createdAt, OrderStatus.PENDING, amountCents, 1L, null);
    }

    public OrderRef ref() {
        return new OrderRef(customerId, createdAt, orderId);
    }

    public Order withStatus(OrderStatus newStatus) {
        return new Order(customerId, orderId, createdAt, newStatus, amountCents, version, expiresAtEpochSeconds);
    }
}
