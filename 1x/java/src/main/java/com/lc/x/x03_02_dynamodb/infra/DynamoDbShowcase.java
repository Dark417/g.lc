package com.lc.x.x03_02_dynamodb.infra;

import static com.lc.x.x03_02_dynamodb.infra.OrderItemMapper.key;
import static com.lc.x.x03_02_dynamodb.infra.OrderItemMapper.n;
import static com.lc.x.x03_02_dynamodb.infra.OrderItemMapper.s;

import com.lc.x.shared.Retry;
import com.lc.x.x03_02_dynamodb.domain.CursorPage;
import com.lc.x.x03_02_dynamodb.domain.IdempotencyRecord;
import com.lc.x.x03_02_dynamodb.domain.Order;
import com.lc.x.x03_02_dynamodb.domain.OrderKeys;
import com.lc.x.x03_02_dynamodb.domain.OrderRef;
import com.lc.x.x03_02_dynamodb.domain.OrderStatus;
import com.lc.x.x03_02_dynamodb.domain.OrderSummary;
import com.lc.x.x03_02_dynamodb.domain.PlaceAttempt;
import com.lc.x.x03_02_dynamodb.domain.ProfileStats;
import com.lc.x.x03_02_dynamodb.domain.VersionConflictException;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;
import software.amazon.awssdk.services.dynamodb.model.AttributeValue;
import software.amazon.awssdk.services.dynamodb.model.BatchGetItemResponse;
import software.amazon.awssdk.services.dynamodb.model.BatchWriteItemResponse;
import software.amazon.awssdk.services.dynamodb.model.CancellationReason;
import software.amazon.awssdk.services.dynamodb.model.ConditionalCheckFailedException;
import software.amazon.awssdk.services.dynamodb.model.GetItemResponse;
import software.amazon.awssdk.services.dynamodb.model.KeysAndAttributes;
import software.amazon.awssdk.services.dynamodb.model.Put;
import software.amazon.awssdk.services.dynamodb.model.PutItemRequest;
import software.amazon.awssdk.services.dynamodb.model.PutRequest;
import software.amazon.awssdk.services.dynamodb.model.QueryRequest;
import software.amazon.awssdk.services.dynamodb.model.QueryResponse;
import software.amazon.awssdk.services.dynamodb.model.ReturnValue;
import software.amazon.awssdk.services.dynamodb.model.ReturnValuesOnConditionCheckFailure;
import software.amazon.awssdk.services.dynamodb.model.ScanRequest;
import software.amazon.awssdk.services.dynamodb.model.ScanResponse;
import software.amazon.awssdk.services.dynamodb.model.TransactWriteItem;
import software.amazon.awssdk.services.dynamodb.model.TransactWriteItemsRequest;
import software.amazon.awssdk.services.dynamodb.model.TransactionCanceledException;
import software.amazon.awssdk.services.dynamodb.model.TransactionInProgressException;
import software.amazon.awssdk.services.dynamodb.model.Update;
import software.amazon.awssdk.services.dynamodb.model.UpdateItemResponse;
import software.amazon.awssdk.services.dynamodb.model.WriteRequest;

/**
 * Low-level DynamoDbClient showcase: one public method per scenario, in the order of docs/03.02.dynamodb.md.
 * - Works on raw Map<String, AttributeValue>; every expression, placeholder and condition is visible.
 * - Key design: domain.OrderKeys (mirrors the terraform/03.02.dynamodb.tf header).
 * - "status" and similar words are reserved in expressions: always use #name placeholders.
 */
@Component
@ConditionalOnProperty(name = "x.dynamodb.enabled", havingValue = "true")
public class DynamoDbShowcase {

    /** BatchWriteItem accepts up to 25 put/delete requests per call (Developer Guide, Service quotas). */
    static final int BATCH_WRITE_MAX = 25;
    /** BatchGetItem accepts up to 100 keys per call. */
    static final int BATCH_GET_MAX = 100;
    static final List<String> TX_LABELS = List.of("order", "idempotency", "profile");

    private final DynamoDbClient client;
    private final DynamoDbProperties props;
    private final Retry retry = Retry.defaults();

    public DynamoDbShowcase(DynamoDbClient client, DynamoDbProperties props) {
        this.client = client;
        this.props = props;
    }

    // ================================================================ 1. put create-only, get strong vs eventual

