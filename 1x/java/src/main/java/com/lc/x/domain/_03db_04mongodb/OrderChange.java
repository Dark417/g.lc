package com.lc.x.domain._03db_04mongodb;

/**
 * One change-stream event, reduced to what a consumer needs.
 * - resumeToken is the event's _id (JSON); persist it AFTER handling the event for at-least-once delivery.
 * - status is null for deletes (no full document).
 */
public record OrderChange(String operationType, String orderId, OrderStatus status, String resumeToken) {
}
