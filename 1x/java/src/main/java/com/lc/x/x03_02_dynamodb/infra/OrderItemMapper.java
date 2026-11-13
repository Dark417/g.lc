package com.lc.x.x03_02_dynamodb.infra;

import com.lc.x.x03_02_dynamodb.domain.IdempotencyRecord;
import com.lc.x.x03_02_dynamodb.domain.Order;
import com.lc.x.x03_02_dynamodb.domain.OrderKeys;
import com.lc.x.x03_02_dynamodb.domain.OrderStatus;
import com.lc.x.x03_02_dynamodb.domain.OrderSummary;
import com.lc.x.x03_02_dynamodb.domain.ProfileStats;
import java.util.HashMap;
import java.util.Map;
import software.amazon.awssdk.services.dynamodb.model.AttributeValue;

/**
 * Low-level mapping: domain record <-> Map<String, AttributeValue>.
 * - Numbers travel as strings (AttributeValue N) to keep full precision; parse explicitly.
 * - Attribute names are part of item size (400 KB limit) and of every RCU/WCU: keep them short in hot tables.
 */
public final class OrderItemMapper {

    private OrderItemMapper() {
    }

    // ---------------------------------------------------------------- order item

    /** Full order item; GSI1 keys only for non-terminal statuses (sparse index). */
    public static Map<String, AttributeValue> toItem(Order o) {
        Map<String, AttributeValue> item = new HashMap<>();
        item.put("PK", s(OrderKeys.customerPk(o.customerId())));
        item.put("SK", s(OrderKeys.orderSk(o.createdAt(), o.orderId())));
        if (!o.status().isTerminal()) {
            item.put("GSI1PK", s(OrderKeys.gsi1Pk(o.status())));
            item.put("GSI1SK", s(OrderKeys.gsi1Sk(o.createdAt())));
        }
        item.put("entityType", s(OrderKeys.ENTITY_ORDER));
        item.put("customerId", s(o.customerId()));
        item.put("orderId", s(o.orderId()));
        item.put("createdAt", s(OrderKeys.iso(o.createdAt())));
        item.put("status", s(o.status().name()));
        item.put("amountCents", n(o.amountCents()));
        item.put("version", n(o.version()));
        if (o.expiresAtEpochSeconds() != null) {
            item.put("expiresAt", n(o.expiresAtEpochSeconds()));
        }
        return item;
    }

    public static Order toOrder(Map<String, AttributeValue> item) {
        AttributeValue expires = item.get("expiresAt");
        return new Order(
                str(item, "customerId"),
                str(item, "orderId"),
                OrderKeys.parseIso(str(item, "createdAt")),
                OrderStatus.valueOf(str(item, "status")),
                num(item, "amountCents"),
                num(item, "version"),
                expires == null ? null : Long.parseLong(expires.n()));
    }

    public static boolean isOrder(Map<String, AttributeValue> item) {
        AttributeValue sk = item.get("SK");
        return sk != null && sk.s() != null && sk.s().startsWith(OrderKeys.ORDER_PREFIX);
    }

    /** GSI1 item: keys + INCLUDE projection only (no status/version attributes). */
    public static OrderSummary toSummary(Map<String, AttributeValue> item) {
        return new OrderSummary(
                str(item, "customerId"),
                str(item, "orderId"),
                OrderKeys.parseIso(str(item, "GSI1SK")),
                num(item, "amountCents"));
    }

    // ---------------------------------------------------------------- profile + idempotency

    public static ProfileStats toProfileStats(String customerId, Map<String, AttributeValue> attrs) {
        return new ProfileStats(
                customerId,
                attrs.containsKey("orderCount") ? num(attrs, "orderCount") : 0L,
                attrs.containsKey("totalSpentCents") ? num(attrs, "totalSpentCents") : 0L,
                attrs.containsKey("lastOrderAt") ? str(attrs, "lastOrderAt") : null);
    }

    public static Map<String, AttributeValue> toItem(IdempotencyRecord r) {
        Map<String, AttributeValue> item = new HashMap<>();
        item.put("idempotencyKey", s(r.idempotencyKey()));
        item.put("requestHash", s(r.requestHash()));
        item.put("customerId", s(r.customerId()));
        item.put("orderId", s(r.orderId()));
        item.put("orderCreatedAt", s(r.orderCreatedAtIso()));
        item.put("expiresAt", n(r.expiresAtEpochSeconds()));
        return item;
    }

    public static IdempotencyRecord toIdempotencyRecord(Map<String, AttributeValue> item) {
        return new IdempotencyRecord(
                str(item, "idempotencyKey"),
                str(item, "requestHash"),
                str(item, "customerId"),
                str(item, "orderId"),
                str(item, "orderCreatedAt"),
                num(item, "expiresAt"));
    }

    // ---------------------------------------------------------------- helpers

    public static AttributeValue s(String v) {
        return AttributeValue.fromS(v);
    }

    public static AttributeValue n(long v) {
        return AttributeValue.fromN(Long.toString(v));
    }

    public static Map<String, AttributeValue> key(String pk, String sk) {
        return Map.of("PK", s(pk), "SK", s(sk));
    }

    static String str(Map<String, AttributeValue> item, String name) {
        AttributeValue v = item.get(name);
        if (v == null || v.s() == null) {
            throw new IllegalStateException("missing string attribute " + name);
        }
        return v.s();
    }

    static long num(Map<String, AttributeValue> item, String name) {
        AttributeValue v = item.get(name);
        if (v == null || v.n() == null) {
            throw new IllegalStateException("missing number attribute " + name);
        }
        return Long.parseLong(v.n());
    }
}
