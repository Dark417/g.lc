package com.lc.x.x03_02_dynamodb.domain;

import java.time.Instant;

/** Full primary key of one order item (PK + SK). */
public record OrderRef(String customerId, Instant createdAt, String orderId) {

    public String pk() {
        return OrderKeys.customerPk(customerId);
    }

    public String sk() {
        return OrderKeys.orderSk(createdAt, orderId);
    }
}
