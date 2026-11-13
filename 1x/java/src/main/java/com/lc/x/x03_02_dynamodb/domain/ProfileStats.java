package com.lc.x.x03_02_dynamodb.domain;

/** Counters on the customer PROFILE item, as returned by UpdateItem ReturnValues=UPDATED_NEW. */
public record ProfileStats(String customerId, long orderCount, long totalSpentCents, String lastOrderAt) {
}
