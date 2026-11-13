package com.lc.x.x03_03_s3.infra;

import com.lc.x.x03_03_s3.domain.CreateResult;
import com.lc.x.x03_03_s3.domain.LakeStore;
import com.lc.x.x03_03_s3.domain.ListingPage;
import com.lc.x.x03_03_s3.domain.ObjectInfo;
import com.lc.x.x03_03_s3.domain.ObjectVersion;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;
import software.amazon.awssdk.core.ResponseBytes;
import software.amazon.awssdk.core.sync.RequestBody;
import software.amazon.awssdk.core.sync.ResponseTransformer;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.AbortMultipartUploadRequest;
import software.amazon.awssdk.services.s3.model.CommonPrefix;
import software.amazon.awssdk.services.s3.model.CompleteMultipartUploadRequest;
import software.amazon.awssdk.services.s3.model.CompletedMultipartUpload;
import software.amazon.awssdk.services.s3.model.CompletedPart;
import software.amazon.awssdk.services.s3.model.CreateMultipartUploadRequest;
import software.amazon.awssdk.services.s3.model.DeleteObjectRequest;
import software.amazon.awssdk.services.s3.model.GetObjectRequest;
import software.amazon.awssdk.services.s3.model.GetObjectResponse;
import software.amazon.awssdk.services.s3.model.HeadObjectRequest;
import software.amazon.awssdk.services.s3.model.HeadObjectResponse;
import software.amazon.awssdk.services.s3.model.ListObjectVersionsRequest;
import software.amazon.awssdk.services.s3.model.ListObjectsV2Request;
import software.amazon.awssdk.services.s3.model.ListObjectsV2Response;
import software.amazon.awssdk.services.s3.model.PutObjectRequest;
import software.amazon.awssdk.services.s3.model.PutObjectResponse;
import software.amazon.awssdk.services.s3.model.S3Exception;
import software.amazon.awssdk.services.s3.model.ServerSideEncryption;
import software.amazon.awssdk.services.s3.model.UploadPartRequest;
import software.amazon.awssdk.services.s3.presigner.S3Presigner;
import software.amazon.awssdk.services.s3.presigner.model.GetObjectPresignRequest;
import software.amazon.awssdk.services.s3.presigner.model.PutObjectPresignRequest;
import software.amazon.awssdk.transfer.s3.S3TransferManager;
import software.amazon.awssdk.transfer.s3.model.CompletedFileDownload;
import software.amazon.awssdk.transfer.s3.model.CompletedFileUpload;
import software.amazon.awssdk.transfer.s3.model.DownloadFileRequest;
import software.amazon.awssdk.transfer.s3.model.UploadFileRequest;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/**
 * Outbound adapter: every S3 scenario of doc 03.03 as one method.
 * Bucket = x.s3.lake-bucket (Terraform output lake_bucket); the bucket default encryption is already SSE-KMS,
 * we still pass the key alias explicitly in put() to show the per-request override.
 */
@Component
@ConditionalOnProperty(name = "x.s3.enabled", havingValue = "true")
public class S3LakeStore implements LakeStore {

    // S3 rule: every part except the last must be >= 5 MiB; max 10,000 parts per upload.
    static final int MIN_PART_BYTES = 5 * 1024 * 1024;

    private final S3Client s3;
    private final S3Presigner presigner;
    private final S3TransferManager transfer;
    private final String bucket;
    private final String kmsKeyAlias;

    public S3LakeStore(S3Client s3, S3Presigner presigner, S3TransferManager transfer,
                       @Value("${x.s3.lake-bucket}") String bucket,
                       @Value("${x.s3.kms-key-alias:alias/x-data}") String kmsKeyAlias) {
        this.s3 = s3;
        this.presigner = presigner;
        this.transfer = transfer;
        this.bucket = bucket;
        this.kmsKeyAlias = kmsKeyAlias;
    }

    // ============================================================ 1. Basic object operations

    // Shows put with user metadata + SSE-KMS (key alias). Use for small objects (< ~100 MiB, hard cap 5 GiB).
    // Catch: user metadata is immutable after write (changing it = copy onto itself); SSE-KMS needs kms:GenerateDataKey.
    @Override
    public ObjectInfo put(String key, byte[] body, String contentType, Map<String, String> metadata) {
        PutObjectResponse r = s3.putObject(PutObjectRequest.builder()
                        .bucket(bucket).key(key).contentType(contentType).metadata(metadata)
                        .serverSideEncryption(ServerSideEncryption.AWS_KMS)
                        .ssekmsKeyId(kmsKeyAlias)
                        .bucketKeyEnabled(true) // fewer KMS calls per object -> lower KMS request cost
                        .build(),
                RequestBody.fromBytes(body));
        return new ObjectInfo(key, body.length, r.eTag(), r.versionId(), contentType,
                r.serverSideEncryptionAsString(), r.ssekmsKeyId(), metadata);
    }

