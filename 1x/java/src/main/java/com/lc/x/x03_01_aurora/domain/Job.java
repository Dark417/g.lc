package com.lc.x.x03_01_aurora.domain;

import java.time.Instant;
import java.util.Map;

/**
 * A job row in the table-backed queue.
 * - lockedBy / lockedUntil: the lease; only the lease owner may complete or fail the job.
 * - attempts: incremented on every claim, so a crash-looping job eventually goes to FAILED.
 */
public record Job(
        long id,
        String kind,
        Map<String, Object> payload,
        JobStatus status,
        int attempts,
        String lockedBy,
        Instant lockedUntil) {
}
