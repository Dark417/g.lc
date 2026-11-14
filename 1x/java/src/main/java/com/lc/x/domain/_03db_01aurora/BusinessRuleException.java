package com.lc.x.domain._03db_01aurora;

/** A domain invariant would break (insufficient stock, credit limit). Not retryable (HTTP 422). */
public class BusinessRuleException extends RuntimeException {

    public BusinessRuleException(String message) {
        super(message);
    }
}
