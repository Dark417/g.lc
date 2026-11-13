package com.lc.x.x03_02_dynamodb.infra;

import com.lc.x.shared.Retry;
import com.lc.x.x03_02_dynamodb.domain.CursorPage;
import com.lc.x.x03_02_dynamodb.domain.IdempotencyRecord;
import com.lc.x.x03_02_dynamodb.domain.Order;
import com.lc.x.x03_02_dynamodb.domain.OrderKeys;
import com.lc.x.x03_02_dynamodb.domain.OrderRef;
import com.lc.x.x03_02_dynamodb.domain.OrderStatus;
import com.lc.x.x03_02_dynamodb.domain.PlaceAttempt;
import com.lc.x.x03_02_dynamodb.domain.VersionConflictException;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;
import software.amazon.awssdk.core.pagination.sync.SdkIterable;
import software.amazon.awssdk.enhanced.dynamodb.DynamoDbEnhancedClient;
import software.amazon.awssdk.enhanced.dynamodb.DynamoDbIndex;
import software.amazon.awssdk.enhanced.dynamodb.DynamoDbTable;
import software.amazon.awssdk.enhanced.dynamodb.Expression;
import software.amazon.awssdk.enhanced.dynamodb.Key;
import software.amazon.awssdk.enhanced.dynamodb.TableSchema;
import software.amazon.awssdk.enhanced.dynamodb.model.BatchGetResultPage;
import software.amazon.awssdk.enhanced.dynamodb.model.BatchWriteResult;
import software.amazon.awssdk.enhanced.dynamodb.model.GetItemEnhancedRequest;
import software.amazon.awssdk.enhanced.dynamodb.model.Page;
import software.amazon.awssdk.enhanced.dynamodb.model.PutItemEnhancedRequest;
import software.amazon.awssdk.enhanced.dynamodb.model.QueryConditional;
import software.amazon.awssdk.enhanced.dynamodb.model.QueryEnhancedRequest;
import software.amazon.awssdk.enhanced.dynamodb.model.ReadBatch;
import software.amazon.awssdk.enhanced.dynamodb.model.TransactPutItemEnhancedRequest;
import software.amazon.awssdk.enhanced.dynamodb.model.TransactWriteItemsEnhancedRequest;
import software.amazon.awssdk.enhanced.dynamodb.model.UpdateItemEnhancedRequest;
import software.amazon.awssdk.enhanced.dynamodb.model.WriteBatch;
import software.amazon.awssdk.services.dynamodb.model.AttributeValue;
import software.amazon.awssdk.services.dynamodb.model.ConditionalCheckFailedException;
import software.amazon.awssdk.services.dynamodb.model.ReturnValuesOnConditionCheckFailure;
import software.amazon.awssdk.services.dynamodb.model.TransactionCanceledException;

/**
 * Enhanced Client showcase: the same scenarios as {@link DynamoDbShowcase}, through the bean mapper.
 * - Less boilerplate: keys come from annotations, items are beans, the paginator is built in.
 * - Version checks come for free from @DynamoDbVersionAttribute (VersionedRecordExtension).
 * - Catch: expressions still exist (Expression objects); the mapper hides AttributeValue, not DynamoDB semantics.
 */
@Component
@ConditionalOnProperty(name = "x.dynamodb.enabled", havingValue = "true")
public class EnhancedClientShowcase {

    private final DynamoDbEnhancedClient enhanced;
    private final DynamoDbTable<OrderItem> orders;
    private final DynamoDbTable<IdempotencyItem> idempotency;
    private final DynamoDbIndex<OrderItem> gsi1;
    private final Retry retry = Retry.defaults();

    public EnhancedClientShowcase(DynamoDbEnhancedClient enhanced, DynamoDbProperties props) {
        this.enhanced = enhanced;
        // TableSchema.fromBean introspects once; keep the schema/table objects (they are immutable and cheap).
        this.orders = enhanced.table(props.ordersTable(), TableSchema.fromBean(OrderItem.class));
        this.idempotency = enhanced.table(props.idempotencyTable(), TableSchema.fromBean(IdempotencyItem.class));
        this.gsi1 = orders.index(props.gsi1Name());
    }

    // ================================================================ 1. put create-only, get strong vs eventual

