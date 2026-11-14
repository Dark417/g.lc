package com.lc.x.domain._03db_02dynamodb;

/** Same idempotency key, different request body: reject (HTTP 422), never replay someone else's result. */
public class IdempotencyKeyReuseException extends RuntimeException {

    public IdempotencyKeyReuseException(String key) {
        super("idempotency key reused with a different request: " + key);
    }
}
