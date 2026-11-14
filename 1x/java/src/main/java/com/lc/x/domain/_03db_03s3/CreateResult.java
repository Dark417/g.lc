package com.lc.x.domain._03db_03s3;

/** Outcome of a create-only write: created, or lost the race (HTTP 412 PreconditionFailed). */
public record CreateResult(boolean created, String etag, String versionId) {
}
