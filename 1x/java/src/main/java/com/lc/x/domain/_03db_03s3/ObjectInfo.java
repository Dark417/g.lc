package com.lc.x.domain._03db_03s3;

import java.util.Map;

/** Result of head/put: what S3 stores next to the bytes (user metadata, etag, version). */
public record ObjectInfo(
        String key, long size, String etag, String versionId, String contentType,
        String sseAlgorithm, String kmsKeyId, Map<String, String> metadata) {
}
