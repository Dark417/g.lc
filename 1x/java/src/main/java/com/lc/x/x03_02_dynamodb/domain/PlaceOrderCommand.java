package com.lc.x.x03_02_dynamodb.domain;

/** Input of the idempotent "place order" use case; idempotencyKey comes from the Idempotency-Key header. */
public record PlaceOrderCommand(String idempotencyKey, String customerId, long amountCents) {
}