    // Shows get of the whole body into memory. Use only for small objects; stream (ResponseInputStream) otherwise.
    // Catch: NoSuchKeyException = 404; with versioning, a delete marker on top also reads as 404.
    @Override
    public byte[] get(String key) {
        ResponseBytes<GetObjectResponse> bytes = s3.getObject(
                GetObjectRequest.builder().bucket(bucket).key(key).build(), ResponseTransformer.toBytes());
        return bytes.asByteArray();
    }

    // Shows head: size/etag/metadata/encryption without the body (cheap existence check).
    // Catch: HEAD has no error body, so a missing key is a bare 404 (NoSuchKeyException), and 403 if s3:ListBucket is missing.
    @Override
    public ObjectInfo head(String key) {
        HeadObjectResponse h = s3.headObject(HeadObjectRequest.builder().bucket(bucket).key(key).build());
        return new ObjectInfo(key, h.contentLength(), h.eTag(), h.versionId(), h.contentType(),
                h.serverSideEncryptionAsString(), h.ssekmsKeyId(), h.metadata());
    }

    // Shows delete. On a versioned bucket it writes a delete marker (data stays, recoverable); it never fails for a missing key.
    // Catch: only deleteObject with a versionId removes bytes permanently.
    @Override
    public void delete(String key) {
        s3.deleteObject(DeleteObjectRequest.builder().bucket(bucket).key(key).build());
    }

    // ============================================================ 2. Listing

    // Shows ListObjectsV2 with prefix + delimiter "/": keys directly under prefix + sub-"folders" as common prefixes.
    // Use the paginator: one response holds max 1,000 keys. Catch: folders are just key prefixes, no directory object exists.
    @Override
    public ListingPage listFolder(String prefix) {
        List<String> keys = new ArrayList<>();
        List<String> folders = new ArrayList<>();
        int pages = 0;
        for (ListObjectsV2Response page : s3.listObjectsV2Paginator(ListObjectsV2Request.builder()
                .bucket(bucket).prefix(prefix).delimiter("/").maxKeys(1000).build())) {
            pages++;
            page.contents().forEach(o -> keys.add(o.key()));
            page.commonPrefixes().stream().map(CommonPrefix::prefix).forEach(folders::add);
        }
        return new ListingPage(keys, folders, pages);
    }

    // ============================================================ 3. Presigned URLs

    // Shows a presigned GET: anyone holding the URL can read until it expires, no AWS credentials needed.
    // Catch: signed by OUR credentials; with a role/STS session the URL dies when the session token expires (earlier than expiry).
    @Override
    public String presignGet(String key, Duration expiry) {
        return presigner.presignGetObject(GetObjectPresignRequest.builder()
                .signatureDuration(expiry)
                .getObjectRequest(GetObjectRequest.builder().bucket(bucket).key(key).build())
                .build()).url().toString();
    }

    // Shows a presigned PUT for direct browser/mobile upload (bytes skip our server).
    // Catch: headers signed into the URL (content-type, SSE headers) must be sent identically, else 403 SignatureDoesNotMatch.
    @Override
    public String presignPut(String key, String contentType, Duration expiry) {
        return presigner.presignPutObject(PutObjectPresignRequest.builder()
                .signatureDuration(expiry)
                .putObjectRequest(PutObjectRequest.builder().bucket(bucket).key(key).contentType(contentType).build())
                .build()).url().toString();
    }

    // ============================================================ 4. Multipart and Transfer Manager

    // Shows low-level multipart: create -> uploadPart loop -> complete, abort on any failure.
    // Use for big files or resumable uploads. Catch: un-aborted uploads keep billing for parts (lifecycle rule aborts after 7 days).
    @Override
    public ObjectInfo multipartUpload(String key, Path file, int partSizeBytes) {
        if (partSizeBytes < MIN_PART_BYTES) {
            throw new IllegalArgumentException("part size must be >= 5 MiB (only the last part may be smaller)");
        }
        String uploadId = s3.createMultipartUpload(CreateMultipartUploadRequest.builder()
                .bucket(bucket).key(key)
                .serverSideEncryption(ServerSideEncryption.AWS_KMS).ssekmsKeyId(kmsKeyAlias)
                .build()).uploadId();
        try (InputStream in = Files.newInputStream(file)) {
            long size = Files.size(file);
            List<CompletedPart> parts = new ArrayList<>();
            int partNumber = 1; // part numbers are 1..10,000
            long sent = 0;
            while (sent < size) {
                byte[] buf = in.readNBytes(partSizeBytes);
                // Retrying one failed part is safe: same partNumber overwrites the earlier attempt.
                String etag = s3.uploadPart(UploadPartRequest.builder()
                                .bucket(bucket).key(key).uploadId(uploadId).partNumber(partNumber).build(),
                        RequestBody.fromBytes(buf)).eTag();
                parts.add(CompletedPart.builder().partNumber(partNumber).eTag(etag).build());
                sent += buf.length;
                partNumber++;
            }
            s3.completeMultipartUpload(CompleteMultipartUploadRequest.builder()
                    .bucket(bucket).key(key).uploadId(uploadId)
                    .multipartUpload(CompletedMultipartUpload.builder().parts(parts).build()).build());
            return head(key);
        } catch (IOException | RuntimeException e) {
            // Partial failure: free the stored parts, otherwise they are billed invisibly.
            s3.abortMultipartUpload(AbortMultipartUploadRequest.builder()
                    .bucket(bucket).key(key).uploadId(uploadId).build());
            throw e instanceof RuntimeException re ? re : new IllegalStateException("multipart failed", e);
        }
    }

