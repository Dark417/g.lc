package com.lc.x.domain._03db_04mongodb;

/** Inventory document: _id = sku, qty = units on hand. */
public record StockLevel(String sku, long qty) {
}
