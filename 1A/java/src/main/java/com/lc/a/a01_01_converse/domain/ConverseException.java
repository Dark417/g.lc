package com.lc.a.a01_01_converse.domain;

/** Non-retryable request problem (ValidationException, AccessDenied) or an exceeded tool-loop cap. */
public class ConverseException extends RuntimeException {

    public ConverseException(String message) {
        super(message);
    }

    public ConverseException(String message, Throwable cause) {
        super(message, cause);
    }
}
