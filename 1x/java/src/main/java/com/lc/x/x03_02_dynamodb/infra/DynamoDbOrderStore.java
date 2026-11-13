package com.lc.x.x03_02_dynamodb.infra;

import com.lc.x.x03_02_dynamodb.domain.CursorPage;
import com.lc.x.x03_02_dynamodb.domain.IdempotencyRecord;
import com.lc.x.x03_02_dynamodb.domain.Order;
import com.lc.x.x03_02_dynamodb.domain.OrderRef;
import com.lc.x.x03_02_dynamodb.domain.OrderStatus;
import com.lc.x.x03_02_dynamodb.domain.OrderStore;
import com.lc.x.x03_02_dynamodb.domain.OrderSummary;
import com.lc.x.x03_02_dynamodb.domain.PlaceAttempt;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;

/** Adapter: the domain port backed by the low-level showcase methods (swap for EnhancedClientShowcase freely). */
@Component
@ConditionalOnProperty(name = "x.dynamodb.enabled", havingValue = "true")
public class DynamoDbOrderStore implements OrderStore {

    private final DynamoDbShowcase dynamo;

    public DynamoDbOrderStore(DynamoDbShowcase dynamo) {
        this.dynamo = dynamo;
    }

    @Override
    public PlaceAttempt placeOrder(Order order, IdempotencyRecord record, Instant now) {
        return dynamo.placeOrderTransaction(order, record, now);
    }

    @Override
    public Optional<Order> getOrder(OrderRef ref, boolean consistentRead) {
        return dynamo.getOrder(ref, consistentRead);
    }

    @Override
    public CursorPage<Order> listOrders(String customerId, int limit, String cursor) {
        return dynamo.queryOrdersPage(customerId, limit, cursor);
    }

    @Override
    public List<OrderSummary> listByStatus(OrderStatus status, int limit) {
        return dynamo.queryByStatus(status, limit);
    }

    @Override
    public Order changeStatus(OrderRef ref, OrderStatus newStatus, long expectedVersion) {
        return dynamo.changeStatusWithVersion(ref, newStatus, expectedVersion);
    }
}
