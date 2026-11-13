"""Domain models for the S3 slice (no SDK imports)."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class ObjectInfo:
    key: str
    size: int
    etag: str | None
    version_id: str | None
    content_type: str | None
    sse_algorithm: str | None
    kms_key_id: str | None
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ListingPage:
    keys: list[str]
    common_prefixes: list[str]  # the "folders"
    pages_fetched: int


@dataclass(frozen=True)
class ObjectVersion:
    key: str
    version_id: str
    is_latest: bool
    is_delete_marker: bool
    last_modified: datetime
    size: int


@dataclass(frozen=True)
class CreateResult:
    created: bool  # False = key already existed (HTTP 412), nothing written
    etag: str | None = None
    version_id: str | None = None
