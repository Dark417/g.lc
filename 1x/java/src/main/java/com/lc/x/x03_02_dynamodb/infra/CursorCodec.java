package com.lc.x.x03_02_dynamodb.infra;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import software.amazon.awssdk.services.dynamodb.model.AttributeValue;

/**
 * LastEvaluatedKey <-> opaque cursor (base64url of a JSON {attributeName: stringValue}).
 * - Works here because every key attribute of x-orders and GSI1 is type S.
 * - Decode validates the attribute names and the partition key, so a client can't jump to another customer.
 * - Catch: base64 is not secrecy; HMAC-sign (or encrypt) the cursor if key values are sensitive.
 */
public final class CursorCodec {

    private static final ObjectMapper JSON = new ObjectMapper();
    private static final TypeReference<Map<String, String>> MAP_TYPE = new TypeReference<>() {
    };

    /** Base-table key names; a GSI cursor adds GSI1PK/GSI1SK. */
    public static final Set<String> TABLE_KEYS = Set.of("PK", "SK");
    public static final Set<String> GSI1_KEYS = Set.of("PK", "SK", "GSI1PK", "GSI1SK");

    private CursorCodec() {
    }

    /** Null/empty LastEvaluatedKey = no more pages = null cursor. */
    public static String encode(Map<String, AttributeValue> lastEvaluatedKey) {
        if (lastEvaluatedKey == null || lastEvaluatedKey.isEmpty()) {
            return null;
        }
        Map<String, String> plain = new TreeMap<>();
        lastEvaluatedKey.forEach((name, value) -> {
            if (value.s() == null) {
                throw new IllegalStateException("cursor supports string keys only: " + name);
            }
            plain.put(name, value.s());
        });
        try {
            byte[] json = JSON.writeValueAsBytes(plain);
            return Base64.getUrlEncoder().withoutPadding().encodeToString(json);
        } catch (JsonProcessingException e) {
            throw new IllegalStateException(e);
        }
    }

    /**
     * Null/blank cursor = first page (null ExclusiveStartKey).
     * @param expectedPk the partition key the query is for; null to skip the check (GSI queries check GSI1PK instead)
     */
    public static Map<String, AttributeValue> decode(
            String cursor, Set<String> expectedNames, String pkName, String expectedPk) {
        if (cursor == null || cursor.isBlank()) {
            return null;
        }
        Map<String, String> plain;
        try {
            plain = JSON.readValue(Base64.getUrlDecoder().decode(cursor.getBytes(StandardCharsets.US_ASCII)), MAP_TYPE);
        } catch (IllegalArgumentException | java.io.IOException e) {
            throw new IllegalArgumentException("malformed cursor", e);
        }
        if (!plain.keySet().equals(expectedNames)) {
            throw new IllegalArgumentException("cursor keys do not match this query");
        }
        if (expectedPk != null && !expectedPk.equals(plain.get(pkName))) {
            throw new IllegalArgumentException("cursor belongs to another partition");
        }
        Map<String, AttributeValue> key = new HashMap<>();
        plain.forEach((name, value) -> key.put(name, AttributeValue.fromS(value)));
        return key;
    }
}