    // Create-only put. version=null makes VersionedRecordExtension add attribute_not_exists(version) and write 1;
    // the explicit attribute_not_exists(PK) is ANDed with it. Either alone is enough; both show the merge.
    // Catch: a plain putItem(bean) with a non-null version is a conditional overwrite, not an insert.
    public boolean putCreateOnly(Order order) {
        try {
            orders.putItem(PutItemEnhancedRequest.builder(OrderItem.class)
                    .item(OrderItem.from(order, null))
                    .conditionExpression(Expression.builder().expression("attribute_not_exists(PK)").build())
                    .build());
            return true;
        } catch (ConditionalCheckFailedException e) {
            return false;
        }
    }

    // GetItem through the mapper; consistentRead toggles strong (2x RCU) vs eventual.
    // Catch: returns null for a missing item.
    public Optional<Order> getOrder(OrderRef ref, boolean consistentRead) {
        OrderItem item = orders.getItem(GetItemEnhancedRequest.builder()
                .key(Key.builder().partitionValue(ref.pk()).sortValue(ref.sk()).build())
                .consistentRead(consistentRead)
                .build());
        return Optional.ofNullable(item).map(OrderItem::toOrder);
    }

    // ================================================================ 3. optimistic lock with @DynamoDbVersionAttribute

    // updateItem(bean): the extension adds "version = :current" and writes version + 1, no expression written by hand.
    // Default null handling = full-state update: null attributes are REMOVEd (terminal status drops GSI1PK/GSI1SK).
    // Catch: with IgnoreNullsMode.SCALAR_ONLY nulls are skipped, so the order would stay in the "pending" index.
    public Order updateWithVersionAttribute(Order current, OrderStatus newStatus) {
        OrderItem changed = OrderItem.from(current.withStatus(newStatus), current.version());
        try {
            OrderItem saved = orders.updateItem(UpdateItemEnhancedRequest.builder(OrderItem.class)
                    .item(changed)
                    .returnValuesOnConditionCheckFailure(ReturnValuesOnConditionCheckFailure.ALL_OLD)
                    .build());
            return saved.toOrder();
        } catch (ConditionalCheckFailedException e) {
            OrderItem winner = e.hasItem() && !e.item().isEmpty() ? orders.tableSchema().mapToItem(e.item()) : null;
            throw new VersionConflictException(winner == null ? null : winner.toOrder());
        }
    }

    // ================================================================ 4-5. Query + GSI + pagination

    // Query with sortBeginsWith + one page + cursor. Page.lastEvaluatedKey() is the raw key map -> CursorCodec.
    // Use this shape for API pagination; iterate the PageIterable only for internal "read all" loops.
    // Catch: PageIterable.items() silently fetches every page; that is the paginator, not one page.
    public CursorPage<Order> queryOrders(String customerId, int limit, String cursor) {
        String pk = OrderKeys.customerPk(customerId);
        Map<String, AttributeValue> startKey = CursorCodec.decode(cursor, CursorCodec.TABLE_KEYS, "PK", pk);
        QueryEnhancedRequest req = QueryEnhancedRequest.builder()
                .queryConditional(QueryConditional.sortBeginsWith(
                        Key.builder().partitionValue(pk).sortValue(OrderKeys.ORDER_PREFIX).build()))
                .scanIndexForward(false)
                .limit(limit)
                .exclusiveStartKey(startKey)
                .build();
        Page<OrderItem> page = orders.query(req).iterator().next(); // first page only
        List<Order> items = page.items().stream().map(OrderItem::toOrder).toList();
        return new CursorPage<>(items, CursorCodec.encode(page.lastEvaluatedKey()));
    }

    // GSI query through DynamoDbIndex; projected-out attributes come back as null fields on the bean.
    // GSI reads are eventually consistent only; consistentRead(true) here is a ValidationException.
    // Catch: status/version are not projected into GSI1; never act on them from an index read.
    public List<OrderItem> queryByStatus(OrderStatus status, int limit) {
        SdkIterable<Page<OrderItem>> pages = gsi1.query(QueryEnhancedRequest.builder()
                .queryConditional(QueryConditional.keyEqualTo(
                        Key.builder().partitionValue(OrderKeys.gsi1Pk(status)).build()))
                .limit(limit)
                .build());
        return pages.iterator().next().items();
    }

