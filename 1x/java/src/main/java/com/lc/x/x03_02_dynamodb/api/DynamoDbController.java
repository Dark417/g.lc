package com.lc.x.x03_02_dynamodb.api;

import com.lc.x.x03_02_dynamodb.domain.CursorPage;
import com.lc.x.x03_02_dynamodb.domain.IdempotencyKeyReuseException;
import com.lc.x.x03_02_dynamodb.domain.Order;
import com.lc.x.x03_02_dynamodb.domain.OrderRef;
import com.lc.x.x03_02_dynamodb.domain.OrderStatus;
import com.lc.x.x03_02_dynamodb.domain.OrderSummary;
import com.lc.x.x03_02_dynamodb.domain.PlaceOrderCommand;
import com.lc.x.x03_02_dynamodb.domain.PlaceOrderResult;
import com.lc.x.x03_02_dynamodb.domain.VersionConflictException;
import com.lc.x.x03_02_dynamodb.service.OrderService;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import java.time.Instant;
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
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/**
 * Thin REST adapter under /dynamodb.
 * - POST requires Idempotency-Key: replay returns 200 with the original order, a new order returns 201.
 * - Lists return an opaque nextCursor; the version is the optimistic-lock token (If-Match style).
 */
@RestController
@RequestMapping("/dynamodb")
@ConditionalOnProperty(name = "x.dynamodb.enabled", havingValue = "true")
public class DynamoDbController {

    private final OrderService orders;

    public DynamoDbController(OrderService orders) {
        this.orders = orders;
    }

    public record PlaceOrderRequest(@NotBlank String customerId, @Positive long amountCents) {
    }

    public record ChangeStatusRequest(@NotNull OrderStatus status, @Positive long expectedVersion) {
    }

    @PostMapping("/orders")
    public ResponseEntity<Order> place(
            @RequestHeader("Idempotency-Key") String idempotencyKey,
            @Valid @RequestBody PlaceOrderRequest body) {
        PlaceOrderResult result = orders.placeOrder(
                new PlaceOrderCommand(idempotencyKey, body.customerId(), body.amountCents()));
        return ResponseEntity.status(result.replayed() ? HttpStatus.OK : HttpStatus.CREATED).body(result.order());
    }

    @GetMapping("/customers/{customerId}/orders")
    public CursorPage<Order> list(
            @PathVariable String customerId,
            @RequestParam(defaultValue = "20") int limit,
            @RequestParam(required = false) String cursor) {
        return orders.listOrders(customerId, limit, cursor);
    }

    @GetMapping("/customers/{customerId}/orders/{orderId}")
    public ResponseEntity<Order> get(
            @PathVariable String customerId,
            @PathVariable String orderId,
            @RequestParam Instant createdAt,
            @RequestParam(defaultValue = "false") boolean consistent) {
        return orders.getOrder(new OrderRef(customerId, createdAt, orderId), consistent)
                .map(ResponseEntity::ok)
                .orElseGet(() -> ResponseEntity.notFound().build());
    }

    @PutMapping("/customers/{customerId}/orders/{orderId}/status")
    public Order changeStatus(
            @PathVariable String customerId,
            @PathVariable String orderId,
            @RequestParam Instant createdAt,
            @Valid @RequestBody ChangeStatusRequest body) {
        return orders.changeStatus(new OrderRef(customerId, createdAt, orderId), body.status(), body.expectedVersion());
    }

    @GetMapping("/orders/by-status/{status}")
    public List<OrderSummary> byStatus(@PathVariable OrderStatus status, @RequestParam(defaultValue = "20") int limit) {
        return orders.listByStatus(status, limit);
    }

    // ---------------------------------------------------------------- error mapping

    @ExceptionHandler(VersionConflictException.class)
    public ResponseEntity<Map<String, Object>> conflict(VersionConflictException e) {
        if (e.current() == null) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("error", "order not found"));
        }
        return ResponseEntity.status(HttpStatus.CONFLICT)
                .body(Map.of("error", "version conflict", "current", e.current()));
    }

    @ExceptionHandler(IdempotencyKeyReuseException.class)
    public ResponseEntity<Map<String, Object>> keyReuse(IdempotencyKeyReuseException e) {
        return ResponseEntity.unprocessableEntity().body(Map.of("error", e.getMessage()));
    }

    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<Map<String, Object>> badCursor(IllegalArgumentException e) {
        return ResponseEntity.badRequest().body(Map.of("error", e.getMessage()));
    }
}
