"""S3 adapter: one function per scenario of doc 03.03 (boto3 client, no calls at import)."""

from pathlib import Path
from typing import Any

from boto3.s3.transfer import TransferConfig
from botocore.exceptions import ClientError

from app.shared.aws import client
from app.shared.config import get_settings
from app.x03_03_s3.domain import CreateResult, ListingPage, ObjectInfo, ObjectVersion

MIN_PART_BYTES = 5 * 1024 * 1024  # every part but the last must be >= 5 MiB; max 10,000 parts


def _s3() -> Any:
    return client("s3")


def _bucket() -> str:
    return get_settings().s3_lake_bucket


def _kms_args() -> dict[str, Any]:
    # SSE-KMS per request (bucket default is already SSE-KMS); Bucket Keys cut KMS request cost.
    return {
        "ServerSideEncryption": "aws:kms",
        "SSEKMSKeyId": get_settings().s3_kms_key_alias,
        "BucketKeyEnabled": True,
    }


# ============================================================ 1. Basic object operations


def put(key: str, body: bytes, content_type: str, metadata: dict[str, str]) -> ObjectInfo:
    # Put with user metadata + SSE-KMS. Use for small objects (hard cap 5 GiB per PUT).
    # Catch: metadata is immutable after write; SSE-KMS needs kms:GenerateDataKey on the caller.
    r = _s3().put_object(
        Bucket=_bucket(), Key=key, Body=body, ContentType=content_type, Metadata=metadata, **_kms_args()
    )
    return ObjectInfo(
        key, len(body), r.get("ETag"), r.get("VersionId"), content_type,
        r.get("ServerSideEncryption"), r.get("SSEKMSKeyId"), metadata,
    )


def get(key: str) -> bytes:
    # Whole-object read into memory. Use only for small objects; stream Body otherwise.
    # Catch: missing key (or delete marker on top) raises ClientError NoSuchKey (404).
    return _s3().get_object(Bucket=_bucket(), Key=key)["Body"].read()


def head(key: str) -> ObjectInfo:
    # Metadata without the body: cheap existence/size check.
    # Catch: a missing key is a bare 404 with code "404" (no body); 403 if s3:ListBucket is missing.
    r = _s3().head_object(Bucket=_bucket(), Key=key)
    return ObjectInfo(
        key, r["ContentLength"], r.get("ETag"), r.get("VersionId"), r.get("ContentType"),
        r.get("ServerSideEncryption"), r.get("SSEKMSKeyId"), r.get("Metadata", {}),
    )


def delete(key: str) -> None:
    # On a versioned bucket this writes a delete marker; bytes stay and are recoverable.
    # Catch: only delete_object with VersionId removes data permanently; deleting a missing key still succeeds.
    _s3().delete_object(Bucket=_bucket(), Key=key)


# ============================================================ 2. Listing


def list_folder(prefix: str) -> ListingPage:
    # list_objects_v2 paginator with prefix + delimiter "/": keys directly under prefix + "folders".
    # Catch: one response = max 1,000 keys; "folders" are only shared key prefixes.
    keys: list[str] = []
    folders: list[str] = []
    pages = 0
    paginator = _s3().get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=_bucket(), Prefix=prefix, Delimiter="/"):
        pages += 1
        keys.extend(o["Key"] for o in page.get("Contents", []))
        folders.extend(p["Prefix"] for p in page.get("CommonPrefixes", []))
    return ListingPage(keys, folders, pages)


# ============================================================ 3. Presigned URLs


def presign_get(key: str, expires_seconds: int = 300) -> str:
    # Presigned GET: holder reads until expiry without AWS credentials. Signed locally, no network call.
    # Catch: with role/STS credentials the URL dies when the session token expires, even before ExpiresIn.
    return _s3().generate_presigned_url(
        "get_object", Params={"Bucket": _bucket(), "Key": key}, ExpiresIn=expires_seconds
    )


def presign_put(key: str, content_type: str, expires_seconds: int = 300) -> str:
    # Presigned PUT for direct browser upload; the client must send the same Content-Type.
    # Catch: any signed header that differs at upload time gives 403 SignatureDoesNotMatch.
    return _s3().generate_presigned_url(
        "put_object",
        Params={"Bucket": _bucket(), "Key": key, "ContentType": content_type},
        ExpiresIn=expires_seconds,
    )


def presign_post(key_prefix: str, max_bytes: int, expires_seconds: int = 300) -> dict[str, Any]:
    # Presigned POST (HTML form upload): a policy can enforce key prefix and max size, which PUT URLs cannot.
    # Catch: the browser must send the returned fields first and the file field last.
    return _s3().generate_presigned_post(
        Bucket=_bucket(),
        Key=key_prefix + "${filename}",
        Conditions=[["starts-with", "$key", key_prefix], ["content-length-range", 1, max_bytes]],
        ExpiresIn=expires_seconds,
    )


