package com.lc.x.x03_01_aurora.infra;

import com.zaxxer.hikari.SQLExceptionOverride;
import java.sql.SQLException;

/**
 * Tells Hikari to throw away a connection on errors that mean "this connection points at the wrong node".
 * - Hikari already evicts on SQLSTATE 08xxx and 57P01/57P02/57P03 (connection lost, admin/crash shutdown).
 * - Added here: 25006 read_only_sql_transaction on the WRITER pool = the connection reached a demoted writer
 *   (cached DNS after failover). Keeping it would fail every write that borrows it.
 * - Catch: only install on the writer pool; on the reader pool 25006 is a bug in the caller, not a stale node.
 */
public final class AuroraEvictionOverride implements SQLExceptionOverride {

    // java.lang.Override spelled out: inside this class the simple name Override means SQLExceptionOverride.Override.
    @java.lang.Override
    public SQLExceptionOverride.Override adjudicate(SQLException e) {
        return AuroraErrors.READ_ONLY_TRANSACTION.equals(e.getSQLState())
                ? SQLExceptionOverride.Override.MUST_EVICT
                : SQLExceptionOverride.Override.CONTINUE_EVICT;
    }
}
