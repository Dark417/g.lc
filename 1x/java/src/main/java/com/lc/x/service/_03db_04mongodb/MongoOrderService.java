package com.lc.x.service._03db_04mongodb;

import com.lc.x.domain._03db_04mongodb.CustomerRevenue;
import com.lc.x.domain._03db_04mongodb.NewOrder;
import com.lc.x.domain._03db_04mongodb.Order;
import com.lc.x.domain._03db_04mongodb.OrderNotFoundException;
import com.lc.x.domain._03db_04mongodb.OrderPage;
import com.lc.x.domain._03db_04mongodb.OrderStatus;
import com.lc.x.domain._03db_04mongodb.OrderStore;
import com.lc.x.domain._03db_04mongodb.QueryPlanSummary;
import java.time.Duration;
import java.time.Instant;
import java.util.List;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;

/**
 * Thin use cases over the OrderStore port: input limits and defaults live here, driver code does not.
 * - Page size is capped so one request cannot pull an unbounded result through the WiredTiger cache.
 */
@Service
@ConditionalOnProperty(name = "x.mongodb.enabled", havingValue = "true")
public class MongoOrderService {

    static final int MAX_PAGE = 100;
    static final int MAX_REPORT_ROWS = 100;

    private final OrderStore store;

    public MongoOrderService(OrderStore store) {
        this.store = store;
    }

    public Order placeOrder(NewOrder order) {
        return store.placeOrder(order);
    }

    public Order getOrder(String orderId) {
        return store.findOrder(orderId).orElseThrow(() -> new OrderNotFoundException(orderId));
    }

    public OrderPage listCustomerOrders(String customerId, int limit, String cursor) {
        return store.listCustomerOrders(customerId, Math.max(1, Math.min(limit, MAX_PAGE)), cursor);
    }

    public Order changeStatus(String orderId, OrderStatus status, long expectedVersion) {
        return store.changeStatus(orderId, status, expectedVersion);
    }

    public List<CustomerRevenue> revenueReport(int days, int limit) {
        Instant since = Instant.now().minus(Duration.ofDays(Math.max(1, days)));
        return store.revenueByCustomer(since, Math.max(1, Math.min(limit, MAX_REPORT_ROWS)));
    }

    public QueryPlanSummary explainCustomerOrders(String customerId) {
        return store.explainCustomerOrders(customerId);
    }

    public List<String> ensureIndexes() {
        return store.ensureIndexes();
    }
}
