package com.lc.x.domain._03db_01aurora;

import java.time.Instant;

/** Inventory row: one per SKU, written by upsert and decremented under a row lock. */
public record StockLevel(String sku, int onHand, Instant updatedAt) {
}
