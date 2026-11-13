package com.lc.x.x03_01_aurora.domain;

import java.util.List;
import java.util.Map;
import java.util.Optional;

/**
 * Port for orders. Methods run in the caller's transaction when one is active.
 * - Writer methods see the latest commit.
 * - Reader methods (pageBy*, findByAttrs, *OnReader) use the reader endpoint and may lag (replica lag).
 */
public interface OrderRepository {

    // ---- CRUD + idempotent create
    Order insert(NewOrder order);

    Optional<Order> insertIdempotent(NewOrder order);

    Optional<Order> findById(long id);

    Optional<Order> findByIdempotencyKey(String idempotencyKey);

    boolean delete(long id);

    // ---- batch
    int batchInsert(List<NewOrder> orders);

    // ---- pagination
    Page<Order> pageByOffset(String customerId, int page, int size);

    Page<Order> pageByKeyset(String customerId, String cursor, int size);

    // ---- optimistic lock
    Order updateStatusIfVersion(long id, int expectedVersion, OrderStatus newStatus);

    // ---- invariant queries
    long sumOpenAmountCents(String customerId);

    // ---- JSONB
    List<Order> findByAttrs(Map<String, Object> containment, int limit);

    // ---- reader endpoint
    Optional<Order> findByIdOnReader(long id);

    long[] countAndSumOnReader(String customerId);

    List<Order> latestOnReader(String customerId, int limit);
}
