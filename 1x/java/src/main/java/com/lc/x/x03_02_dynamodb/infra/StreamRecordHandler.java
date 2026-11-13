package com.lc.x.x03_02_dynamodb.infra;

import com.lc.x.x03_02_dynamodb.domain.Order;
import com.lc.x.x03_02_dynamodb.domain.OrderChange;
import java.time.Instant;
import java.util.Map;
import java.util.Optional;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;
import software.amazon.awssdk.services.dynamodb.model.AttributeValue;
import software.amazon.awssdk.services.dynamodb.model.Identity;
import software.amazon.awssdk.services.dynamodb.model.OperationType;
import software.amazon.awssdk.services.dynamodb.model.Record;
import software.amazon.awssdk.services.dynamodb.model.StreamRecord;
import software.amazon.awssdk.services.dynamodb.model.StreamViewType;

/**
 * DynamoDB Streams record shape for x-orders (StreamViewType NEW_AND_OLD_IMAGES).
 * - Record = what DynamoDbStreamsClient.getRecords returns (the Lambda event has the same JSON shape).
 * - Images are plain Map<String, AttributeValue>, parsed with the same mapper as table reads.
 * - Catch: consumers retry batches, so processing is at-least-once; dedupe by eventID or by item version.
 */
@Component
@ConditionalOnProperty(name = "x.dynamodb.enabled", havingValue = "true")
public class StreamRecordHandler {

    /** TTL deletes are performed by this service principal (userIdentity.type = "Service"). */
    static final String TTL_PRINCIPAL = "dynamodb.amazonaws.com";

    // Parse one record into a domain change; non-order items (PROFILE) are ignored.
    // INSERT has only NewImage, REMOVE only OldImage, MODIFY both; ttlExpiry flags REMOVEs done by TTL.
    // Catch: a stream keeps records 24 h; a consumer down longer loses changes (use Kinesis Data Streams if needed).
    public Optional<OrderChange> handle(Record record) {
        StreamRecord ddb = record.dynamodb();
        Map<String, AttributeValue> keys = ddb.hasKeys() ? ddb.keys() : Map.of();
        if (!OrderItemMapper.isOrder(keys)) {
            return Optional.empty();
        }
        Order before = ddb.hasOldImage() && !ddb.oldImage().isEmpty() ? OrderItemMapper.toOrder(ddb.oldImage()) : null;
        Order after = ddb.hasNewImage() && !ddb.newImage().isEmpty() ? OrderItemMapper.toOrder(ddb.newImage()) : null;
        Identity who = record.userIdentity();
        boolean ttl = record.eventName() == OperationType.REMOVE
                && who != null && "Service".equals(who.type()) && TTL_PRINCIPAL.equals(who.principalId());
        return Optional.of(new OrderChange(
                record.eventID(),
                ddb.sequenceNumber(),
                OrderChange.Type.valueOf(record.eventNameAsString()),
                before,
                after,
                ttl));
    }

    // Builds a MODIFY record by hand: documents the exact shape and makes the handler testable without AWS.
    // Use in unit tests and to explain what a consumer receives.
    // Catch: real records also carry eventSource "aws:dynamodb", awsRegion, SizeBytes and ApproximateCreationDateTime.
    public static Record sampleModifyRecord(Order before, Order after) {
        Map<String, AttributeValue> oldImage = OrderItemMapper.toItem(before);
        Map<String, AttributeValue> newImage = OrderItemMapper.toItem(after);
        return Record.builder()
                .eventID("sample-event-1")
                .eventName(OperationType.MODIFY)
                .eventSource("aws:dynamodb")
                .dynamodb(StreamRecord.builder()
                        .keys(Map.of("PK", newImage.get("PK"), "SK", newImage.get("SK")))
                        .oldImage(oldImage)
                        .newImage(newImage)
                        .sequenceNumber("100000000000000000001")
                        .approximateCreationDateTime(Instant.now())
                        .streamViewType(StreamViewType.NEW_AND_OLD_IMAGES)
                        .build())
                .build();
    }
}
