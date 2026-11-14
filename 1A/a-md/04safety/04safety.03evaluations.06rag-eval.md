# 04safety.03evaluations.06rag-eval Evaluating Retrieval-Augmented Generation (RAG)

> Score retrieval and generation separately so a bad answer points at the stage that failed (lecture 21).

## Index

- [1. Two Stages, Two Metric Families](#1-two-stages-two-metric-families)
- [2. Diagnosis Grid](#2-diagnosis-grid)
- [3. Code: Retrieval-Augmented Generation (RAG) Eval Job](#3-code-retrieval-augmented-generation-rag-eval-job)
- [4. Online Counterpart](#4-online-counterpart)

Back to [00index](04safety.03evaluations.00index.md).

## 1. Two Stages, Two Metric Families

Retrieval metrics say whether the right context arrived; generation metrics say whether the model used it.

| Stage | Question | Bedrock metric | Classic Information Retrieval (IR) metric |
|---|---|---|---|
| Retrieval | Did the right chunks come back? | ContextRelevance, ContextCoverage | recall@k, precision@k, Mean Reciprocal Rank (MRR), Normalized Discounted Cumulative Gain (nDCG) |
| Generation | Did the answer use them correctly? | Faithfulness, Correctness, Completeness, Citation* | — |
| End to end | Is the user helped? | Helpfulness, LogicalCoherence, Refusal | task success rate |

## 2. Diagnosis Grid

→ Low context relevance.  
→ Fix retrieval: chunking, embeddings, hybrid search, reranking, metadata filters (02rag.x).

→ High context relevance, low faithfulness.  
→ Fix generation: prompt, model, guardrail grounding threshold ([04safety.01guardrails](04safety.01guardrails.00index.md)).

→ Low coverage.  
⇒ Top-k too small or chunks too narrow.

- Retrieve-only eval is cheaper and isolates the vector store
  - run it first on every chunking/embedding change
- Include unanswerable questions to test refusals and faithfulness

## 3. Code: Retrieval-Augmented Generation (RAG) Eval Job

- `applicationType = RagEvaluation`, always judged by an evaluator model
- `retrieve_only=True`
  - `retrieveConfig` + ContextRelevance/ContextCoverage
- `False`
  - `retrieveAndGenerateConfig` + Correctness/Faithfulness/…
- `taskType` is ignored for RAG

```python
# app/infra/_04safety_03evaluations.py  (create_rag_eval, trimmed)
search = {"vectorSearchConfiguration": {"numberOfResults": s.rag_number_of_results}}  # 1..100
if retrieve_only:
    kind = JobKind.RAG_RETRIEVE
    names = list(metrics or RAG_RETRIEVE_METRICS)
    kb_config: Json = {"retrieveConfig": {"knowledgeBaseId": kb, "knowledgeBaseRetrievalConfiguration": search}}
else:
    kind = JobKind.RAG_RETRIEVE_GENERATE
    names = list(metrics or ("Builtin.Correctness", "Builtin.Completeness", "Builtin.Faithfulness",
                             "Builtin.Helpfulness"))
    kb_config = {
        "retrieveAndGenerateConfig": {
            "type": "KNOWLEDGE_BASE",  # or EXTERNAL_SOURCES (documents passed inline)
            "knowledgeBaseConfiguration": {
                "knowledgeBaseId": kb,
                "modelArn": model_arn(generator_model_id or _generator()),  # ARN, not a bare model id
                "retrievalConfiguration": search,
                "generationConfiguration": {
                    "kbInferenceConfig": {"textInferenceConfig": {"maxTokens": 512, "temperature": 0.0}}
                },
            },
        }
    }
req = _common(kind, client_token) | {
    "applicationType": "RagEvaluation",
    "evaluationConfig": {
        "automated": {
            "datasetMetricConfigs": [
                {
                    "taskType": "QuestionAndAnswer",
                    "dataset": {"name": "rag-golden", "datasetLocation": {"s3Uri": dataset_uri}},
                    "metricNames": names,
                }
            ],
            "evaluatorModelConfig": {
                "bedrockEvaluatorModels": [{"modelIdentifier": judge_model_id or s.judge_model_id}]
            },
        }
    },
    "inferenceConfig": {"ragConfigs": [{"knowledgeBaseConfig": kb_config}]},
}
```

```python
# app/infra/_04safety_03evaluations.py
def model_arn(model_id: str) -> str:
    """RAG retrieveAndGenerate needs an ARN: inference profile (geo-prefixed id) or foundation model."""
    if model_id.startswith("arn:"):
        return model_id
    region = get_settings().aws_region
    if model_id.startswith(GEO_PREFIXES):  # us. eu. apac. global. ...
        return f"arn:aws:bedrock:{region}:{_account_id()}:inference-profile/{model_id}"
    return f"arn:aws:bedrock:{region}::foundation-model/{model_id}"
```

- Catch
  - `numberOfResults` trades coverage vs noise
    - coverage low ⇒ raise it

## 4. Online Counterpart

- Guardrails contextual grounding scores per request
  - = a free faithfulness signal in production
- Sampled judging and grounding scores feed failures back into the offline set
  - see [08offline-online](04safety.03evaluations.08offline-online.md)
