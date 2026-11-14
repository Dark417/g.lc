package com.lc.x.domain._03db_01aurora;

/** Port for stock levels: upsert, pessimistic lock, atomic conditional decrement. */
public interface InventoryRepository {

    StockLevel upsertStock(String sku, int onHand);

    int lockStockForUpdate(String sku);

    void decrementStock(String sku, int quantity);

    boolean decrementStockIfAvailable(String sku, int quantity);
}
