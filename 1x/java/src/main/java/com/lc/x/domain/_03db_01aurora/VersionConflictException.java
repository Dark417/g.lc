package com.lc.x.domain._03db_01aurora;

/** Optimistic-lock failure: the row changed since the caller read it (HTTP 409; client re-reads). */
public class VersionConflictException extends RuntimeException {

    public VersionConflictException(String message) {
        super(message);
    }
}
