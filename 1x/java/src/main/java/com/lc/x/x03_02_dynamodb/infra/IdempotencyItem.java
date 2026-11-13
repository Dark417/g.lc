package com.lc.x.x03_02_dynamodb.infra;

import com.lc.x.x03_02_dynamodb.domain.IdempotencyRecord;
import software.amazon.awssdk.enhanced.dynamodb.mapper.annotations.DynamoDbBean;
import software.amazon.awssdk.enhanced.dynamodb.mapper.annotations.DynamoDbPartitionKey;

/** Enhanced Client mapping of an "x-idempotency" item (hash key idempotencyKey, TTL attribute expiresAt). */
@DynamoDbBean
public class IdempotencyItem {

    private String idempotencyKey;
    private String requestHash;
    private String customerId;
    private String orderId;
    private String orderCreatedAt;
    private Long expiresAt;

    public IdempotencyItem() {
    }

    public static IdempotencyItem from(IdempotencyRecord r) {
        IdempotencyItem i = new IdempotencyItem();
        i.setIdempotencyKey(r.idempotencyKey());
        i.setRequestHash(r.requestHash());
        i.setCustomerId(r.customerId());
        i.setOrderId(r.orderId());
        i.setOrderCreatedAt(r.orderCreatedAtIso());
        i.setExpiresAt(r.expiresAtEpochSeconds());
        return i;
    }

    @DynamoDbPartitionKey
    public String getIdempotencyKey() {
        return idempotencyKey;
    }

    public void setIdempotencyKey(String idempotencyKey) {
        this.idempotencyKey = idempotencyKey;
    }

    public String getRequestHash() {
        return requestHash;
    }

    public void setRequestHash(String requestHash) {
        this.requestHash = requestHash;
    }

    public String getCustomerId() {
        return customerId;
    }

    public void setCustomerId(String customerId) {
        this.customerId = customerId;
    }

    public String getOrderId() {
        return orderId;
    }

    public void setOrderId(String orderId) {
        this.orderId = orderId;
    }

    public String getOrderCreatedAt() {
        return orderCreatedAt;
    }

    public void setOrderCreatedAt(String orderCreatedAt) {
        this.orderCreatedAt = orderCreatedAt;
    }

    public Long getExpiresAt() {
        return expiresAt;
    }

    public void setExpiresAt(Long expiresAt) {
        this.expiresAt = expiresAt;
    }
}
