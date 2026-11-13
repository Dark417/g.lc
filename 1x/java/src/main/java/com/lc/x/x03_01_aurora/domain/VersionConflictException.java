package com.lc.x.x03_01_aurora.domain;

/** Optimistic-lock failure: the row changed since the caller read it (HTTP 409; client re-reads). */
public class VersionConflictException extends RuntimeException {

    public VersionConflictException(String message) {
        super(message);
    }
}
