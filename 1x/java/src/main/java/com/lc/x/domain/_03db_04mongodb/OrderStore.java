package com.lc.x.domain._03db_04mongodb;

import java.time.Instant;
import java.util.List;
import java.util.Optional;

/**
 * Port for the MongoDB slice; the adapter is infra/_03db_04mongodb/MongoOrderStore.
 * No driver types here: ids are hex strings, cursors are opaque strings.
 */
public interface OrderStore {

    /** Insert the order and decrement inventory atomically (multi-document transaction). */
    Order placeOrder(NewOrder order);

    Optional<Order> findOrder(String orderId);

    /** Keyset page of one customer's orders, newest first. */
    OrderPage listCustomerOrders(String customerId, int limit, String cursor);

    /** Guarded status change; throws VersionConflictException or OrderNotFoundException. */
    Order changeStatus(String orderId, OrderStatus status, long expectedVersion);

    List<CustomerRevenue> revenueByCustomer(Instant since, int limit);

    QueryPlanSummary explainCustomerOrders(String customerId);

    /** Idempotent: createIndex with the same spec is a no-op. Returns the index names. */
    List<String> ensureIndexes();
}
