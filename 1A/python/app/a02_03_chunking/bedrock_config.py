"""Bedrock KB vectorIngestionConfiguration dicts, exactly as bedrock-agent CreateDataSource takes them.

- 02.04 (create_data_source) duplicates these shapes on purpose: slices stay independent.
- Ranges below come from the botocore model for bedrock-agent (boto3 1.44, read 2026-11).
- Chunking is fixed per data source: AWS docs say it can't be changed after creation
  ⇒ new strategy = new data source (or recreate) + full re-ingest.
"""

from typing import Any

from app.a02_03_chunking.domain import ChunkingStrategy

Config = dict[str, Any]


def _check(name: str, value: int, lo: int, hi: int | None = None) -> None:
    if value < lo or (hi is not None and value > hi):
        raise ValueError(f"{name}={value} outside [{lo}, {hi if hi is not None else '∞'}]")


# ================================================================ chunking strategies


def fixed_size_config(max_tokens: int = 300, overlap_percentage: int = 20) -> Config:
    """FIXED_SIZE: maxTokens 1–8192 (keep under the embedding model's limit), overlapPercentage 1–99.

    Default console values: 300 tokens, 20% overlap. Trade: bigger chunks = more context per hit, blurrier vectors.
    """
    _check("maxTokens", max_tokens, 1, 8192)
    _check("overlapPercentage", overlap_percentage, 1, 99)
    return {
        "chunkingConfiguration": {
            "chunkingStrategy": ChunkingStrategy.FIXED_SIZE.value,
            "fixedSizeChunkingConfiguration": {"maxTokens": max_tokens, "overlapPercentage": overlap_percentage},
        }
    }


def hierarchical_config(parent_max_tokens: int = 1500, child_max_tokens: int = 300, overlap_tokens: int = 60) -> Config:
    """HIERARCHICAL: levelConfigurations = [parent, child] (two levels), each maxTokens 1–8192; overlapTokens ≥ 1.

    Children are embedded and matched; parents are returned. Default console values: 1500 / 300 / 60.
    Catch: Retrieve may return fewer results than numberOfResults (children collapse into one parent).
    """
    _check("parent maxTokens", parent_max_tokens, 1, 8192)
    _check("child maxTokens", child_max_tokens, 1, 8192)
    _check("overlapTokens", overlap_tokens, 1)
    if child_max_tokens >= parent_max_tokens:
        raise ValueError("child chunks must be smaller than parent chunks")
    return {
        "chunkingConfiguration": {
            "chunkingStrategy": ChunkingStrategy.HIERARCHICAL.value,
            "hierarchicalChunkingConfiguration": {
                "levelConfigurations": [{"maxTokens": parent_max_tokens}, {"maxTokens": child_max_tokens}],
                "overlapTokens": overlap_tokens,
            },
        }
    }


def semantic_config(max_tokens: int = 300, buffer_size: int = 0, breakpoint_percentile_threshold: int = 95) -> Config:
    """SEMANTIC: maxTokens 1–8192, bufferSize 0–1 (neighbour sentences per side), breakpointPercentileThreshold 50–99.

    Higher threshold = fewer breaks = larger chunks. Catch: uses a foundation model during ingestion ⇒ extra cost.
    """
    _check("maxTokens", max_tokens, 1, 8192)
    _check("bufferSize", buffer_size, 0, 1)
    _check("breakpointPercentileThreshold", breakpoint_percentile_threshold, 50, 99)
    return {
        "chunkingConfiguration": {
            "chunkingStrategy": ChunkingStrategy.SEMANTIC.value,
            "semanticChunkingConfiguration": {
                "maxTokens": max_tokens,
                "bufferSize": buffer_size,
                "breakpointPercentileThreshold": breakpoint_percentile_threshold,
            },
        }
    }


def no_chunking_config() -> Config:
    """NONE: each file is one chunk. Use for pre-chunked files or when a custom Lambda does the chunking."""
    return {"chunkingConfiguration": {"chunkingStrategy": ChunkingStrategy.NONE.value}}


def config_for(strategy: ChunkingStrategy) -> Config:
    return {
        ChunkingStrategy.FIXED_SIZE: fixed_size_config,
        ChunkingStrategy.HIERARCHICAL: hierarchical_config,
        ChunkingStrategy.SEMANTIC: semantic_config,
        ChunkingStrategy.NONE: no_chunking_config,
    }[strategy]()


# ================================================================ parsing strategies (compose with any chunking)


def with_foundation_model_parsing(config: Config, model_arn: str, prompt: str | None = None) -> Config:
    """parsingStrategy BEDROCK_FOUNDATION_MODEL: a multimodal FM reads PDFs, tables, images into text.

    Default (no parsingConfiguration) = text extraction only. Catch: per-page FM cost at ingestion.
    """
    fm: dict[str, Any] = {"modelArn": model_arn}
    if prompt:
        fm["parsingPrompt"] = {"parsingPromptText": prompt}
    return config | {"parsingConfiguration": {"parsingStrategy": "BEDROCK_FOUNDATION_MODEL", "bedrockFoundationModelConfiguration": fm}}


def with_data_automation_parsing(config: Config, multimodal: bool = False) -> Config:
    """parsingStrategy BEDROCK_DATA_AUTOMATION: BDA extracts text, tables, figures (03.01). parsingModality MULTIMODAL
    also keeps images for multimodal retrieval. Newer values (SMART_PARSING, MULTI_MODAL_EMBEDDINGS) exist in the
    API model; check the KB parsing docs before relying on them."""
    bda: dict[str, Any] = {"parsingModality": "MULTIMODAL"} if multimodal else {}
    return config | {"parsingConfiguration": {"parsingStrategy": "BEDROCK_DATA_AUTOMATION", "bedrockDataAutomationConfiguration": bda}}


def with_custom_transformation(config: Config, lambda_arn: str, intermediate_s3_uri: str) -> Config:
    """Custom Lambda after chunking (stepToApply POST_CHUNKING): enrich metadata, or re-chunk your way
    (pair with NONE). The Lambda reads/writes batches in the intermediate S3 location."""
    return config | {
        "customTransformationConfiguration": {
            "intermediateStorage": {"s3Location": {"uri": intermediate_s3_uri}},
            "transformations": [
                {"stepToApply": "POST_CHUNKING", "transformationFunction": {"transformationLambdaConfiguration": {"lambdaArn": lambda_arn}}}
            ],
        }
    }
