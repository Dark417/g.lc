package com.lc.x.domain._03db_02dynamodb;

/** replayed = true when the key was seen before and the stored order is returned instead of a new one. */
public record PlaceOrderResult(Order order, boolean replayed) {
}
