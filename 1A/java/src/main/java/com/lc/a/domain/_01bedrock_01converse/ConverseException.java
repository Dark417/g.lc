package com.lc.a.domain._01bedrock_01converse;

/** Non-retryable request problem (ValidationException, AccessDenied) or an exceeded tool-loop cap. */
public class ConverseException extends RuntimeException {

    public ConverseException(String message) {
        super(message);
    }

    public ConverseException(String message, Throwable cause) {
        super(message, cause);
    }
}
