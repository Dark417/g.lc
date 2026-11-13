package com.lc.x.x03_02_dynamodb.domain;

/**
 * One item in "x-idempotency": the result of a request, keyed by the caller-scoped idempotency key.
 * - requestHash detects key reuse with a different body (reject, don't replay).
 * - expiresAtEpochSeconds = TTL; must outlive the client's maximum retry window.
 */
public record IdempotencyRecord(
        String idempotencyKey,
        String requestHash,
        String customerId,
        String orderId,
        String orderCreatedAtIso,
        long expiresAtEpochSeconds) {
}
