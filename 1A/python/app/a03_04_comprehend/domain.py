"""Routing decision (pure logic) and result models. No SDK imports."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Signals:
    language: str
    sentiment: str  # POSITIVE | NEGATIVE | NEUTRAL | MIXED
    sentiment_scores: dict[str, float]
    key_phrases: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Route:
    tier: str  # "fast" | "strong"
    system_prompt: str
    reason: str


@dataclass
class BatchResult:
    ok: dict[int, list[dict]] = field(default_factory=dict)  # input index -> entities
    failed: dict[int, str] = field(default_factory=dict)  # input index -> "ErrorCode: message"


def choose_route(sig: Signals, negative_threshold: float = 0.7) -> Route:
    """Pick prompt + model tier from cheap signals (lecture 51).

    Rules: strongly negative or mixed -> strong model + empathetic prompt; non-English -> answer in that language;
    everything else -> fast model. Thresholds are starting points: tune on labeled traffic.
    """
    negative = sig.sentiment_scores.get("Negative", 0.0)
    lang = f" Reply in the language with code '{sig.language}'." if sig.language != "en" else ""
    topics = f" Customer topics: {', '.join(sig.key_phrases[:5])}." if sig.key_phrases else ""
    if sig.sentiment == "NEGATIVE" and negative >= negative_threshold:
        return Route("strong", "You are a calm, empathetic support agent. Acknowledge the problem first, then give steps." + topics + lang, "negative")
    if sig.sentiment == "MIXED":
        return Route("strong", "You are a careful support agent. Address both the praise and the complaint." + topics + lang, "mixed")
    return Route("fast", "You are a concise support agent." + topics + lang, "default")
