package com.lc.x.domain._03db_04mongodb;

import java.util.List;

/**
 * Input to place an order.
 * - customerName is an extended reference: copied onto the order so the list view needs no $lookup.
 * - Max 100 items keeps the embedded array bounded (16 MB document cap, multikey index size).
 */
public record NewOrder(String customerId, String customerName, List<LineItem> items, String note) {

    public static final int MAX_ITEMS = 100;

    public NewOrder {
        if (customerId == null || customerId.isBlank()) {
            throw new IllegalArgumentException("customerId required");
        }
        if (items == null || items.isEmpty() || items.size() > MAX_ITEMS) {
            throw new IllegalArgumentException("1.." + MAX_ITEMS + " items required");
        }
        items = List.copyOf(items);
    }

    public long totalCents() {
        return items.stream().mapToLong(LineItem::subtotalCents).sum();
    }
}
