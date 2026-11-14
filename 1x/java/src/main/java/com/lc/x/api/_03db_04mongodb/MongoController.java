package com.lc.x.api._03db_04mongodb;

import com.lc.x.domain._03db_04mongodb.CustomerRevenue;
import com.lc.x.domain._03db_04mongodb.InsufficientStockException;
import com.lc.x.domain._03db_04mongodb.LineItem;
import com.lc.x.domain._03db_04mongodb.NewOrder;
import com.lc.x.domain._03db_04mongodb.Order;
import com.lc.x.domain._03db_04mongodb.OrderNotFoundException;
import com.lc.x.domain._03db_04mongodb.OrderPage;
import com.lc.x.domain._03db_04mongodb.OrderStatus;
import com.lc.x.domain._03db_04mongodb.QueryPlanSummary;
import com.lc.x.domain._03db_04mongodb.VersionConflictException;
import com.lc.x.service._03db_04mongodb.MongoOrderService;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import jakarta.validation.constraints.PositiveOrZero;
import jakarta.validation.constraints.Size;
import java.util.List;
import java.util.Map;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/**
 * Thin REST adapter under /mongodb.
 * - POST /orders runs the order + inventory transaction; insufficient stock = 409.
 * - Lists return an opaque nextCursor (keyset); version is the optimistic-lock token (409 on conflict).
 */
@RestController
@RequestMapping("/mongodb")
@ConditionalOnProperty(name = "x.mongodb.enabled", havingValue = "true")
public class MongoController {

    private final MongoOrderService orders;

    public MongoController(MongoOrderService orders) {
        this.orders = orders;
    }

    public record LineItemRequest(@NotBlank String sku, @Positive int qty, @PositiveOrZero long priceCents) {
    }

    public record PlaceOrderRequest(
            @NotBlank String customerId,
            String customerName,
            @NotEmpty @Size(max = NewOrder.MAX_ITEMS) List<@Valid LineItemRequest> items,
            String note) {
    }

    public record ChangeStatusRequest(@NotNull OrderStatus status, @Positive long expectedVersion) {
    }

    @PostMapping("/orders")
    public ResponseEntity<Order> place(@Valid @RequestBody PlaceOrderRequest body) {
        List<LineItem> items = body.items().stream()
                .map(i -> new LineItem(i.sku(), i.qty(), i.priceCents()))
                .toList();
        Order placed = orders.placeOrder(new NewOrder(body.customerId(), body.customerName(), items, body.note()));
        return ResponseEntity.status(HttpStatus.CREATED).body(placed);
    }

    @GetMapping("/orders/{orderId}")
    public Order get(@PathVariable String orderId) {
        return orders.getOrder(orderId);
    }

    @GetMapping("/customers/{customerId}/orders")
    public OrderPage list(
            @PathVariable String customerId,
            @RequestParam(defaultValue = "20") int limit,
            @RequestParam(required = false) String cursor) {
        return orders.listCustomerOrders(customerId, limit, cursor);
    }

    @PutMapping("/orders/{orderId}/status")
    public Order changeStatus(@PathVariable String orderId, @Valid @RequestBody ChangeStatusRequest body) {
        return orders.changeStatus(orderId, body.status(), body.expectedVersion());
    }

    @GetMapping("/reports/revenue")
    public List<CustomerRevenue> revenue(
            @RequestParam(defaultValue = "30") int days,
            @RequestParam(defaultValue = "10") int limit) {
        return orders.revenueReport(days, limit);
    }

    @PostMapping("/admin/indexes")
    public List<String> ensureIndexes() {
        return orders.ensureIndexes();
    }

    @GetMapping("/explain/customer-orders")
    public QueryPlanSummary explain(@RequestParam String customerId) {
        return orders.explainCustomerOrders(customerId);
    }

    @ExceptionHandler(OrderNotFoundException.class)
    public ResponseEntity<Map<String, Object>> notFound(OrderNotFoundException e) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("error", e.getMessage()));
    }

    @ExceptionHandler(VersionConflictException.class)
    public ResponseEntity<Map<String, Object>> conflict(VersionConflictException e) {
        return ResponseEntity.status(HttpStatus.CONFLICT)
                .body(Map.of("error", e.getMessage(), "current", e.current()));
    }

    @ExceptionHandler(InsufficientStockException.class)
    public ResponseEntity<Map<String, Object>> noStock(InsufficientStockException e) {
        return ResponseEntity.status(HttpStatus.CONFLICT).body(Map.of("error", e.getMessage()));
    }

    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<Map<String, Object>> badRequest(IllegalArgumentException e) {
        return ResponseEntity.badRequest().body(Map.of("error", e.getMessage()));
    }
}
