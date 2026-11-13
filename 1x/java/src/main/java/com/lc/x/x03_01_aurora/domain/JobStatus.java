package com.lc.x.x03_01_aurora.domain;

/** Job queue states: READY -> RUNNING (leased) -> DONE, or back to READY / FAILED on error. */
public enum JobStatus {
    READY,
    RUNNING,
    DONE,
    FAILED
}
