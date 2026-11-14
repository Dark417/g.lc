package com.lc.x.domain._03db_04mongodb;

/**
 * Business failure inside a transaction body. A non-Mongo exception aborts withTransaction WITHOUT a retry,
 * which is what we want: retrying cannot create stock.
 */
public class InsufficientStockException extends RuntimeException {

    public InsufficientStockException(String sku, int requested) {
        super("insufficient stock for " + sku + " (requested " + requested + ")");
    }
}
