# embeddings Embeddings and Vector Search

> Entry point for embeddings, similarity, exact vs Approximate Nearest Neighbor (ANN) search, quantization, and hybrid retrieval.

## Index

- [1. Source And Scope](#1-source-and-scope)
- [2. One-Minute Version](#2-one-minute-version)
- [3. File Index](#3-file-index)
- [4. Code Map](#4-code-map)
- [References](#references)

## 1. Source And Scope

This component covers the retrieval math under every Retrieval-Augmented Generation (RAG) system.

- Lectures: AIP-C01 #13, #14, #20 (slides p.29–35, 45–48)
- Scope: Python only
- Code: `app/infra/_02rag_01embeddings.py` (Bedrock embeddings) and `app/service/_02rag_01embeddings/similarity.py` (math, exact vs ANN, quantization)
- Terraform: none of its own
  - `bedrock:InvokeModel` on the embedding model belongs to `01bedrock_01converse` ([module](../../terraform/modules/01bedrock_01converse/main.tf))
    - It must list `amazon.titan-embed-text-v2:0`
    - For the Cohere contrast, it must also list `cohere.embed-english-v3`
  - The vector store itself is [opensearch](opensearch.00index.md) (OpenSearch Serverless)
  - The managed pipeline is [knowledge-bases](knowledge-bases.00index.md)
- Numbers: Bedrock User Guide and OpenSearch k-Nearest Neighbors (k-NN) docs, read 2026-11, unless marked "order of magnitude"

## 2. One-Minute Version

RAG retrieves relevant text, puts it in the prompt, then generates.

- **What**
  - RAG = retrieve relevant text, put it in the prompt, then generate
  - An **embedding** = a fixed-length vector whose direction encodes meaning
  - **Vector search** = find the stored vectors nearest to the query vector
- **Why**
  - The model does not know your private or recent data
  - Fine-tuning is slow, costly, and cannot cite sources

    ⇒ retrieval adds knowledge at query time, and is updated by re-indexing

- **How**: see the index-time and query-time flows below
- **Catch**
  - Exact k-Nearest Neighbors (kNN) is O(N·d) per query
    - ⇒ every real store uses ANN (Hierarchical Navigable Small World (HNSW) or Inverted File Index (IVF)), trading recall for speed
  - Index and query must use the same model, dimensions, and normalization
  - Pure vector search misses exact terms (Stock Keeping Units (SKUs), error codes)
    - ⇒ hybrid search (Best Matching 25 (BM25) + vector)
  - Memory is the cost driver
    - 1M × 1024-dim float32 ≈ 4 gigabytes (GB) raw, ≈ 4.6 GB in HNSW
- **Default on Amazon Web Services (AWS)**
  - Titan Text Embeddings V2, 1024 dims, normalized
  - OpenSearch Serverless (HNSW, faiss) behind a Bedrock Knowledge Base

**Index time**

→ chunk documents  
→ embed each chunk  
→ store vector + text + metadata

**Query time**

→ embed the question with the same model  
→ kNN search (top k)  
→ stuff chunks into the prompt  
→ generate with citations

- 🗣 "Retrieval quality caps answer quality: the model can't cite what the retriever never returned."
- 🗣 "ANN is a recall-for-latency trade; ef_search and n_probe are the dials."
- 🗣 "Normalize once at write time, then cosine is just a dot product."

## 3. File Index

Read top to bottom: pipeline, then vectors, then search structures, then retrieval quality.

- **Foundations**
  - [01 RAG pipeline](embeddings.01rag-pipeline.md): why RAG exists, index time vs query time
  - [02 Embedding models](embeddings.02embedding-models.md): Titan V2, Cohere, embedding cache
  - [03 Similarity metrics](embeddings.03similarity-metrics.md): cosine, dot, L2, normalization
- **Search structures**
  - [04 Exact kNN vs ANN](embeddings.04exact-vs-ann.md): brute force, recall@k, the trade triangle
  - [05 HNSW and IVF](embeddings.05hnsw-ivf.md): graph vs inverted-file ANN
  - [06 Quantization](embeddings.06quantization.md): fp16, int8, binary, Product Quantization (PQ), memory math
- **Retrieval quality**
  - [07 Hybrid search and reranking](embeddings.07hybrid-rerank.md): BM25 + vector fusion, cross-encoders
- **Decisions and practice**
  - [98 Tradeoffs](embeddings.98tradeoffs.md): when to use, knobs, store comparison, failure modes
  - [99 Interview](embeddings.99interview.md): Level 4 (L4) + Level 5 (L5) questions

## 4. Code Map

Each concept file maps to Python functions in the new layer-first layout.

| Concept file | Python path | Function / class |
|---|---|---|
| 02 Titan V2 body (dimensions, normalize, embeddingTypes) | `app/infra/_02rag_01embeddings.py` | `titan_body` |
| 02 Embed one text (query time) | `app/infra/_02rag_01embeddings.py` | `embed_text` |
| 02 Embed many texts (bounded parallel, retries) | `app/infra/_02rag_01embeddings.py` | `embed_batch` |
| 02 Cohere asymmetric body (`input_type`) | `app/infra/_02rag_01embeddings.py` | `cohere_body`, `embed_cohere` |
| 02 Embedding cache (content hash + model) | `app/infra/_02rag_01embeddings.py` | `cache_key`, `InMemoryEmbeddingCache`, `CachedTitanEmbedder` |

| Concept file | Python path | Function / class |
|---|---|---|
| 03 Cosine / dot / L2 / normalize | `app/service/_02rag_01embeddings/similarity.py` | `cosine`, `dot`, `l2_distance`, `normalize`, `score` |
| 04 VectorStore port | `app/domain/_02rag_01embeddings.py` | `VectorStore`, `Embedder`, `EmbeddingCache` |
| 04 Exact kNN adapter (ground truth) | `app/service/_02rag_01embeddings/similarity.py` | `ExactVectorStore` |
| 04 recall@k and the n_probe sweep | `app/service/_02rag_01embeddings/similarity.py` | `recall_at_k`, `recall_experiment` |
| 05 ANN (IVF: train, add, probe) | `app/service/_02rag_01embeddings/similarity.py` | `IvfIndex` |
| 05 / 06 Memory math | `app/service/_02rag_01embeddings/similarity.py` | `vector_memory_bytes`, `hnsw_memory_bytes` |

| Concept file | Python path | Function / class |
|---|---|---|
| 06 Binary quantization + Hamming + rescoring | `app/service/_02rag_01embeddings/similarity.py` | `binary_quantize`, `hamming`, `binary_search_with_rescore` |
| Settings (`A_EMBEDDINGS_`) | `app/config/_02rag_01embeddings.py` | `EmbeddingsSettings` |
| Representational State Transfer (REST) | `app/api/_02rag_01embeddings.py` | `router` (`/embeddings/embed`, `/similarity`, `/recall-demo`, `/memory-estimate`) |

- Gaps (doc only)
  - HNSW graph itself
    - Shown in OpenSearch ([opensearch](opensearch.04knn-plugin.md))
    - IVF stands in for "ANN" here
  - PQ encoding (only memory math)
  - Hybrid fusion and reranking calls
    - See [opensearch](opensearch.06filtering-hybrid.md) `hybrid_query`
    - See [knowledge-bases](knowledge-bases.03retrieve.md) `retrieve` with reranking
  - Bedrock batch inference for bulk embedding
  - Multimodal embeddings

## References

- [aws-samples/amazon-bedrock-samples: rag and embeddings notebooks](https://github.com/aws-samples/amazon-bedrock-samples)
- [Bedrock User Guide: Amazon Titan Embeddings Text model parameters](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-titan-embed-text.html)
- [Bedrock User Guide: Cohere Embed models](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-embed.html)
- [OpenSearch docs: k-NN index and memory estimation](https://opensearch.org/docs/latest/search-plugins/knn/knn-index/)
- [Malkov & Yashunin, "Efficient and robust approximate nearest neighbor search using HNSW graphs", 2016](https://arxiv.org/abs/1603.09320)
