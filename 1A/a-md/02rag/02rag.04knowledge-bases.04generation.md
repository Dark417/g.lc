# 02rag.04knowledge-bases.04generation Generation

> RetrieveAndGenerate: prompt template, citations, sessions, guardrails, and query decomposition.

## Index

- [1. Prompt Template](#1-prompt-template)
- [2. Citations](#2-citations)
- [3. Sessions](#3-sessions)
- [4. Guardrails](#4-guardrails)
- [5. Query Decomposition](#5-query-decomposition)
- [6. The RetrieveAndGenerate Call](#6-the-retrieveandgenerate-call)

## 1. Prompt Template

`generationConfiguration.promptTemplate.textPromptTemplate` controls grounding.

- `$search_results$` is required
- `$query$` and `$output_format_instructions$` are available
- Dropping `$output_format_instructions$` can break citation parsing
- Instruct "answer only from the results; say you don't know otherwise"

```python
# app/infra/_02rag_04knowledge_bases.py
# $search_results$ (required), $query$, $output_format_instructions$ (keeps the citation
# format Bedrock parses into `citations`). Check the KB prompt-template docs for the current list.
DEFAULT_PROMPT_TEMPLATE = """You answer questions using only the search results below.
If the results do not contain the answer, say you don't know. Do not use outside knowledge.

<search_results>
$search_results$
</search_results>

$output_format_instructions$

Question: $query$"""
```

## 2. Citations

Each citation = a span of the generated text + the retrieved references.

- References carry text, location, metadata
- Show them to users
- Log them for evals (faithfulness, [04safety.03evaluations](../04safety/04safety.03evaluations.00index.md))
- No citations on a factual claim = a grounding red flag

```python
# app/infra/_02rag_04knowledge_bases.py
def extract_citations(resp: dict[str, Any]) -> list[Citation]:
    out: list[Citation] = []
    for c in resp.get("citations", []):
        part = c.get("generatedResponsePart", {}).get("textResponsePart", {})
        span = part.get("span", {})
        refs = c.get("retrievedReferences", [])
        out.append(Citation(
            answer_span=part.get("text", ""),  # the generated sentence(s) this citation supports
            start=span.get("start", 0),
            end=span.get("end", 0),
            sources=[_source_uri(r.get("location", {})) for r in refs],
            excerpts=[r.get("content", {}).get("text", "")[:300] for r in refs],
        ))
    return out
```

## 3. Sessions

Bedrock keeps conversation context when you pass the session id back.

- First call: no `sessionId`; Bedrock returns one
- Follow-ups: pass it back
  - ⇒ Bedrock rewrites the follow-up with conversation context
- Optional `sessionConfiguration.kmsKeyArn`
- Sessions expire (check the docs for the window)

```python
# app/domain/_02rag_04knowledge_bases.py
@dataclass(frozen=True)
class RagAnswer:
    text: str
    session_id: str  # pass back for follow-up questions
    citations: list[Citation]
    guardrail_action: str = "NONE"  # INTERVENED when a guardrail blocked or masked content
```

## 4. Guardrails

A guardrail screens the query and the generated answer ([04safety.01guardrails](../04safety/04safety.01guardrails.00index.md)).

- `generationConfiguration.guardrailConfiguration { guardrailId, guardrailVersion }`
- Response `guardrailAction = INTERVENED` when it blocked or masked
- Use a published version, not DRAFT, in production

```python
# app/config/_02rag_04knowledge_bases.py
guardrail_id: str = ""  # 04safety.01 output; empty = no guardrail on RetrieveAndGenerate
guardrail_version: str = "1"  # a published version; DRAFT only for testing
```

## 5. Query Decomposition

Split compound questions into sub-queries before retrieval.

- `orchestrationConfiguration.queryTransformationConfiguration.type = QUERY_DECOMPOSITION`
- Concept: [02rag.03chunking.06pre-retrieval-metadata](02rag.03chunking.06pre-retrieval-metadata.md)

## 6. The RetrieveAndGenerate Call

Retrieve + prompt + generate + citations in one call.

```python
# app/infra/_02rag_04knowledge_bases.py
def retrieve_and_generate(question, session_id=None, flt=None, prompt_template=None,
                          decompose=False, use_guardrail=True) -> RagAnswer:
    s = get_kb_settings()
    generation: dict[str, Any] = {
        "promptTemplate": {"textPromptTemplate": prompt_template or DEFAULT_PROMPT_TEMPLATE},
        "inferenceConfig": {"textInferenceConfig": {"maxTokens": 1024, "temperature": 0.0, "topP": 1.0}},
    }
    if use_guardrail and s.guardrail_id:
        generation["guardrailConfiguration"] = {"guardrailId": s.guardrail_id, "guardrailVersion": s.guardrail_version}
    vsc: dict[str, Any] = {"numberOfResults": s.number_of_results}  # same retrieval knobs as Retrieve
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
        kwargs["sessionId"] = session_id  # omit on the first turn
    resp = _runtime().retrieve_and_generate(**kwargs)
    return RagAnswer(text=resp["output"]["text"], session_id=resp["sessionId"],
                     citations=extract_citations(resp), guardrail_action=resp.get("guardrailAction", "NONE"))
```

- **Catch**: less control than Retrieve + Converse
  - One model call
  - Fixed citation format
  - No streaming here (`RetrieveAndGenerateStream` exists for streaming)
