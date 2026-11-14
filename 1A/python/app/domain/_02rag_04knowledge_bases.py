"""Models for KB ingestion and retrieval, plus metadata-filter builders. No SDK imports.

Filter builders produce the RetrievalFilter union of the bedrock-agent-runtime API
(equals, notEquals, in, notIn, greaterThan[OrEquals], lessThan[OrEquals], startsWith, stringContains, listContains,
andAll, orAll). Keys are the attribute names from <file>.metadata.json sidecars.
"""

from dataclasses import dataclass, field
from typing import Any

RetrievalFilter = dict[str, Any]

TERMINAL_STATUSES = {"COMPLETE", "FAILED", "STOPPED"}


@dataclass(frozen=True)
class IngestionStats:
    scanned: int = 0
    metadata_scanned: int = 0
    new_indexed: int = 0
    modified_indexed: int = 0
    deleted: int = 0
    failed: int = 0
    skipped: int = 0  # unchanged since last sync (incremental change detection)


@dataclass(frozen=True)
class IngestionJob:
    job_id: str
    status: str  # STARTING | IN_PROGRESS | COMPLETE | FAILED | STOPPING | STOPPED
    stats: IngestionStats = IngestionStats()
    failure_reasons: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RetrievedChunk:
    text: str
    score: float
    source_uri: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Citation:
    answer_span: str  # the generated sentence(s) this citation supports
    start: int
    end: int
    sources: list[str]  # S3 URIs (or other locations) of the supporting chunks
    excerpts: list[str]


@dataclass(frozen=True)
class RagAnswer:
    text: str
    session_id: str  # pass back for follow-up questions (conversation context kept by Bedrock)
    citations: list[Citation]
    guardrail_action: str = "NONE"  # INTERVENED when a guardrail blocked or masked content


def eq(key: str, value: str | int | float | bool) -> RetrievalFilter:
    return {"equals": {"key": key, "value": value}}


def in_(key: str, values: list[str | int | float]) -> RetrievalFilter:
    return {"in": {"key": key, "value": values}}


def gte(key: str, value: int | float) -> RetrievalFilter:
    return {"greaterThanOrEquals": {"key": key, "value": value}}


def and_all(*filters: RetrievalFilter) -> RetrievalFilter:
    # andAll / orAll require at least 2 members: a single filter is passed through unchanged.
    return filters[0] if len(filters) == 1 else {"andAll": list(filters)}


def or_all(*filters: RetrievalFilter) -> RetrievalFilter:
    return filters[0] if len(filters) == 1 else {"orAll": list(filters)}