# ============================================================ 4. Multipart and Transfer Manager


def multipart_upload(key: str, file: Path, part_size: int = MIN_PART_BYTES) -> ObjectInfo:
    # Low-level multipart: create -> upload_part loop -> complete, abort on any failure.
    # Catch: un-aborted uploads keep billing for parts (lifecycle rule aborts after 7 days).
    if part_size < MIN_PART_BYTES:
        raise ValueError("part size must be >= 5 MiB (only the last part may be smaller)")
    s3 = _s3()
    upload_id = s3.create_multipart_upload(Bucket=_bucket(), Key=key, **_kms_args())["UploadId"]
    try:
        parts: list[dict[str, Any]] = []
        with file.open("rb") as fh:
            part_number = 1  # 1..10,000
            while chunk := fh.read(part_size):
                # Retrying one part is safe: the same PartNumber overwrites the earlier attempt.
                etag = s3.upload_part(
                    Bucket=_bucket(), Key=key, UploadId=upload_id, PartNumber=part_number, Body=chunk
                )["ETag"]
                parts.append({"PartNumber": part_number, "ETag": etag})
                part_number += 1
        s3.complete_multipart_upload(
            Bucket=_bucket(), Key=key, UploadId=upload_id, MultipartUpload={"Parts": parts}
        )
    except Exception:
        # Partial failure: free stored parts, otherwise they are billed invisibly.
        s3.abort_multipart_upload(Bucket=_bucket(), Key=key, UploadId=upload_id)
        raise
    return head(key)


def transfer_upload(key: str, file: Path) -> None:
    # upload_file = managed transfer: auto-multipart above the threshold, parallel parts, abort on failure.
    # Default for files. Catch: it uses threads, so max_concurrency x part size bounds memory use.
    config = TransferConfig(
        multipart_threshold=16 * 1024 * 1024,
        multipart_chunksize=16 * 1024 * 1024,
        max_concurrency=8,
        use_threads=True,
    )
    _s3().upload_file(str(file), _bucket(), key, ExtraArgs=_kms_args(), Config=config)


def transfer_download(key: str, target: Path) -> None:
    # download_file = parallel ranged GETs into a local file.
    # Catch: writes to a temp file, then renames; a failure leaves no partial target.
    _s3().download_file(_bucket(), key, str(target), Config=TransferConfig(max_concurrency=8))


# ============================================================ 5. Conditional write, versions, range


def put_if_absent(key: str, body: bytes) -> CreateResult:
    # Create-only put (If-None-Match: *): first writer wins, the loser gets 412. Use for locks / idempotent creates.
    # Catch: 409 ConditionalRequestConflict can happen under concurrent writes: retry it; 412 = already exists.
    try:
        r = _s3().put_object(Bucket=_bucket(), Key=key, Body=body, IfNoneMatch="*")
    except ClientError as e:
        status = e.response["ResponseMetadata"]["HTTPStatusCode"]
        if status == 412:  # PreconditionFailed: key exists, nothing written
            return CreateResult(created=False)
        raise  # 409 and others: caller decides
    return CreateResult(created=True, etag=r.get("ETag"), version_id=r.get("VersionId"))


def list_versions(key_prefix: str) -> list[ObjectVersion]:
    # list_object_versions paginator: versions + delete markers (needs s3:ListBucketVersions).
    # Catch: lifecycle noncurrent expiry (30 days under raw/) removes old versions from this list.
    out: list[ObjectVersion] = []
    for page in _s3().get_paginator("list_object_versions").paginate(Bucket=_bucket(), Prefix=key_prefix):
        for v in page.get("Versions", []):
            out.append(ObjectVersion(v["Key"], v["VersionId"], v["IsLatest"], False, v["LastModified"], v["Size"]))
        for m in page.get("DeleteMarkers", []):
            out.append(ObjectVersion(m["Key"], m["VersionId"], m["IsLatest"], True, m["LastModified"], 0))
    return out


def get_version(key: str, version_id: str) -> bytes:
    # Read one specific old version (needs s3:GetObjectVersion). Use for rollback or audit.
    # Catch: a delete marker's VersionId returns 405, not 404.
    return _s3().get_object(Bucket=_bucket(), Key=key, VersionId=version_id)["Body"].read()


def get_range(key: str, first_byte: int, last_byte: int) -> bytes:
    # Ranged GET (inclusive bounds): read a Parquet footer or resume a download.
    # Catch: a start beyond the object size returns 416 InvalidRange.
    return _s3().get_object(
        Bucket=_bucket(), Key=key, Range=f"bytes={first_byte}-{last_byte}"
    )["Body"].read()
