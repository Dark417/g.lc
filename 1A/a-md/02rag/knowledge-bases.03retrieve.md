# knowledge-bases.03retrieve Retrieve, Filters, and Reranking

> Choose between the two query Application Programming Interfaces (APIs), then tune result count, search type, metadata filters, and reranking.

## Index

- [1. Retrieve vs RetrieveAndGenerate](#1-retrieve-vs-retrieveandgenerate)
- [2. Result Count And Search Type](#2-result-count-and-search-type)
- [3. Metadata Filters](#3-metadata-filters)
  - [3.1 Sidecars](#31-sidecars)
  - [3.2 Operators And Builders](#32-operators-and-builders)
- [4. Reranking](#4-reranking)
- [5. The Retrieve Call](#5-the-retrieve-call)

## 1. Retrieve vs RetrieveAndGenerate

Retrieve returns chunks; RetrieveAndGenerate returns an answer.

| Aspect | `Retrieve` | `RetrieveAndGenerate` |
|---|---|---|
| Returns | chunks, scores, locations, metadata | answer, citations, `sessionId` |
| Prompt | yours | template with `$search_results$` |
| Model call | yours (Converse, any model, streaming, tools) | Bedrock's, one model per call |
| Conversation | you manage history | `sessionId` keeps context |
| Use when | agents, custom prompts, multi-source fusion, evals | quick grounded Question and Answer (Q&A) with citations |

- Streaming variant: `RetrieveAndGenerateStream`
- Generation details: [04 Generation](knowledge-bases.04generation.md)

Pick: `Retrieve` + Converse in production services, unless built-in citations and sessions are enough.

## 2. Result Count And Search Type

Two knobs shape the candidate set.

- **`numberOfResults`**: 1–100, default 5
  - Hierarchical chunking dedupes children into parents ⇒ may return fewer
- **`overrideSearchType`**
  - `SEMANTIC`: vector only
  - `HYBRID`: vector + keyword on the text field
    - Only for stores that support it (OpenSearch, and some others; check the Knowledge Base (KB) docs)
  - Unset: Bedrock picks

```python
# app/config/_02rag_04knowledge_bases.py
number_of_results: int = 5  # 1–100; hierarchical chunking may return fewer
search_type: str = "HYBRID"  # HYBRID | SEMANTIC; unset = Bedrock decides per store
```

## 3. Metadata Filters

Filters restrict retrieval to chunks whose sidecar attributes match.

### 3.1 Sidecars

A sidecar JavaScript Object Notation (JSON) next to each document supplies the attributes.

- Path: `s3://…/doc.pdf.metadata.json`
- Body: `{"metadataAttributes": {"dept": "hr", "year": 2025}}`
- Must share the document's prefix and name
- Must stay small (check the KB quotas page for the size limit)
- A change needs a new sync

```python
# app/infra/_02rag_04knowledge_bases.py
def write_metadata_sidecar(document_key: str, attributes: dict[str, str | int | float | bool | list[str]]) -> str:
    s = get_kb_settings()
    if not document_key.startswith(s.kb_docs_prefix):
        raise ValueError(f"documents must live under {s.kb_docs_prefix}")
    key = f"{document_key}.metadata.json"
    aws.client("s3").put_object(
        Bucket=get_settings().data_bucket, Key=key,
        Body=json.dumps({"metadataAttributes": attributes}).encode(),  # attributes become filterable fields
        ContentType="application/json",
    )
    return key
```

### 3.2 Operators And Builders

Filters run inside the vector store query (pre-filter), not after.

- **Operators**
  - `equals`, `notEquals`, `in`, `notIn`
  - `greaterThan[OrEquals]`, `lessThan[OrEquals]`
  - `startsWith`, `stringContains`, `listContains`
  - `andAll`, `orAll` (need at least two members)
- **Implicit filtering** (`implicitFilterConfiguration`)
  - A model derives filters from the query using attribute descriptions
  - Doc only in this repo

```python
# app/domain/_02rag_04knowledge_bases.py
RetrievalFilter = dict[str, Any]


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
```

- **Catch**: filters are an authorization boundary only if enforced server-side
  - Never build the tenant filter from client input

## 4. Reranking

Retrieve wide, rerank to the top few (lecture 81 preview).

- Config: `rerankingConfiguration.bedrockRerankingConfiguration`
  - Reranker `modelArn`
  - `numberOfRerankedResults`
  - Metadata selection: `ALL` | `SELECTIVE` with `fieldsToInclude` / `fieldsToExclude`
- Retrieve wide (e.g. 25), rerank to the top 5
- Models: `amazon.rerank-v1:0`, `cohere.rerank-v3-5:0` (Region availability varies)
- **Cost**: reranker charge per query + latency
- Mechanism: [embeddings.07hybrid-rerank](embeddings.07hybrid-rerank.md)

```python
# app/config/_02rag_04knowledge_bases.py
rerank_model_arn: str = "arn:aws:bedrock:us-east-1::foundation-model/amazon.rerank-v1:0"
```

## 5. The Retrieve Call

Embed query, vector or hybrid search, optional rerank; no generation.

```python
# app/infra/_02rag_04knowledge_bases.py
def retrieve(query: str, k: int | None = None, search_type: str | None = None,
             flt: RetrievalFilter | None = None, rerank: bool = False) -> list[RetrievedChunk]:
    s = get_kb_settings()
    n = k or s.number_of_results
    vsc: dict[str, Any] = {"numberOfResults": n}
    st = search_type or s.search_type
    if st:
        vsc["overrideSearchType"] = st
    if flt:
        vsc["filter"] = flt  # e.g. and_all(eq("dept", "hr"), gte("year", 2024)); evaluated in the store
    if rerank:
        vsc["numberOfResults"] = min(100, n * 5)  # wide candidate set for the reranker
        vsc["rerankingConfiguration"] = {
            "type": "BEDROCK_RERANKING_MODEL",
            "bedrockRerankingConfiguration": {
                "modelConfiguration": {"modelArn": s.rerank_model_arn},
                "numberOfRerankedResults": n,
                "metadataConfiguration": {"selectionMode": "ALL"},
            },
        }
    resp = _runtime().retrieve(
        knowledgeBaseId=s.knowledge_base_id,
        retrievalQuery={"text": query},
        retrievalConfiguration={"vectorSearchConfiguration": vsc},
    )
    return [
        RetrievedChunk(text=r["content"].get("text", ""), score=r.get("score", 0.0),
                       source_uri=_source_uri(r.get("location", {})), metadata=r.get("metadata", {}))
        for r in resp["retrievalResults"]
    ]
```

- **When to use**: you own the prompt / model call, or you merge results from several sources
