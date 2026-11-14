"""Document records: heterogeneous metadata, one JSON document per file.

- JsonFileDocumentRepository: ILLUSTRATION. One JSON file, no server. Lite mode and tests.
- MongoDocumentRepository: PRODUCTION. MongoDB locally (docker compose); on GCP the same code
  talks to Firestore with MongoDB compatibility (just a different MONGO_URL).
"""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Protocol

from app.domain.models import DocumentRecord

log = logging.getLogger(__name__)


class DocumentRepository(Protocol):
    async def init(self) -> None: ...
    async def get(self, doc_id: str) -> DocumentRecord | None: ...
    async def get_by_sha(self, sha256: str) -> DocumentRecord | None: ...
    async def list(
        self, *, category: str | None = None, limit: int = 500
    ) -> list[DocumentRecord]: ...
    async def upsert(self, record: DocumentRecord) -> None: ...
    async def delete(self, doc_id: str) -> None: ...
    async def close(self) -> None: ...


def _sorted(records, category, limit):
    out = [r for r in records if not category or r.category.lower() == category.lower()]
    out.sort(key=lambda r: r.updated_at, reverse=True)
    return out[:limit]


class JsonFileDocumentRepository:
    def __init__(self, path: str) -> None:
        self._path = Path(path)
        self._lock = asyncio.Lock()

    def _read(self) -> dict[str, dict]:
        if not self._path.exists():
            return {}
        return json.loads(self._path.read_text() or "{}")

    def _write(self, data: dict[str, dict]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self._path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=1))
        tmp.replace(self._path)  # atomic on POSIX

    async def init(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)

    async def get(self, doc_id: str) -> DocumentRecord | None:
        raw = self._read().get(doc_id)
        return DocumentRecord.model_validate(raw) if raw else None

    async def get_by_sha(self, sha256: str) -> DocumentRecord | None:
        for raw in self._read().values():
            if raw["sha256"] == sha256:
                return DocumentRecord.model_validate(raw)
        return None

    async def list(self, *, category: str | None = None, limit: int = 500) -> list[DocumentRecord]:
        records = [DocumentRecord.model_validate(r) for r in self._read().values()]
        return _sorted(records, category, limit)

    async def upsert(self, record: DocumentRecord) -> None:
        async with self._lock:
            data = self._read()
            data[record.id] = record.model_dump(mode="json")
            self._write(data)

    async def delete(self, doc_id: str) -> None:
        async with self._lock:
            data = self._read()
            data.pop(doc_id, None)
            self._write(data)

    async def close(self) -> None:
        return None


class MongoDocumentRepository:
    """Works against MongoDB and Firestore (MongoDB compatibility). Records are stored as JSON
    (ISO dates, string enums) so both backends and the file repo see identical shapes."""

    def __init__(self, url: str, db: str, collection: str = "documents") -> None:
        from pymongo import AsyncMongoClient

        self._client = AsyncMongoClient(url, tz_aware=True)
        self._col = self._client[db][collection]

    async def init(self) -> None:
        try:
            await self._col.create_index("sha256")
            await self._col.create_index([("category", 1), ("updated_at", -1)])
        except Exception as e:  # index support differs across Mongo-compatible backends
            log.warning("mongo index creation skipped: %s", e)

    @staticmethod
    def _from(doc: dict | None) -> DocumentRecord | None:
        if not doc:
            return None
        doc = dict(doc)
        doc["id"] = doc.pop("_id")
        return DocumentRecord.model_validate(doc)

    async def get(self, doc_id: str) -> DocumentRecord | None:
        return self._from(await self._col.find_one({"_id": doc_id}))

    async def get_by_sha(self, sha256: str) -> DocumentRecord | None:
        return self._from(await self._col.find_one({"sha256": sha256}))

    async def list(self, *, category: str | None = None, limit: int = 500) -> list[DocumentRecord]:
        query = {"category": category} if category else {}
        cursor = self._col.find(query).sort("updated_at", -1).limit(limit)
        return [self._from(d) async for d in cursor]

    async def upsert(self, record: DocumentRecord) -> None:
        doc = record.model_dump(mode="json")
        doc["_id"] = doc.pop("id")
        await self._col.replace_one({"_id": doc["_id"]}, doc, upsert=True)

    async def delete(self, doc_id: str) -> None:
        await self._col.delete_one({"_id": doc_id})

    async def close(self) -> None:
        await self._client.close()
