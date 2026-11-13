"""Bedrock Knowledge Bases showcase (boto3), in the order of docs/02.04.knowledge-bases.md.

- bedrock-agent (control plane): data sources, ingestion jobs (= "sync")
- bedrock-agent-runtime (data plane): Retrieve, RetrieveAndGenerate
- s3: metadata sidecars next to source documents under kb-docs/
- The KB, its data source, and the vector index are created by Terraform (02.04) + Python (02.02 create_kb_index);
  create_data_source here exists to show the chunking console screen as code.
- No AWS call at import time.
"""

import hashlib
import json
import time
import uuid
from typing import Any

from botocore.exceptions import ClientError

from app.a02_04_knowledge_bases.config import get_kb_settings
from app.a02_04_knowledge_bases.domain import (
    TERMINAL_STATUSES,
    Citation,
    IngestionJob,
    IngestionStats,
    RagAnswer,
    RetrievalFilter,
    RetrievedChunk,
)
from app.shared import aws
from app.shared.config import get_settings


def _agent() -> Any:
    return aws.client("bedrock-agent")


def _runtime() -> Any:
    return aws.client("bedrock-agent-runtime")


def client_token(*parts: str) -> str:
    """Idempotency token (API: 33–256 chars). Same inputs ⇒ same token ⇒ a retried call does not start a 2nd job."""
    return hashlib.sha256("|".join(parts).encode()).hexdigest()  # 64 hex chars


# ================================================================ ingestion jobs (sync)


def _to_job(j: dict[str, Any]) -> IngestionJob:
    s = j.get("statistics", {})
    return IngestionJob(
        job_id=j["ingestionJobId"],
        status=j["status"],
        stats=IngestionStats(
            scanned=s.get("numberOfDocumentsScanned", 0),
            metadata_scanned=s.get("numberOfMetadataDocumentsScanned", 0),
            new_indexed=s.get("numberOfNewDocumentsIndexed", 0),
            modified_indexed=s.get("numberOfModifiedDocumentsIndexed", 0),
            deleted=s.get("numberOfDocumentsDeleted", 0),
            failed=s.get("numberOfDocumentsFailed", 0),
            skipped=s.get("numberOfDocumentsSkipped", 0),
        ),
        failure_reasons=j.get("failureReasons", []),
    )


def start_ingestion_job(token: str | None = None, description: str = "") -> IngestionJob:
    """Start a sync: Bedrock scans the S3 prefix, re-processes only new/changed/deleted files (change detection).

    When to use: after uploads, on a schedule, or from an S3 event (service.handle_s3_event).
    Catch: one running job per data source ⇒ ConflictException while another runs (check the quotas page).
    """
    s = get_kb_settings()
    resp = _agent().start_ingestion_job(
        knowledgeBaseId=s.knowledge_base_id,
        dataSourceId=s.data_source_id,
        clientToken=token or client_token(str(uuid.uuid4()), str(uuid.uuid4())),
        description=description or "1A sync",
    )
    return _to_job(resp["ingestionJob"])


def get_ingestion_job(job_id: str) -> IngestionJob:
    s = get_kb_settings()
    resp = _agent().get_ingestion_job(knowledgeBaseId=s.knowledge_base_id, dataSourceId=s.data_source_id, ingestionJobId=job_id)
    return _to_job(resp["ingestionJob"])


def wait_for_ingestion(job_id: str) -> IngestionJob:
    """Poll until COMPLETE / FAILED / STOPPED or the deadline. COMPLETE can still have failed documents:
    always check stats.failed and failure_reasons (bad metadata JSON, file too large, unsupported type)."""
    s = get_kb_settings()
    deadline = time.monotonic() + s.poll_deadline_s
    while True:
        job = get_ingestion_job(job_id)
        if job.status in TERMINAL_STATUSES:
            return job
        if time.monotonic() > deadline:
            raise TimeoutError(f"ingestion job {job_id} still {job.status} after {s.poll_deadline_s}s")
        time.sleep(s.poll_interval_s)


def list_ingestion_jobs(status: str | None = None) -> list[IngestionJob]:
    """All jobs for the data source, newest first, across pages (paginator follows nextToken; maxResults ≤ 1000)."""
    s = get_kb_settings()
    kwargs: dict[str, Any] = {
        "knowledgeBaseId": s.knowledge_base_id,
        "dataSourceId": s.data_source_id,
        "sortBy": {"attribute": "STARTED_AT", "order": "DESCENDING"},
        "PaginationConfig": {"PageSize": 100},
    }
    if status:
        kwargs["filters"] = [{"attribute": "STATUS", "operator": "EQ", "values": [status]}]
    jobs: list[IngestionJob] = []
    for page in _agent().get_paginator("list_ingestion_jobs").paginate(**kwargs):
        for summary in page["ingestionJobSummaries"]:
            jobs.append(_to_job(summary))
    return jobs


