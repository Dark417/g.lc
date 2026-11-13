"""Comprehend + Comprehend Medical SDK calls, one function per API."""

from typing import Any

from app.a03_04_comprehend.config import get_comprehend_settings
from app.a03_04_comprehend.domain import BatchResult
from app.shared.aws import client


def _c() -> Any:
    return client("comprehend")


def _trim(text: str) -> str:
    """Cut to max bytes on a UTF-8 boundary (the sync APIs limit input size in bytes)."""
    return text.encode()[: get_comprehend_settings().max_text_bytes].decode(errors="ignore")


# ---------------------------------------------------------------- 1.2 Detect* APIs


def detect_entities(text: str, lang: str | None = None) -> list[dict[str, Any]]:
    """DetectEntities: PERSON, ORGANIZATION, LOCATION, DATE, ... Catch: filter by Score; offsets are character offsets."""
    cfg = get_comprehend_settings()
    resp = _c().detect_entities(Text=_trim(text), LanguageCode=lang or cfg.default_language)
    return [e for e in resp["Entities"] if e["Score"] >= cfg.min_entity_score]


def detect_key_phrases(text: str, lang: str | None = None) -> list[str]:
    """DetectKeyPhrases: noun phrases sorted by Score. Use for tags or retrieval query expansion."""
    resp = _c().detect_key_phrases(Text=_trim(text), LanguageCode=lang or get_comprehend_settings().default_language)
    return [p["Text"] for p in sorted(resp["KeyPhrases"], key=lambda p: -p["Score"])]


def detect_sentiment(text: str, lang: str | None = None) -> dict[str, Any]:
    """DetectSentiment: whole-text label + scores. Catch: a MIXED label hides which part is negative."""
    return _c().detect_sentiment(Text=_trim(text), LanguageCode=lang or get_comprehend_settings().default_language)


def detect_targeted_sentiment(text: str, lang: str | None = None) -> list[dict[str, Any]]:
    """DetectTargetedSentiment: sentiment per entity mention (which thing is liked or hated). English only at the time of writing: check."""
    resp = _c().detect_targeted_sentiment(Text=_trim(text), LanguageCode=lang or get_comprehend_settings().default_language)
    return resp["Entities"]


def detect_dominant_language(text: str) -> str:
    """DetectDominantLanguage: best language code. No language input; run it first on mixed traffic."""
    langs = _c().detect_dominant_language(Text=_trim(text))["Languages"]
    return max(langs, key=lambda x: x["Score"])["LanguageCode"] if langs else get_comprehend_settings().default_language


def detect_syntax(text: str, lang: str | None = None) -> list[dict[str, Any]]:
    """DetectSyntax: tokens with part-of-speech tags. Rarely needed once an LLM is in the loop."""
    resp = _c().detect_syntax(Text=_trim(text), LanguageCode=lang or get_comprehend_settings().default_language)
    return [{"text": t["Text"], "pos": t["PartOfSpeech"]["Tag"]} for t in resp["SyntaxTokens"]]


# ---------------------------------------------------------------- batch with partial failures


def batch_detect_entities(texts: list[str], lang: str | None = None) -> BatchResult:
    """BatchDetectEntities in chunks of batch_size (25); per-item failures come back in ErrorList, not as exceptions.

    Catch: indexes in the response are relative to the chunk; we map them back to the global input index.
    """
    cfg = get_comprehend_settings()
    out = BatchResult()
    for start in range(0, len(texts), cfg.batch_size):
        chunk = [_trim(t) for t in texts[start : start + cfg.batch_size]]
        resp = _c().batch_detect_entities(TextList=chunk, LanguageCode=lang or cfg.default_language)
        for item in resp["ResultList"]:
            out.ok[start + item["Index"]] = [e for e in item["Entities"] if e["Score"] >= cfg.min_entity_score]
        for err in resp["ErrorList"]:
            out.failed[start + err["Index"]] = f"{err['ErrorCode']}: {err['ErrorMessage']}"
    return out


# ---------------------------------------------------------------- Comprehend Medical (lecture 52)


def detect_entities_v2(text: str) -> list[dict[str, Any]]:
    """Comprehend Medical DetectEntitiesV2: medications, conditions, tests with traits (negation...).

    Catch: input length is limited (characters, check the quota page); never log the text (PHI).
    """
    return client("comprehendmedical").detect_entities_v2(Text=text)["Entities"]


def detect_phi(text: str) -> list[dict[str, Any]]:
    """Comprehend Medical DetectPHI: protected health information spans (NAME, DATE, ID, ...)."""
    return client("comprehendmedical").detect_phi(Text=text)["Entities"]


def infer_icd10cm(text: str) -> list[dict[str, Any]]:
    """InferICD10CM: link conditions to ICD-10-CM codes with scores. Catch: candidates, not coding decisions."""
    return client("comprehendmedical").infer_icd10_cm(Text=text)["Entities"]
