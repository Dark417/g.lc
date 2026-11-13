"""Lecture 51 pattern: Comprehend signals -> route -> Bedrock converse."""

from typing import Any

from app.a03_04_comprehend.config import get_comprehend_settings
from app.a03_04_comprehend.domain import Signals, choose_route
from app.a03_04_comprehend.infra import detect_dominant_language, detect_key_phrases, detect_sentiment
from app.shared.aws import client
from app.shared.config import get_settings


def gather_signals(text: str) -> Signals:
    """Three cheap calls: language, then sentiment + key phrases in that language."""
    lang = detect_dominant_language(text)
    sent = detect_sentiment(text, lang)
    phrases = detect_key_phrases(text, lang)[:5]
    return Signals(lang, sent["Sentiment"], sent["SentimentScore"], phrases)


def route_and_answer(text: str) -> dict[str, Any]:
    """Detect sentiment + key phrases, choose prompt and model tier, call converse.

    Catch: Detect* can raise UnsupportedLanguageException; a production version falls back to the strong model.
    """
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
