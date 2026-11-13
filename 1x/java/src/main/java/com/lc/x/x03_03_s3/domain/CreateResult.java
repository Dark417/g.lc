package com.lc.x.x03_03_s3.domain;

/** Outcome of a create-only write: created, or lost the race (HTTP 412 PreconditionFailed). */
public record CreateResult(boolean created, String etag, String versionId) {
}
