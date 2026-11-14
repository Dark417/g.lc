package com.lc.x.infra._03db_04mongodb;

import com.lc.x.domain._03db_04mongodb.CustomerRevenue;
import com.lc.x.domain._03db_04mongodb.NewOrder;
import com.lc.x.domain._03db_04mongodb.Order;
import com.lc.x.domain._03db_04mongodb.OrderPage;
import com.lc.x.domain._03db_04mongodb.OrderStatus;
import com.lc.x.domain._03db_04mongodb.OrderStore;
import com.lc.x.domain._03db_04mongodb.QueryPlanSummary;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;

/** Adapter: the OrderStore port on top of the showcase classes. All driver code lives in the showcases. */
@Component
@ConditionalOnProperty(name = "x.mongodb.enabled", havingValue = "true")
public class MongoOrderStore implements OrderStore {

    private final MongoShowcase showcase;
    private final MongoTransactions transactions;

    public MongoOrderStore(MongoShowcase showcase, MongoTransactions transactions) {
        this.showcase = showcase;
        this.transactions = transactions;
    }

    @Override
    public Order placeOrder(NewOrder order) {
        return transactions.placeOrder(order);
    }

    @Override
    public Optional<Order> findOrder(String orderId) {
        return showcase.findOrder(orderId);
    }

    @Override
    public OrderPage listCustomerOrders(String customerId, int limit, String cursor) {
        return showcase.listCustomerOrders(customerId, limit, cursor);
    }

    @Override
    public Order changeStatus(String orderId, OrderStatus status, long expectedVersion) {
        return showcase.changeStatusWithVersion(orderId, status, expectedVersion);
    }

    @Override
    public List<CustomerRevenue> revenueByCustomer(Instant since, int limit) {
        return showcase.revenueByCustomer(since, limit);
    }

    @Override
    public QueryPlanSummary explainCustomerOrders(String customerId) {
        return showcase.explainCustomerOrders(customerId);
    }

    @Override
    public List<String> ensureIndexes() {
        return showcase.ensureIndexes();
    }
}
