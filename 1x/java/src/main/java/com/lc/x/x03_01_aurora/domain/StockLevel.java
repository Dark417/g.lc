package com.lc.x.x03_01_aurora.domain;

import java.time.Instant;

/** Inventory row: one per SKU, written by upsert and decremented under a row lock. */
public record StockLevel(String sku, int onHand, Instant updatedAt) {
}
