package com.lc.x.x03_02_dynamodb.domain;

/** Optimistic-lock failure; current = the winner's item (from ALL_OLD), or null when the item is missing. */
public class VersionConflictException extends RuntimeException {

    private final transient Order current;

    public VersionConflictException(Order current) {
        super(current == null ? "order not found" : "version conflict, current version " + current.version());
        this.current = current;
    }

    public Order current() {
        return current;
    }
}
