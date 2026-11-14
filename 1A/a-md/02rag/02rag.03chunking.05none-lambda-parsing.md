# 02rag.03chunking.05none-lambda-parsing None, Custom Lambda, and Parsing

> Skip chunking, own it with a Lambda, and fix parsing before any chunking choice matters.

## Index

- [1. None](#1-none)
- [2. Custom Transformation Lambda](#2-custom-transformation-lambda)
- [3. Parsing Before Chunking](#3-parsing-before-chunking)
  - [3.1 Parsers](#31-parsers)
  - [3.2 Parsing Config](#32-parsing-config)
- [4. Chunking Is Immutable](#4-chunking-is-immutable)

## 1. None

Each file becomes one chunk.

- Use when files are already chunk-sized (one Frequently Asked Question (FAQ) per file)
- Use when files are pre-chunked upstream

```python
# app/service/_02rag_03chunking/chunkers.py
def no_chunking(text: str, doc_id: str = "doc") -> list[Chunk]:
    n = len(_words(text))
    return [Chunk(id=_chunk_id(doc_id, 0, n, text), text=text, start_word=0, end_word=n)]
```

```python
# app/infra/_02rag_03chunking/bedrock_config.py
def no_chunking_config() -> Config:
    """NONE: each file is one chunk. Pre-chunked files or a custom Lambda does the chunking."""
    return {"chunkingConfiguration": {"chunkingStrategy": ChunkingStrategy.NONE.value}}
```

- **Catch**: a long document becomes one blurred vector
  - It may exceed the embedding model's input limit

## 2. Custom Transformation Lambda

A Lambda runs after chunking to modify chunks and metadata.

- Config: `customTransformationConfiguration { intermediateStorage.s3Location, transformations: [{ stepToApply: POST_CHUNKING, lambdaArn }] }`
- The Lambda reads chunk batches from intermediate Simple Storage Service (S3)
  - Returns modified chunks and metadata
- Pair with `NONE` to own chunking end to end
- Pair with any strategy to enrich metadata
- **Cost**: you own the Lambda's latency, errors, and scaling during ingestion

```python
# app/infra/_02rag_03chunking/bedrock_config.py
def with_custom_transformation(config: Config, lambda_arn: str, intermediate_s3_uri: str) -> Config:
    return config | {
        "customTransformationConfiguration": {
            "intermediateStorage": {"s3Location": {"uri": intermediate_s3_uri}},  # Lambda reads/writes batches here
            "transformations": [
                {"stepToApply": "POST_CHUNKING",
                 "transformationFunction": {"transformationLambdaConfiguration": {"lambdaArn": lambda_arn}}}
            ],
        }
    }
```

- **Gap**: the repo has only the config, not the Lambda itself

## 3. Parsing Before Chunking

No chunking strategy recovers a table that was flattened into word soup.

### 3.1 Parsers

Three parsers trade ingestion cost against fidelity.

- **Default parser**
  - Extracts text from txt, md, html, doc/docx, csv, xls/xlsx, pdf
  - Tables and images in Portable Document Format files (PDFs) lose structure
- **Foundation-model parser** (`BEDROCK_FOUNDATION_MODEL`)
  - A multimodal model reads each page; optional `parsingPrompt`
  - Better tables and figures
  - Costs model tokens per page
- **Bedrock Data Automation parser** (`BEDROCK_DATA_AUTOMATION`, [03data.01data-automation](../03data/03data.01data-automation.00index.md))
  - Managed extraction of text, tables, figures
  - `parsingModality: MULTIMODAL` keeps images for multimodal retrieval
- **Newer values**: `SMART_PARSING` and `MULTI_MODAL_EMBEDDINGS` (boto3 1.44 Application Programming Interface (API) model)
  - ⇒ check the Knowledge Base (KB) parsing docs before relying on them
- **Rule**: fix parsing first

### 3.2 Parsing Config

Parsing composes with any chunking strategy.

```python
# app/infra/_02rag_03chunking/bedrock_config.py
def with_foundation_model_parsing(config: Config, model_arn: str, prompt: str | None = None) -> Config:
    fm: dict[str, Any] = {"modelArn": model_arn}
    if prompt:
        fm["parsingPrompt"] = {"parsingPromptText": prompt}  # e.g. force Markdown tables
    return config | {"parsingConfiguration": {
        "parsingStrategy": "BEDROCK_FOUNDATION_MODEL", "bedrockFoundationModelConfiguration": fm}}


def with_data_automation_parsing(config: Config, multimodal: bool = False) -> Config:
    bda: dict[str, Any] = {"parsingModality": "MULTIMODAL"} if multimodal else {}
    return config | {"parsingConfiguration": {
        "parsingStrategy": "BEDROCK_DATA_AUTOMATION", "bedrockDataAutomationConfiguration": bda}}
```

- **Catch**: Foundation Model (FM) parsing costs per page at ingestion
  - Apply it only to the documents that need it (separate data source)

## 4. Chunking Is Immutable

Amazon Web Services (AWS) docs say chunking can't be changed after the data source is created.

- New strategy = new data source (or recreate) + full re-ingest
- `create_data_source` in [02rag.04knowledge-bases.02ingestion](02rag.04knowledge-bases.02ingestion.md) duplicates these shapes on purpose
  - Components stay independent

```python
# app/infra/_02rag_03chunking/bedrock_config.py
def config_for(strategy: ChunkingStrategy) -> Config:
    return {
        ChunkingStrategy.FIXED_SIZE: fixed_size_config,
        ChunkingStrategy.HIERARCHICAL: hierarchical_config,
        ChunkingStrategy.SEMANTIC: semantic_config,
        ChunkingStrategy.NONE: no_chunking_config,
    }[strategy]()  # defaults mirror the Bedrock console
```
