"""Operational commands. Same container as the API.

python -m app.cli seed                       # sample rules + documents (idempotent)
python -m app.cli ingest ./policies          # every supported file under a directory
python -m app.cli ingest gs://bucket/inbox   # the Cloud Run job does this
python -m app.cli import-rules rules.csv
python -m app.cli reindex                    # after changing EMBEDDER / EMBEDDING_DIM
"""

import argparse
import asyncio
import logging
from pathlib import Path

from app.container import get_container
from app.rag.parsers import PARSERS, RULE_FORMATS, format_of
from app.services.rule_extraction import parse_rules_file
from app.storage.blobs import GcsBlobStore

SAMPLES = Path(__file__).resolve().parents[1] / "data" / "samples"
log = logging.getLogger("cli")


async def _iter_files(source: str):
    if source.startswith("gs://"):
        bucket, _, prefix = source[5:].partition("/")
        store = GcsBlobStore(bucket)
        for key in await store.list(prefix):
            yield Path(key).name, await store.get(key)
    else:
        for p in sorted(Path(source).rglob("*")):
            if p.is_file():
                yield p.name, p.read_bytes()


async def import_rules(c, data: bytes, filename: str, actor: str) -> int:
    existing = {r.code for r in await c.rules.list(status=None, limit=100_000)}
    new = [
        r for r in parse_rules_file(data, filename) if not r.code or r.code.upper() not in existing
    ]
    await c.rule_service.create_many(new, actor)
    return len(new)


async def ingest(c, source: str, actor: str) -> dict:
    stats = {"documents": 0, "rules": 0, "skipped": 0, "failed": 0}
    async for name, data in _iter_files(source):
        fmt = format_of(name)
        try:
            if fmt in RULE_FORMATS:
                stats["rules"] += await import_rules(c, data, name, actor)
            elif fmt in PARSERS:
                doc = await c.ingestion.ingest(data, name, actor=actor)
                log.info("%-45s %s (%d chunks)", name, doc.status, doc.chunk_count)
                stats["documents"] += 1
            else:
                stats["skipped"] += 1
        except Exception as e:
            log.error("%s: %s", name, e)
            stats["failed"] += 1
    return stats


async def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="python -m app.cli")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("seed")
    p_ing = sub.add_parser("ingest")
    p_ing.add_argument("source")
    p_imp = sub.add_parser("import-rules")
    p_imp.add_argument("file")
    sub.add_parser("reindex")
    parser.add_argument("--actor", default="cli@system")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    c = get_container()
    await c.init()
    try:
        if args.cmd == "seed":
            # rules first, so documents' evidence lines up with rule codes
            print("rules:", await ingest(c, str(SAMPLES / "rules"), args.actor))
            print("documents:", await ingest(c, str(SAMPLES / "documents"), args.actor))
        elif args.cmd == "ingest":
            print(await ingest(c, args.source, args.actor))
        elif args.cmd == "import-rules":
            path = Path(args.file)
            print("imported:", await import_rules(c, path.read_bytes(), path.name, args.actor))
        elif args.cmd == "reindex":
            print("rules reindexed:", await c.rule_service.reindex())
            for d in await c.docs.list(limit=100_000):
                data = await c.ingestion.original_of(d)
                await c.ingestion.docs.delete(d.id)  # force a fresh pass
                await c.ingestion.ingest(
                    data, d.filename, actor=d.uploaded_by, title=d.title, category=d.category
                )
            print("documents reindexed")
    finally:
        await c.close()


if __name__ == "__main__":
    asyncio.run(main())
