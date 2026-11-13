package com.lc.x.x03_02_dynamodb.domain;

import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.util.zip.CRC32;

/**
 * Single-table key design for "x-orders" (mirrors the header of terraform/03.02.dynamodb.tf).
 * - PK = CUSTOMER#<customerId>, SK = ORDER#<createdAtIso>#<orderId> | PROFILE
 * - GSI1PK = STATUS#<status>, GSI1SK = <createdAtIso>
 * - Sort keys compare as strings, byte by byte, so timestamps MUST be fixed width (see {@link #iso}).
 */
public final class OrderKeys {

    public static final String CUSTOMER_PREFIX = "CUSTOMER#";
    public static final String ORDER_PREFIX = "ORDER#";
    public static final String PROFILE_SK = "PROFILE";
    public static final String STATUS_PREFIX = "STATUS#";
    public static final String ENTITY_ORDER = "ORDER";

    // Fixed width with millis. Instant.toString() drops zero fractions ("...00Z" vs "...00.123Z"),
    // and 'Z' (0x5A) > '.' (0x2E) would sort the earlier timestamp AFTER the later one.
    private static final DateTimeFormatter ISO_MILLIS =
            DateTimeFormatter.ofPattern("uuuu-MM-dd'T'HH:mm:ss.SSS'Z'").withZone(ZoneOffset.UTC);

    private OrderKeys() {
    }

    public static String iso(Instant t) {
        return ISO_MILLIS.format(t);
    }

    public static Instant parseIso(String iso) {
        return Instant.parse(iso);
    }

    public static String customerPk(String customerId) {
        return CUSTOMER_PREFIX + customerId;
    }

    public static String orderSk(Instant createdAt, String orderId) {
        return ORDER_PREFIX + iso(createdAt) + "#" + orderId;
    }

    /** Lower/upper bound for BETWEEN: "ORDER#<iso>" sorts before every "ORDER#<iso>#<id>". */
    public static String orderSkBound(Instant t) {
        return ORDER_PREFIX + iso(t);
    }

    public static String gsi1Pk(OrderStatus status) {
        return STATUS_PREFIX + status.name();
    }

    public static String gsi1Sk(Instant createdAt) {
        return iso(createdAt);
    }

    /**
     * Write-sharded GSI key: STATUS#PENDING#<0..shards-1>.
     * - Calculated suffix (CRC32 of orderId) so Java and Python writers agree and one order maps to one shard.
     * - Catch: every reader must then scatter-gather all shards; pick one scheme per table, not both.
     */
    public static String gsi1PkSharded(OrderStatus status, String orderId, int shards) {
        return gsi1Pk(status) + "#" + shardOf(orderId, shards);
    }

    public static String gsi1PkShard(OrderStatus status, int shard) {
        return gsi1Pk(status) + "#" + shard;
    }

    public static int shardOf(String orderId, int shards) {
        CRC32 crc = new CRC32();
        crc.update(orderId.getBytes(StandardCharsets.UTF_8));
        return (int) (crc.getValue() % shards);
    }

    /** Scope the client's key by caller so two customers can't collide on "retry-1". */
    public static String scopedIdempotencyKey(String customerId, String clientKey) {
        return customerId + "#" + clientKey;
    }
}