    // Create-only put: attribute_not_exists(PK) is checked against the ONE item with this PK+SK, not the partition.
    // Use for any "insert, never overwrite" write; a plain PutItem silently replaces the whole item.
    // Catch: a failed condition still consumes WCU; ALL_OLD returns the existing item without a second read.
    public boolean putOrderCreateOnly(Order order) {
        try {
            client.putItem(PutItemRequest.builder()
                    .tableName(props.ordersTable())
                    .item(OrderItemMapper.toItem(order))
                    .conditionExpression("attribute_not_exists(PK)")
                    .returnValuesOnConditionCheckFailure(ReturnValuesOnConditionCheckFailure.ALL_OLD)
                    .build());
            return true;
        } catch (ConditionalCheckFailedException e) {
            return false; // e.item() = the order that already exists
        }
    }

    // GetItem by full key. consistentRead=false (default): 0.5 RCU per 4 KB, may miss the latest write.
    // consistentRead=true: 1 RCU per 4 KB (2x), served by the partition leader; base table and LSI only.
    // Catch: a missing item is an empty response, not an exception.
    public Optional<Order> getOrder(OrderRef ref, boolean consistentRead) {
        GetItemResponse resp = client.getItem(r -> r
                .tableName(props.ordersTable())
                .key(key(ref.pk(), ref.sk()))
                .consistentRead(consistentRead));
        if (!resp.hasItem() || resp.item().isEmpty()) {
            return Optional.empty();
        }
        return Optional.of(OrderItemMapper.toOrder(resp.item()));
    }

    // ================================================================ 2. UpdateItem: SET / ADD / REMOVE + ReturnValues

    // One UpdateItem with all clause kinds on the PROFILE item; creates the item if missing (upsert).
    // SET overwrites (if_not_exists keeps the first value), ADD increments atomically, REMOVE deletes attributes.
    // Catch: ADD is not idempotent; a blind retry after a timeout double-counts (guard with a condition or a tx).
    public ProfileStats recordOrderOnProfile(String customerId, long amountCents, Instant at) {
        UpdateItemResponse resp = client.updateItem(r -> r
                .tableName(props.ordersTable())
                .key(key(OrderKeys.customerPk(customerId), OrderKeys.PROFILE_SK))
                .updateExpression("SET lastOrderAt = :at, displayName = if_not_exists(displayName, :anon) "
                        + "ADD orderCount :one, totalSpentCents :amount "
                        + "REMOVE pendingCartId")
                .expressionAttributeValues(Map.of(
                        ":at", s(OrderKeys.iso(at)),
                        ":anon", s("anonymous"),
                        ":one", n(1),
                        ":amount", n(amountCents)))
                // UPDATED_NEW = only the attributes this update touched, after the change. No read-after-write.
                .returnValues(ReturnValue.UPDATED_NEW));
        return OrderItemMapper.toProfileStats(customerId, resp.attributes());
    }

    // ================================================================ 3. optimistic lock (version condition)

    // Status change guarded by "version = :expected"; increments version in the same write.
    // Terminal statuses REMOVE GSI1PK/GSI1SK so the order leaves the "pending" GSI (sparse index).
    // Catch: on conflict, ALL_OLD returns the winner's item; the caller re-reads/merges or returns HTTP 409.
    public Order changeStatusWithVersion(OrderRef ref, OrderStatus newStatus, long expectedVersion) {
        Map<String, AttributeValue> values = new HashMap<>();
        values.put(":new", s(newStatus.name()));
        values.put(":expected", n(expectedVersion));
        values.put(":one", n(1));
        String update;
        if (newStatus.isTerminal()) {
            update = "SET #status = :new, #version = #version + :one REMOVE GSI1PK, GSI1SK";
        } else {
            update = "SET #status = :new, #version = #version + :one, GSI1PK = :gsiPk";
            values.put(":gsiPk", s(OrderKeys.gsi1Pk(newStatus)));
        }
        try {
            UpdateItemResponse resp = client.updateItem(r -> r
                    .tableName(props.ordersTable())
                    .key(key(ref.pk(), ref.sk()))
                    .updateExpression(update)
                    .conditionExpression("attribute_exists(PK) AND #version = :expected")
                    .expressionAttributeNames(Map.of("#status", "status", "#version", "version"))
                    .expressionAttributeValues(values)
                    .returnValues(ReturnValue.ALL_NEW)
                    .returnValuesOnConditionCheckFailure(ReturnValuesOnConditionCheckFailure.ALL_OLD));
            return OrderItemMapper.toOrder(resp.attributes());
        } catch (ConditionalCheckFailedException e) {
            // No item in the exception = attribute_exists(PK) failed = the order does not exist.
            throw new VersionConflictException(e.hasItem() && !e.item().isEmpty()
                    ? OrderItemMapper.toOrder(e.item()) : null);
        }
    }