# ================================================================ Retrieve (search only, you generate)


def _source_uri(location: dict[str, Any]) -> str:
    kind = location.get("type", "")
    inner = next((v for k, v in location.items() if k.endswith("Location") and isinstance(v, dict)), {})
    return inner.get("uri") or inner.get("url") or kind


def retrieve(
    query: str,
    k: int | None = None,
    search_type: str | None = None,
    flt: RetrievalFilter | None = None,
    rerank: bool = False,
) -> list[RetrievedChunk]:
    """Retrieve = embed query + vector (or hybrid) search + optional rerank; no generation.

    Knobs (vectorSearchConfiguration):
    - numberOfResults 1–100 (default 5)
    - overrideSearchType HYBRID (BM25 + vector; supported stores only) | SEMANTIC (vector only)
    - filter: metadata from sidecars, e.g. and_all(eq("dept", "hr"), gte("year", 2024)); evaluated in the store
    - rerankingConfiguration: a reranker model rescoring a wider candidate set (numberOfRerankedResults)
    When to use: you own the prompt / model call, or you merge results from several sources.
    """
    s = get_kb_settings()
    n = k or s.number_of_results
    vsc: dict[str, Any] = {"numberOfResults": n}
    st = search_type or s.search_type
    if st:
        vsc["overrideSearchType"] = st
    if flt:
        vsc["filter"] = flt
    if rerank:
        vsc["numberOfResults"] = min(100, n * 5)  # wide candidate set for the reranker
        vsc["rerankingConfiguration"] = {
            "type": "BEDROCK_RERANKING_MODEL",
            "bedrockRerankingConfiguration": {
                "modelConfiguration": {"modelArn": s.rerank_model_arn},
                "numberOfRerankedResults": n,
                # Send only useful metadata to the reranker (ALL | SELECTIVE with fieldsToInclude/Exclude).
                "metadataConfiguration": {"selectionMode": "ALL"},
            },
        }
    resp = _runtime().retrieve(
        knowledgeBaseId=s.knowledge_base_id,
        retrievalQuery={"text": query},
        retrievalConfiguration={"vectorSearchConfiguration": vsc},
    )
    return [
        RetrievedChunk(
            text=r["content"].get("text", ""),
            score=r.get("score", 0.0),
            source_uri=_source_uri(r.get("location", {})),
            metadata=r.get("metadata", {}),
        )
        for r in resp["retrievalResults"]
    ]


# ================================================================ RetrieveAndGenerate (managed RAG + citations)

# Placeholders: $search_results$ (required: the retrieved chunks), $query$, $output_format_instructions$
# (keeps the citation format Bedrock parses into `citations`). Check the KB prompt-template docs for the current list.
DEFAULT_PROMPT_TEMPLATE = """You answer questions using only the search results below.
If the results do not contain the answer, say you don't know. Do not use outside knowledge.

<search_results>
$search_results$
</search_results>

$output_format_instructions$

Question: $query$"""


def extract_citations(resp: dict[str, Any]) -> list[Citation]:
    """Map each generated span to the chunks that support it. No citations on a factual claim = a grounding red flag."""
    out: list[Citation] = []
    for c in resp.get("citations", []):
        part = c.get("generatedResponsePart", {}).get("textResponsePart", {})
        span = part.get("span", {})
        refs = c.get("retrievedReferences", [])
        out.append(
            Citation(
                answer_span=part.get("text", ""),
                start=span.get("start", 0),
                end=span.get("end", 0),
                sources=[_source_uri(r.get("location", {})) for r in refs],
                excerpts=[r.get("content", {}).get("text", "")[:300] for r in refs],
            )
        )
    return out


