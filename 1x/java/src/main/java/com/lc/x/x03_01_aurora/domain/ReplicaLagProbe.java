package com.lc.x.x03_01_aurora.domain;

import java.util.Map;

/** Port that reports per-reader replica lag in milliseconds. */
public interface ReplicaLagProbe {

    Map<String, Long> replicaLagMillis();
}
