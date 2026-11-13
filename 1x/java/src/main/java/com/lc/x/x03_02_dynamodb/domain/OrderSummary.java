package com.lc.x.x03_02_dynamodb.domain;

import java.time.Instant;

/**
 * What GSI1 returns: keys + the INCLUDE projection (orderId, customerId, amountCents).
 * - No version/status attributes: fetch the base item (strong read) before acting on it.
 */
public record OrderSummary(String customerId, String orderId, Instant createdAt, long amountCents) {
}
