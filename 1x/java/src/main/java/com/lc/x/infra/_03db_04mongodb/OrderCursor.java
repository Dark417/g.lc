package com.lc.x.infra._03db_04mongodb;

import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.Base64;
import org.bson.types.ObjectId;

/**
 * Opaque keyset cursor = the sort key of the last row returned: (createdAt millis, _id).
 * - _id is the tiebreaker: two orders can share a createdAt millisecond, so createdAt alone skips or repeats rows.
 * - Base64 is not secrecy; sign it (HMAC) if the key values are sensitive.
 */
public record OrderCursor(Instant createdAt, ObjectId id) {

    public String encode() {
        String raw = createdAt.toEpochMilli() + "." + id.toHexString();
        return Base64.getUrlEncoder().withoutPadding().encodeToString(raw.getBytes(StandardCharsets.UTF_8));
    }

    /** Null/blank = first page. A malformed cursor is the caller's fault: IllegalArgumentException (HTTP 400). */
    public static OrderCursor decode(String cursor) {
        if (cursor == null || cursor.isBlank()) {
            return null;
        }
        try {
            String raw = new String(Base64.getUrlDecoder().decode(cursor), StandardCharsets.UTF_8);
            int dot = raw.indexOf('.');
            return new OrderCursor(
                    Instant.ofEpochMilli(Long.parseLong(raw.substring(0, dot))),
                    OrderDocuments.objectId(raw.substring(dot + 1)));
        } catch (RuntimeException e) {
            throw new IllegalArgumentException("invalid cursor", e);
        }
    }
}
