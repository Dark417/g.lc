"""Raw files and extracted text. Local directory or GCS, same interface."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Protocol


class BlobStore(Protocol):
    async def put(self, key: str, data: bytes, content_type: str = "") -> str: ...
    async def get(self, key: str) -> bytes: ...
    async def list(self, prefix: str) -> list[str]: ...
    async def delete_prefix(self, prefix: str) -> None: ...


class LocalBlobStore:
    """ILLUSTRATION: a directory on disk. Fine for one machine."""

    def __init__(self, root: str) -> None:
        self._root = Path(root).resolve()

    def _path(self, key: str) -> Path:
        path = (self._root / key).resolve()
        if self._root not in path.parents and path != self._root:
            raise ValueError(f"invalid blob key: {key}")
        return path

    async def put(self, key: str, data: bytes, content_type: str = "") -> str:
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path.as_uri()

    async def get(self, key: str) -> bytes:
        return self._path(key).read_bytes()

    async def list(self, prefix: str) -> list[str]:
        base = self._path(prefix) if prefix else self._root
        if not base.exists():
            return []
        return sorted(str(p.relative_to(self._root)) for p in base.rglob("*") if p.is_file())

    async def delete_prefix(self, prefix: str) -> None:
        base = self._path(prefix)
        if base.exists():
            for p in sorted(base.rglob("*"), reverse=True):
                p.unlink() if p.is_file() else p.rmdir()
            base.rmdir()


class GcsBlobStore:
    """PRODUCTION: Google Cloud Storage. The client is sync, so calls run in a thread."""

    def __init__(self, bucket: str) -> None:
        from google.cloud import storage

        self._bucket_name = bucket
        self._bucket = storage.Client().bucket(bucket)

    async def put(self, key: str, data: bytes, content_type: str = "") -> str:
        blob = self._bucket.blob(key)
        await asyncio.to_thread(
            blob.upload_from_string, data, content_type=content_type or "application/octet-stream"
        )
        return f"gs://{self._bucket_name}/{key}"

    async def get(self, key: str) -> bytes:
        return await asyncio.to_thread(self._bucket.blob(key).download_as_bytes)

    async def list(self, prefix: str) -> list[str]:
        blobs = await asyncio.to_thread(lambda: list(self._bucket.list_blobs(prefix=prefix)))
        return [b.name for b in blobs if not b.name.endswith("/")]

    async def delete_prefix(self, prefix: str) -> None:
        for name in await self.list(prefix):
            await asyncio.to_thread(self._bucket.blob(name).delete)