    // ================================================================ 4. Query: PK + begins_with / between, GSI

    // A customer's orders, newest first: PK equality + begins_with on SK skips the PROFILE item.
    // Key conditions are applied BEFORE the read, so you pay only for matching items (unlike filters).
    // Catch: Limit is per page; one call returns at most Limit items or 1 MB, whichever comes first.
    public List<Order> queryOrdersByPrefix(String customerId, int limit) {
        QueryResponse resp = client.query(r -> r
                .tableName(props.ordersTable())
                .keyConditionExpression("PK = :pk AND begins_with(SK, :prefix)")
                .expressionAttributeValues(Map.of(
                        ":pk", s(OrderKeys.customerPk(customerId)),
                        ":prefix", s(OrderKeys.ORDER_PREFIX)))
                .scanIndexForward(false) // descending SK = newest first
                .limit(limit));
        return resp.items().stream().map(OrderItemMapper::toOrder).toList();
    }

    // Time range with BETWEEN (inclusive). Every SK ends with "#<orderId>", so BETWEEN ORDER#<from> AND ORDER#<to>
    // behaves as [from, to). Uses the paginator, which follows LastEvaluatedKey until the range is exhausted.
    // Catch: only correct because timestamps are fixed-width (OrderKeys.iso); variable width breaks string order.
    public List<Order> queryOrdersBetween(String customerId, Instant from, Instant to) {
        QueryRequest req = QueryRequest.builder()
                .tableName(props.ordersTable())
                .keyConditionExpression("PK = :pk AND SK BETWEEN :from AND :to")
                .expressionAttributeValues(Map.of(
                        ":pk", s(OrderKeys.customerPk(customerId)),
                        ":from", s(OrderKeys.orderSkBound(from)),
                        ":to", s(OrderKeys.orderSkBound(to))))
                .build();
        return client.queryPaginator(req).items().stream().map(OrderItemMapper::toOrder).toList();
    }

    // GSI query: "all PENDING orders, oldest first". Returns only keys + the INCLUDE projection.
    // GSIs are updated asynchronously: reads are eventually consistent, and ConsistentRead=true is rejected.
    // Catch: never use a GSI read for uniqueness or to decide a write; re-read the base item (strong) first.
    public List<OrderSummary> queryByStatus(OrderStatus status, int limit) {
        QueryResponse resp = client.query(r -> r
                .tableName(props.ordersTable())
                .indexName(props.gsi1Name())
                .keyConditionExpression("GSI1PK = :pk")
                .expressionAttributeValues(Map.of(":pk", s(OrderKeys.gsi1Pk(status))))
                .scanIndexForward(true) // ascending GSI1SK (createdAt) = oldest first
                .limit(limit));
        return resp.items().stream().map(OrderItemMapper::toSummary).toList();
    }

    // ================================================================ 5. pagination: LastEvaluatedKey <-> cursor

    // API pagination: one Query per call, LastEvaluatedKey returned as an opaque base64 cursor, decoded on the way in.
    // The cursor is validated against this customer's PK so a client can't page through someone else's partition.
    // Catch: a short or even empty page can still have a next cursor (1 MB cap, filters); only null means "done".
    public CursorPage<Order> queryOrdersPage(String customerId, int limit, String cursor) {
        String pk = OrderKeys.customerPk(customerId);
        Map<String, AttributeValue> startKey = CursorCodec.decode(cursor, CursorCodec.TABLE_KEYS, "PK", pk);
        QueryRequest.Builder req = QueryRequest.builder()
                .tableName(props.ordersTable())
                .keyConditionExpression("PK = :pk AND begins_with(SK, :prefix)")
                .expressionAttributeValues(Map.of(":pk", s(pk), ":prefix", s(OrderKeys.ORDER_PREFIX)))
                .scanIndexForward(false)
                .limit(limit);
        if (startKey != null) {
            req.exclusiveStartKey(startKey);
        }
        QueryResponse resp = client.query(req.build());
        List<Order> items = resp.items().stream().map(OrderItemMapper::toOrder).toList();
        String next = resp.hasLastEvaluatedKey() ? CursorCodec.encode(resp.lastEvaluatedKey()) : null;
        return new CursorPage<>(items, next);
    }

