package com.lc.x.x03_02_dynamodb.domain;

import java.time.Instant;
import java.util.List;
import java.util.Optional;

/** Port used by the service layer; implemented in infra by DynamoDbOrderStore. No SDK types here. */
public interface OrderStore {

    PlaceAttempt placeOrder(Order order, IdempotencyRecord record, Instant now);

    Optional<Order> getOrder(OrderRef ref, boolean consistentRead);

    CursorPage<Order> listOrders(String customerId, int limit, String cursor);

    List<OrderSummary> listByStatus(OrderStatus status, int limit);

    Order changeStatus(OrderRef ref, OrderStatus newStatus, long expectedVersion);
}
