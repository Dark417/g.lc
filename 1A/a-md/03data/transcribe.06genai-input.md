# transcribe Generative Artificial Intelligence (GenAI) Input

> Feed a transcript to a Large Language Model (LLM): render turns with timestamps, summarize with Converse, window long calls.

## Index

- [1. Pipeline](#1-pipeline)
- [2. Rendering Turns](#2-rendering-turns)
- [3. Summarizing With Converse](#3-summarizing-with-converse)

## 1. Pipeline

The transcript becomes prompt text and Retrieval-Augmented Generation (RAG) chunks with timestamp metadata.

→ Transcribe (redacted) → chunk by speaker turn or time window  
→ Summarize / extract action items with an LLM  
→ Index chunks (with timestamp metadata) for RAG  
⇒ Long calls exceed context: summarize per window, then reduce.

- Keep timestamps as citation metadata

## 2. Rendering Turns

One line per turn with a timestamp gives the model speaker context cheaply.

```python
# app/domain/_03data_03transcribe.py
def render_turns(t: Transcript) -> str:
    """Text for an LLM prompt: one line per turn with a timestamp."""
    if not t.turns:
        return t.text  # no diarization/channels: plain transcript
    return "\n".join(f"[{x.start:.0f}s] {x.speaker}: {x.text}" for x in t.turns)
```

- **Catch**: speaker labels are `spk_0`, `spk_1`, not names
  - Map to roles (agent, customer) only when channels make it certain

## 3. Summarizing With Converse

A fast model at temperature 0 gives stable short-call summaries.

```python
# app/infra/_03data_03transcribe.py
def summarize(transcript: Transcript, max_tokens: int = 500) -> str:
    resp = client("bedrock-runtime").converse(
        modelId=get_settings().fast_model_id,
        system=[{"text": "Summarize the call in 5 bullets and list action items. Do not invent facts."}],
        messages=[{"role": "user", "content": [{"text": render_turns(transcript)}]}],
        inferenceConfig={"maxTokens": max_tokens, "temperature": 0.0},  # 0 keeps summaries stable
    )
    return resp["output"]["message"]["content"][0]["text"]
```

- **Catch**: send the REDACTED transcript only
- **Catch**: for short calls only
  - Window and reduce for long ones
