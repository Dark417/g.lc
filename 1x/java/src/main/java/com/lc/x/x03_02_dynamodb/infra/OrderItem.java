package com.lc.x.x03_02_dynamodb.infra;

import com.lc.x.x03_02_dynamodb.domain.Order;
import com.lc.x.x03_02_dynamodb.domain.OrderKeys;
import com.lc.x.x03_02_dynamodb.domain.OrderStatus;
import software.amazon.awssdk.enhanced.dynamodb.mapper.annotations.DynamoDbAttribute;
import software.amazon.awssdk.enhanced.dynamodb.mapper.annotations.DynamoDbBean;
import software.amazon.awssdk.enhanced.dynamodb.mapper.annotations.DynamoDbPartitionKey;
import software.amazon.awssdk.enhanced.dynamodb.mapper.annotations.DynamoDbSecondaryPartitionKey;
import software.amazon.awssdk.enhanced.dynamodb.mapper.annotations.DynamoDbSecondarySortKey;
import software.amazon.awssdk.enhanced.dynamodb.mapper.annotations.DynamoDbSortKey;
import software.amazon.awssdk.enhanced.dynamodb.extensions.annotations.DynamoDbVersionAttribute;

/**
 * Enhanced Client mapping of an order item (mutable bean: TableSchema.fromBean needs getters/setters + no-arg ctor).
 * - Persistence-only type; the domain keeps the immutable {@link Order} record.
 * - @DynamoDbVersionAttribute: the VersionedRecordExtension adds "version = :old" (or attribute_not_exists) to
 *   every put/update and increments the value. Catch: index names in annotations are compile-time constants.
 */
@DynamoDbBean
public class OrderItem {

    private String pk;
    private String sk;
    private String gsi1Pk;
    private String gsi1Sk;
    private String entityType;
    private String customerId;
    private String orderId;
    private String createdAt;
    private String status;
    private Long amountCents;
    private Long version;
    private Long expiresAt;

    public OrderItem() {
    }

    /** version is copied as-is: null = new item (create-only), non-null = expected current version. */
    public static OrderItem from(Order o, Long version) {
        OrderItem i = new OrderItem();
        i.setPk(OrderKeys.customerPk(o.customerId()));
        i.setSk(OrderKeys.orderSk(o.createdAt(), o.orderId()));
        if (!o.status().isTerminal()) {
            i.setGsi1Pk(OrderKeys.gsi1Pk(o.status()));
            i.setGsi1Sk(OrderKeys.gsi1Sk(o.createdAt()));
        }
        i.setEntityType(OrderKeys.ENTITY_ORDER);
        i.setCustomerId(o.customerId());
        i.setOrderId(o.orderId());
        i.setCreatedAt(OrderKeys.iso(o.createdAt()));
        i.setStatus(o.status().name());
        i.setAmountCents(o.amountCents());
        i.setVersion(version);
        i.setExpiresAt(o.expiresAtEpochSeconds());
        return i;
    }

    public Order toOrder() {
        return new Order(customerId, orderId, OrderKeys.parseIso(createdAt), OrderStatus.valueOf(status),
                amountCents == null ? 0L : amountCents, version == null ? 0L : version, expiresAt);
    }

    @DynamoDbPartitionKey
    @DynamoDbAttribute("PK")
    public String getPk() {
        return pk;
    }

    public void setPk(String pk) {
        this.pk = pk;
    }

    @DynamoDbSortKey
    @DynamoDbAttribute("SK")
    public String getSk() {
        return sk;
    }

    public void setSk(String sk) {
        this.sk = sk;
    }

    @DynamoDbSecondaryPartitionKey(indexNames = "GSI1")
    @DynamoDbAttribute("GSI1PK")
    public String getGsi1Pk() {
        return gsi1Pk;
    }

    public void setGsi1Pk(String gsi1Pk) {
        this.gsi1Pk = gsi1Pk;
    }

    @DynamoDbSecondarySortKey(indexNames = "GSI1")
    @DynamoDbAttribute("GSI1SK")
    public String getGsi1Sk() {
        return gsi1Sk;
    }

    public void setGsi1Sk(String gsi1Sk) {
        this.gsi1Sk = gsi1Sk;
    }

    public String getEntityType() {
        return entityType;
    }

    public void setEntityType(String entityType) {
        this.entityType = entityType;
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

    public String getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(String createdAt) {
        this.createdAt = createdAt;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public Long getAmountCents() {
        return amountCents;
    }

    public void setAmountCents(Long amountCents) {
        this.amountCents = amountCents;
    }

    @DynamoDbVersionAttribute
    public Long getVersion() {
        return version;
    }

    public void setVersion(Long version) {
        this.version = version;
    }

    public Long getExpiresAt() {
        return expiresAt;
    }

    public void setExpiresAt(Long expiresAt) {
        this.expiresAt = expiresAt;
    }
}
