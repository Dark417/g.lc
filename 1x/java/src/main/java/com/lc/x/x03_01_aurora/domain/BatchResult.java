package com.lc.x.x03_01_aurora.domain;

import java.util.List;

/**
 * Outcome of a chunked import.
 * - Each chunk is its own transaction: a bad chunk fails alone, good chunks stay committed.
 * - failures: one line per failed chunk (index range + reason), so the caller can resubmit just those rows.
 */
public record BatchResult(int requested, int inserted, List<String> failures) {

    public BatchResult {
        failures = List.copyOf(failures);
    }
}
