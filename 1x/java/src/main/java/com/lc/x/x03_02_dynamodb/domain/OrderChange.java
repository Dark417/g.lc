package com.lc.x.x03_02_dynamodb.domain;

/**
 * A parsed stream record (NEW_AND_OLD_IMAGES) for an order item.
 * - before is null for INSERT, after is null for REMOVE.
 * - ttlExpiry = the REMOVE was done by the TTL process, not by the application.
 */
public record OrderChange(
        String eventId,
        String sequenceNumber,
        Type type,
        Order before,
        Order after,
        boolean ttlExpiry) {

    public enum Type {
        INSERT,
        MODIFY,
        REMOVE
    }

    public boolean statusChanged() {
        return before != null && after != null && before.status() != after.status();
    }
}
