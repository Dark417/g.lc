package com.lc.x.x03_01_aurora.api;

import com.lc.x.x03_01_aurora.domain.BatchResult;
import com.lc.x.x03_01_aurora.domain.BusinessRuleException;
import com.lc.x.x03_01_aurora.domain.CustomerSummary;
import com.lc.x.x03_01_aurora.domain.Job;
import com.lc.x.x03_01_aurora.domain.LeaseLostException;
import com.lc.x.x03_01_aurora.domain.NewOrder;
import com.lc.x.x03_01_aurora.domain.Order;
import com.lc.x.x03_01_aurora.domain.OrderNotFoundException;
import com.lc.x.x03_01_aurora.domain.OrderStatus;
import com.lc.x.x03_01_aurora.domain.Page;
import com.lc.x.x03_01_aurora.domain.StockLevel;
import com.lc.x.x03_01_aurora.domain.VersionConflictException;
import com.lc.x.x03_01_aurora.infra.AuroraErrors;
import com.lc.x.x03_01_aurora.service.AuroraOrderService;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import jakarta.validation.constraints.PositiveOrZero;
import java.time.Duration;
import java.util.List;
import java.util.Map;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.dao.DataAccessException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ProblemDetail;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/**
 * Thin HTTP adapter under /aurora: maps headers and bodies to service calls, and domain errors to status codes.
 * - Idempotency-Key header -> retried, deduplicated create; no header -> single attempt.
 * - If-Match: <version> -> optimistic update; the response ETag carries the new version (read-your-writes token).
 */
@RestController
@RequestMapping("/aurora")
@ConditionalOnProperty(name = "x.aurora.enabled", havingValue = "true")
public class AuroraController {

    private final AuroraOrderService service;

    public AuroraController(AuroraOrderService service) {
        this.service = service;
    }

    public record OrderRequest(
            @NotBlank String customerId,
            @NotBlank String sku,
            @Positive int quantity,
            @PositiveOrZero long amountCents,
            Map<String, Object> attrs) {

        NewOrder toCommand(String idempotencyKey) {
            return new NewOrder(customerId, sku, quantity, amountCents, idempotencyKey, attrs);
        }
    }

    public record StatusRequest(@NotNull OrderStatus status) {
    }

    public record StockRequest(@PositiveOrZero int onHand) {
    }

    public record JobRequest(@NotBlank String kind, Map<String, Object> payload) {
    }

    // ---------------------------------------------------------------- orders

    @PostMapping("/orders")
    public ResponseEntity<Order> create(
            @RequestHeader(name = "Idempotency-Key", required = false) String key,
            @Valid @RequestBody OrderRequest body) {
        Order order = key == null
                ? service.createOrderOnce(body.toCommand(null))
                : service.placeOrder(body.toCommand(key));
        return ResponseEntity.status(HttpStatus.CREATED).eTag(Integer.toString(order.version())).body(order);
    }

    @PostMapping("/orders/credit-checked")
    public ResponseEntity<Order> createWithinCreditLimit(
            @RequestHeader("Idempotency-Key") String key, @Valid @RequestBody OrderRequest body) {
        Order order = service.placeOrderWithinCreditLimit(body.toCommand(key));
        return ResponseEntity.status(HttpStatus.CREATED).eTag(Integer.toString(order.version())).body(order);
    }

    @GetMapping("/orders/{id}")
    public Order get(
            @PathVariable long id,
            @RequestParam(defaultValue = "false") boolean strong,
            @RequestParam(required = false) Integer minVersion) {
        return service.getOrder(id, strong, minVersion);
    }

    @PatchMapping("/orders/{id}/status")
    public ResponseEntity<Order> changeStatus(
            @PathVariable long id,
            @RequestHeader("If-Match") String ifMatch,
            @Valid @RequestBody StatusRequest body) {
        int expected = Integer.parseInt(ifMatch.replace("\"", "").trim());
        Order order = service.changeStatus(id, expected, body.status());
        return ResponseEntity.ok().eTag(Integer.toString(order.version())).body(order);
    }

    @DeleteMapping("/orders/{id}")
    public ResponseEntity<Void> delete(@PathVariable long id) {
        return service.deleteOrder(id) ? ResponseEntity.noContent().build() : ResponseEntity.notFound().build();
    }

    @PostMapping("/orders/import")
    public BatchResult importOrders(@RequestBody List<@Valid OrderRequest> rows) {
        // Row-level idempotency key derived by the client is better; here a missing key stays null (not deduplicated).
        return service.importOrders(rows.stream().map(r -> r.toCommand(null)).toList());
    }

