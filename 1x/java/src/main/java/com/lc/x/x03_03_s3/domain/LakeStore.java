package com.lc.x.x03_03_s3.domain;

import java.nio.file.Path;
import java.time.Duration;
import java.util.Map;

/** Port: the S3 scenarios of doc 03.03, no SDK types. Adapter: infra.S3LakeStore. */
public interface LakeStore {

    // ---- 1. Basic object operations
    ObjectInfo put(String key, byte[] body, String contentType, Map<String, String> metadata);

    byte[] get(String key);

    ObjectInfo head(String key);

    void delete(String key);

    // ---- 2. Listing
    ListingPage listFolder(String prefix);

    // ---- 3. Presigned URLs
    String presignGet(String key, Duration expiry);

    String presignPut(String key, String contentType, Duration expiry);

    // ---- 4. Multipart and Transfer Manager
    ObjectInfo multipartUpload(String key, Path file, int partSizeBytes);

    ObjectInfo transferUpload(String key, Path file);

    long transferDownload(String key, Path target);

    // ---- 5. Conditional write, versions, range
    CreateResult putIfAbsent(String key, byte[] body);

    java.util.List<ObjectVersion> listVersions(String keyPrefix);

    byte[] getVersion(String key, String versionId);

    byte[] getRange(String key, long firstByte, long lastByte);
}
