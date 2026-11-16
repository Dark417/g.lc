# comprehend Why And Application Programming Interfaces (APIs)

> Why Comprehend exists and what each Detect* Application Programming Interface (API) returns, with one function per API.

## Index

- [1. Why It Was Created](#1-why-it-was-created)
- [2. API Catalog](#2-api-catalog)
- [3. Entities And Key Phrases](#3-entities-and-key-phrases)
- [4. Sentiment](#4-sentiment)
- [5. Language And Syntax](#5-language-and-syntax)

## 1. Why It Was Created

Comprehend packages the common Natural Language Processing (NLP) tasks as API calls.

- **The pain**: NLP needed trained models per task and per language
- **Use cases**
  - Voice-of-customer sentiment, topic extraction
  - Language detection to route to a translation or the right index
  - Medical text → coded entities

## 2. API Catalog

Each API answers one narrow question about a text.

| API | Returns | Notes |
|---|---|---|
| `DetectEntities` | PERSON, ORGANIZATION, LOCATION, DATE, QUANTITY, ... with score and offsets | Custom entity recognizer via `EndpointArn` |
| `DetectKeyPhrases` | Noun phrases with score | Good for tagging, search facets |
| `DetectSentiment` | POSITIVE / NEGATIVE / NEUTRAL / MIXED + scores | Whole text |
| `DetectTargetedSentiment` | Sentiment per entity mention | Where the opinion lands |

| API | Returns | Notes |
|---|---|---|
| `DetectDominantLanguage` | Language codes + scores | No language input needed |
| `DetectSyntax` | Tokens with part-of-speech | Rarely needed with Large Language Models (LLMs) |
| `ClassifyDocument` | Class labels | Needs a custom classifier endpoint (or a flywheel) |
| `DetectPiiEntities` | Personally Identifiable Information (PII) spans | See [pii-redaction](../04safety/pii-redaction.00index.md) |

- Batch and async variants: see [02 Batch And Async](comprehend.02batch-and-async.md)

## 3. Entities And Key Phrases

Entities give typed spans; key phrases give tags and query expansion terms.

- Filter entities by `Score`
  - ~0.8 is a common start; tune on your data
- Offsets are character offsets
- Pass `LanguageCode` when known

```python
# app/infra/_03data_04comprehend.py
def detect_entities(text: str, lang: str | None = None) -> list[dict[str, Any]]:
    cfg = get_comprehend_settings()
    resp = _c().detect_entities(Text=_trim(text), LanguageCode=lang or cfg.default_language)
    return [e for e in resp["Entities"] if e["Score"] >= cfg.min_entity_score]  # drop low confidence


def detect_key_phrases(text: str, lang: str | None = None) -> list[str]:
    """Noun phrases sorted by Score. Use for tags or retrieval query expansion."""
    resp = _c().detect_key_phrases(Text=_trim(text), LanguageCode=lang or get_comprehend_settings().default_language)
    return [p["Text"] for p in sorted(resp["KeyPhrases"], key=lambda p: -p["Score"])]
```

- **Catch**: entity types are fixed
  - New types need a custom entity recognizer ([03 Custom Models](comprehend.03custom-models.md))

## 4. Sentiment

Whole-text sentiment is one label; targeted sentiment says which thing is liked or hated.

```python
# app/infra/_03data_04comprehend.py
def detect_sentiment(text: str, lang: str | None = None) -> dict[str, Any]:
    """Whole-text label + scores. Catch: a MIXED label hides which part is negative."""
    return _c().detect_sentiment(Text=_trim(text), LanguageCode=lang or get_comprehend_settings().default_language)


def detect_targeted_sentiment(text: str, lang: str | None = None) -> list[dict[str, Any]]:
    """Sentiment per entity mention. English only at the time of writing: check."""
    resp = _c().detect_targeted_sentiment(Text=_trim(text), LanguageCode=lang or get_comprehend_settings().default_language)
    return resp["Entities"]
```

- **Catch**: sentiment of a truncated text is partial
  - Wrong routing follows; use full text and thresholds on score
- **Catch**: sarcasm and domain slang ⇒ LLM

## 5. Language And Syntax

Language detection needs no language input, so it runs first on mixed traffic.

```python
# app/infra/_03data_04comprehend.py
def detect_dominant_language(text: str) -> str:
    langs = _c().detect_dominant_language(Text=_trim(text))["Languages"]
    # best code by score; fall back to the default when nothing is detected
    return max(langs, key=lambda x: x["Score"])["LanguageCode"] if langs else get_comprehend_settings().default_language


def detect_syntax(text: str, lang: str | None = None) -> list[dict[str, Any]]:
    """Tokens with part-of-speech tags. Rarely needed once an LLM is in the loop."""
    resp = _c().detect_syntax(Text=_trim(text), LanguageCode=lang or get_comprehend_settings().default_language)
    return [{"text": t["Text"], "pos": t["PartOfSpeech"]["Tag"]} for t in resp["SyntaxTokens"]]
```

```python
# app/api/_03data_04comprehend.py
@router.post("/analyze")
def analyze(body: TextRequest) -> dict[str, Any]:
    sig = service.gather_signals(body.text)
    return {"language": sig.language, "sentiment": sig.sentiment, "key_phrases": sig.key_phrases,
            "entities": infra.detect_entities(body.text, sig.language)}
```

- **Catch**: `UnsupportedLanguageException` when the API lacks the language
  - Detect language first; fall back to the LLM
