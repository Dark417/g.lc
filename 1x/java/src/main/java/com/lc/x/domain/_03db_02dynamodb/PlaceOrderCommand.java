package com.lc.x.domain._03db_02dynamodb;

/** Input of the idempotent "place order" use case; idempotencyKey comes from the Idempotency-Key header. */
public record PlaceOrderCommand(String idempotencyKey, String customerId, long amountCents) {
}
