package com.lc.x.infra._03db_04mongodb;

import com.lc.x.domain._03db_04mongodb.LineItem;
import com.lc.x.domain._03db_04mongodb.NewOrder;
import com.lc.x.domain._03db_04mongodb.Order;
import com.lc.x.domain._03db_04mongodb.OrderStatus;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Date;
import java.util.List;
import org.bson.Document;
import org.bson.types.ObjectId;

/**
 * Collection names + Document <-> record mapping for the MongoDB slice.
 * - Plain org.bson.Document on purpose: filters, updates and pipelines are all just BSON documents,
 *   so what you read here is exactly what mongosh would send.
 * - Order shape (one document):
 *   { _id: ObjectId, customerId, customerName,            // extended reference: no $lookup on reads
 *     status, items: [ {sku, qty, priceCents} ],           // embedded, bounded (<= 100)
 *     totalCents: int64, note, createdAt: Date, updatedAt: Date, version: int64,
 *     deletedAt?, purgeAt? }                               // soft delete + TTL purge
 */
public final class OrderDocuments {

    public static final String ORDERS = "orders";
    public static final String INVENTORY = "inventory";
    public static final String CUSTOMERS = "customers";
    public static final String ORDER_EVENTS = "order_events";
    public static final String COUNTERS = "counters";
    public static final String LEDGER = "ledger";
    public static final String ROTAS = "oncall_rotas";
    public static final String RESUME_TOKENS = "resume_tokens";
    public static final String DAILY_REVENUE = "daily_revenue";

    private OrderDocuments() {
    }

    /** BSON Date is millisecond precision: truncate BEFORE writing so the in-memory value equals the stored one. */
    public static Instant nowMillis() {
        return Instant.now().truncatedTo(ChronoUnit.MILLIS);
    }

    public static ObjectId objectId(String hex) {
        if (hex == null || !ObjectId.isValid(hex)) {
            throw new IllegalArgumentException("not an ObjectId: " + hex);
        }
        return new ObjectId(hex);
    }

    public static Document newOrderDocument(ObjectId id, NewOrder o, Instant now) {
        return new Document("_id", id)
                .append("customerId", o.customerId())
                .append("customerName", o.customerName())
                .append("status", OrderStatus.PENDING.name())
                .append("items", o.items().stream().map(OrderDocuments::itemDocument).toList())
                .append("totalCents", o.totalCents()) // long -> BSON int64
                .append("note", o.note())
                .append("createdAt", now)               // Instant -> BSON Date (Jsr310 codec in the default registry)
                .append("updatedAt", now)
                .append("version", 1L);
    }

    public static Document itemDocument(LineItem i) {
        return new Document("sku", i.sku()).append("qty", i.qty()).append("priceCents", i.priceCents());
    }

    public static Order toOrder(Document d) {
        List<Document> items = d.getList("items", Document.class, List.of());
        return new Order(
                d.getObjectId("_id").toHexString(),
                d.getString("customerId"),
                d.getString("customerName"),
                OrderStatus.valueOf(d.getString("status")),
                items.stream().map(OrderDocuments::toItem).toList(),
                num(d, "totalCents"),
                d.getString("note"),
                instant(d, "createdAt"),
                instant(d, "updatedAt"),
                num(d, "version"));
    }

    public static LineItem toItem(Document d) {
        return new LineItem(d.getString("sku"), (int) num(d, "qty"), num(d, "priceCents"));
    }

    /** Numbers may arrive as int32 or int64 (mongosh writes int32/double): read through Number. */
    static long num(Document d, String key) {
        Object v = d.get(key);
        return v == null ? 0L : ((Number) v).longValue();
    }

    static Instant instant(Document d, String key) {
        Date date = d.getDate(key); // the driver decodes BSON Date as java.util.Date
        return date == null ? null : date.toInstant();
    }
}
