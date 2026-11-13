package com.lc.x.x03_01_aurora.domain;

import java.time.Instant;
import java.util.Map;

/**
 * Persisted order.
 * - version: optimistic-lock counter; every update bumps it. Also usable as a read-your-writes token.
 * - createdAt + id: the keyset pagination key (id breaks ties: rows in one transaction share now()).
 */
public record Order(
        long id,
        String customerId,
        String sku,
        int quantity,
        long amountCents,
        OrderStatus status,
        int version,
        String idempotencyKey,
        Map<String, Object> attrs,
        Instant createdAt,
        Instant updatedAt) {
}