    // Internal "read everything" path: the SDK paginator loops on LastEvaluatedKey for you, lazily.
    // Use for jobs and small item collections; never to build an unbounded API response.
    // Catch: each page is a separate request; the result is not a snapshot (concurrent writes may show up).
    public List<Order> queryAllOrders(String customerId) {
        QueryRequest req = QueryRequest.builder()
                .tableName(props.ordersTable())
                .keyConditionExpression("PK = :pk AND begins_with(SK, :prefix)")
                .expressionAttributeValues(Map.of(
                        ":pk", s(OrderKeys.customerPk(customerId)),
                        ":prefix", s(OrderKeys.ORDER_PREFIX)))
                .build();
        List<Order> all = new ArrayList<>();
        for (QueryResponse page : client.queryPaginator(req)) {
            page.items().forEach(i -> all.add(OrderItemMapper.toOrder(i)));
        }
        return all;
    }

    // ================================================================ 6. Scan + parallel Scan (and why to avoid)

    // Full-table Scan: reads EVERY item (orders, profiles, ...) and only then applies the filter.
    // You pay RCU for ScannedCount, not Count; on a big table it is slow and costly. Avoid in request paths.
    // Prefer: a GSI for the access pattern, or "Export to S3" + Athena for analytics.
    public long scanAllOrders(Consumer<Order> sink) {
        ScanRequest req = ScanRequest.builder()
                .tableName(props.ordersTable())
                .filterExpression("entityType = :order")
                .expressionAttributeValues(Map.of(":order", s(OrderKeys.ENTITY_ORDER)))
                .build();
        long scanned = 0;
        for (ScanResponse page : client.scanPaginator(req)) {
            scanned += page.scannedCount(); // what you pay for
            page.items().forEach(i -> sink.accept(OrderItemMapper.toOrder(i)));
        }
        return scanned;
    }

