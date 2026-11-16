# chunking Chunking and Pre-Retrieval

> Entry point for splitting documents into retrievable units and reshaping questions before search.

## Index

- [1. Source And Scope](#1-source-and-scope)
- [2. One-Minute Version](#2-one-minute-version)
- [3. File Index](#3-file-index)
- [4. Code Map](#4-code-map)
- [References](#references)

## 1. Source And Scope

This component decides what one vector represents.

- Lectures: AIP-C01 #18, #19 (slides p.39–44)
- Scope: Python only
- Code
  - `app/service/_02rag_03chunking/chunkers.py`: local strategies
  - `app/infra/_02rag_03chunking/bedrock_config.py`: Knowledge Base (KB) `vectorIngestionConfiguration` as code
- Terraform: none of its own
  - The chunking config lives on the KB data source
  - `aws_bedrockagent_data_source.s3` in [modules/02rag_04knowledge_bases](../../terraform/modules/02rag_04knowledge_bases/main.tf)
- Numbers: Bedrock User Guide (Knowledge Bases) and the bedrock-agent Application Programming Interface (API) model, read 2026-11, unless marked "order of magnitude"

## 2. One-Minute Version

Chunking splits documents into the units that get embedded, retrieved, and shown to the model.

- **What**
  - **Chunking** = splitting documents into embedded, retrieved, and shown units
  - **Pre-retrieval** = reshaping the user's question before search (rewrite, decompose, Hypothetical Document Embeddings (HyDE))
- **Why**
  - One vector per whole document blurs many topics into one point ⇒ poor matching
  - The prompt has a token budget ⇒ send the relevant passage, not the book
- **How** (Bedrock KB `chunkingStrategy`)
  - `FIXED_SIZE`: `maxTokens` + `overlapPercentage` (console default 300 / 20%)
  - `HIERARCHICAL`: parent + child `maxTokens`, `overlapTokens` (default 1500 / 300 / 60)
    - Match child, return parent
  - `SEMANTIC`: cut where embedding distance between sentences jumps
    - `breakpointPercentileThreshold`, `bufferSize`, `maxTokens`
  - `NONE`: one chunk per file (pre-chunked or Lambda-chunked)
  - Custom Lambda (`POST_CHUNKING`) for your own logic or metadata
- **Catch**
  - Chunking is fixed per data source (KB user guide)
    - ⇒ changing it = new data source + full re-ingest
  - Small chunks match precisely but lose context
  - Large chunks keep context but match vaguely
  - Hierarchical returns parents
    - ⇒ fewer results than `numberOfResults`, more tokens per result
  - Semantic chunking calls a model at ingestion ⇒ extra cost and time
- **Default**: hierarchical for long structured docs, fixed size 300 / 20% as the baseline
- 🗣 "Chunk size is a precision-vs-context dial; hierarchical chunking turns it into two dials."
- 🗣 "Retrieve small, read big: match the child, hand the model the parent."
- 🗣 "Chunking is a schema decision: changing it means re-ingesting everything."

## 3. File Index

Read from the reason to chunk, through each strategy, to what happens around chunking.

- **Foundations**
  - [01 Why chunk](chunking.01why-chunk.md): the pain, the picture, token approximation
- **Strategies**
  - [02 Fixed size and recursive](chunking.02fixed-recursive.md): sliding window, separator recursion
  - [03 Hierarchical](chunking.03hierarchical.md): parent / child, retrieve small read big
  - [04 Semantic](chunking.04semantic.md): embedding-distance breakpoints
  - [05 None, Lambda, and parsing](chunking.05none-lambda-parsing.md): one chunk per file, custom Lambda, parsers
- **Around chunking**
  - [06 Pre-retrieval and metadata](chunking.06pre-retrieval-metadata.md): rewrite, decomposition, HyDE, enrichment
- **Decisions and practice**
  - [98 Tradeoffs](chunking.98tradeoffs.md): strategy by content, knobs, comparison, failure modes
  - [99 Interview](chunking.99interview.md): Level 4 (L4) + Level 5 (L5) questions

## 4. Code Map

Local chunkers live in the domain layer; KB configs live in the infra layer.

| Concept file | Python path | Function / class |
|---|---|---|
| 01 Token approximation by words | `app/service/_02rag_03chunking/chunkers.py` | `approx_tokens`, `tokens_to_words` |
| 02 Fixed size with overlap | `app/service/_02rag_03chunking/chunkers.py` | `fixed_size_chunks` |
| 02 Recursive splitter on separators | `app/service/_02rag_03chunking/chunkers.py` | `recursive_split` |
| 03 Hierarchical parent/child + id links | `app/service/_02rag_03chunking/chunkers.py` | `hierarchical_chunks`, `expand_to_parents` |
| 04 Semantic breakpoints (percentile) | `app/service/_02rag_03chunking/chunkers.py` | `semantic_chunks`, `split_sentences`, `percentile` |
| 05 None (one chunk per doc) | `app/service/_02rag_03chunking/chunkers.py` | `no_chunking` |

| Concept file | Python path | Function / class |
|---|---|---|
| 04 Embedder port + fake for tests | `app/domain/_02rag_03chunking.py`, `.../chunkers.py` | `Embedder`, `HashingEmbedder` |
| 02–05 KB FIXED_SIZE / HIERARCHICAL / SEMANTIC / NONE | `app/infra/_02rag_03chunking/bedrock_config.py` | `fixed_size_config`, `hierarchical_config`, `semantic_config`, `no_chunking_config`, `config_for` |
| 05 Parsing strategies | `app/infra/_02rag_03chunking/bedrock_config.py` | `with_foundation_model_parsing`, `with_data_automation_parsing` |
| 05 Custom Lambda POST_CHUNKING | `app/infra/_02rag_03chunking/bedrock_config.py` | `with_custom_transformation` |
| Settings (`A_CHUNKING_`) | `app/config/_02rag_03chunking.py` | `ChunkingSettings` |
| Representational State Transfer (REST) | `app/api/_02rag_03chunking.py` | `router` (`/chunking/chunk`, `/recursive`, `/bedrock-config/{strategy}`) |

- Related code in other components
  - Data source with these configs (Software Development Kit (SDK)): `create_data_source` in [knowledge-bases.02ingestion](knowledge-bases.02ingestion.md)
  - Data source in Terraform: `aws_bedrockagent_data_source.s3` (modules/02rag_04knowledge_bases)
- Gaps (doc only)
  - Query rewriting / HyDE / multi-query
    - Decomposition is shown in knowledge-bases `retrieve_and_generate`
  - The custom transformation Lambda itself (only its config)
  - Contextual retrieval enrichment
  - Real tokenizer counts (words approximate tokens)

## References

- [aws-samples/amazon-bedrock-samples: knowledge bases advanced chunking](https://github.com/aws-samples/amazon-bedrock-samples/tree/main/rag)
- [Bedrock User Guide: How content chunking works for knowledge bases](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-chunking.html)
- [Bedrock User Guide: Parsing options for your data source](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-advanced-parsing.html)
- [Gao et al., "Precise Zero-Shot Dense Retrieval without Relevance Labels" (HyDE), 2022](https://arxiv.org/abs/2212.10496)
- [Anthropic, "Introducing Contextual Retrieval", 2024](https://www.anthropic.com/news/contextual-retrieval)
