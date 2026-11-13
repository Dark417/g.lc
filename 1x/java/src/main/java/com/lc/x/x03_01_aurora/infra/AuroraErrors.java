package com.lc.x.x03_01_aurora.infra;

import java.sql.SQLException;
import java.util.Set;

/**
 * SQLSTATE classification for retries.
 * - Spring wraps SQLException in DataAccessException; the SQLSTATE is found by walking the cause chain.
 * - Retry only whole transactions, from outside them, and only idempotent writes (see AuroraOrderService.withRetry).
 */
public final class AuroraErrors {

    public static final String SERIALIZATION_FAILURE = "40001";
    public static final String DEADLOCK_DETECTED = "40P01";
    public static final String READ_ONLY_TRANSACTION = "25006";
    public static final String LOCK_NOT_AVAILABLE = "55P03";
    public static final String UNIQUE_VIOLATION = "23505";

    /** Server shutting down / restarting / not yet accepting connections: seen during failover and reboots. */
    private static final Set<String> SHUTDOWN = Set.of("57P01", "57P02", "57P03");

    private AuroraErrors() {
    }

    /** First SQLSTATE found in the cause chain, or null (e.g. pool wait timeout with no prior connection error). */
    public static String sqlState(Throwable t) {
        for (Throwable c = t; c != null; c = c.getCause()) {
            if (c instanceof SQLException sql) {
                for (SQLException s = sql; s != null; s = s.getNextException()) {
                    if (s.getSQLState() != null) {
                        return s.getSQLState();
                    }
                }
            }
            if (c.getCause() == c) {
                break;
            }
        }
        return null;
    }

    /**
     * Transient = a fresh transaction may succeed.
     * - 40001 / 40P01: the database chose this transaction as the victim; retry the whole thing.
     * - 08xxx / 57P0x: connection lost or node restarting (failover). Commit outcome may be unknown => idempotency key.
     * - 25006: writer pool reached a demoted node (stale DNS); the connection is evicted, the retry gets a new one.
     * - 55P03: lock_timeout fired under contention.
     * - Not retried: 23xxx constraint violations, 42xxx bugs, null SQLSTATE (pool saturated: shed load, don't amplify).
     */
    public static boolean isRetryable(Throwable t) {
        String state = sqlState(t);
        if (state == null) {
            return false;
        }
        return state.equals(SERIALIZATION_FAILURE)
                || state.equals(DEADLOCK_DETECTED)
                || state.startsWith("08")
                || SHUTDOWN.contains(state)
                || state.equals(READ_ONLY_TRANSACTION)
                || state.equals(LOCK_NOT_AVAILABLE);
    }
}
