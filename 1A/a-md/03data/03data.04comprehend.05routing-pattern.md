# 03data.04comprehend Routing Pattern

> Detect, then decide: cheap Comprehend signals choose the prompt and the model tier before Bedrock answers (lecture 51).

## Index

- [1. Picture](#1-picture)
- [2. Gathering Signals](#2-gathering-signals)
- [3. Choosing The Route](#3-choosing-the-route)
- [4. Answering](#4-answering)

## 1. Picture

A Lambda (here, the service) calls Comprehend first and spends Large Language Model (LLM) tokens only where the signals say it matters.

```text
 request ─► Lambda ─► Comprehend (language, sentiment, key phrases)
                         │ decision
              ┌──────────┴───────────┐
              ▼                      ▼
   fast model + short prompt   strong model + empathetic prompt
              └──────────┬───────────┘
                         ▼ converse → answer
```

Notice both branches end in the same `converse` call; only the model and prompt change.

→ Detect language and sentiment (cheap, deterministic)  
→ Pick prompt template and model tier from the result  
→ Add key phrases to the prompt or to the retrieval query  
⇒ LLM spend goes where it matters; behavior is explainable.

## 2. Gathering Signals

Three cheap calls: language first, then sentiment and key phrases in that language.

```python
# app/domain/_03data_04comprehend.py
@dataclass(frozen=True)
class Signals:
    language: str
    sentiment: str  # POSITIVE | NEGATIVE | NEUTRAL | MIXED
    sentiment_scores: dict[str, float]
    key_phrases: list[str] = field(default_factory=list)
```

```python
# app/service/_03data_04comprehend.py
def gather_signals(text: str) -> Signals:
    lang = detect_dominant_language(text)
    sent = detect_sentiment(text, lang)
    phrases = detect_key_phrases(text, lang)[:5]
    return Signals(lang, sent["Sentiment"], sent["SentimentScore"], phrases)
```

- **Catch**: cache results by text hash for repeated inputs

## 3. Choosing The Route

Routing is pure logic in the domain layer, so it is unit-testable and explainable.

- Strongly negative → strong model + empathetic prompt
- Mixed → strong model + careful prompt
- Non-English → answer in that language
- Everything else → fast model
- Thresholds are starting points
  - Tune on labeled traffic

```python
# app/domain/_03data_04comprehend.py
def choose_route(sig: Signals, negative_threshold: float = 0.7) -> Route:
    negative = sig.sentiment_scores.get("Negative", 0.0)
    lang = f" Reply in the language with code '{sig.language}'." if sig.language != "en" else ""
    topics = f" Customer topics: {', '.join(sig.key_phrases[:5])}." if sig.key_phrases else ""
    if sig.sentiment == "NEGATIVE" and negative >= negative_threshold:
        return Route("strong", "You are a calm, empathetic support agent. Acknowledge the problem first, then give steps." + topics + lang, "negative")
    if sig.sentiment == "MIXED":
        return Route("strong", "You are a careful support agent. Address both the praise and the complaint." + topics + lang, "mixed")
    return Route("fast", "You are a concise support agent." + topics + lang, "default")
```

- **Catch**: misrouting is the main risk
  - Sample and measure
  - Shadow-evaluate routing regularly

## 4. Answering

The route picks the model id and system prompt for one `converse` call.

```python
# app/service/_03data_04comprehend.py
def route_and_answer(text: str) -> dict[str, Any]:
    sig = gather_signals(text)
    route = choose_route(sig, get_comprehend_settings().negative_threshold)
    settings = get_settings()
    model = settings.text_model_id if route.tier == "strong" else settings.fast_model_id
    resp = client("bedrock-runtime").converse(
        modelId=model,
        system=[{"text": route.system_prompt}],
        messages=[{"role": "user", "content": [{"text": text}]}],
        inferenceConfig={"maxTokens": 400, "temperature": 0.2},
    )
    return {
        "route": {"tier": route.tier, "reason": route.reason, "language": sig.language, "sentiment": sig.sentiment},
        "answer": resp["output"]["message"]["content"][0]["text"],
    }
```

```python
# app/api/_03data_04comprehend.py
@router.post("/route")
def route(body: TextRequest) -> dict[str, Any]:
    return service.route_and_answer(body.text)
```

- **Catch**: `Detect*` can raise `UnsupportedLanguageException`
  - A production version falls back to the strong model
