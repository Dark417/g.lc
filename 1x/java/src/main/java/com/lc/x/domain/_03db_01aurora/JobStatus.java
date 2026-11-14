package com.lc.x.domain._03db_01aurora;

/** Job queue states: READY -> RUNNING (leased) -> DONE, or back to READY / FAILED on error. */
public enum JobStatus {
    READY,
    RUNNING,
    DONE,
    FAILED
}
