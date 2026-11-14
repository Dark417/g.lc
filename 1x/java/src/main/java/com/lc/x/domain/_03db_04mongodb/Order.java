package com.lc.x.domain._03db_04mongodb;

import java.time.Instant;
import java.util.List;

/**
 * Order as stored in the "orders" collection: one document, items embedded, customer name duplicated.
 * - id = ObjectId hex; createdAt has millisecond precision (BSON Date), which the keyset cursor relies on.
 * - version = optimistic-lock token, incremented by every guarded update.
 */
public record Order(
        String id,
        String customerId,
        String customerName,
        OrderStatus status,
        List<LineItem> items,
        long totalCents,
        String note,
        Instant createdAt,
        Instant updatedAt,
        long version) {

    public Order {
        items = items == null ? List.of() : List.copyOf(items);
    }
}
