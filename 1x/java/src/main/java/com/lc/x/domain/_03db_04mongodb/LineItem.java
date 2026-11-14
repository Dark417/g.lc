package com.lc.x.domain._03db_04mongodb;

/**
 * One embedded line item: bounded (an order has tens of items, not millions), read and written with its order.
 * - Money is int64 minor units (cents): exact in every driver, loud when wrong; never a double.
 */
public record LineItem(String sku, int qty, long priceCents) {

    public LineItem {
        if (sku == null || sku.isBlank() || qty <= 0 || priceCents < 0) {
            throw new IllegalArgumentException("sku required, qty > 0, priceCents >= 0");
        }
    }

    public long subtotalCents() {
        return qty * priceCents;
    }
}
