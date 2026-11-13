package com.lc.x.x03_01_aurora.domain;

import java.time.Duration;
import java.util.List;
import java.util.Map;

/** Port for a table-backed job queue (FOR UPDATE SKIP LOCKED + leases). Delivery is at least once. */
public interface JobQueue {

    long enqueue(String kind, Map<String, Object> payload);

    List<Job> claim(String workerId, int limit, Duration lease);

    void complete(long jobId, String workerId);

    void fail(long jobId, String workerId, String error, Duration retryDelay, int maxAttempts);

    int requeueExpired(int maxAttempts);
}
