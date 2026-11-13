package com.lc.x.x03_01_aurora.domain;

import java.util.Map;
import java.util.Objects;

/**
 * Command to create an order.
 * - idempotencyKey: client-chosen, unique per logical request; a retry with the same key returns the same order.
 * - attrs: free-form attributes stored as JSONB (queried with @> and a GIN index).
 */
public record NewOrder(
        String customerId,
        String sku,
        int quantity,
        long amountCents,
        String idempotencyKey,
        Map<String, Object> attrs) {

    public NewOrder {
        Objects.requireNonNull(customerId, "customerId");
        Objects.requireNonNull(sku, "sku");
        if (quantity <= 0) {
            throw new IllegalArgumentException("quantity must be > 0");
        }
        if (amountCents < 0) {
            throw new IllegalArgumentException("amountCents must be >= 0");
        }
        attrs = attrs == null ? Map.of() : Map.copyOf(attrs);
    }
}