def retrieve_and_generate(
    question: str,
    session_id: str | None = None,
    flt: RetrievalFilter | None = None,
    prompt_template: str | None = None,
    decompose: bool = False,
    use_guardrail: bool = True,
) -> RagAnswer:
    """Managed RAG: retrieve + prompt + generate + citations in one call.

    - sessionId: omit on the first turn; pass the returned id on follow-ups ⇒ Bedrock keeps conversation context
    - generationConfiguration: promptTemplate ($search_results$), inferenceConfig, guardrailConfiguration
    - orchestrationConfiguration.queryTransformationConfiguration QUERY_DECOMPOSITION: split compound questions
    Catch: less control than Retrieve + Converse (one model call, fixed citation format, no streaming here;
    RetrieveAndGenerateStream exists for streaming).
    """
    s = get_kb_settings()
    generation: dict[str, Any] = {
        "promptTemplate": {"textPromptTemplate": prompt_template or DEFAULT_PROMPT_TEMPLATE},
        "inferenceConfig": {"textInferenceConfig": {"maxTokens": 1024, "temperature": 0.0, "topP": 1.0}},
    }
    if use_guardrail and s.guardrail_id:
        # Guardrail screens the query and the generated answer (04.01); guardrailAction reports INTERVENED.
        generation["guardrailConfiguration"] = {"guardrailId": s.guardrail_id, "guardrailVersion": s.guardrail_version}
    vsc: dict[str, Any] = {"numberOfResults": s.number_of_results}
    if s.search_type:
        vsc["overrideSearchType"] = s.search_type
    if flt:
        vsc["filter"] = flt
    kb_config: dict[str, Any] = {
        "knowledgeBaseId": s.knowledge_base_id,
        "modelArn": s.generator_model_id or get_settings().text_model_id,  # model id / inference profile / ARN
        "retrievalConfiguration": {"vectorSearchConfiguration": vsc},
        "generationConfiguration": generation,
    }
    if decompose:
        kb_config["orchestrationConfiguration"] = {"queryTransformationConfiguration": {"type": "QUERY_DECOMPOSITION"}}
    kwargs: dict[str, Any] = {
        "input": {"text": question},
        "retrieveAndGenerateConfiguration": {"type": "KNOWLEDGE_BASE", "knowledgeBaseConfiguration": kb_config},
    }
    if session_id:
        kwargs["sessionId"] = session_id
    resp = _runtime().retrieve_and_generate(**kwargs)
    return RagAnswer(
        text=resp["output"]["text"],
        session_id=resp["sessionId"],
        citations=extract_citations(resp),
        guardrail_action=resp.get("guardrailAction", "NONE"),
    )


# ================================================================ metadata sidecars


def write_metadata_sidecar(document_key: str, attributes: dict[str, str | int | float | bool | list[str]]) -> str:
    """Write s3://bucket/<document_key>.metadata.json next to the document. Attributes become filterable fields.

    Format: {"metadataAttributes": {"dept": "hr", "year": 2025}}. Catch: the sidecar must share the document's
    prefix and name, stay small (check the KB quotas page for the size limit), and a change needs a new sync.
    """
    s = get_kb_settings()
    if not document_key.startswith(s.kb_docs_prefix):
        raise ValueError(f"documents must live under {s.kb_docs_prefix}")
    key = f"{document_key}.metadata.json"
    aws.client("s3").put_object(
        Bucket=get_settings().data_bucket,
        Key=key,
        Body=json.dumps({"metadataAttributes": attributes}).encode(),
        ContentType="application/json",
    )
    return key


# ================================================================ data source as code (chunking console screen)

# Shapes duplicated from 02.03 bedrock_config on purpose (slices stay independent).
CHUNKING_CONFIGS: dict[str, dict[str, Any]] = {
    "FIXED_SIZE": {
        "chunkingStrategy": "FIXED_SIZE",
        "fixedSizeChunkingConfiguration": {"maxTokens": 300, "overlapPercentage": 20},
    },
    "HIERARCHICAL": {
        "chunkingStrategy": "HIERARCHICAL",
        "hierarchicalChunkingConfiguration": {
            "levelConfigurations": [{"maxTokens": 1500}, {"maxTokens": 300}],
            "overlapTokens": 60,
        },
    },
    "SEMANTIC": {
        "chunkingStrategy": "SEMANTIC",
        "semanticChunkingConfiguration": {"maxTokens": 300, "bufferSize": 0, "breakpointPercentileThreshold": 95},
    },
    "NONE": {"chunkingStrategy": "NONE"},
}


def create_data_source(name: str, strategy: str, prefix: str | None = None) -> dict[str, Any]:
    """Create an S3 data source with a chosen chunking strategy (the KB console's data-source screen as code).

    - dataDeletionPolicy: DELETE (vectors removed with the data source) | RETAIN (default; vectors stay)
    - vectorIngestionConfiguration: chunking (immutable after create), optional parsing / custom Lambda
    - clientToken derived from name + strategy ⇒ a retry returns the same data source instead of a duplicate
    When to use: compare strategies side by side on one KB (one data source per strategy and prefix).
    """
    s = get_kb_settings()
    resp = _agent().create_data_source(
        knowledgeBaseId=s.knowledge_base_id,
        clientToken=client_token("data-source", name, strategy),
        name=name,
        description=f"{strategy} chunking over {prefix or s.kb_docs_prefix}",
        dataSourceConfiguration={
            "type": "S3",
            "s3Configuration": {
                "bucketArn": f"arn:aws:s3:::{get_settings().data_bucket}",
                "inclusionPrefixes": [prefix or s.kb_docs_prefix],
            },
        },
        dataDeletionPolicy="DELETE",
        vectorIngestionConfiguration={"chunkingConfiguration": CHUNKING_CONFIGS[strategy]},
    )
    ds = resp["dataSource"]
    return {"data_source_id": ds["dataSourceId"], "status": ds["status"], "name": ds["name"]}


def is_conflict(e: Exception) -> bool:
    return isinstance(e, ClientError) and e.response["Error"]["Code"] == "ConflictException"
