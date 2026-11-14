package com.lc.x.domain._03db_01aurora;

/** Port for an append-only audit trail. Whether a row survives a rollback depends on the caller's propagation. */
public interface AuditLog {

    void append(String action, String detail);
}
