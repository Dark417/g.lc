# chunking.06pre-retrieval-metadata Pre-Retrieval and Metadata Enrichment

> Reshape the question before search, and attach context and filterable attributes to each chunk.

## Index

- [1. Query Rewriting](#1-query-rewriting)
- [2. Query Decomposition](#2-query-decomposition)
- [3. Hypothetical Document Embeddings (HyDE)](#3-hypothetical-document-embeddings-hyde)
- [4. Multi-Query And Cost](#4-multi-query-and-cost)
- [5. Metadata Enrichment](#5-metadata-enrichment)

## 1. Query Rewriting

A Large Language Model (LLM) turns a chatty, context-dependent question into a standalone search query.

- Needed in multi-turn chat ("what about the second one?")
- Bedrock Knowledge Base (KB) sessions do this for follow-ups ([knowledge-bases.04generation](knowledge-bases.04generation.md))

```python
# illustrative: rewrite a follow-up into a standalone query (not in the repo)
REWRITE_PROMPT = (
    "Rewrite the last user question as a standalone search query.\n"
    "Conversation:\n{history}\nQuestion: {question}\nQuery:"
)


def rewrite_query(history: str, question: str, llm) -> str:
    return llm(REWRITE_PROMPT.format(history=history, question=question)).strip()
```

## 2. Query Decomposition

Split a compound question into sub-questions, retrieve for each, merge.

- Bedrock: `orchestrationConfiguration.queryTransformationConfiguration.type = QUERY_DECOMPOSITION`
  - In RetrieveAndGenerate ([knowledge-bases.04generation](knowledge-bases.04generation.md))

```python
# app/infra/_02rag_04knowledge_bases.py  (inside retrieve_and_generate)
if decompose:
    kb_config["orchestrationConfiguration"] = {
        "queryTransformationConfiguration": {"type": "QUERY_DECOMPOSITION"}  # split before retrieval
    }
```

## 3. Hypothetical Document Embeddings (HyDE)

Hypothetical Document Embeddings (Gao et al., 2022) searches with a fake answer.

→ LLM writes a hypothetical answer  
→ embed that answer, not the question  
→ search with it

- Works because answers look more like documents than questions do
- **Risk**: a confidently wrong hypothesis steers retrieval off course

```python
# illustrative: HyDE on top of the repo's embedder and vector store (not in the repo)
def hyde_search(question: str, llm, embedder, store, k: int = 5):
    hypothetical = llm(f"Write a short passage that answers: {question}")
    return store.query(embedder.embed(hypothetical), k)  # embed the answer, not the question
```

## 4. Multi-Query And Cost

Several paraphrases, union of results: a cheap recall boost.

- **Cost**: each technique adds an LLM call before retrieval
  - +hundreds of ms, order of magnitude
- Apply conditionally: multi-turn, long, or vague questions

## 5. Metadata Enrichment

Anything users filter by must be metadata, not hoped-for text similarity.

- **Sidecar** `<file>.metadata.json` in Simple Storage Service (S3)
  - ⇒ attributes for filters (department, year, tenant)
  - See [knowledge-bases.03retrieve](knowledge-bases.03retrieve.md)
- **Contextual headers**: prepend title / section path to each chunk before embedding
  - Anthropic "Contextual Retrieval" (2024) reports fewer retrieval failures
    - By prepending chunk-specific context
- **Custom Lambda**: adds per-chunk metadata (section, page, entity tags)
  - See [05 None, Lambda, and parsing](chunking.05none-lambda-parsing.md)

```python
# app/infra/_02rag_04knowledge_bases.py
def write_metadata_sidecar(document_key: str, attributes: dict[str, str | int | float | bool | list[str]]) -> str:
    s = get_kb_settings()
    if not document_key.startswith(s.kb_docs_prefix):
        raise ValueError(f"documents must live under {s.kb_docs_prefix}")
    key = f"{document_key}.metadata.json"  # same prefix and name as the document
    aws.client("s3").put_object(
        Bucket=get_settings().data_bucket, Key=key,
        Body=json.dumps({"metadataAttributes": attributes}).encode(),
        ContentType="application/json",
    )
    return key
```

- **Gap**: contextual retrieval enrichment is doc only in this repo
