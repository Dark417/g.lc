package com.lc.x.x03_01_aurora.domain;

/** Port for an append-only audit trail. Whether a row survives a rollback depends on the caller's propagation. */
public interface AuditLog {

    void append(String action, String detail);
}
