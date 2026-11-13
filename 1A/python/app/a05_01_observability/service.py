"""Use cases wiring the sink to the instrumented call."""

from dataclasses import asdict
from typing import Any

from app.a05_01_observability.infra import instrumented_converse, make_sink


def ask(prompt: str) -> dict[str, Any]:
    """One instrumented model call; the sink comes from config (cloudwatch or emf)."""
    return asdict(instrumented_converse(prompt, make_sink()))
