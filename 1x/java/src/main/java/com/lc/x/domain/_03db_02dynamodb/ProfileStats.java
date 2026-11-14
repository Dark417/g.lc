package com.lc.x.domain._03db_02dynamodb;

/** Counters on the customer PROFILE item, as returned by UpdateItem ReturnValues=UPDATED_NEW. */
public record ProfileStats(String customerId, long orderCount, long totalSpentCents, String lastOrderAt) {
}
