package com.lc.x.x03_01_aurora.domain;

/** A domain invariant would break (insufficient stock, credit limit). Not retryable (HTTP 422). */
public class BusinessRuleException extends RuntimeException {

    public BusinessRuleException(String message) {
        super(message);
    }
}