    // Shows Transfer Manager upload: it chooses part size, uploads parts in parallel, aborts on failure.
    // Use as the default for files. Catch: needs the async client with multipart; throughput is bounded by local disk/NIC.
    @Override
    public ObjectInfo transferUpload(String key, Path file) {
        CompletedFileUpload done = transfer.uploadFile(UploadFileRequest.builder()
                .source(file)
                .putObjectRequest(PutObjectRequest.builder().bucket(bucket).key(key)
                        .serverSideEncryption(ServerSideEncryption.AWS_KMS).ssekmsKeyId(kmsKeyAlias).build())
                .build()).completionFuture().join();
        return new ObjectInfo(key, -1, done.response().eTag(), done.response().versionId(), null,
                done.response().serverSideEncryptionAsString(), done.response().ssekmsKeyId(), Map.of());
    }

    // Shows Transfer Manager download to a file using parallel ranged GETs. Returns bytes written.
    // Catch: the target file must not exist yet (the request fails rather than overwrite).
    @Override
    public long transferDownload(String key, Path target) {
        CompletedFileDownload done = transfer.downloadFile(DownloadFileRequest.builder()
                .getObjectRequest(GetObjectRequest.builder().bucket(bucket).key(key).build())
                .destination(target).build()).completionFuture().join();
        return done.response().contentLength();
    }

    // ============================================================ 5. Conditional write, versions, range

    // Shows create-only put (If-None-Match: *): the first writer wins, the loser gets 412. Use for locks/idempotent creates.
    // Catch: 409 ConditionalRequestConflict can occur on concurrent writes: retry it; 412 means "already exists".
    @Override
    public CreateResult putIfAbsent(String key, byte[] body) {
        try {
            PutObjectResponse r = s3.putObject(PutObjectRequest.builder()
                    .bucket(bucket).key(key).ifNoneMatch("*").build(), RequestBody.fromBytes(body));
            return new CreateResult(true, r.eTag(), r.versionId());
        } catch (S3Exception e) {
            if (e.statusCode() == 412) { // PreconditionFailed: key already exists, nothing written
                return new CreateResult(false, null, null);
            }
            throw e; // 409 and others: let the caller / SDK retry policy decide
        }
    }

    // Shows ListObjectVersions: real versions and delete markers for a key prefix (needs s3:ListBucketVersions).
    // Catch: the lifecycle noncurrent expiry (30 days under raw/) removes old versions from this list.
    @Override
    public List<ObjectVersion> listVersions(String keyPrefix) {
        List<ObjectVersion> out = new ArrayList<>();
        s3.listObjectVersionsPaginator(ListObjectVersionsRequest.builder().bucket(bucket).prefix(keyPrefix).build())
                .forEach(page -> {
                    page.versions().forEach(v -> out.add(new ObjectVersion(
                            v.key(), v.versionId(), Boolean.TRUE.equals(v.isLatest()), false, v.lastModified(), v.size())));
                    page.deleteMarkers().forEach(m -> out.add(new ObjectVersion(
                            m.key(), m.versionId(), Boolean.TRUE.equals(m.isLatest()), true, m.lastModified(), 0L)));
                });
        return out;
    }

    // Shows reading one specific old version (needs s3:GetObjectVersion). Use for rollback or audit.
    // Catch: passing a delete marker's versionId returns 405, not 404.
    @Override
    public byte[] getVersion(String key, String versionId) {
        return s3.getObject(GetObjectRequest.builder().bucket(bucket).key(key).versionId(versionId).build(),
                ResponseTransformer.toBytes()).asByteArray();
    }

    // Shows a ranged GET (HTTP Range, inclusive bounds): read a Parquet footer or resume a download.
    // Catch: a start beyond the object size returns 416; the range is on stored bytes, not on decrypted logical rows.
    @Override
    public byte[] getRange(String key, long firstByte, long lastByte) {
        return s3.getObject(GetObjectRequest.builder().bucket(bucket).key(key)
                .range("bytes=" + firstByte + "-" + lastByte).build(), ResponseTransformer.toBytes()).asByteArray();
    }
}
