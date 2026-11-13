package com.lc.x.x03_03_s3.domain;

import java.time.Instant;

/** One entry of ListObjectVersions: a real version, or a delete marker (isDeleteMarker = true). */
public record ObjectVersion(String key, String versionId, boolean isLatest, boolean isDeleteMarker,
                            Instant lastModified, long size) {
}
