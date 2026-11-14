package com.lc.x.domain._03db_01aurora;

import java.util.Map;

/** Port that reports per-reader replica lag in milliseconds. */
public interface ReplicaLagProbe {

    Map<String, Long> replicaLagMillis();
}
