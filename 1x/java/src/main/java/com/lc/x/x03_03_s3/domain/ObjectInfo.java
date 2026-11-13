package com.lc.x.x03_03_s3.domain;

import java.util.Map;

/** Result of head/put: what S3 stores next to the bytes (user metadata, etag, version). */
public record ObjectInfo(
        String key, long size, String etag, String versionId, String contentType,
        String sseAlgorithm, String kmsKeyId, Map<String, String> metadata) {
}
