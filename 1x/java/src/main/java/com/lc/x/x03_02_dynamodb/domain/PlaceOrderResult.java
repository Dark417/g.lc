package com.lc.x.x03_02_dynamodb.domain;

/** replayed = true when the key was seen before and the stored order is returned instead of a new one. */
public record PlaceOrderResult(Order order, boolean replayed) {
}
