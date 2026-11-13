package com.lc.x.x03_02_dynamodb.domain;

/**
 * Order lifecycle.
 * - Non-terminal statuses are indexed in GSI1 (GSI1PK = STATUS#<status>).
 * - Terminal statuses drop out of GSI1 (sparse index): the writer REMOVEs GSI1PK/GSI1SK.
 */
public enum OrderStatus {
    PENDING,
    PAID,
    SHIPPED,
    DELIVERED,
    CANCELLED;

    public boolean isTerminal() {
        return this == DELIVERED || this == CANCELLED;
    }
}