    @PostMapping("/orders/search")
    public List<Order> search(@RequestBody Map<String, Object> containment,
            @RequestParam(defaultValue = "20") int limit) {
        return service.search(containment, limit);
    }

    @GetMapping("/customers/{customerId}/orders")
    public Page<Order> listKeyset(@PathVariable String customerId,
            @RequestParam(required = false) String cursor,
            @RequestParam(defaultValue = "20") int size) {
        return service.listByKeyset(customerId, cursor, size);
    }

    @GetMapping("/customers/{customerId}/orders/offset")
    public Page<Order> listOffset(@PathVariable String customerId,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        return service.listByOffset(customerId, page, size);
    }

    @GetMapping("/customers/{customerId}/summary")
    public CustomerSummary summary(@PathVariable String customerId) {
        return service.customerSummary(customerId);
    }

    // ---------------------------------------------------------------- inventory

    @PutMapping("/inventory/{sku}")
    public StockLevel restock(@PathVariable String sku, @Valid @RequestBody StockRequest body) {
        return service.restock(sku, body.onHand());
    }

    // ---------------------------------------------------------------- jobs

    @PostMapping("/jobs")
    public ResponseEntity<Map<String, Long>> enqueue(@Valid @RequestBody JobRequest body) {
        long id = service.enqueueJob(body.kind(), body.payload() == null ? Map.of() : body.payload());
        return ResponseEntity.status(HttpStatus.CREATED).body(Map.of("id", id));
    }

    @PostMapping("/jobs/claim")
    public List<Job> claim(@RequestParam String workerId,
            @RequestParam(defaultValue = "10") int limit,
            @RequestParam(defaultValue = "60") long leaseSeconds) {
        return service.claimJobs(workerId, limit, Duration.ofSeconds(leaseSeconds));
    }

    @PostMapping("/jobs/{id}/complete")
    public ResponseEntity<Void> complete(@PathVariable long id, @RequestParam String workerId) {
        service.completeJob(id, workerId);
        return ResponseEntity.noContent().build();
    }

    @PostMapping("/jobs/{id}/fail")
    public ResponseEntity<Void> fail(@PathVariable long id, @RequestParam String workerId,
            @RequestBody(required = false) String error) {
        service.failJob(id, workerId, error == null ? "" : error);
        return ResponseEntity.noContent().build();
    }

    @PostMapping("/jobs/requeue-expired")
    public Map<String, Integer> requeueExpired() {
        return Map.of("requeued", service.requeueExpiredJobs());
    }

    // ---------------------------------------------------------------- ops

    @GetMapping("/replica-lag")
    public Map<String, Long> replicaLag() {
        return service.replicaLag();
    }

    @PostMapping("/admin/schema")
    public ResponseEntity<Void> applySchema() {
        service.applySchema();
        return ResponseEntity.noContent().build();
    }

    // ---------------------------------------------------------------- error mapping (this controller only)

    @ExceptionHandler(OrderNotFoundException.class)
    ProblemDetail notFound(OrderNotFoundException e) {
        return ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, e.getMessage());
    }

    @ExceptionHandler({VersionConflictException.class, LeaseLostException.class})
    ProblemDetail conflict(RuntimeException e) {
        return ProblemDetail.forStatusAndDetail(HttpStatus.CONFLICT, e.getMessage());
    }

    @ExceptionHandler(BusinessRuleException.class)
    ProblemDetail rule(BusinessRuleException e) {
        return ProblemDetail.forStatusAndDetail(HttpStatus.UNPROCESSABLE_ENTITY, e.getMessage());
    }

    @ExceptionHandler(IllegalArgumentException.class)
    ProblemDetail badRequest(IllegalArgumentException e) {
        return ProblemDetail.forStatusAndDetail(HttpStatus.BAD_REQUEST, e.getMessage());
    }

    // Retries exhausted on a transient error => 503 so the client may retry later (same Idempotency-Key).
    @ExceptionHandler(DataAccessException.class)
    ProblemDetail database(DataAccessException e) {
        String state = AuroraErrors.sqlState(e);
        HttpStatus status = AuroraErrors.isRetryable(e) ? HttpStatus.SERVICE_UNAVAILABLE : HttpStatus.INTERNAL_SERVER_ERROR;
        return ProblemDetail.forStatusAndDetail(status, "database error" + (state == null ? "" : " " + state));
    }
}
