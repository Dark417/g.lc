# data-automation Knowledge Base Parser

> Bedrock Data Automation (BDA) as the parsing strategy of a knowledge base data source: better chunks for extra ingestion cost.

## Index

- [1. BDA As Parser](#1-bda-as-parser)

## 1. BDA As Parser

A knowledge base can hand each file to BDA before chunking, so tables and layout survive as text.

- Knowledge base data source → parsing strategy "Bedrock Data Automation as parser"
- Same idea as foundation-model parsing
  - But BDA handles tables, images and layout
- **Trade-off**
  - Extra per-page parse cost at ingestion
  - Better chunks at query time
- Detail lives in [knowledge-bases](../02rag/knowledge-bases.00index.md)

```python
# illustrative (no repo code): KB data source with BDA parsing
client("bedrock-agent").create_data_source(
    knowledgeBaseId=kb_id,
    name="docs",
    dataSourceConfiguration={"type": "S3", "s3Configuration": {"bucketArn": bucket_arn}},
    vectorIngestionConfiguration={
        "parsingConfiguration": {
            "parsingStrategy": "BEDROCK_DATA_AUTOMATION",  # vs BEDROCK_FOUNDATION_MODEL
            "bedrockDataAutomationConfiguration": {"parsingModality": "MULTIMODAL"},
        }
    },
)
```

- **Catch**: changing the parser requires a re-ingest
- **Catch**: measure the gain with Retrieval-Augmented Generation (RAG) evals
  - See [evaluations](../04safety/evaluations.00index.md)
