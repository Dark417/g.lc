package com.lc.x.x03_01_aurora.service;

import com.lc.x.x03_01_aurora.domain.AuditLog;
import com.lc.x.x03_01_aurora.infra.AuroraConfig;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;

/**
 * Propagation side by side. A separate bean on purpose: @Transactional works through the Spring proxy,
 * so calling these from inside AuroraOrderTx (another bean) goes through the proxy; a self-call would not.
 */
@Service
@ConditionalOnProperty(name = "x.aurora.enabled", havingValue = "true")
public class AuroraAuditService {

    private final AuditLog audit;

    public AuroraAuditService(AuditLog audit) {
        this.audit = audit;
    }

    // REQUIRED (default): joins the caller's transaction; the audit row commits or rolls back WITH the business change.
    // When to use: "this happened" records that must not exist if the change didn't. Catch: an exception here marks the
    // whole outer transaction rollback-only, even if the caller catches it (UnexpectedRollbackException at commit).
    @Transactional(transactionManager = AuroraConfig.WRITER_TX, propagation = Propagation.REQUIRED)
    public void recordJoined(String action, String detail) {
        audit.append(action, detail);
    }

    // REQUIRES_NEW: suspends the caller's transaction and commits this row on a SECOND connection right away.
    // When to use: attempt logs that must survive the caller's rollback. Catch: two connections per request =>
    // with pool size <= concurrent callers every thread holds one and waits for a second (pool starvation).
    @Transactional(transactionManager = AuroraConfig.WRITER_TX, propagation = Propagation.REQUIRES_NEW)
    public void recordIndependent(String action, String detail) {
        audit.append(action, detail);
    }
}