    // Parallel Scan: TotalSegments splits the key space; each worker scans one Segment with its own LastEvaluatedKey.
    // Use only for offline jobs (backfills, migrations) that must touch every item.
    // Catch: N workers burn N times the throughput at once and can throttle live traffic; cap N and rate-limit.
    public List<Order> parallelScan(int totalSegments) {
        ExecutorService pool = Executors.newFixedThreadPool(totalSegments);
        ConcurrentLinkedQueue<Order> out = new ConcurrentLinkedQueue<>();
        try {
            List<Future<?>> futures = new ArrayList<>();
            for (int segment = 0; segment < totalSegments; segment++) {
                final int seg = segment;
                futures.add(pool.submit(() -> {
                    Map<String, AttributeValue> startKey = null;
                    do {
                        ScanRequest.Builder req = ScanRequest.builder()
                                .tableName(props.ordersTable())
                                .segment(seg)
                                .totalSegments(totalSegments)
                                .filterExpression("entityType = :order")
                                .expressionAttributeValues(Map.of(":order", s(OrderKeys.ENTITY_ORDER)));
                        if (startKey != null) {
                            req.exclusiveStartKey(startKey);
                        }
                        ScanResponse page = client.scan(req.build());
                        page.items().forEach(i -> out.add(OrderItemMapper.toOrder(i)));
                        startKey = page.hasLastEvaluatedKey() && !page.lastEvaluatedKey().isEmpty()
                                ? page.lastEvaluatedKey() : null;
                    } while (startKey != null);
                }));
            }
            for (Future<?> f : futures) {
                f.get();
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new IllegalStateException("parallel scan interrupted", e);
        } catch (ExecutionException e) {
            throw new IllegalStateException("parallel scan segment failed", e.getCause());
        } finally {
            pool.shutdownNow();
        }
        return new ArrayList<>(out);
    }

    // ================================================================ 7. BatchWriteItem / BatchGetItem + unprocessed retry

    // Bulk put in chunks of 25. The batch is NOT atomic and takes no conditions: some items may come back
    // in UnprocessedItems (throttling). Resend only those, with full-jitter backoff, then give up loudly.
    // Catch: a 200 response with UnprocessedItems is a partial failure; ignoring it silently drops data.
    public void batchPutOrders(List<Order> orders) {
        for (List<Order> chunk : chunks(orders, BATCH_WRITE_MAX)) {
            requireUniqueKeys(chunk.stream().map(Order::ref).toList()); // duplicates -> ValidationException
            List<WriteRequest> writes = chunk.stream()
                    .map(o -> WriteRequest.builder()
                            .putRequest(PutRequest.builder().item(OrderItemMapper.toItem(o)).build())
                            .build())
                    .toList();
            Map<String, List<WriteRequest>> pending = Map.of(props.ordersTable(), writes);
            for (int attempt = 0; !pending.isEmpty(); attempt++) {
                if (attempt == 5) {
                    int left = pending.values().stream().mapToInt(List::size).sum();
                    throw new IllegalStateException(left + " items still unprocessed after retries");
                }
                if (attempt > 0) {
                    Retry.sleep(retry.backoff(attempt));
                }
                final Map<String, List<WriteRequest>> request = pending;
                BatchWriteItemResponse resp = client.batchWriteItem(r -> r.requestItems(request));
                pending = resp.hasUnprocessedItems() ? resp.unprocessedItems() : Map.of();
            }
        }
    }

    // Bulk get in chunks of 100 keys, following UnprocessedKeys with full-jitter backoff.
    // Results come back in NO particular order and missing keys are simply absent; re-key by PK+SK if needed.
    // Catch: the SDK's batchGetItemPaginator also follows UnprocessedKeys, but without backoff between calls.
    public List<Order> batchGetOrders(List<OrderRef> refs, boolean consistentRead) {
        List<Order> found = new ArrayList<>();
        Map<String, OrderRef> byKey = new LinkedHashMap<>();
        refs.forEach(r -> byKey.putIfAbsent(r.pk() + "|" + r.sk(), r)); // duplicate keys -> ValidationException
        List<OrderRef> unique = new ArrayList<>(byKey.values());
        for (List<OrderRef> chunk : chunks(unique, BATCH_GET_MAX)) {
            List<Map<String, AttributeValue>> keys = chunk.stream().map(r -> key(r.pk(), r.sk())).toList();
            Map<String, KeysAndAttributes> pending = Map.of(props.ordersTable(),
                    KeysAndAttributes.builder().keys(keys).consistentRead(consistentRead).build());
            for (int attempt = 0; !pending.isEmpty(); attempt++) {
                if (attempt == 5) {
                    throw new IllegalStateException("keys still unprocessed after retries");
                }
                if (attempt > 0) {
                    Retry.sleep(retry.backoff(attempt));
                }
                final Map<String, KeysAndAttributes> request = pending;
                BatchGetItemResponse resp = client.batchGetItem(r -> r.requestItems(request));
                resp.responses().getOrDefault(props.ordersTable(), List.of())
                        .forEach(i -> found.add(OrderItemMapper.toOrder(i)));
                pending = resp.hasUnprocessedKeys() ? resp.unprocessedKeys() : Map.of();
            }
        }
        return found;
    }

    // ================================================================ 8. TransactWriteItems + cancellation reasons

    // One atomic write across 2 tables and 3 items: order (create-only) + idempotency record (create-only, or
    // expired) + profile counters. All or nothing; 2x WCU. ClientRequestToken makes SDK retries of THIS call
    // idempotent for 10 minutes. Catch: the token can't cover a client retrying later; the idempotency item does.
    public PlaceAttempt placeOrderTransaction(Order order, IdempotencyRecord record, Instant now) {
        TransactWriteItem putOrder = TransactWriteItem.builder().put(Put.builder()
                .tableName(props.ordersTable())
                .item(OrderItemMapper.toItem(order))
                .conditionExpression("attribute_not_exists(PK)")
                .build()).build();
        // TTL deletion is lazy (typically within days): an expired-but-present record must count as absent.
        TransactWriteItem putIdempotency = TransactWriteItem.builder().put(Put.builder()
                .tableName(props.idempotencyTable())
                .item(OrderItemMapper.toItem(record))
                .conditionExpression("attribute_not_exists(idempotencyKey) OR expiresAt < :now")
                .expressionAttributeValues(Map.of(":now", n(now.getEpochSecond())))
                // On failure, the stored record comes back inside the cancellation reason: no extra read.
                .returnValuesOnConditionCheckFailure(ReturnValuesOnConditionCheckFailure.ALL_OLD)
                .build()).build();
        TransactWriteItem bumpProfile = TransactWriteItem.builder().update(Update.builder()
                .tableName(props.ordersTable())
                .key(key(OrderKeys.customerPk(order.customerId()), OrderKeys.PROFILE_SK))
                .updateExpression("SET lastOrderAt = :at ADD orderCount :one, totalSpentCents :amount")
                .expressionAttributeValues(Map.of(
                        ":at", s(OrderKeys.iso(order.createdAt())),
                        ":one", n(1),
                        ":amount", n(order.amountCents())))
                .build()).build();

        // Token: 1-36 chars. Derived from key + orderId (fresh per attempt), so a different request can never
        // reuse it (IdempotentParameterMismatchException) while SDK-level resends of this request still dedupe.
        String token = UUID.nameUUIDFromBytes(
                (record.idempotencyKey() + "|" + order.orderId()).getBytes(StandardCharsets.UTF_8)).toString();
        TransactWriteItemsRequest req = TransactWriteItemsRequest.builder()
                .transactItems(putOrder, putIdempotency, bumpProfile) // order MUST match TX_LABELS
                .clientRequestToken(token)
                .build();
        try {
            retry.call(() -> client.transactWriteItems(req), DynamoDbShowcase::isRetryableTransactionFailure);
            return PlaceAttempt.committed();
        } catch (TransactionCanceledException e) {
            TxCancellation c = parseCancellation(e, TX_LABELS);
            if (c.failedWith("idempotency", "ConditionalCheckFailed")) {
                return PlaceAttempt.keyAlreadyUsed(OrderItemMapper.toIdempotencyRecord(c.itemOf("idempotency")));
            }
            if (c.failedWith("order", "ConditionalCheckFailed")) {
                return PlaceAttempt.orderAlreadyExists();
            }
            throw e; // ValidationError, retries exhausted on conflicts/throttling, ...
        }
    }

    // Turns the exception into labeled reasons. Reasons are positional: reasons[i] belongs to transactItems[i].
    // ConditionalCheckFailed = business outcome (don't retry); TransactionConflict = concurrent writer (retry).
    // Catch: if the SDK model has no reasons (rare), treat the failure as non-retryable and surface it.
    public static TxCancellation parseCancellation(TransactionCanceledException e, List<String> labels) {
        List<TxCancellation.Reason> reasons = new ArrayList<>();
        if (e.hasCancellationReasons()) {
            List<CancellationReason> raw = e.cancellationReasons();
            for (int i = 0; i < raw.size(); i++) {
                CancellationReason r = raw.get(i);
                reasons.add(new TxCancellation.Reason(
                        i,
                        i < labels.size() ? labels.get(i) : "item" + i,
                        r.code(),
                        r.message(),
                        r.hasItem() ? r.item() : Map.of()));
            }
        }
        return new TxCancellation(reasons);
    }

    static boolean isRetryableTransactionFailure(Throwable t) {
        if (t instanceof TransactionInProgressException) {
            return true; // same ClientRequestToken still being applied: wait and resend
        }
        return t instanceof TransactionCanceledException e && parseCancellation(e, TX_LABELS).retryable();
    }

    // ================================================================ 9. TTL write + expired-item filter

    // TTL: set "expiresAt" (Number, epoch SECONDS) and a background process deletes the item later, for free.
    // Use for carts, sessions, idempotency records, soft-deleted orders.
    // Catch: deletion is not exact (typically within days); epoch millis would mean "expires in 50,000 years".
    public long expireOrderAfter(OrderRef ref, Duration ttl) {
        long expiresAt = Instant.now().plus(ttl).getEpochSecond();
        client.updateItem(r -> r
                .tableName(props.ordersTable())
                .key(key(ref.pk(), ref.sk()))
                .updateExpression("SET expiresAt = :exp")
                .conditionExpression("attribute_exists(PK)") // don't create a stub item for a missing order
                .expressionAttributeValues(Map.of(":exp", n(expiresAt))));
        return expiresAt;
    }

    // Reads must hide expired items that TTL hasn't deleted yet. Filter runs after the read (you still pay for them).
    // Use whenever expiry has business meaning (an expired session must not authenticate).
    // Catch: Limit counts items before the filter, so a page can come back short.
    public List<Order> queryLiveOrders(String customerId, Instant now) {
        QueryRequest req = QueryRequest.builder()
                .tableName(props.ordersTable())
                .keyConditionExpression("PK = :pk AND begins_with(SK, :prefix)")
                .filterExpression("attribute_not_exists(expiresAt) OR expiresAt > :now")
                .expressionAttributeValues(Map.of(
                        ":pk", s(OrderKeys.customerPk(customerId)),
                        ":prefix", s(OrderKeys.ORDER_PREFIX),
                        ":now", n(now.getEpochSecond())))
                .build();
        return client.queryPaginator(req).items().stream().map(OrderItemMapper::toOrder).toList();
    }

    // ================================================================ 10. hot partition: write sharding + scatter-gather

    // Every new order writes GSI1PK=STATUS#PENDING: one GSI partition takes ALL order writes (max 1,000 WCU), and
    // GSI throttling back-pressures base-table writes. Sharding spreads it over STATUS#PENDING#0..N-1.
    // Catch: a variant of the .tf key design; all writers and readers must use the same N and suffix function.
    public boolean putOrderShardedStatus(Order order, int shards) {
        Map<String, AttributeValue> item = OrderItemMapper.toItem(order);
        if (!order.status().isTerminal()) {
            item.put("GSI1PK", s(OrderKeys.gsi1PkSharded(order.status(), order.orderId(), shards)));
        }
        try {
            client.putItem(r -> r
                    .tableName(props.ordersTable())
                    .item(item)
                    .conditionExpression("attribute_not_exists(PK)"));
            return true;
        } catch (ConditionalCheckFailedException e) {
            return false;
        }
    }

    // Scatter-gather read: query all N shards in parallel, merge by GSI1SK (createdAt), keep the oldest `limit`.
    // Each shard returns at most `limit`, so the merged top-`limit` is exact.
    // Catch: N queries per read (N x latency tail, N x request cost); choose N from peak writes / 1,000 WCU.
    public List<OrderSummary> scatterGatherByStatus(OrderStatus status, int shards, int limit) {
        ExecutorService pool = Executors.newFixedThreadPool(Math.min(shards, 16));
        try {
            List<Future<List<Map<String, AttributeValue>>>> futures = new ArrayList<>();
            for (int shard = 0; shard < shards; shard++) {
                String shardKey = OrderKeys.gsi1PkShard(status, shard);
                futures.add(pool.submit(() -> client.query(r -> r
                        .tableName(props.ordersTable())
                        .indexName(props.gsi1Name())
                        .keyConditionExpression("GSI1PK = :pk")
                        .expressionAttributeValues(Map.of(":pk", s(shardKey)))
                        .scanIndexForward(true)
                        .limit(limit)).items()));
            }
            List<OrderSummary> merged = new ArrayList<>();
            for (Future<List<Map<String, AttributeValue>>> f : futures) {
                f.get().forEach(i -> merged.add(OrderItemMapper.toSummary(i)));
            }
            return merged.stream()
                    .sorted(Comparator.comparing(OrderSummary::createdAt))
                    .limit(limit)
                    .collect(Collectors.toList());
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new IllegalStateException("scatter-gather interrupted", e);
        } catch (ExecutionException e) {
            throw new IllegalStateException("shard query failed", e.getCause());
        } finally {
            pool.shutdownNow();
        }
    }

    // ================================================================ helpers

    static <T> List<List<T>> chunks(List<T> items, int size) {
        List<List<T>> out = new ArrayList<>();
        for (int i = 0; i < items.size(); i += size) {
            out.add(items.subList(i, Math.min(i + size, items.size())));
        }
        return out;
    }

    static void requireUniqueKeys(Collection<OrderRef> refs) {
        Set<String> seen = new HashSet<>();
        for (OrderRef r : refs) {
            if (!seen.add(r.pk() + "|" + r.sk())) {
                throw new IllegalArgumentException("duplicate key in one batch: " + r);
            }
        }
    }
}
