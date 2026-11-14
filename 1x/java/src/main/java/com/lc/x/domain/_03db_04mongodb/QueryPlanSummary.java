package com.lc.x.domain._03db_04mongodb;

/**
 * The numbers from explain("executionStats") that decide whether a query is healthy.
 * - keysExamined / nReturned near 1 = selective index; a stage name of IXSCAN alone proves nothing.
 * - blockingSort = an in-memory SORT stage (100 MB limit); covered = no FETCH stage.
 */
public record QueryPlanSummary(
        String winningStage,
        String indexName,
        long keysExamined,
        long docsExamined,
        long nReturned,
        long executionMillis,
        boolean blockingSort,
        boolean covered) {

    public double keysPerResult() {
        return nReturned == 0 ? keysExamined : (double) keysExamined / nReturned;
    }
}
