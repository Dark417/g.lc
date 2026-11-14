package com.lc.x.domain._03db_04mongodb;

/** Optimistic-lock miss: the document exists but its version moved. current = the winner's state. */
public class VersionConflictException extends RuntimeException {

    private final transient Order current;

    public VersionConflictException(String orderId, long expectedVersion, Order current) {
        super("order " + orderId + " is not at version " + expectedVersion);
        this.current = current;
    }

    public Order current() {
        return current;
    }
}
