package com.lc.x.x03_01_aurora.domain;

/** A worker tried to finish a job it no longer owns (its lease expired and another worker re-claimed it). */
public class LeaseLostException extends RuntimeException {

    public LeaseLostException(long jobId, String workerId) {
        super("job " + jobId + " is not leased by " + workerId);
    }
}