    // ================================================================ 7. batch write / batch get

    // Batch put through WriteBatch; BatchWriteResult exposes unprocessed beans per table, resent with backoff.
    // Catch: no retry of unprocessed items and no 25-item chunking for you; and batch writes take no conditions,
    // so the @DynamoDbVersionAttribute check is not enforced here (bulk loads only).
    public void batchPut(List<Order> toWrite) {
        for (List<Order> chunk : DynamoDbShowcase.chunks(toWrite, DynamoDbShowcase.BATCH_WRITE_MAX)) {
            List<OrderItem> pending = chunk.stream().map(o -> OrderItem.from(o, o.version())).toList();
            for (int attempt = 0; !pending.isEmpty(); attempt++) {
                if (attempt == 5) {
                    throw new IllegalStateException(pending.size() + " items still unprocessed after retries");
                }
                if (attempt > 0) {
                    Retry.sleep(retry.backoff(attempt));
                }
                WriteBatch.Builder<OrderItem> batch = WriteBatch.builder(OrderItem.class).mappedTableResource(orders);
                pending.forEach(batch::addPutItem);
                BatchWriteResult result = enhanced.batchWriteItem(r -> r.writeBatches(batch.build()));
                pending = result.unprocessedPutItemsForTable(orders);
            }
        }
    }

    // Batch get: the result iterable requests the next page with the previous page's UnprocessedKeys.
    // Use for <= 100 keys per call; results are unordered.
    // Catch: those follow-up calls have no backoff between them; under heavy throttling prefer the low-level loop.
    public List<Order> batchGet(List<OrderRef> refs) {
        ReadBatch.Builder<OrderItem> batch = ReadBatch.builder(OrderItem.class).mappedTableResource(orders);
        refs.forEach(r -> batch.addGetItem(Key.builder().partitionValue(r.pk()).sortValue(r.sk()).build()));
        List<Order> found = new ArrayList<>();
        for (BatchGetResultPage page : enhanced.batchGetItem(r -> r.readBatches(batch.build()))) {
            page.resultsForTable(orders).forEach(i -> found.add(i.toOrder()));
        }
        return found;
    }

    // ================================================================ 8. transaction

    // Same transaction as the low-level version (order + idempotency record), with beans.
    // The VersionedRecordExtension also applies inside transactions (version=null -> create-only).
    // Catch: the exception is still the low-level TransactionCanceledException; parse reasons the same way.
    public PlaceAttempt placeOrderTransaction(Order order, IdempotencyRecord record, Instant now) {
        String token = UUID.nameUUIDFromBytes(
                (record.idempotencyKey() + "|" + order.orderId()).getBytes(StandardCharsets.UTF_8)).toString();
        TransactWriteItemsEnhancedRequest req = TransactWriteItemsEnhancedRequest.builder()
                .addPutItem(orders, TransactPutItemEnhancedRequest.builder(OrderItem.class)
                        .item(OrderItem.from(order, null))
                        .conditionExpression(Expression.builder().expression("attribute_not_exists(PK)").build())
                        .build())
                .addPutItem(idempotency, TransactPutItemEnhancedRequest.builder(IdempotencyItem.class)
                        .item(IdempotencyItem.from(record))
                        .conditionExpression(Expression.builder()
                                .expression("attribute_not_exists(idempotencyKey) OR expiresAt < :now")
                                .putExpressionValue(":now", AttributeValue.fromN(Long.toString(now.getEpochSecond())))
                                .build())
                        .returnValuesOnConditionCheckFailure(ReturnValuesOnConditionCheckFailure.ALL_OLD)
                        .build())
                .clientRequestToken(token)
                .build();
        try {
            enhanced.transactWriteItems(req);
            return PlaceAttempt.committed();
        } catch (TransactionCanceledException e) {
            TxCancellation c = DynamoDbShowcase.parseCancellation(e, List.of("order", "idempotency"));
            if (c.failedWith("idempotency", "ConditionalCheckFailed")) {
                return PlaceAttempt.keyAlreadyUsed(OrderItemMapper.toIdempotencyRecord(c.itemOf("idempotency")));
            }
            if (c.failedWith("order", "ConditionalCheckFailed")) {
                return PlaceAttempt.orderAlreadyExists();
            }
            throw e;
        }
    }
}
