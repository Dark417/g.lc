package com.lc.x.domain._03db_04mongodb;

import java.util.List;

/**
 * Result of an unordered bulk write. errors lists "index:code:message" per failed op;
 * the successful ops are NOT rolled back (bulk writes are not transactions).
 */
public record BulkSummary(int inserted, int matched, int modified, int upserted, int deleted, List<String> errors) {

    public BulkSummary {
        errors = List.copyOf(errors);
    }
}
