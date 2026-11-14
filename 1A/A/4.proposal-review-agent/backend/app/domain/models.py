"""Rules and documents as the rest of the app sees them. Storage-agnostic."""

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field


def utcnow() -> datetime:
    return datetime.now(UTC)


class Severity(StrEnum):
    HARD = "hard"  # a violation blocks, no exceptions
    FLEXIBLE = "flexible"  # a violation is allowed with conditions or an approved exception


class RuleStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    RETIRED = "retired"


class RuleIn(BaseModel):
    code: str | None = Field(default=None, description="e.g. PRIV-003. Generated when omitted.")
    title: str = Field(min_length=3, max_length=200)
    statement: str = Field(min_length=5)
    severity: Severity
    category: str = Field(min_length=2, max_length=60)
    rationale: str = ""
    exception_process: str = ""
    source_document_id: str = ""
    source_ref: str = ""
    status: RuleStatus = RuleStatus.ACTIVE


class RuleUpdate(BaseModel):
    title: str | None = None
    statement: str | None = None
    severity: Severity | None = None
    category: str | None = None
    rationale: str | None = None
    exception_process: str | None = None
    status: RuleStatus | None = None
    change_note: str = ""


class Rule(RuleIn):
    id: str
    code: str
    version: int
    created_by: str
    created_at: datetime
    updated_at: datetime


# LLM-facing schemas have no defaults: Gemini's response_schema rejects default values.
class ProposedRule(BaseModel):
    code: str
    title: str
    statement: str
    severity: Severity
    category: str
    rationale: str
    exception_process: str
    source_ref: str


class ProposedRules(BaseModel):
    rules: list[ProposedRule]


class DocSummary(BaseModel):
    summary: str
    key_points: list[str]
    suggested_category: str


class DocumentStatus(StrEnum):
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class DocumentRecord(BaseModel):
    id: str
    title: str
    filename: str
    format: str
    mime_type: str
    size_bytes: int
    sha256: str
    category: str = ""
    tags: list[str] = []
    status: DocumentStatus = DocumentStatus.PROCESSING
    error: str | None = None
    summary: str = ""
    key_points: list[str] = []
    outline: list[str] = []
    page_count: int | None = None
    chunk_count: int = 0
    blob_uri: str = ""
    text_uri: str = ""
    extracted_rule_codes: list[str] = []
    uploaded_by: str
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
